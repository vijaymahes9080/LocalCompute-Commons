"""
Worker Node Lifecycle and Telemetry API
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import (
    WorkerNodeDB, NodeHeartbeatDB, AuditEventDB
)
from packages.shared.models.schemas import (
    WorkerNodeRegisterRequest, WorkerNodeResponse,
    NodeHeartbeatRequest, NodeHeartbeatResponse,
    NodeCapability
)
from packages.shared.models.enums import (
    NodeStatus, UserRole, AuditEventType, ApprovalAction
)
from packages.shared.security.auth import create_node_token
from packages.shared.security.crypto import compute_audit_event_hash
from apps.coordinator.api.deps import get_current_user, require_role, get_current_worker
from apps.coordinator.core.approval_engine import ApprovalEngine
from services.monitoring.logger import logger

router = APIRouter(prefix="/nodes", tags=["Worker Nodes"])

@router.post("/register", response_model=WorkerNodeResponse)
async def register_node(
    req: WorkerNodeRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WorkerNodeDB).where(WorkerNodeDB.node_id == req.node_id)
    )
    node = result.scalar_one_or_none()
    
    token = create_node_token(req.node_id, req.organization_id)
    
    if node:
        # Update existing node
        node.node_name = req.node_name
        node.capabilities = req.capabilities.model_dump(mode="json")
        node.trust_level = req.trust_level
        node.is_localhost = req.is_localhost
        node.is_airgapped = req.is_airgapped
        node.endpoint_url = req.endpoint_url
        node.status = NodeStatus.ONLINE
        node.last_heartbeat_at = datetime.utcnow()
    else:
        node = WorkerNodeDB(
            node_id=req.node_id,
            node_name=req.node_name,
            organization_id=req.organization_id,
            capabilities=req.capabilities.model_dump(mode="json"),
            trust_level=req.trust_level,
            is_localhost=req.is_localhost,
            is_airgapped=req.is_airgapped,
            endpoint_url=req.endpoint_url,
            status=NodeStatus.ONLINE,
            last_heartbeat_at=datetime.utcnow()
        )
        db.add(node)
        
    await db.flush()

    # Record Audit
    ev_hash = compute_audit_event_hash(
        AuditEventType.NODE_REGISTERED.value,
        req.node_id,
        node.id,
        datetime.utcnow().isoformat(),
        {"node_name": req.node_name, "trust_level": req.trust_level.value}
    )
    audit = AuditEventDB(
        event_type=AuditEventType.NODE_REGISTERED,
        actor_id=req.node_id,
        actor_role="worker",
        target_type="worker_node",
        target_id=node.id,
        action_details={"node_name": req.node_name, "trust_level": req.trust_level.value},
        event_hash=ev_hash
    )
    db.add(audit)
    await db.commit()

    resp = WorkerNodeResponse(
        id=node.id,
        node_id=node.node_id,
        node_name=node.node_name,
        organization_id=node.organization_id,
        status=node.status,
        trust_level=node.trust_level,
        is_localhost=node.is_localhost,
        is_airgapped=node.is_airgapped,
        capabilities=NodeCapability.model_validate(node.capabilities),
        last_heartbeat_at=node.last_heartbeat_at,
        registered_at=node.registered_at,
        consecutive_failures=node.consecutive_failures,
        active_leases_count=node.active_leases_count,
        token=token
    )
    return resp

@router.post("/heartbeat", response_model=NodeHeartbeatResponse)
async def heartbeat_node(
    req: NodeHeartbeatRequest,
    worker: WorkerNodeDB = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db)
):
    worker.last_heartbeat_at = datetime.utcnow()
    worker.capabilities = req.capabilities.model_dump(mode="json")
    worker.active_leases_count = len(req.active_tasks)
    
    # Store heartbeat record
    hb = NodeHeartbeatDB(
        node_id=worker.id,
        cpu_utilization_pct=req.capabilities.cpu_utilization_pct,
        memory_available_mb=req.capabilities.memory_available_mb,
        vram_available_mb=req.capabilities.vram_available_mb or 0,
        battery_level=req.capabilities.battery_level,
        is_charging=req.capabilities.is_charging,
        network_mbps=req.capabilities.network_mbps,
        clock_skew_ms=req.capabilities.clock_skew_ms,
        active_tasks_count=len(req.active_tasks)
    )
    db.add(hb)
    await db.commit()
    
    return NodeHeartbeatResponse(
        acknowledged=True,
        status=worker.status,
        server_time=datetime.utcnow()
    )

@router.get("", response_model=List[WorkerNodeResponse])
async def list_nodes(
    status: Optional[NodeStatus] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    query = select(WorkerNodeDB)
    if status:
        query = query.where(WorkerNodeDB.status == status)
    result = await db.execute(query)
    nodes = result.scalars().all()
    
    return [
        WorkerNodeResponse(
            id=n.id,
            node_id=n.node_id,
            node_name=n.node_name,
            organization_id=n.organization_id,
            status=n.status,
            trust_level=n.trust_level,
            is_localhost=n.is_localhost,
            is_airgapped=n.is_airgapped,
            capabilities=NodeCapability.model_validate(n.capabilities),
            last_heartbeat_at=n.last_heartbeat_at,
            registered_at=n.registered_at,
            consecutive_failures=n.consecutive_failures,
            active_leases_count=n.active_leases_count
        )
        for n in nodes
    ]

@router.post("/{node_id}/pause")
async def pause_node(
    node_id: str,
    duration_minutes: int = 30,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
):
    result = await db.execute(select(WorkerNodeDB).where(WorkerNodeDB.node_id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if duration_minutes > 60:
        # Requires approval
        approval = await ApprovalEngine.request_approval(
            session=db,
            action=ApprovalAction.PAUSE_NODE_EXTENDED,
            requester_id=user.id,
            requester_username=user.username,
            target_id=node.node_id,
            target_type="worker_node",
            reason=f"Extended pause requested for {duration_minutes} minutes",
            parameters={"duration_minutes": duration_minutes}
        )
        return {"status": "approval_required", "approval_id": approval.id}

    node.status = NodeStatus.PAUSED
    await db.commit()
    return {"status": "paused", "node_id": node_id}

@router.post("/{node_id}/resume")
async def resume_node(
    node_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.OPERATOR, UserRole.ADMIN))
):
    result = await db.execute(select(WorkerNodeDB).where(WorkerNodeDB.node_id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    node.status = NodeStatus.ONLINE
    await db.commit()
    return {"status": "online", "node_id": node_id}

@router.post("/{node_id}/revoke")
async def revoke_node(
    node_id: str,
    reason: str = "Administrative security policy enforcement",
    force: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(UserRole.ADMIN))
):
    result = await db.execute(select(WorkerNodeDB).where(WorkerNodeDB.node_id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Non-negotiable rule 5: Require explicit approval for node revocation
    approval = await ApprovalEngine.request_approval(
        session=db,
        action=ApprovalAction.REVOKE_NODE,
        requester_id=user.id,
        requester_username=user.username,
        target_id=node.node_id,
        target_type="worker_node",
        reason=reason,
        parameters={"node_id": node.node_id, "node_name": node.node_name}
    )
    return {
        "status": "approval_required",
        "approval_id": approval.id,
        "message": "Node revocation request submitted for administrative multi-party authorization."
    }
