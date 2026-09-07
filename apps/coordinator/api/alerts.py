"""
System Alerts and Outage Incident API (Used by n8n and internal monitors)
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import AlertDB
from packages.shared.models.schemas import AlertCreateRequest, AlertResponse
from packages.shared.models.enums import UserRole
from apps.coordinator.api.deps import get_current_user, require_role

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
async def list_alerts(
    unresolved_only: bool = True,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    query = select(AlertDB).order_by(AlertDB.created_at.desc())
    if unresolved_only:
        query = query.where(AlertDB.is_resolved == False)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return [AlertResponse.model_validate(a) for a in alerts]

@router.post("", response_model=AlertResponse)
async def create_alert(
    req: AlertCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
):
    alert = AlertDB(
        title=req.title,
        severity=req.severity,
        source=req.source,
        details=req.details,
        is_resolved=False
    )
    db.add(alert)
    await db.commit()
    return AlertResponse.model_validate(alert)

@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
):
    result = await db.execute(select(AlertDB).where(AlertDB.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    await db.commit()
    return AlertResponse.model_validate(alert)
