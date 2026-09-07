import {
  User, WorkerNode, Job, CapacitySnapshot, Approval, AuditEvent
} from '../types';

const API_BASE = '/api/v1';

class ApiClient {
  private token: string | null = localStorage.getItem('lc_token');

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
    const data = await this.request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Nodes
  async getNodes(): Promise<WorkerNode[]> {
    return this.request<WorkerNode[]>('/nodes');
  }

  async pauseNode(nodeId: string, durationMinutes: number = 30) {
    return this.request(`/nodes/${nodeId}/pause?duration_minutes=${durationMinutes}`, {
      method: 'POST',
    });
  }

  async resumeNode(nodeId: string) {
    return this.request(`/nodes/${nodeId}/resume`, { method: 'POST' });
  }

  async revokeNode(nodeId: string, reason: string) {
    return this.request(`/nodes/${nodeId}/revoke`, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    });
  }

  // Workloads & Jobs
  async submitWorkload(payload: {
    title: string;
    privacy_class: string;
    required_model: string;
    priority: number;
    documents: { text: string }[];
  }): Promise<Job> {
    return this.request<Job>('/workloads/submit', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getJobs(): Promise<Job[]> {
    return this.request<Job[]>('/jobs');
  }

  async getJobDetail(jobId: string): Promise<Job> {
    return this.request<Job>(`/jobs/${jobId}`);
  }

  async cancelJob(jobId: string) {
    return this.request(`/jobs/${jobId}/cancel`, { method: 'POST' });
  }

  // Capacity & Monitoring
  async getCapacitySnapshot(): Promise<CapacitySnapshot> {
    return this.request<CapacitySnapshot>('/capacity/snapshot');
  }

  // Approvals
  async getApprovals(): Promise<Approval[]> {
    return this.request<Approval[]>('/approvals');
  }

  async decideApproval(approvalId: string, approved: boolean, reason?: string): Promise<Approval> {
    return this.request<Approval>(`/approvals/${approvalId}/decide`, {
      method: 'POST',
      body: JSON.stringify({ approved, reason }),
    });
  }

  // Audit
  async getAuditEvents(limit: number = 50): Promise<AuditEvent[]> {
    return this.request<AuditEvent[]>(`/audit?limit=${limit}`);
  }
}

export const api = new ApiClient();
