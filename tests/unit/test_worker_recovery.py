"""
Unit Tests for Worker Failure Recovery and Lease Timeout Logic
"""
import pytest
from datetime import datetime, timedelta
from packages.shared.models.db_models import JobTaskDB, JobDB, WorkerNodeDB, WorkloadDB
from packages.shared.models.enums import TaskState, JobState, NodeStatus, TrustLevel, PrivacyClass, WorkloadType
from apps.coordinator.core.recovery_engine import RecoveryEngine

@pytest.mark.asyncio
async def test_lease_expiration_and_requeue(db_session):
    engine = RecoveryEngine()

    # Create a workload & job
    workload = WorkloadDB(
        user_id="user-admin-1",
        title="Recovery Test Workload",
        workload_type=WorkloadType.SUMMARIZATION,
        privacy_class=PrivacyClass.STANDARD
    )
    db_session.add(workload)
    await db_session.flush()

    job = JobDB(
        workload_id=workload.id,
        user_id="user-admin-1",
        title="Recovery Test Job",
        state=JobState.RUNNING,
        total_tasks=1,
        running_tasks=1
    )
    db_session.add(job)
    await db_session.flush()

    # Create task with expired lease
    past_time = datetime.utcnow() - timedelta(seconds=120)
    task = JobTaskDB(
        job_id=job.id,
        sequence_num=1,
        state=TaskState.RUNNING,
        assigned_node_id="node-alpha",
        lease_expires_at=past_time,
        attempt_count=0,
        max_retries=3,
        input_payload={"text": "Chunk text"}
    )
    db_session.add(task)
    await db_session.commit()

    # Run recovery cycle
    await engine.recover_expired_leases()

    # Verify task was re-queued
    await db_session.refresh(task)
    assert task.state == TaskState.QUEUED
    assert task.attempt_count == 1
    assert task.assigned_node_id is None
    assert task.lease_expires_at is None

@pytest.mark.asyncio
async def test_max_retries_exceeded_fails_permanently(db_session):
    engine = RecoveryEngine()

    workload = WorkloadDB(
        user_id="user-admin-1",
        title="Max Retry Workload",
        workload_type=WorkloadType.SUMMARIZATION
    )
    db_session.add(workload)
    await db_session.flush()

    job = JobDB(
        workload_id=workload.id,
        user_id="user-admin-1",
        title="Max Retry Job",
        state=JobState.RUNNING,
        total_tasks=1,
        running_tasks=1
    )
    db_session.add(job)
    await db_session.flush()

    # Create task already at max retries - 1
    past_time = datetime.utcnow() - timedelta(seconds=100)
    task = JobTaskDB(
        job_id=job.id,
        sequence_num=1,
        state=TaskState.RUNNING,
        assigned_node_id="node-alpha",
        lease_expires_at=past_time,
        attempt_count=2,
        max_retries=3,
        input_payload={"text": "Fail text"}
    )
    db_session.add(task)
    await db_session.commit()

    await engine.recover_expired_leases()

    await db_session.refresh(task)
    assert task.state == TaskState.FAILED
    assert task.attempt_count == 3
    assert "Exceeded maximum retries" in task.error_message
