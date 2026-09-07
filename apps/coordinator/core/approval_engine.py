"""
Administrative Approval Engine and Gatekeeper
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from packages.shared.models.db_models import ApprovalDB, AuditEventDB, WorkerNodeDB, JobDB
from packages.shared.models.enums import (
    ApprovalAction, ApprovalStatus, NodeStatus, JobState, AuditEventType, UserRole
)
from packages.shared.security.crypto import compute_audit_event_hash
from services.monitoring.logger import logger

class ApprovalRequiredError(Exception):
    def __init__(self, approval_id: str, message: str):
        super().__init__(message)
        self.approval_id = approval_id

class ApprovalEngine:
    """
    Guards sensitive cluster operations, enforcing multi-party authorization or operator review.
    """
    @staticmethod
    def requires_approval(action: ApprovalAction, parameters: Dict[str, Any], user_role: UserRole) -> bool:
        """Determines if the action requires explicit approval workflow."""
        if action == ApprovalAction.REVOKE_NODE:
            return True
        if action == ApprovalAction.MODIFY_TRUST_POLICY:
            return True
        if action == ApprovalAction.FORCED_SHUTDOWN:
            return True
        if action == ApprovalAction.BULK_CANCEL_JOBS:
            job_count = parameters.get("job_count", 1)
            return job_count > 5
        if action == ApprovalAction.PAUSE_NODE_EXTENDED:
            duration_minutes = parameters.get("duration_minutes", 0)
            return duration_minutes > 60
        return False

    @staticmethod
    async def request_approval(
        session: AsyncSession,
        action: ApprovalAction,
        requester_id: str,
        requester_username: str,
        target_id: str,
        target_type: str,
        reason: str,
        parameters: Dict[str, Any],
        expires_in_hours: int = 24
    ) -> ApprovalDB:
        """Creates a pending approval record and audits the request."""
        approval = ApprovalDB(
            action=action,
            requester_user_id=requester_id,
            requester_username=requester_username,
            target_id=target_id,
            target_type=target_type,
            reason=reason,
            parameters=parameters,
            status=ApprovalStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=expires_in_hours)
        )
        session.add(approval)
        await session.flush()

        # Audit
        ev_hash = compute_audit_event_hash(
            AuditEventType.APPROVAL_REQUESTED.value,
            requester_id,
            approval.id,
            datetime.utcnow().isoformat(),
            {"action": action.value, "target_id": target_id, "reason": reason}
        )
        audit = AuditEventDB(
            event_type=AuditEventType.APPROVAL_REQUESTED,
            actor_id=requester_id,
            actor_role="user",
            target_type="approval",
            target_id=approval.id,
            action_details={"action": action.value, "target_id": target_id, "reason": reason},
            event_hash=ev_hash
        )
        session.add(audit)
        await session.commit()
        return approval

    @staticmethod
    async def execute_approved_action(
        session: AsyncSession,
        approval: ApprovalDB,
        approver_id: str,
        approver_username: str
    ):
        """Executes the gated action after successful approval."""
        if approval.action == ApprovalAction.REVOKE_NODE:
            from sqlalchemy import select
            res = await session.execute(
                select(WorkerNodeDB).where(WorkerNodeDB.node_id == approval.target_id)
            )
            node = res.scalar_one_or_none()
            if node:
                node.status = NodeStatus.REVOKED
                logger.warning(f"Node {node.node_id} has been REVOKED following approval {approval.id}")
                
        elif approval.action == ApprovalAction.BULK_CANCEL_JOBS:
            from sqlalchemy import select
            job_ids = approval.parameters.get("job_ids", [])
            for jid in job_ids:
                res = await session.execute(
                    select(JobDB).where(JobDB.id == jid)
                )
                j = res.scalar_one_or_none()
                if j and j.state not in [JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED]:
                    j.state = JobState.CANCELLED
            logger.warning(f"Bulk cancelled {len(job_ids)} jobs following approval {approval.id}")

        await session.commit()
