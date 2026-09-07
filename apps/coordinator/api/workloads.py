"""
Workload Ingestion and Scheduling Submission API
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from packages.shared.database import get_db
from packages.shared.models.db_models import (
    WorkloadDB, JobDB, JobTaskDB, WorkerNodeDB, AuditEventDB
)
from packages.shared.models.schemas import (
    WorkloadCreateRequest, JobResponse, JobDetailResponse,
    JobTaskResponse, WorkerNodeResponse, NodeCapability
)
from packages.shared.models.enums import (
    JobState, TaskState, AuditEventType, NodeStatus
)
from packages.shared.security.crypto import compute_audit_event_hash
from packages.shared.security.sanitization import redact_sensitive_metadata
from apps.coordinator.api.deps import get_current_user
from services.scheduler.engine import deterministic_scheduler
from services.monitoring.metrics import TASKS_SUBMITTED_TOTAL, QUEUE_PENDING_TASKS
from services.monitoring.logger import logger

router = APIRouter(prefix="/workloads", tags=["Workloads"])

@router.post("/submit", response_model=JobDetailResponse)
async def submit_workload(
    req: WorkloadCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    # Idempotency Check
    if req.idempotency_key:
        existing_res = await db.execute(
            select(WorkloadDB).where(WorkloadDB.idempotency_key == req.idempotency_key)
        )
        existing_w = existing_res.scalar_one_or_none()
        if existing_w:
            j_res = await db.execute(select(JobDB).where(JobDB.workload_id == existing_w.id))
            existing_job = j_res.scalar_one_or_none()
            if existing_job:
                t_res = await db.execute(select(JobTaskDB).where(JobTaskDB.job_id == existing_job.id))
                tasks = t_res.scalars().all()
                return JobDetailResponse(
                    id=existing_job.id,
                    workload_id=existing_w.id,
                    user_id=existing_w.user_id,
                    title=existing_job.title,
                    state=existing_job.state,
                    privacy_class=existing_job.privacy_class,
                    required_model=existing_job.required_model,
                    priority=existing_job.priority,
                    total_tasks=existing_job.total_tasks,
                    pending_tasks=existing_job.pending_tasks,
                    running_tasks=existing_job.running_tasks,
                    succeeded_tasks=existing_job.succeeded_tasks,
                    failed_tasks=existing_job.failed_tasks,
                    created_at=existing_job.created_at,
                    updated_at=existing_job.updated_at,
                    completed_at=existing_job.completed_at,
                    scheduling_explanation=existing_job.scheduling_explanation,
                    aggregated_result=existing_job.aggregated_result,
                    tasks=[JobTaskResponse.model_validate(t) for t in tasks]
                )

    # 1. Create Workload
    workload = WorkloadDB(
        user_id=user.id,
        title=req.title,
        description=req.description,
        workload_type=req.workload_type,
        privacy_class=req.privacy_class,
        required_model=req.required_model,
        priority=req.priority,
        max_runtime_seconds=req.max_runtime_seconds,
        retry_limit=req.retry_limit,
        idempotency_key=req.idempotency_key,
        parameters=req.parameters
    )
    db.add(workload)
    await db.flush()

    # 2. Fetch Active Nodes for Deterministic Scheduling
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

    # 3. Create Job
    num_docs = len(req.documents)
    job = JobDB(
        workload_id=workload.id,
        user_id=user.id,
        title=req.title,
        state=JobState.QUEUED,
        privacy_class=req.privacy_class,
        required_model=req.required_model,
        priority=req.priority,
        total_tasks=num_docs,
        pending_tasks=num_docs,
        running_tasks=0,
        succeeded_tasks=0,
        failed_tasks=0
    )
    db.add(job)
    await db.flush()

    # Compute Deterministic Scheduling Explanation
    explanation = deterministic_scheduler.filter_and_score_nodes(
        job_id=job.id,
        privacy_class=req.privacy_class,
        required_model=req.required_model,
        nodes=node_schemas
    )
    job.scheduling_explanation = explanation.model_dump(mode="json")

    # 4. Create Job Tasks
    task_responses = []
    for idx, doc in enumerate(req.documents, 1):
        # Privacy redaction on task input if necessary
        clean_doc = redact_sensitive_metadata(doc, req.privacy_class)
        clean_doc["model"] = req.required_model
        
        task = JobTaskDB(
            job_id=job.id,
            sequence_num=idx,
            state=TaskState.QUEUED,
            input_payload=clean_doc,
            max_retries=req.retry_limit
        )
        db.add(task)
        await db.flush()
        
        task_responses.append(JobTaskResponse(
            id=task.id,
            job_id=job.id,
            sequence_num=task.sequence_num,
            state=task.state,
            input_payload=task.input_payload,
            attempt_count=0,
            max_retries=task.max_retries
        ))
        
        TASKS_SUBMITTED_TOTAL.labels(
            workload_type=req.workload_type.value,
            privacy_class=req.privacy_class.value
        ).inc()

    QUEUE_PENDING_TASKS.inc(num_docs)

    # 5. Audit Log
    ev_hash = compute_audit_event_hash(
        AuditEventType.WORKLOAD_SUBMITTED.value,
        user.id,
        job.id,
        datetime.utcnow().isoformat(),
        {"title": req.title, "tasks": num_docs, "privacy": req.privacy_class.value}
    )
    audit = AuditEventDB(
        event_type=AuditEventType.WORKLOAD_SUBMITTED,
        actor_id=user.id,
        actor_role=user.role.value,
        target_type="job",
        target_id=job.id,
        action_details={"title": req.title, "tasks_count": num_docs, "model": req.required_model},
        event_hash=ev_hash
    )
    db.add(audit)
    await db.commit()

    return JobDetailResponse(
        id=job.id,
        workload_id=workload.id,
        user_id=user.id,
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
        tasks=task_responses
    )
