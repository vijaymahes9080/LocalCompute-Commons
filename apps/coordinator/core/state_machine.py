"""
Deterministic State Machine for Jobs and Tasks
"""
from typing import Set, Dict
from packages.shared.models.enums import JobState, TaskState

class InvalidStateTransitionError(Exception):
    pass

# Valid Job Transitions
VALID_JOB_TRANSITIONS: Dict[JobState, Set[JobState]] = {
    JobState.PENDING: {JobState.QUEUED, JobState.CANCELLED},
    JobState.QUEUED: {JobState.ASSIGNED, JobState.RUNNING, JobState.CANCELLED, JobState.EXPIRED},
    JobState.ASSIGNED: {JobState.RUNNING, JobState.QUEUED, JobState.FAILED, JobState.CANCELLED},
    JobState.RUNNING: {JobState.SUCCEEDED, JobState.FAILED, JobState.RETRYING, JobState.CANCELLED},
    JobState.RETRYING: {JobState.QUEUED, JobState.RUNNING, JobState.FAILED, JobState.CANCELLED},
    JobState.SUCCEEDED: set(),  # Terminal
    JobState.FAILED: set(),     # Terminal
    JobState.CANCELLED: set(),  # Terminal
    JobState.EXPIRED: set(),    # Terminal
}

# Valid Task Transitions
VALID_TASK_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.PENDING: {TaskState.QUEUED, TaskState.CANCELLED},
    TaskState.QUEUED: {TaskState.ASSIGNED, TaskState.CANCELLED, TaskState.EXPIRED},
    TaskState.ASSIGNED: {TaskState.RUNNING, TaskState.QUEUED, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.RUNNING: {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.RETRYING, TaskState.QUEUED, TaskState.CANCELLED},
    TaskState.RETRYING: {TaskState.QUEUED, TaskState.ASSIGNED, TaskState.FAILED, TaskState.CANCELLED},
    TaskState.SUCCEEDED: set(),  # Terminal
    TaskState.FAILED: set(),     # Terminal
    TaskState.CANCELLED: set(),  # Terminal
    TaskState.EXPIRED: set(),    # Terminal
}

def validate_job_transition(current: JobState, target: JobState) -> bool:
    """Validates if transitioning from current to target JobState is permissible."""
    if current == target:
        return True
    allowed = VALID_JOB_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(
            f"Invalid Job transition from {current.value} to {target.value}. Allowed: {[s.value for s in allowed]}"
        )
    return True

def validate_task_transition(current: TaskState, target: TaskState) -> bool:
    """Validates if transitioning from current to target TaskState is permissible."""
    if current == target:
        return True
    allowed = VALID_TASK_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionError(
            f"Invalid Task transition from {current.value} to {target.value}. Allowed: {[s.value for s in allowed]}"
        )
    return True
