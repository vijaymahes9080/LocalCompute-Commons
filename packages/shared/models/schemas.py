"""
Pydantic Schemas for LocalCompute Commons
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from packages.shared.models.enums import (
    JobState, TaskState, NodeStatus, TrustLevel, PrivacyClass,
    WorkloadType, UserRole, ApprovalStatus, ApprovalAction,
    AlertSeverity, AuditEventType
)

# Base Schema
class CoreModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# ---------------------------------------------------------
# User & Organization
# ---------------------------------------------------------
class UserBase(CoreModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER
    organization_id: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class Token(CoreModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenPayload(CoreModel):
    sub: str
    role: UserRole
    org_id: Optional[str] = None
    type: str  # 'access' | 'refresh' | 'worker'
    exp: int

class OrganizationBase(CoreModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=50)
    trust_level: TrustLevel = TrustLevel.COMMUNITY
    description: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime

# ---------------------------------------------------------
# Worker Node & Telemetry
# ---------------------------------------------------------
class NodeCapability(CoreModel):
    cpu_cores: int = Field(..., ge=1)
    cpu_utilization_pct: float = Field(0.0, ge=0.0, le=100.0)
    memory_mb: int = Field(..., ge=256)
    memory_available_mb: int = Field(..., ge=0)
    gpu_name: Optional[str] = None
    vram_mb: Optional[int] = 0
    vram_available_mb: Optional[int] = 0
    os_name: str
    os_version: str
    cached_models: List[str] = Field(default_factory=list)
    battery_level: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_charging: Optional[bool] = True
    power_state: str = "ac"  # 'ac' | 'battery' | 'low_power'
    network_mbps: float = Field(100.0, ge=0.1)
    clock_skew_ms: float = 0.0

class WorkerNodeRegisterRequest(CoreModel):
    node_id: str = Field(..., description="Stable hardware/UUID for node")
    node_name: str = Field(..., min_length=2, max_length=100)
    organization_id: Optional[str] = None
    capabilities: NodeCapability
    trust_level: TrustLevel = TrustLevel.COMMUNITY
    is_localhost: bool = False
    is_airgapped: bool = False
    endpoint_url: Optional[str] = None

class WorkerNodeResponse(CoreModel):
    id: str
    node_id: str
    node_name: str
    organization_id: Optional[str] = None
    status: NodeStatus
    trust_level: TrustLevel
    is_localhost: bool
    is_airgapped: bool
    capabilities: NodeCapability
    last_heartbeat_at: Optional[datetime] = None
    registered_at: datetime
    consecutive_failures: int = 0
    active_leases_count: int = 0
    token: Optional[str] = None

class NodeHeartbeatRequest(CoreModel):
    node_id: str
    capabilities: NodeCapability
    active_tasks: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class NodeHeartbeatResponse(CoreModel):
    acknowledged: bool = True
    status: NodeStatus
    server_time: datetime = Field(default_factory=datetime.utcnow)
    token_renewal: Optional[str] = None
    pending_tasks_count: int = 0

class TrustPolicy(CoreModel):
    id: str
    organization_id: str
    allowed_privacy_classes: List[PrivacyClass] = [PrivacyClass.STANDARD, PrivacyClass.TRUSTED_NODES]
    min_trust_level: TrustLevel = TrustLevel.COMMUNITY
    require_approval_for_external: bool = True
    metadata_retention_days: int = 30
    store_raw_documents: bool = False

# ---------------------------------------------------------
# Workload, Job & Task
# ---------------------------------------------------------
class WorkloadCreateRequest(CoreModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    workload_type: WorkloadType = WorkloadType.SUMMARIZATION
    privacy_class: PrivacyClass = PrivacyClass.STANDARD
    required_model: str = Field("llama3:8b", description="Target model e.g. llama3:8b or mistral:7b")
    priority: int = Field(5, ge=1, le=10, description="1 (Lowest) to 10 (Highest)")
    max_runtime_seconds: int = Field(300, ge=10, le=3600)
    retry_limit: int = Field(3, ge=0, le=10)
    idempotency_key: Optional[str] = None
    documents: List[Dict[str, Any]] = Field(..., min_length=1, description="List of document chunks/items")
    parameters: Dict[str, Any] = Field(default_factory=dict)

class WorkloadResponse(CoreModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    workload_type: WorkloadType
    privacy_class: PrivacyClass
    required_model: str
    priority: int
    total_tasks: int
    created_at: datetime

class JobTaskResponse(CoreModel):
    id: str
    job_id: str
    sequence_num: int
    state: TaskState
    assigned_node_id: Optional[str] = None
    assigned_node_name: Optional[str] = None
    lease_expires_at: Optional[datetime] = None
    attempt_count: int = 0
    max_retries: int = 3
    input_payload: Dict[str, Any]
    output_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    result_checksum: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class JobResponse(CoreModel):
    id: str
    workload_id: str
    user_id: str
    title: str
    state: JobState
    privacy_class: PrivacyClass
    required_model: str
    priority: int
    total_tasks: int
    pending_tasks: int
    running_tasks: int
    succeeded_tasks: int
    failed_tasks: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    scheduling_explanation: Optional[Dict[str, Any]] = None
    aggregated_result: Optional[str] = None

class JobDetailResponse(JobResponse):
    tasks: List[JobTaskResponse] = Field(default_factory=list)

class TaskClaimRequest(CoreModel):
    node_id: str
    max_tasks: int = Field(1, ge=1, le=5)

class TaskClaimResponse(CoreModel):
    tasks: List[JobTaskResponse] = Field(default_factory=list)

class TaskCompleteRequest(CoreModel):
    node_id: str
    task_id: str
    output_payload: Dict[str, Any]
    result_checksum: str
    metrics: Dict[str, Any] = Field(default_factory=dict)
    execution_time_seconds: float

class TaskFailRequest(CoreModel):
    node_id: str
    task_id: str
    error_message: str
    is_fatal: bool = False

# ---------------------------------------------------------
# Scheduling Explanation Models
# ---------------------------------------------------------
class ScoreFactor(CoreModel):
    factor_name: str
    raw_value: Any
    weight: float
    contribution: float
    description: str

class ExcludedNode(CoreModel):
    node_id: str
    node_name: str
    reason: str
    violates_constraint: str

class SchedulingExplanation(CoreModel):
    job_id: str
    task_id: Optional[str] = None
    selected_node_id: Optional[str] = None
    selected_node_name: Optional[str] = None
    total_score: float = 0.0
    factors: List[ScoreFactor] = Field(default_factory=list)
    excluded_nodes: List[ExcludedNode] = Field(default_factory=list)
    policy_version: str = "v1.2.0-deterministic"
    requires_approval: bool = False
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# ---------------------------------------------------------
# Approval, Audit & Alerts
# ---------------------------------------------------------
class ApprovalCreateRequest(CoreModel):
    action: ApprovalAction
    target_id: str
    target_type: str
    reason: str = Field(..., min_length=5, max_length=500)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    expires_in_hours: int = 24

class ApprovalResponse(CoreModel):
    id: str
    action: ApprovalAction
    requester_user_id: str
    requester_username: str
    target_id: str
    target_type: str
    reason: str
    parameters: Dict[str, Any]
    status: ApprovalStatus
    approver_user_id: Optional[str] = None
    approver_username: Optional[str] = None
    decision_reason: Optional[str] = None
    created_at: datetime
    decided_at: Optional[datetime] = None
    expires_at: datetime

class ApprovalDecisionRequest(CoreModel):
    approved: bool
    reason: Optional[str] = None

class AuditEventCreate(CoreModel):
    event_type: AuditEventType
    actor_id: Optional[str] = None
    actor_role: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    action_details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditEventResponse(CoreModel):
    id: str
    event_type: AuditEventType
    actor_id: Optional[str]
    actor_role: Optional[str]
    target_type: Optional[str]
    target_id: Optional[str]
    action_details: Dict[str, Any]
    ip_address: Optional[str]
    event_hash: str
    timestamp: datetime

class AlertCreateRequest(CoreModel):
    title: str
    severity: AlertSeverity = AlertSeverity.WARNING
    source: str = "system"
    details: Dict[str, Any] = Field(default_factory=dict)

class AlertResponse(CoreModel):
    id: str
    title: str
    severity: AlertSeverity
    source: str
    details: Dict[str, Any]
    is_resolved: bool
    created_at: datetime
    resolved_at: Optional[datetime] = None

class CapacitySnapshot(CoreModel):
    total_nodes: int
    online_nodes: int
    paused_nodes: int
    total_cpu_cores: int
    available_cpu_cores: int
    total_memory_gb: float
    available_memory_gb: float
    total_vram_gb: float
    available_vram_gb: float
    cached_models_summary: Dict[str, int]
    active_jobs: int
    pending_tasks: int
    running_tasks: int
    avg_queue_wait_seconds: float
    snapshot_time: datetime = Field(default_factory=datetime.utcnow)
