"""
Pytest Fixtures for LocalCompute Commons Test Suite
"""
import pytest
import pytest_asyncio
import os
import sys
import asyncio
from typing import AsyncGenerator

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

TEST_DB_PATH = os.path.abspath("test_localcompute_suite.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Set test environment variables
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-unit-tests-12345"
os.environ["MOCK_INFERENCE"] = "true"

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import packages.shared.database as db_module
from packages.shared.models.db_models import Base, UserDB, OrganizationDB, WorkerNodeDB
from packages.shared.models.enums import UserRole, TrustLevel, NodeStatus
from packages.shared.security.auth import get_password_hash, create_access_token
from apps.coordinator.main import app

# Create shared engine and sessionmaker
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

# Patch shared database module to use the test engine
db_module.engine = test_engine
db_module.AsyncSessionLocal = TestSessionLocal

@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        # Seed test organization
        org = OrganizationDB(
            id="test-org-1",
            name="Test Lab Org",
            slug="test-lab",
            trust_level=TrustLevel.TRUSTED_LAB
        )
        session.add(org)

        # Seed admin
        admin = UserDB(
            id="user-admin-1",
            username="admin",
            email="admin@test.local",
            password_hash=get_password_hash("AdminLocalCompute2026!"),
            role=UserRole.ADMIN,
            organization_id=org.id
        )
        session.add(admin)

        # Seed operator
        operator = UserDB(
            id="user-operator-1",
            username="operator1",
            email="operator@test.local",
            password_hash=get_password_hash("OperatorPassword2026!"),
            role=UserRole.OPERATOR,
            organization_id=org.id
        )
        session.add(operator)

        # Seed user
        user = UserDB(
            id="user-researcher-1",
            username="researcher1",
            email="researcher@test.local",
            password_hash=get_password_hash("ResearcherPassword2026!"),
            role=UserRole.USER,
            organization_id=org.id
        )
        session.add(user)

        # Seed worker node
        node = WorkerNodeDB(
            id="node-db-1",
            node_id="node-alpha",
            node_name="Lab-Alpha",
            organization_id=org.id,
            status=NodeStatus.ONLINE,
            trust_level=TrustLevel.TRUSTED_LAB,
            is_localhost=True,
            capabilities={
                "cpu_cores": 16,
                "cpu_utilization_pct": 10.0,
                "memory_mb": 32768,
                "memory_available_mb": 24576,
                "gpu_name": "RTX 4090",
                "vram_mb": 24576,
                "vram_available_mb": 20480,
                "os_name": "Linux",
                "os_version": "6.5.0",
                "cached_models": ["llama3:8b", "mistral:7b"],
                "battery_level": 100.0,
                "is_charging": True,
                "power_state": "ac",
                "network_mbps": 1000.0,
                "clock_skew_ms": 2.0
            }
        )
        session.add(node)
        await session.commit()
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[db_module.get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def admin_token() -> str:
    return create_access_token({"sub": "admin", "role": UserRole.ADMIN.value})

@pytest.fixture
def user_token() -> str:
    return create_access_token({"sub": "researcher1", "role": UserRole.USER.value})
