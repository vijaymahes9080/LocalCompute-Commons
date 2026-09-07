import React from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Shield, Clock, Check, X } from 'lucide-react';
import { Approval, User } from '../types';

interface ApprovalCenterProps {
  approvals: Approval[];
  user: User | null;
  onDecide: (approvalId: string, approved: boolean, reason?: string) => void;
  refreshApprovals: () => void;
}

export const ApprovalCenter: React.FC<ApprovalCenterProps> = ({
  approvals,
  user,
  onDecide,
  refreshApprovals,
}) => {
  const canDecide = user?.role === 'admin' || user?.role === 'operator';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-sky-400" />
            Administrative Approval Center
          </h2>
          <p className="text-xs text-slate-400">
            Multi-party authorization gatekeeper for high-impact cluster operations.
          </p>
        </div>
        <button
          onClick={refreshApprovals}
          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
        >
          Refresh
        </button>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5 font-semibold">Action & Target</th>
                <th className="px-5 py-3.5 font-semibold">Requester</th>
                <th className="px-5 py-3.5 font-semibold">Reason</th>
                <th className="px-5 py-3.5 font-semibold">Status</th>
                <th className="px-5 py-3.5 font-semibold">Requested At</th>
                <th className="px-5 py-3.5 font-semibold text-right">Decision</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {approvals.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-slate-500">
                    No pending approval requests.
                  </td>
                </tr>
              ) : (
                approvals.map((app) => {
                  const isPending = app.status === 'pending';

                  return (
                    <tr key={app.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-4">
                        <div className="font-bold text-sm text-white capitalize">
                          {app.action.replace(/_/g, ' ')}
                        </div>
                        <div className="font-mono text-[11px] text-slate-400 mt-0.5">
                          {app.target_type}: {app.target_id}
                        </div>
                      </td>
                      <td className="px-5 py-4 text-slate-300">
                        <span className="font-semibold text-white">{app.requester_username}</span>
                      </td>
                      <td className="px-5 py-4 text-slate-300 max-w-xs">
                        <p className="line-clamp-2">{app.reason}</p>
                      </td>
                      <td className="px-5 py-4">
                        <span
                          className={`px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider border ${
                            app.status === 'approved'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                              : app.status === 'rejected'
                              ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse'
                          }`}
                        >
                          {app.status}
                        </span>
                      </td>
                      <td className="px-5 py-4 font-mono text-[11px] text-slate-400">
                        {new Date(app.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-right">
                        {isPending ? (
                          canDecide ? (
                            <div className="flex items-center justify-end gap-2">
                              <button
                                onClick={() => onDecide(app.id, true, 'Approved by operator/admin')}
                                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 transition"
                              >
                                <Check className="w-3.5 h-3.5" />
                                <span>Approve</span>
                              </button>
                              <button
                                onClick={() => onDecide(app.id, false, 'Rejected by operator/admin')}
                                className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 transition"
                              >
                                <X className="w-3.5 h-3.5" />
                                <span>Reject</span>
                              </button>
                            </div>
                          ) : (
                            <span className="text-[11px] text-slate-500 italic">Admin Review Required</span>
                          )
                        ) : (
                          <div className="text-[11px] text-slate-400">
                            <span>Decided by {app.approver_username || 'System'}</span>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
