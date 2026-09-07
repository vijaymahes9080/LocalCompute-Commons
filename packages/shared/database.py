"""
Database Engine, Session, and Lifecycle Management
"""
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from packages.shared.config import settings
from packages.shared.models.db_models import Base, UserDB, OrganizationDB
from packages.shared.models.enums import UserRole, TrustLevel
import bcrypt

logger = logging.getLogger("localcompute.database")

# Setup async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def hash_password_sync(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

async def init_db():
    """Initializes schema and provisions default organization and admin user."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed Default Organization and Admin User
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        # Check org
        result = await session.execute(
            select(OrganizationDB).where(OrganizationDB.slug == "default-lab")
        )
        org = result.scalar_one_or_none()
        if not org:
            org = OrganizationDB(
                name="Default Research Lab",
                slug="default-lab",
                trust_level=TrustLevel.TRUSTED_LAB,
                description="Default primary research cluster organization"
            )
            session.add(org)
            await session.flush()

        # Check admin user
        result = await session.execute(
            select(UserDB).where(UserDB.username == settings.DEFAULT_ADMIN_USERNAME)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            admin = UserDB(
                username=settings.DEFAULT_ADMIN_USERNAME,
                email=settings.DEFAULT_ADMIN_EMAIL,
                password_hash=hash_password_sync(settings.DEFAULT_ADMIN_PASSWORD),
                full_name="Cluster Administrator",
                role=UserRole.ADMIN,
                organization_id=org.id,
                is_active=True
            )
            session.add(admin)

            # Also create an operator user for tests/evaluation
            operator = UserDB(
                username="operator1",
                email="operator@localcompute.local",
                password_hash=hash_password_sync("OperatorPassword2026!"),
                full_name="Lab Operator",
                role=UserRole.OPERATOR,
                organization_id=org.id,
                is_active=True
            )
            session.add(operator)

            # And a standard researcher user
            researcher = UserDB(
                username="researcher1",
                email="researcher@localcompute.local",
                password_hash=hash_password_sync("ResearcherPassword2026!"),
                full_name="AI Researcher",
                role=UserRole.USER,
                organization_id=org.id,
                is_active=True
            )
            session.add(researcher)

            await session.commit()
            logger.info("Initialized default database seed records.")
