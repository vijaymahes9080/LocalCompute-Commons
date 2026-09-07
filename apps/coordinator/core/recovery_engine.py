"""
Background Lease Recovery and Automated Failure Recovery Engine
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, update
from packages.shared.database import AsyncSessionLocal
from packages.shared.models.db_models import (
    JobTaskDB, JobDB, WorkerNodeDB, AuditEventDB, TaskAttemptDB
)
from packages.shared.models.enums import (
    TaskState, JobState, NodeStatus, AuditEventType
)
from packages.shared.security.crypto import compute_audit_event_hash
from services.aggregation.aggregator import BatchResultAggregator
from services.monitoring.logger import logger
from services.monitoring.metrics import (
    TASKS_RETRIED_TOTAL, TASKS_FAILED_TOTAL, ACTIVE_WORKER_NODES
)

class RecoveryEngine:
    """
    Asynchronous background watcher that detects:
    1. Expired worker task leases
    2. Dead / unresponsive worker nodes
    3. Job completion aggregation
    """
    def __init__(self, check_interval_seconds: float = 3.0):
        self.check_interval_seconds = check_interval_seconds
        self.is_running = False
        self._task: asyncio.Task = None

    async def start(self):
        self.is_running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("RecoveryEngine started.")

    async def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
        logger.info("RecoveryEngine stopped.")

    async def _run_loop(self):
        while self.is_running:
            try:
                await self.check_node_health()
                await self.recover_expired_leases()
                await self.evaluate_job_aggregations()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"Error in RecoveryEngine cycle: {exc}", exc_info=True)
            await asyncio.sleep(self.check_interval_seconds)

    async def check_node_health(self):
        """Marks worker nodes OFFLINE if heartbeat is older than 30s."""
        cutoff = datetime.utcnow() - timedelta(seconds=30)
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(WorkerNodeDB).where(
                    WorkerNodeDB.status == NodeStatus.ONLINE,
                    WorkerNodeDB.last_heartbeat_at < cutoff
                )
            )
            offline_nodes = result.scalars().all()
            for node in offline_nodes:
                node.status = NodeStatus.OFFLINE
                logger.warning(f"Worker node '{node.node_name}' ({node.node_id}) timed out; marked OFFLINE")
                
                # Audit event
                ev_hash = compute_audit_event_hash(
                    AuditEventType.SECURITY_ALERT.value,
                    "system",
                    node.node_id,
                    datetime.utcnow().isoformat(),
                    {"reason": "heartbeat_timeout"}
                )
                audit = AuditEventDB(
                    event_type=AuditEventType.SECURITY_ALERT,
                    actor_id="system",
                    actor_role="system",
                    target_type="worker_node",
                    target_id=node.node_id,
                    action_details={"reason": "Node marked OFFLINE due to missed heartbeats (>30s)"},
                    event_hash=ev_hash
                )
                session.add(audit)
            if offline_nodes:
                await session.commit()

    async def recover_expired_leases(self):
        """Recovers tasks whose lease expired while running."""
        now = datetime.utcnow()
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(JobTaskDB).where(
                    JobTaskDB.state.in_([TaskState.RUNNING, TaskState.ASSIGNED]),
                    JobTaskDB.lease_expires_at < now
                )
            )
            expired_tasks = result.scalars().all()
            
            for task in expired_tasks:
                task.attempt_count += 1
                TASKS_RETRIED_TOTAL.labels(reason="lease_timeout").inc()
                
                old_node_id = task.assigned_node_id
                task.assigned_node_id = None
                task.lease_expires_at = None
                
                if task.attempt_count >= task.max_retries:
                    task.state = TaskState.FAILED
                    task.error_message = f"Exceeded maximum retries ({task.max_retries}). Last failure: lease expired on node {old_node_id}"
                    TASKS_FAILED_TOTAL.labels(worker_id=str(old_node_id), reason="max_retries_exceeded").inc()
                    logger.error(f"Task {task.id} failed permanently after {task.attempt_count} attempts")
                else:
                    task.state = TaskState.QUEUED
                    logger.warning(f"Task {task.id} lease expired on node {old_node_id}; re-queued for retry ({task.attempt_count}/{task.max_retries})")
                
                # Record attempt history
                attempt = TaskAttemptDB(
                    task_id=task.id,
                    node_id=old_node_id or "unknown",
                    attempt_num=task.attempt_count,
                    status="expired",
                    error_message="Worker lease expired before completion"
                )
                session.add(attempt)
                
                # Audit
                audit_hash = compute_audit_event_hash(
                    AuditEventType.TASK_RECOVERED.value,
                    "system",
                    task.id,
                    datetime.utcnow().isoformat(),
                    {"attempt": task.attempt_count, "previous_node": old_node_id}
                )
                audit = AuditEventDB(
                    event_type=AuditEventType.TASK_RECOVERED,
                    actor_id="system",
                    actor_role="system",
                    target_type="job_task",
                    target_id=task.id,
                    action_details={"attempt": task.attempt_count, "previous_node": old_node_id},
                    event_hash=audit_hash
                )
                session.add(audit)

            if expired_tasks:
                await session.commit()

    async def evaluate_job_aggregations(self):
        """Checks if all tasks of running/queued jobs are complete and performs batch aggregation."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(JobDB).where(JobDB.state.in_([JobState.RUNNING, JobState.QUEUED, JobState.ASSIGNED]))
            )
            jobs = result.scalars().all()
            
            for job in jobs:
                t_res = await session.execute(
                    select(JobTaskDB).where(JobTaskDB.job_id == job.id)
                )
                tasks = t_res.scalars().all()
                
                total = len(tasks)
                succeeded = sum(1 for t in tasks if t.state == TaskState.SUCCEEDED)
                failed = sum(1 for t in tasks if t.state == TaskState.FAILED)
                running = sum(1 for t in tasks if t.state == TaskState.RUNNING)
                pending = sum(1 for t in tasks if t.state in [TaskState.QUEUED, TaskState.ASSIGNED, TaskState.RETRYING])
                
                job.total_tasks = total
                job.succeeded_tasks = succeeded
                job.failed_tasks = failed
                job.running_tasks = running
                job.pending_tasks = pending
                
                if succeeded == total and total > 0:
                    job.state = JobState.SUCCEEDED
                    job.completed_at = datetime.utcnow()
                    # Perform Aggregation
                    task_dicts = [
                        {
                            "id": t.id,
                            "sequence_num": t.sequence_num,
                            "output_payload": t.output_payload,
                            "assigned_node_name": t.assigned_node_id
                        }
                        for t in tasks
                    ]
                    job.aggregated_result = BatchResultAggregator.aggregate_summaries(task_dicts, job.title)
                    logger.info(f"Job {job.id} ('{job.title}') completed successfully with aggregated result.")
                elif failed > 0 and (succeeded + failed == total):
                    job.state = JobState.FAILED
                    job.completed_at = datetime.utcnow()
                    logger.warning(f"Job {job.id} finished with {failed} failed tasks.")
                elif running > 0:
                    job.state = JobState.RUNNING

            if jobs:
                await session.commit()

recovery_engine = RecoveryEngine()
