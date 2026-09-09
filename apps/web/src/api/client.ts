import {
  User, WorkerNode, Job, CapacitySnapshot, Approval, AuditEvent
} from '../types';
import {
  INITIAL_USER,
  INITIAL_NODES,
  INITIAL_SNAPSHOT,
  INITIAL_JOBS,
  INITIAL_APPROVALS,
  INITIAL_AUDIT_EVENTS
} from './mockData';

const API_BASE = '/api/v1';

class ApiClient {
  private token: string | null = localStorage.getItem('lc_token');
  private isSimulated = false;

  // Local simulated state
  private nodes: WorkerNode[] = JSON.parse(JSON.stringify(INITIAL_NODES));
  private jobs: Job[] = JSON.parse(JSON.stringify(INITIAL_JOBS));
  private snapshot: CapacitySnapshot = JSON.parse(JSON.stringify(INITIAL_SNAPSHOT));
  private approvals: Approval[] = JSON.parse(JSON.stringify(INITIAL_APPROVALS));
  private auditEvents: AuditEvent[] = JSON.parse(JSON.stringify(INITIAL_AUDIT_EVENTS));
  private currentUser: User | null = INITIAL_USER;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('lc_token', token);
    } else {
      localStorage.removeItem('lc_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  isDemoMode(): boolean {
    return this.isSimulated;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.setToken(null);
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(errorData.detail || errorData.message || 'API request failed');
    }

    return response.json();
  }

  // Auth
  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
    try {
      const data = await this.request<{ access_token: string; user: User }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      this.setToken(data.access_token);
      this.isSimulated = false;
      return data;
    } catch {
      this.isSimulated = true;
      const role = username.toLowerCase().includes('admin')
        ? 'admin'
        : username.toLowerCase().includes('oper')
        ? 'operator'
        : 'user';
      const user: User = {
        id: `usr_${Date.now().toString(36)}`,
        username: username || 'admin',
        email: `${username || 'admin'}@localcompute.commons`,
        full_name: username === 'admin' ? 'Cluster Administrator' : username,
        role: role as any,
      };
      this.currentUser = user;
      const token = `demo-token-${Date.now()}`;
      this.setToken(token);
      return { access_token: token, user };
    }
  }

  async getMe(): Promise<User> {
    try {
      const u = await this.request<User>('/auth/me');
      this.isSimulated = false;
      return u;
    } catch {
      this.isSimulated = true;
      return this.currentUser || INITIAL_USER;
    }
  }

  // Nodes
  async getNodes(): Promise<WorkerNode[]> {
    try {
      const res = await this.request<WorkerNode[]>('/nodes');
      this.isSimulated = false;
      return res;
    } catch {
      this.isSimulated = true;
      return this.nodes;
    }
  }

  async pauseNode(nodeId: string, durationMinutes: number = 30) {
    try {
      return await this.request(`/nodes/${nodeId}/pause?duration_minutes=${durationMinutes}`, {
        method: 'POST',
      });
    } catch {
      this.isSimulated = true;
      const node = this.nodes.find(n => n.node_id === nodeId || n.id === nodeId);
      if (node) {
        node.status = 'paused';
        this.snapshot.paused_nodes += 1;
        this.snapshot.online_nodes = Math.max(0, this.snapshot.online_nodes - 1);
        this.auditEvents.unshift({
          id: `aud_${Date.now().toString(36)}`,
          event_type: 'NODE_PAUSED',
          actor_id: this.currentUser?.id || 'usr_admin',
          actor_role: this.currentUser?.role || 'admin',
          target_type: 'worker_node',
          target_id: nodeId,
          action_details: { duration_minutes: durationMinutes },
          ip_address: '127.0.0.1 (Web Demo)',
          event_hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
          timestamp: new Date().toISOString(),
        });
      }
      return { success: true, node_id: nodeId, status: 'paused' };
    }
  }

  async resumeNode(nodeId: string) {
    try {
      return await this.request(`/nodes/${nodeId}/resume`, { method: 'POST' });
    } catch {
      this.isSimulated = true;
      const node = this.nodes.find(n => n.node_id === nodeId || n.id === nodeId);
      if (node) {
        node.status = 'online';
        this.snapshot.paused_nodes = Math.max(0, this.snapshot.paused_nodes - 1);
        this.snapshot.online_nodes += 1;
        this.auditEvents.unshift({
          id: `aud_${Date.now().toString(36)}`,
          event_type: 'NODE_RESUMED',
          actor_id: this.currentUser?.id || 'usr_admin',
          actor_role: this.currentUser?.role || 'admin',
          target_type: 'worker_node',
          target_id: nodeId,
          action_details: { status: 'online' },
          ip_address: '127.0.0.1 (Web Demo)',
          event_hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
          timestamp: new Date().toISOString(),
        });
      }
      return { success: true, node_id: nodeId, status: 'online' };
    }
  }

  async revokeNode(nodeId: string, reason: string) {
    try {
      return await this.request(`/nodes/${nodeId}/revoke`, {
        method: 'POST',
        body: JSON.stringify({ reason }),
      });
    } catch {
      this.isSimulated = true;
      const node = this.nodes.find(n => n.node_id === nodeId || n.id === nodeId);
      if (node) {
        node.status = 'revoked';
        this.auditEvents.unshift({
          id: `aud_${Date.now().toString(36)}`,
          event_type: 'NODE_REVOKED',
          actor_id: this.currentUser?.id || 'usr_admin',
          actor_role: this.currentUser?.role || 'admin',
          target_type: 'worker_node',
          target_id: nodeId,
          action_details: { reason },
          ip_address: '127.0.0.1 (Web Demo)',
          event_hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
          timestamp: new Date().toISOString(),
        });
      }
      return { success: true, node_id: nodeId, status: 'revoked' };
    }
  }

  // Workloads & Jobs
  async submitWorkload(payload: {
    title: string;
    privacy_class: string;
    required_model: string;
    priority: number;
    documents: { text: string }[];
  }): Promise<Job> {
    try {
      return await this.request<Job>('/workloads/submit', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    } catch {
      this.isSimulated = true;
      const totalTasks = Math.max(1, payload.documents.length);
      const selectedNode = this.nodes.find(n => n.status === 'online') || this.nodes[0];
      const newJob: Job = {
        id: `job-${Math.random().toString(36).substring(2, 10)}`,
        workload_id: `wl_${Date.now().toString(36)}`,
        user_id: this.currentUser?.id || 'usr_admin',
        title: payload.title || 'Distributed Inference Batch',
        state: 'running',
        privacy_class: payload.privacy_class as any,
        required_model: payload.required_model,
        priority: payload.priority,
        total_tasks: totalTasks,
        pending_tasks: 0,
        running_tasks: 1,
        succeeded_tasks: totalTasks > 1 ? totalTasks - 1 : 0,
        failed_tasks: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        scheduling_explanation: {
          job_id: `job-sim`,
          selected_node_id: selectedNode.node_id,
          selected_node_name: selectedNode.node_name,
          total_score: 95.8,
          policy_version: '2026.1-privacy-strict',
          requires_approval: false,
          generated_at: new Date().toISOString(),
          factors: [
            {
              factor_name: 'Privacy Class Compatibility',
              raw_value: payload.privacy_class,
              weight: 0.4,
              contribution: 40.0,
              description: `Node trust matches workload policy (${payload.privacy_class}).`,
            },
            {
              factor_name: 'Model Warmth Cache',
              raw_value: payload.required_model,
              weight: 0.35,
              contribution: 33.5,
              description: `Model ${payload.required_model} preloaded in memory.`,
            },
            {
              factor_name: 'Resource Headroom',
              raw_value: 'Healthy',
              weight: 0.25,
              contribution: 22.3,
              description: 'Ample compute and memory headroom available.',
            },
          ],
          excluded_nodes: [],
        },
        tasks: payload.documents.map((doc, idx) => ({
          id: `task-${Date.now()}-${idx + 1}`,
          job_id: 'job-sim',
          sequence_num: idx + 1,
          state: idx === 0 ? 'running' : 'succeeded',
          assigned_node_id: selectedNode.node_id,
          assigned_node_name: selectedNode.node_name,
          attempt_count: 1,
          max_retries: 3,
          input_payload: { text_preview: doc.text.substring(0, 80) },
          started_at: new Date().toISOString(),
        })),
      };

      this.jobs.unshift(newJob);
      this.snapshot.active_jobs += 1;
      this.snapshot.running_tasks += 1;

      this.auditEvents.unshift({
        id: `aud_${Date.now().toString(36)}`,
        event_type: 'WORKLOAD_SUBMITTED',
        actor_id: this.currentUser?.id || 'usr_admin',
        actor_role: this.currentUser?.role || 'admin',
        target_type: 'job',
        target_id: newJob.id,
        action_details: { title: payload.title, tasks: totalTasks },
        ip_address: '127.0.0.1 (Web Demo)',
        event_hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
        timestamp: new Date().toISOString(),
      });

      return newJob;
    }
  }

  async getJobs(): Promise<Job[]> {
    try {
      const j = await this.request<Job[]>('/jobs');
      this.isSimulated = false;
      return j;
    } catch {
      this.isSimulated = true;
      return this.jobs;
    }
  }

  async getJobDetail(jobId: string): Promise<Job> {
    try {
      return await this.request<Job>(`/jobs/${jobId}`);
    } catch {
      this.isSimulated = true;
      const found = this.jobs.find(j => j.id === jobId);
      if (found) return found;
      return this.jobs[0];
    }
  }

  async cancelJob(jobId: string) {
    try {
      return await this.request(`/jobs/${jobId}/cancel`, { method: 'POST' });
    } catch {
      this.isSimulated = true;
      const found = this.jobs.find(j => j.id === jobId);
      if (found) {
        found.state = 'cancelled';
      }
      return { success: true, job_id: jobId, state: 'cancelled' };
    }
  }

  // Capacity & Monitoring
  async getCapacitySnapshot(): Promise<CapacitySnapshot> {
    try {
      const snap = await this.request<CapacitySnapshot>('/capacity/snapshot');
      this.isSimulated = false;
      return snap;
    } catch {
      this.isSimulated = true;
      return this.snapshot;
    }
  }

  // Approvals
  async getApprovals(): Promise<Approval[]> {
    try {
      const a = await this.request<Approval[]>('/approvals');
      this.isSimulated = false;
      return a;
    } catch {
      this.isSimulated = true;
      return this.approvals;
    }
  }

  async decideApproval(approvalId: string, approved: boolean, reason?: string): Promise<Approval> {
    try {
      return await this.request<Approval>(`/approvals/${approvalId}/decide`, {
        method: 'POST',
        body: JSON.stringify({ approved, reason }),
      });
    } catch {
      this.isSimulated = true;
      const appr = this.approvals.find(a => a.id === approvalId);
      if (appr) {
        appr.status = approved ? 'approved' : 'rejected';
        appr.approver_username = this.currentUser?.username || 'admin';
        appr.decision_reason = reason || (approved ? 'Authorized by operator' : 'Denied by operator');
        appr.decided_at = new Date().toISOString();

        this.auditEvents.unshift({
          id: `aud_${Date.now().toString(36)}`,
          event_type: approved ? 'APPROVAL_GRANTED' : 'APPROVAL_REJECTED',
          actor_id: this.currentUser?.id || 'usr_admin',
          actor_role: this.currentUser?.role || 'admin',
          target_type: 'approval',
          target_id: approvalId,
          action_details: { approved, reason: appr.decision_reason },
          ip_address: '127.0.0.1 (Web Demo)',
          event_hash: Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
          timestamp: new Date().toISOString(),
        });
      }
      return appr || this.approvals[0];
    }
  }

  // Audit
  async getAuditEvents(limit: number = 50): Promise<AuditEvent[]> {
    try {
      const aud = await this.request<AuditEvent[]>(`/audit?limit=${limit}`);
      this.isSimulated = false;
      return aud;
    } catch {
      this.isSimulated = true;
      return this.auditEvents.slice(0, limit);
    }
  }
}

export const api = new ApiClient();
