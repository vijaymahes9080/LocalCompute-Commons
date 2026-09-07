"""
Core Enums for LocalCompute Commons
"""
from enum import Enum

class JobState(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TaskState(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class NodeStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    PAUSED = "paused"
    REVOKED = "revoked"

class TrustLevel(str, Enum):
    UNTRUSTED = "untrusted"
    COMMUNITY = "community"
    TRUSTED_LAB = "trusted_lab"
    AIRGAPPED = "airgapped"

class PrivacyClass(str, Enum):
    LOCAL_ONLY = "local_only"
    TRUSTED_NODES = "trusted_nodes"
    STANDARD = "standard"

class WorkloadType(str, Enum):
    SUMMARIZATION = "summarization"
    EMBEDDING = "embedding"
    QA = "qa"
    TRANSCRIPTION = "transcription"

class UserRole(str, Enum):
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class ApprovalAction(str, Enum):
    REVOKE_NODE = "revoke_node"
    PAUSE_NODE_EXTENDED = "pause_node_extended"
    BULK_CANCEL_JOBS = "bulk_cancel_jobs"
    MODIFY_TRUST_POLICY = "modify_trust_policy"
    CHANGE_PRIVACY_POLICY = "change_privacy_policy"
    FORCED_SHUTDOWN = "forced_shutdown"

class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AuditEventType(str, Enum):
    NODE_REGISTERED = "node_registered"
    NODE_HEARTBEAT = "node_heartbeat"
    NODE_PAUSED = "node_paused"
    NODE_RESUMED = "node_resumed"
    NODE_REVOKED = "node_revoked"
    WORKLOAD_SUBMITTED = "workload_submitted"
    JOB_SCHEDULED = "job_scheduled"
    TASK_CLAIMED = "task_claimed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_RECOVERED = "task_recovered"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RESOLVED = "approval_resolved"
    SECURITY_ALERT = "security_alert"
