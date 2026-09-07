import React, { useState } from 'react';
import { History, ShieldCheck, Filter, RefreshCw, Key } from 'lucide-react';
import { AuditEvent } from '../types';

interface AuditLogViewerProps {
  events: AuditEvent[];
  onRefresh: () => void;
}

export const AuditLogViewer: React.FC<AuditLogViewerProps> = ({ events, onRefresh }) => {
  const [filterType, setFilterType] = useState<string>('all');

  const filtered =
    filterType === 'all'
      ? events
      : events.filter((e) => e.event_type.toLowerCase().includes(filterType.toLowerCase()));

  const getEventBadge = (type: string) => {
    if (type.includes('security')) return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    if (type.includes('recovered') || type.includes('failed'))
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    if (type.includes('completed') || type.includes('registered'))
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-sky-400" />
            Immutable Audit Trail & Proofs
          </h2>
          <p className="text-xs text-slate-400">
            Cryptographically-verified record of all scheduling, task handshakes, and administrative actions.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-1.5 rounded-lg text-xs bg-slate-800 border border-slate-700 text-slate-200 focus:outline-none focus:border-sky-500"
          >
            <option value="all">All Event Types</option>
            <option value="node">Node Lifecycle</option>
            <option value="task">Task Execution & Leases</option>
            <option value="approval">Approvals</option>
            <option value="security">Security & Failures</option>
          </select>
          <button
            onClick={onRefresh}
            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5 font-semibold">Event Type</th>
                <th className="px-5 py-3.5 font-semibold">Actor / Role</th>
                <th className="px-5 py-3.5 font-semibold">Target Entity</th>
                <th className="px-5 py-3.5 font-semibold">Action Details</th>
                <th className="px-5 py-3.5 font-semibold">Integrity Hash</th>
                <th className="px-5 py-3.5 font-semibold text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-slate-500 font-sans">
                    No audit records match the selected filter.
                  </td>
                </tr>
              ) : (
                filtered.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-5 py-3.5">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border ${getEventBadge(
                          ev.event_type
                        )}`}
                      >
                        {ev.event_type}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-300">
                      <span>{ev.actor_id || 'system'}</span>
                      <span className="text-[10px] text-slate-500 block uppercase">
                        {ev.actor_role || 'daemon'}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-400">
                      <span>{ev.target_id || '-'}</span>
                      <span className="text-[10px] text-slate-500 block">{ev.target_type}</span>
                    </td>
                    <td className="px-5 py-3.5 text-slate-300 font-sans max-w-xs truncate">
                      {JSON.stringify(ev.action_details)}
                    </td>
                    <td className="px-5 py-3.5 text-purple-400">
                      <span className="inline-flex items-center gap-1 bg-purple-950/40 px-1.5 py-0.5 rounded border border-purple-800/40">
                        <ShieldCheck className="w-3 h-3 text-purple-400" />
                        {ev.event_hash.substring(0, 12)}...
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right text-slate-400">
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
