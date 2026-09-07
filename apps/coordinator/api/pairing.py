"""
Node Mutual Pairing API Router
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from packages.shared.database import get_db
from packages.shared.models.enums import UserRole
from packages.shared.security.auth import create_node_token
from apps.coordinator.api.deps import get_current_user, require_role
from services.worker_agent.pairing import pairing_engine

router = APIRouter(prefix="/pairing", tags=["Node Pairing"])

class GeneratePairingResponse(BaseModel):
    code: str
    expires_in_seconds: int = 300
    qr_payload: str

class ClaimPairingRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)
    node_id: str
    node_name: str

class ClaimPairingResponse(BaseModel):
    node_id: str
    token: str
    status: str = "paired"

@router.post("/generate", response_model=GeneratePairingResponse)
async def generate_pairing_code(
    user=Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
):
    code, secret = pairing_engine.generate_pairing_code(user.organization_id)
    qr_payload = f"localcompute://pair?code={code}&org={user.organization_id or ''}"
    return GeneratePairingResponse(
        code=code,
        expires_in_seconds=300,
        qr_payload=qr_payload
    )

@router.post("/claim", response_model=ClaimPairingResponse)
async def claim_pairing(req: ClaimPairingRequest):
    session = pairing_engine.claim_pairing_code(req.code)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid, expired, or already claimed pairing code")
        
    token = create_node_token(req.node_id, session.organization_id)
    return ClaimPairingResponse(
        node_id=req.node_id,
        token=token,
        status="paired"
    )
