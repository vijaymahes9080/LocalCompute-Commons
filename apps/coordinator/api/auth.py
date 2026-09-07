"""
Authentication API Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import UserDB
from packages.shared.models.schemas import UserCreate, UserResponse, Token
from packages.shared.security.auth import (
    verify_password, get_password_hash,
    create_access_token, create_refresh_token, decode_token
)
from apps.coordinator.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(credentials: dict, db: AsyncSession = Depends(get_db)):
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
        
    result = await db.execute(select(UserDB).where(UserDB.username == username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
        
    access_token = create_access_token({"sub": user.username, "role": user.role.value, "org_id": user.organization_id})
    refresh_token = create_refresh_token({"sub": user.username, "role": user.role.value})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=3600,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserDB = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(body: dict, db: AsyncSession = Depends(get_db)):
    refresh_token = body.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        username = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(UserDB).where(UserDB.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token({"sub": user.username, "role": user.role.value, "org_id": user.organization_id})
    new_refresh = create_refresh_token({"sub": user.username, "role": user.role.value})
    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=3600,
        user=UserResponse.model_validate(user)
    )
