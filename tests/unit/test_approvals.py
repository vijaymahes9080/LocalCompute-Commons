"""
Unit Tests for Administrative Approval Workflows
"""
import pytest
from packages.shared.models.enums import ApprovalAction, ApprovalStatus, UserRole, NodeStatus
from apps.coordinator.core.approval_engine import ApprovalEngine
from packages.shared.models.db_models import WorkerNodeDB
from sqlalchemy import select

@pytest.mark.asyncio
async def test_approval_requirement_triggers():
    # Revoke node requires approval
    assert ApprovalEngine.requires_approval(ApprovalAction.REVOKE_NODE, {}, UserRole.ADMIN) is True
    
    # Extended pause > 60 min requires approval
    assert ApprovalEngine.requires_approval(ApprovalAction.PAUSE_NODE_EXTENDED, {"duration_minutes": 120}, UserRole.OPERATOR) is True
    assert ApprovalEngine.requires_approval(ApprovalAction.PAUSE_NODE_EXTENDED, {"duration_minutes": 30}, UserRole.OPERATOR) is False

    # Bulk cancel > 5 jobs requires approval
    assert ApprovalEngine.requires_approval(ApprovalAction.BULK_CANCEL_JOBS, {"job_count": 10}, UserRole.OPERATOR) is True
    assert ApprovalEngine.requires_approval(ApprovalAction.BULK_CANCEL_JOBS, {"job_count": 2}, UserRole.OPERATOR) is False

@pytest.mark.asyncio
async def test_approval_creation_and_execution(db_session):
    # Request node revocation approval
    approval = await ApprovalEngine.request_approval(
        session=db_session,
        action=ApprovalAction.REVOKE_NODE,
        requester_id="user-operator-1",
        requester_username="operator1",
        target_id="node-alpha",
        target_type="worker_node",
        reason="Suspected firmware compromise",
        parameters={"node_id": "node-alpha"}
    )
    
    assert approval.id is not None
    assert approval.status == ApprovalStatus.PENDING

    # Execute approved action
    await ApprovalEngine.execute_approved_action(
        session=db_session,
        approval=approval,
        approver_id="user-admin-1",
        approver_username="admin"
    )

    # Verify node status updated to REVOKED
    res = await db_session.execute(select(WorkerNodeDB).where(WorkerNodeDB.node_id == "node-alpha"))
    node = res.scalar_one_or_none()
    assert node.status == NodeStatus.REVOKED
