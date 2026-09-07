"""
Audit Trail Query API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import AuditEventDB
from packages.shared.models.schemas import AuditEventResponse
from packages.shared.models.enums import AuditEventType
from apps.coordinator.api.deps import get_current_user

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("", response_model=List[AuditEventResponse])
async def list_audit_events(
    event_type: Optional[AuditEventType] = None,
    target_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    query = select(AuditEventDB).order_by(AuditEventDB.timestamp.desc()).limit(limit)
    if event_type:
        query = query.where(AuditEventDB.event_type == event_type)
    if target_id:
        query = query.where(AuditEventDB.target_id == target_id)
    result = await db.execute(query)
    events = result.scalars().all()
    return [AuditEventResponse.model_validate(e) for e in events]
