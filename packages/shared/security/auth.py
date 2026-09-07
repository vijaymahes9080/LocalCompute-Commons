"""
JWT Authentication, Password Hashing and Token Rotation
"""
import time
from datetime import timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
from packages.shared.config import settings
from packages.shared.models.enums import UserRole

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expires_seconds = int(expires_delta.total_seconds()) if expires_delta else (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    now_ts = int(time.time())
    to_encode.update({
        "exp": now_ts + expires_seconds,
        "iat": now_ts,
        "type": "access"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    expires_seconds = int(expires_delta.total_seconds()) if expires_delta else (settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)
    now_ts = int(time.time())
    to_encode.update({
        "exp": now_ts + expires_seconds,
        "iat": now_ts,
        "type": "refresh"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_node_token(
    node_id: str,
    org_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    expires_seconds = int(expires_delta.total_seconds()) if expires_delta else (settings.NODE_TOKEN_EXPIRE_HOURS * 3600)
    now_ts = int(time.time())
    payload = {
        "sub": node_id,
        "node_id": node_id,
        "org_id": org_id,
        "role": UserRole.OPERATOR.value,
        "type": "worker",
        "exp": now_ts + expires_seconds,
        "iat": now_ts
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
