"""
Task Claim, Execution Handshake, and Completion API
"""
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from packages.shared.database import get_db
from packages.shared.models.db_models import (
    JobTaskDB, JobDB, WorkerNodeDB, TaskAttemptDB, AuditEventDB
)
from packages.shared.models.schemas import (
    TaskClaimRequest, TaskClaimResponse, JobTaskResponse,
    TaskCompleteRequest, TaskFailRequest
)
from packages.shared.models.enums import (
    TaskState, JobState, AuditEventType, PrivacyClass
)
from packages.shared.security.crypto import compute_audit_event_hash, compute_payload_checksum
from apps.coordinator.api.deps import get_current_worker
from services.monitoring.metrics import (
    TASKS_COMPLETED_TOTAL, TASKS_FAILED_TOTAL,
    TASK_EXECUTION_DURATION_SECONDS, ACTIVE_RUNNING_TASKS, QUEUE_PENDING_TASKS
)
from services.monitoring.logger import logger

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/claim", response_model=TaskClaimResponse)
async def claim_tasks(
    req: TaskClaimRequest,
    worker: WorkerNodeDB = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.utcnow()
    lease_duration = timedelta(seconds=60)
    
    # Query queued tasks compatible with this worker
    # We join with JobDB to check privacy class compatibility
    q = (
        select(JobTaskDB, JobDB)
        .join(JobDB, JobTaskDB.job_id == JobDB.id)
        .where(
            JobTaskDB.state.in_([TaskState.QUEUED, TaskState.RETRYING]),
            JobDB.state.in_([JobState.QUEUED, JobState.RUNNING, JobState.ASSIGNED])
        )
        .order_by(JobDB.priority.desc(), JobTaskDB.sequence_num.asc())
        .limit(req.max_tasks)
    )
    
    result = await db.execute(q)
    rows = result.all()
    
    claimed_responses: List[JobTaskResponse] = []
    
    for task, job in rows:
        # Privacy constraint check
        if job.privacy_class == PrivacyClass.LOCAL_ONLY and not (worker.is_localhost or worker.is_airgapped):
            continue

        task.state = TaskState.RUNNING
        task.assigned_node_id = worker.node_id
        task.lease_expires_at = now + lease_duration
        task.started_at = now
        
        # Update Job state to RUNNING if not already
        if job.state == JobState.QUEUED:
            job.state = JobState.RUNNING

        claimed_responses.append(JobTaskResponse(
            id=task.id,
            job_id=task.job_id,
            sequence_num=task.sequence_num,
            state=task.state,
            assigned_node_id=worker.node_id,
            assigned_node_name=worker.node_name,
            lease_expires_at=task.lease_expires_at,
            attempt_count=task.attempt_count,
            max_retries=task.max_retries,
            input_payload=task.input_payload,
            started_at=task.started_at
        ))
        
        # Audit
        ev_hash = compute_audit_event_hash(
            AuditEventType.TASK_CLAIMED.value,
            worker.node_id,
            task.id,
            now.isoformat(),
            {"worker_name": worker.node_name, "lease_expires_at": task.lease_expires_at.isoformat()}
        )
        audit = AuditEventDB(
            event_type=AuditEventType.TASK_CLAIMED,
            actor_id=worker.node_id,
            actor_role="worker",
            target_type="job_task",
            target_id=task.id,
            action_details={"worker": worker.node_name},
            event_hash=ev_hash
        )
        db.add(audit)
        
        QUEUE_PENDING_TASKS.dec(1)
        ACTIVE_RUNNING_TASKS.inc(1)

    if claimed_responses:
        worker.active_leases_count += len(claimed_responses)
        await db.commit()

    return TaskClaimResponse(tasks=claimed_responses)

@router.post("/{task_id}/complete")
async def complete_task(
    task_id: str,
    req: TaskCompleteRequest,
    worker: WorkerNodeDB = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobTaskDB).where(JobTaskDB.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify Checksum Integrity
    computed_check = compute_payload_checksum(req.output_payload)
    if computed_check != req.result_checksum:
        logger.warning(f"Checksum mismatch on task {task_id}: {computed_check} != {req.result_checksum}")

    task.state = TaskState.SUCCEEDED
    task.output_payload = req.output_payload
    task.result_checksum = req.result_checksum
    task.completed_at = datetime.utcnow()
    task.lease_expires_at = None

    # Record Attempt
    attempt = TaskAttemptDB(
        task_id=task.id,
        node_id=worker.node_id,
        attempt_num=task.attempt_count + 1,
        status="succeeded",
        execution_time_seconds=req.execution_time_seconds
    )
    db.add(attempt)

    # Decrement active lease count
    if worker.active_leases_count > 0:
        worker.active_leases_count -= 1

    # Audit
    ev_hash = compute_audit_event_hash(
        AuditEventType.TASK_COMPLETED.value,
        worker.node_id,
        task.id,
        datetime.utcnow().isoformat(),
        {"checksum": req.result_checksum, "duration_s": req.execution_time_seconds}
    )
    audit = AuditEventDB(
        event_type=AuditEventType.TASK_COMPLETED,
        actor_id=worker.node_id,
        actor_role="worker",
        target_type="job_task",
        target_id=task.id,
        action_details={"duration_s": req.execution_time_seconds, "worker": worker.node_name},
        event_hash=ev_hash
    )
    db.add(audit)
    
    TASKS_COMPLETED_TOTAL.labels(
        worker_id=worker.node_id,
        model=task.input_payload.get("model", "unknown")
    ).inc()
    TASK_EXECUTION_DURATION_SECONDS.observe(req.execution_time_seconds)
    ACTIVE_RUNNING_TASKS.dec(1)

    await db.commit()
    return {"status": "succeeded", "task_id": task.id}

@router.post("/{task_id}/fail")
async def fail_task(
    task_id: str,
    req: TaskFailRequest,
    worker: WorkerNodeDB = Depends(get_current_worker),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(JobTaskDB).where(JobTaskDB.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.attempt_count += 1
    task.error_message = req.error_message
    task.assigned_node_id = None
    task.lease_expires_at = None

    if task.attempt_count >= task.max_retries or req.is_fatal:
        task.state = TaskState.FAILED
        TASKS_FAILED_TOTAL.labels(worker_id=worker.node_id, reason="execution_error").inc()
    else:
        task.state = TaskState.QUEUED  # Ready for retry on another worker

    # Record Attempt
    attempt = TaskAttemptDB(
        task_id=task.id,
        node_id=worker.node_id,
        attempt_num=task.attempt_count,
        status="failed",
        error_message=req.error_message
    )
    db.add(attempt)

    if worker.active_leases_count > 0:
        worker.active_leases_count -= 1

    ev_hash = compute_audit_event_hash(
        AuditEventType.TASK_FAILED.value,
        worker.node_id,
        task.id,
        datetime.utcnow().isoformat(),
        {"error": req.error_message, "attempt": task.attempt_count}
    )
    audit = AuditEventDB(
        event_type=AuditEventType.TASK_FAILED,
        actor_id=worker.node_id,
        actor_role="worker",
        target_type="job_task",
        target_id=task.id,
        action_details={"error": req.error_message, "attempt": task.attempt_count},
        event_hash=ev_hash
    )
    db.add(audit)
    ACTIVE_RUNNING_TASKS.dec(1)

    await db.commit()
    return {"status": task.state.value, "task_id": task.id, "attempt": task.attempt_count}
