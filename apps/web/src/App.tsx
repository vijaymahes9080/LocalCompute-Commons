import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { PrivacyBanner } from './components/PrivacyBanner';
import { CapacityDashboard } from './components/CapacityDashboard';
import { NodeInventory } from './components/NodeInventory';
import { WorkloadForm } from './components/WorkloadForm';
import { JobQueue } from './components/JobQueue';
import { ApprovalCenter } from './components/ApprovalCenter';
import { AuditLogViewer } from './components/AuditLogViewer';
import { LoginModal } from './components/LoginModal';
import { api } from './api/client';
import { User, WorkerNode, Job, CapacitySnapshot, Approval, AuditEvent } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [user, setUser] = useState<User | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  const [nodes, setNodes] = useState<WorkerNode[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [snapshot, setSnapshot] = useState<CapacitySnapshot | null>(null);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(false);

  // Initial Auth Check
  useEffect(() => {
    const checkUser = async () => {
      if (api.getToken()) {
        try {
          const me = await api.getMe();
          setUser(me);
        } catch {
          api.setToken(null);
          setUser(null);
        }
      }
    };
    checkUser();
  }, []);

  // Fetch all cluster state
  const refreshAllData = async () => {
    setLoading(true);
    try {
      const [n, j, s, a, aud] = await Promise.allSettled([
        api.getNodes(),
        api.getJobs(),
        api.getCapacitySnapshot(),
        api.getApprovals(),
        api.getAuditEvents(50),
      ]);

      if (n.status === 'fulfilled') setNodes(n.value);
      if (j.status === 'fulfilled') setJobs(j.value);
      if (s.status === 'fulfilled') setSnapshot(s.value);
      if (a.status === 'fulfilled') setApprovals(a.value);
      if (aud.status === 'fulfilled') setAuditEvents(aud.value);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshAllData();
    const interval = setInterval(refreshAllData, 4000);
    return () => clearInterval(interval);
  }, [user]);

  // Auth Handlers
  const handleLogin = async (u: string, p: string) => {
    const res = await api.login(u, p);
    setUser(res.user);
    refreshAllData();
  };

  const handleLogout = () => {
    api.setToken(null);
    setUser(null);
  };

  // Node Actions
  const handlePauseNode = async (nodeId: string) => {
    await api.pauseNode(nodeId);
    refreshAllData();
  };

  const handleResumeNode = async (nodeId: string) => {
    await api.resumeNode(nodeId);
    refreshAllData();
  };

  const handleRevokeNode = async (nodeId: string, reason: string) => {
    await api.revokeNode(nodeId, reason);
    refreshAllData();
  };

  // Workload Actions
  const handleSubmitWorkload = async (data: any) => {
    await api.submitWorkload(data);
    setActiveTab('jobs');
    refreshAllData();
  };

  const handleCancelJob = async (jobId: string) => {
    await api.cancelJob(jobId);
    refreshAllData();
  };

  const handleSelectJob = async (jobId: string) => {
    return api.getJobDetail(jobId);
  };

  // Approval Decisions
  const handleDecideApproval = async (approvalId: string, approved: boolean, reason?: string) => {
    await api.decideApproval(approvalId, approved, reason);
    refreshAllData();
  };

  const pendingApprovalsCount = approvals.filter((a) => a.status === 'pending').length;

  return (
    <div className="min-h-screen bg-[#0b0f19] flex flex-col">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onOpenLogin={() => setShowLoginModal(true)}
        onLogout={handleLogout}
        pendingApprovalsCount={pendingApprovalsCount}
      />
      <PrivacyBanner />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <CapacityDashboard snapshot={snapshot} loading={loading} />
            <NodeInventory
              nodes={nodes}
              user={user}
              onPause={handlePauseNode}
              onResume={handleResumeNode}
              onRevoke={handleRevokeNode}
              refreshNodes={refreshAllData}
            />
          </div>
        )}

        {activeTab === 'nodes' && (
          <NodeInventory
            nodes={nodes}
            user={user}
            onPause={handlePauseNode}
            onResume={handleResumeNode}
            onRevoke={handleRevokeNode}
            refreshNodes={refreshAllData}
          />
        )}

        {activeTab === 'submit' && (
          <WorkloadForm onSubmit={handleSubmitWorkload} loading={loading} />
        )}

        {activeTab === 'jobs' && (
          <JobQueue
            jobs={jobs}
            onCancelJob={handleCancelJob}
            onRefresh={refreshAllData}
            onSelectJob={handleSelectJob}
          />
        )}

        {activeTab === 'approvals' && (
          <ApprovalCenter
            approvals={approvals}
            user={user}
            onDecide={handleDecideApproval}
            refreshApprovals={refreshAllData}
          />
        )}

        {activeTab === 'audit' && (
          <AuditLogViewer events={auditEvents} onRefresh={refreshAllData} />
        )}
      </main>

      {showLoginModal && (
        <LoginModal
          onClose={() => setShowLoginModal(false)}
          onLogin={handleLogin}
        />
      )}
    </div>
  );
};
