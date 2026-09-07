"""
Cluster Capacity & Compute Snapshot API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import (
    WorkerNodeDB, JobDB, JobTaskDB, CapacitySnapshotDB
)
from packages.shared.models.schemas import (
    CapacitySnapshot, WorkerNodeResponse, NodeCapability
)
from packages.shared.models.enums import JobState, TaskState
from services.monitoring.snapshots import generate_cluster_capacity_snapshot
from apps.coordinator.api.deps import get_current_user

router = APIRouter(prefix="/capacity", tags=["Capacity"])

@router.get("/snapshot", response_model=CapacitySnapshot)
async def get_capacity_snapshot(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    # Query current nodes
    n_res = await db.execute(select(WorkerNodeDB))
    db_nodes = n_res.scalars().all()
    node_schemas = [
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
        for n in db_nodes
    ]

    # Active jobs
    j_res = await db.execute(select(JobDB).where(JobDB.state.in_([JobState.QUEUED, JobState.RUNNING])))
    active_jobs = len(j_res.scalars().all())

    # Tasks
    pending_res = await db.execute(select(JobTaskDB).where(JobTaskDB.state.in_([TaskState.QUEUED, TaskState.RETRYING])))
    pending_tasks = len(pending_res.scalars().all())

    running_res = await db.execute(select(JobTaskDB).where(JobTaskDB.state == TaskState.RUNNING))
    running_tasks = len(running_res.scalars().all())

    snapshot = generate_cluster_capacity_snapshot(
        nodes=node_schemas,
        active_jobs=active_jobs,
        pending_tasks=pending_tasks,
        running_tasks=running_tasks
    )

    # Persist snapshot record
    db_snap = CapacitySnapshotDB(
        total_nodes=snapshot.total_nodes,
        online_nodes=snapshot.online_nodes,
        paused_nodes=snapshot.paused_nodes,
        total_cpu_cores=snapshot.total_cpu_cores,
        available_cpu_cores=snapshot.available_cpu_cores,
        total_memory_gb=snapshot.total_memory_gb,
        available_memory_gb=snapshot.available_memory_gb,
        total_vram_gb=snapshot.total_vram_gb,
        available_vram_gb=snapshot.available_vram_gb,
        cached_models_summary=snapshot.cached_models_summary,
        active_jobs=snapshot.active_jobs,
        pending_tasks=snapshot.pending_tasks,
        running_tasks=snapshot.running_tasks,
        avg_queue_wait_seconds=snapshot.avg_queue_wait_seconds
    )
    db.add(db_snap)
    await db.commit()

    return snapshot
