export type JobState = 'pending' | 'queued' | 'assigned' | 'running' | 'succeeded' | 'failed' | 'retrying' | 'cancelled' | 'expired';
export type TaskState = 'pending' | 'queued' | 'assigned' | 'running' | 'succeeded' | 'failed' | 'retrying' | 'cancelled' | 'expired';
export type NodeStatus = 'online' | 'offline' | 'paused' | 'revoked';
export type TrustLevel = 'untrusted' | 'community' | 'trusted_lab' | 'airgapped';
export type PrivacyClass = 'local_only' | 'trusted_nodes' | 'standard';
export type UserRole = 'user' | 'operator' | 'admin';
export type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'expired';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  organization_id?: string;
}

export interface NodeCapability {
  cpu_cores: number;
  cpu_utilization_pct: number;
  memory_mb: number;
  memory_available_mb: number;
  gpu_name?: string;
  vram_mb?: number;
  vram_available_mb?: number;
  os_name: string;
  os_version: string;
  cached_models: string[];
  battery_level?: number;
  is_charging?: boolean;
  power_state: string;
  network_mbps: number;
  clock_skew_ms: number;
}

export interface WorkerNode {
  id: string;
  node_id: string;
  node_name: string;
  organization_id?: string;
  status: NodeStatus;
  trust_level: TrustLevel;
  is_localhost: boolean;
  is_airgapped: boolean;
  capabilities: NodeCapability;
  last_heartbeat_at?: string;
  registered_at: string;
  active_leases_count: number;
}

export interface ScoreFactor {
  factor_name: string;
  raw_value: any;
  weight: number;
  contribution: number;
  description: string;
}

export interface ExcludedNode {
  node_id: string;
  node_name: string;
  reason: string;
  violates_constraint: string;
}

export interface SchedulingExplanation {
  job_id: string;
  task_id?: string;
  selected_node_id?: string;
  selected_node_name?: string;
  total_score: number;
  factors: ScoreFactor[];
  excluded_nodes: ExcludedNode[];
  policy_version: string;
  requires_approval: boolean;
  generated_at: string;
}

export interface JobTask {
  id: string;
  job_id: string;
  sequence_num: number;
  state: TaskState;
  assigned_node_id?: string;
  assigned_node_name?: string;
  lease_expires_at?: string;
  attempt_count: number;
  max_retries: number;
  input_payload: Record<string, any>;
  output_payload?: Record<string, any>;
  error_message?: string;
  result_checksum?: string;
  started_at?: string;
  completed_at?: string;
}

export interface Job {
  id: string;
  workload_id: string;
  user_id: string;
  title: string;
  state: JobState;
  privacy_class: PrivacyClass;
  required_model: string;
  priority: number;
  total_tasks: number;
  pending_tasks: number;
  running_tasks: number;
  succeeded_tasks: number;
  failed_tasks: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  scheduling_explanation?: SchedulingExplanation;
  aggregated_result?: string;
  tasks?: JobTask[];
}

export interface Approval {
  id: string;
  action: string;
  requester_user_id: string;
  requester_username: string;
  target_id: string;
  target_type: string;
  reason: string;
  parameters: Record<string, any>;
  status: ApprovalStatus;
  approver_username?: string;
  decision_reason?: string;
  created_at: string;
  decided_at?: string;
  expires_at: string;
}

export interface AuditEvent {
  id: string;
  event_type: string;
  actor_id?: string;
  actor_role?: string;
  target_type?: string;
  target_id?: string;
  action_details: Record<string, any>;
  ip_address?: string;
  event_hash: string;
  timestamp: string;
}

export interface CapacitySnapshot {
  total_nodes: number;
  online_nodes: number;
  paused_nodes: number;
  total_cpu_cores: number;
  available_cpu_cores: number;
  total_memory_gb: number;
  available_memory_gb: number;
  total_vram_gb: number;
  available_vram_gb: number;
  cached_models_summary: Record<string, number>;
  active_jobs: number;
  pending_tasks: number;
  running_tasks: number;
  avg_queue_wait_seconds: number;
  snapshot_time: string;
}
