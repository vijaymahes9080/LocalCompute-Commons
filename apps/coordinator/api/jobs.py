"""
Job Lifecycle Management and Inspection API
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import JobDB, JobTaskDB, AuditEventDB
from packages.shared.models.schemas import JobResponse, JobDetailResponse, JobTaskResponse
from packages.shared.models.enums import JobState, TaskState, AuditEventType, UserRole
from packages.shared.security.crypto import compute_audit_event_hash
from apps.coordinator.api.deps import get_current_user, require_role

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobResponse])
async def list_jobs(
    state: Optional[JobState] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    query = select(JobDB).order_by(JobDB.created_at.desc()).limit(limit)
    if state:
        query = query.where(JobDB.state == state)
    result = await db.execute(query)
    jobs = result.scalars().all()
    return [JobResponse.model_validate(j) for j in jobs]

@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    j_res = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = j_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    t_res = await db.execute(select(JobTaskDB).where(JobTaskDB.job_id == job.id).order_by(JobTaskDB.sequence_num.asc()))
    tasks = t_res.scalars().all()

    return JobDetailResponse(
        id=job.id,
        workload_id=job.workload_id,
        user_id=job.user_id,
        title=job.title,
        state=job.state,
        privacy_class=job.privacy_class,
        required_model=job.required_model,
        priority=job.priority,
        total_tasks=job.total_tasks,
        pending_tasks=job.pending_tasks,
        running_tasks=job.running_tasks,
        succeeded_tasks=job.succeeded_tasks,
        failed_tasks=job.failed_tasks,
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
        scheduling_explanation=job.scheduling_explanation,
        aggregated_result=job.aggregated_result,
        tasks=[JobTaskResponse.model_validate(t) for t in tasks]
    )

@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    j_res = await db.execute(select(JobDB).where(JobDB.id == job_id))
    job = j_res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if user.role != UserRole.ADMIN and job.user_id != user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to cancel this job")

    job.state = JobState.CANCELLED
    
    # Cancel pending tasks
    t_res = await db.execute(select(JobTaskDB).where(JobTaskDB.job_id == job.id, JobTaskDB.state.in_([TaskState.QUEUED, TaskState.PENDING, TaskState.RETRYING])))
    tasks = t_res.scalars().all()
    for t in tasks:
        t.state = TaskState.CANCELLED

    ev_hash = compute_audit_event_hash(
        AuditEventType.APPROVAL_RESOLVED.value,
        user.id,
        job.id,
        datetime.utcnow().isoformat(),
        {"action": "cancel_job"}
    )
    audit = AuditEventDB(
        event_type=AuditEventType.APPROVAL_RESOLVED,
        actor_id=user.id,
        actor_role=user.role.value,
        target_type="job",
        target_id=job.id,
        action_details={"action": "cancelled_by_user"},
        event_hash=ev_hash
    )
    db.add(audit)
    await db.commit()
    return {"status": "cancelled", "job_id": job.id}
