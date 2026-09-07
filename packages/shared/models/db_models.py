"""
SQLAlchemy Async ORM Models for LocalCompute Commons
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.orm import declarative_base, relationship
from packages.shared.models.enums import (
    JobState, TaskState, NodeStatus, TrustLevel, PrivacyClass,
    WorkloadType, UserRole, ApprovalStatus, ApprovalAction,
    AlertSeverity, AuditEventType
)

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization = relationship("OrganizationDB", back_populates="users")
    workloads = relationship("WorkloadDB", back_populates="user")

class OrganizationDB(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    trust_level = Column(SQLEnum(TrustLevel), default=TrustLevel.COMMUNITY, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("UserDB", back_populates="organization")
    nodes = relationship("WorkerNodeDB", back_populates="organization")

class WorkerNodeDB(Base):
    __tablename__ = "worker_nodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    node_id = Column(String(100), unique=True, nullable=False, index=True)
    node_name = Column(String(100), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    status = Column(SQLEnum(NodeStatus), default=NodeStatus.ONLINE, nullable=False)
    trust_level = Column(SQLEnum(TrustLevel), default=TrustLevel.COMMUNITY, nullable=False)
    is_localhost = Column(Boolean, default=False, nullable=False)
    is_airgapped = Column(Boolean, default=False, nullable=False)
    endpoint_url = Column(String(255), nullable=True)
    token_hash = Column(String(255), nullable=True)
    capabilities = Column(JSON, default=dict, nullable=False)
    last_heartbeat_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    consecutive_failures = Column(Integer, default=0, nullable=False)
    active_leases_count = Column(Integer, default=0, nullable=False)

    organization = relationship("OrganizationDB", back_populates="nodes")
    heartbeats = relationship("NodeHeartbeatDB", back_populates="node", cascade="all, delete-orphan")
    assigned_tasks = relationship("JobTaskDB", back_populates="assigned_node")

class NodeHeartbeatDB(Base):
    __tablename__ = "node_heartbeats"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    node_id = Column(String(36), ForeignKey("worker_nodes.id"), nullable=False, index=True)
    cpu_utilization_pct = Column(Float, nullable=False)
    memory_available_mb = Column(Integer, nullable=False)
    vram_available_mb = Column(Integer, default=0)
    battery_level = Column(Float, nullable=True)
    is_charging = Column(Boolean, default=True)
    network_mbps = Column(Float, default=100.0)
    clock_skew_ms = Column(Float, default=0.0)
    active_tasks_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    node = relationship("WorkerNodeDB", back_populates="heartbeats")

class WorkloadDB(Base):
    __tablename__ = "workloads"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    workload_type = Column(SQLEnum(WorkloadType), default=WorkloadType.SUMMARIZATION, nullable=False)
    privacy_class = Column(SQLEnum(PrivacyClass), default=PrivacyClass.STANDARD, nullable=False)
    required_model = Column(String(100), default="llama3:8b", nullable=False)
    priority = Column(Integer, default=5, nullable=False)
    max_runtime_seconds = Column(Integer, default=300, nullable=False)
    retry_limit = Column(Integer, default=3, nullable=False)
    idempotency_key = Column(String(100), unique=True, nullable=True, index=True)
    parameters = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("UserDB", back_populates="workloads")
    jobs = relationship("JobDB", back_populates="workload", cascade="all, delete-orphan")

class JobDB(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workload_id = Column(String(36), ForeignKey("workloads.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    state = Column(SQLEnum(JobState), default=JobState.PENDING, nullable=False, index=True)
    privacy_class = Column(SQLEnum(PrivacyClass), default=PrivacyClass.STANDARD, nullable=False)
    required_model = Column(String(100), default="llama3:8b", nullable=False)
    priority = Column(Integer, default=5, nullable=False)
    total_tasks = Column(Integer, default=0, nullable=False)
    pending_tasks = Column(Integer, default=0, nullable=False)
    running_tasks = Column(Integer, default=0, nullable=False)
    succeeded_tasks = Column(Integer, default=0, nullable=False)
    failed_tasks = Column(Integer, default=0, nullable=False)
    scheduling_explanation = Column(JSON, nullable=True)
    aggregated_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    workload = relationship("WorkloadDB", back_populates="jobs")
    tasks = relationship("JobTaskDB", back_populates="job", cascade="all, delete-orphan")

class JobTaskDB(Base):
    __tablename__ = "job_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    sequence_num = Column(Integer, default=0, nullable=False)
    state = Column(SQLEnum(TaskState), default=TaskState.PENDING, nullable=False, index=True)
    assigned_node_id = Column(String(36), ForeignKey("worker_nodes.id"), nullable=True, index=True)
    lease_expires_at = Column(DateTime, nullable=True, index=True)
    attempt_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    input_payload = Column(JSON, nullable=False)
    output_payload = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    result_checksum = Column(String(64), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    job = relationship("JobDB", back_populates="tasks")
    assigned_node = relationship("WorkerNodeDB", back_populates="assigned_tasks")
    attempts = relationship("TaskAttemptDB", back_populates="task", cascade="all, delete-orphan")

class TaskAttemptDB(Base):
    __tablename__ = "task_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("job_tasks.id"), nullable=False, index=True)
    node_id = Column(String(36), ForeignKey("worker_nodes.id"), nullable=False)
    attempt_num = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    error_message = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, default=0.0)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    task = relationship("JobTaskDB", back_populates="attempts")

class ApprovalDB(Base):
    __tablename__ = "approvals"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    action = Column(SQLEnum(ApprovalAction), nullable=False)
    requester_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    requester_username = Column(String(50), nullable=False)
    target_id = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=False)
    parameters = Column(JSON, default=dict, nullable=False)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    approver_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approver_username = Column(String(50), nullable=True)
    decision_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)

class AuditEventDB(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_type = Column(SQLEnum(AuditEventType), nullable=False, index=True)
    actor_id = Column(String(50), nullable=True, index=True)
    actor_role = Column(String(50), nullable=True)
    target_type = Column(String(50), nullable=True)
    target_id = Column(String(100), nullable=True, index=True)
    action_details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    event_hash = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class AlertDB(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.WARNING, nullable=False)
    source = Column(String(100), default="system", nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

class CapacitySnapshotDB(Base):
    __tablename__ = "capacity_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    total_nodes = Column(Integer, nullable=False)
    online_nodes = Column(Integer, nullable=False)
    paused_nodes = Column(Integer, nullable=False)
    total_cpu_cores = Column(Integer, nullable=False)
    available_cpu_cores = Column(Integer, nullable=False)
    total_memory_gb = Column(Float, nullable=False)
    available_memory_gb = Column(Float, nullable=False)
    total_vram_gb = Column(Float, nullable=False)
    available_vram_gb = Column(Float, nullable=False)
    cached_models_summary = Column(JSON, default=dict, nullable=False)
    active_jobs = Column(Integer, nullable=False)
    pending_tasks = Column(Integer, nullable=False)
    running_tasks = Column(Integer, nullable=False)
    avg_queue_wait_seconds = Column(Float, default=0.0)
    snapshot_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
