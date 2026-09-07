"""
Administrative Approval Management API
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import ApprovalDB, AuditEventDB
from packages.shared.models.schemas import ApprovalResponse, ApprovalDecisionRequest
from packages.shared.models.enums import ApprovalStatus, UserRole, AuditEventType
from packages.shared.security.crypto import compute_audit_event_hash
from apps.coordinator.api.deps import get_current_user, require_role
from apps.coordinator.core.approval_engine import ApprovalEngine

router = APIRouter(prefix="/approvals", tags=["Approvals"])

@router.get("", response_model=List[ApprovalResponse])
async def list_approvals(
    status: Optional[ApprovalStatus] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    query = select(ApprovalDB).order_by(ApprovalDB.created_at.desc())
    if status:
        query = query.where(ApprovalDB.status == status)
    result = await db.execute(query)
    approvals = result.scalars().all()
    return [ApprovalResponse.model_validate(a) for a in approvals]

@router.post("/{approval_id}/decide", response_model=ApprovalResponse)
async def decide_approval(
    approval_id: str,
    req: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
):
    result = await db.execute(select(ApprovalDB).where(ApprovalDB.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Approval is already {approval.status.value}")

    approval.approver_user_id = user.id
    approval.approver_username = user.username
    approval.decision_reason = req.reason
    approval.decided_at = datetime.utcnow()
    
    if req.approved:
        approval.status = ApprovalStatus.APPROVED
        await ApprovalEngine.execute_approved_action(
            session=db,
            approval=approval,
            approver_id=user.id,
            approver_username=user.username
        )
    else:
        approval.status = ApprovalStatus.REJECTED

    # Audit
    ev_hash = compute_audit_event_hash(
        AuditEventType.APPROVAL_RESOLVED.value,
        user.id,
        approval.id,
        datetime.utcnow().isoformat(),
        {"approved": req.approved, "action": approval.action.value, "reason": req.reason}
    )
    audit = AuditEventDB(
        event_type=AuditEventType.APPROVAL_RESOLVED,
        actor_id=user.id,
        actor_role=user.role.value,
        target_type="approval",
        target_id=approval.id,
        action_details={"approved": req.approved, "action": approval.action.value},
        event_hash=ev_hash
    )
    db.add(audit)
    await db.commit()

    return ApprovalResponse.model_validate(approval)
