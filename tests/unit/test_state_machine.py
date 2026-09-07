"""
Unit Tests for State Machine Transitions
"""
import pytest
from packages.shared.models.enums import JobState, TaskState
from apps.coordinator.core.state_machine import (
    validate_job_transition, validate_task_transition, InvalidStateTransitionError
)

def test_valid_job_transitions():
    assert validate_job_transition(JobState.PENDING, JobState.QUEUED)
    assert validate_job_transition(JobState.QUEUED, JobState.ASSIGNED)
    assert validate_job_transition(JobState.ASSIGNED, JobState.RUNNING)
    assert validate_job_transition(JobState.RUNNING, JobState.SUCCEEDED)
    assert validate_job_transition(JobState.RUNNING, JobState.FAILED)
    assert validate_job_transition(JobState.RUNNING, JobState.RETRYING)
    assert validate_job_transition(JobState.RETRYING, JobState.QUEUED)

def test_invalid_job_transitions():
    # Succeeded is terminal
    with pytest.raises(InvalidStateTransitionError):
        validate_job_transition(JobState.SUCCEEDED, JobState.RUNNING)
        
    # Failed is terminal
    with pytest.raises(InvalidStateTransitionError):
        validate_job_transition(JobState.FAILED, JobState.QUEUED)
        
    # Pending cannot jump to succeeded directly
    with pytest.raises(InvalidStateTransitionError):
        validate_job_transition(JobState.PENDING, JobState.SUCCEEDED)

def test_valid_task_transitions():
    assert validate_task_transition(TaskState.QUEUED, TaskState.ASSIGNED)
    assert validate_task_transition(TaskState.ASSIGNED, TaskState.RUNNING)
    assert validate_task_transition(TaskState.RUNNING, TaskState.SUCCEEDED)
    assert validate_task_transition(TaskState.RUNNING, TaskState.RETRYING)
    assert validate_task_transition(TaskState.RETRYING, TaskState.QUEUED)

def test_invalid_task_transitions():
    with pytest.raises(InvalidStateTransitionError):
        validate_task_transition(TaskState.SUCCEEDED, TaskState.ASSIGNED)
