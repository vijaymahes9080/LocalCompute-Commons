"""
FastAPI Dependencies: Authentication, RBAC, and Context Ingestion
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import UserDB, WorkerNodeDB
from packages.shared.models.enums import UserRole
from packages.shared.security.auth import decode_token
from services.monitoring.logger import (
    ctx_request_id, ctx_job_id, ctx_task_id, ctx_worker_id
)

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserDB:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(credentials.credentials)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        
    result = await db.execute(select(UserDB).where(UserDB.username == username))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")
    return user

def require_role(*required_roles: UserRole):
    """RBAC dependency gatekeeper."""
    async def role_checker(current_user: UserDB = Depends(get_current_user)) -> UserDB:
        if current_user.role not in required_roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of roles: {[r.value for r in required_roles]}"
            )
        return current_user
    return role_checker

async def get_current_worker(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> WorkerNodeDB:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Worker token missing")
    try:
        payload = decode_token(credentials.credentials)
        node_id = payload.get("node_id") or payload.get("sub")
        if not node_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid worker token")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid worker credentials")

    result = await db.execute(select(WorkerNodeDB).where(WorkerNodeDB.node_id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker node not registered")
    
    ctx_worker_id.set(node.node_id)
    return node
