import React, { useState } from 'react';
import {
  Server, Cpu, Database, Battery, BatteryCharging, Zap,
  Wifi, Clock, Shield, AlertTriangle, Pause, Play, Trash2
} from 'lucide-react';
import { WorkerNode, User } from '../types';

interface NodeInventoryProps {
  nodes: WorkerNode[];
  user: User | null;
  onPause: (nodeId: string) => void;
  onResume: (nodeId: string) => void;
  onRevoke: (nodeId: string, reason: string) => void;
  refreshNodes: () => void;
}

export const NodeInventory: React.FC<NodeInventoryProps> = ({
  nodes,
  user,
  onPause,
  onResume,
  onRevoke,
  refreshNodes,
}) => {
  const [revokingNode, setRevokingNode] = useState<string | null>(null);
  const [revokeReason, setRevokeReason] = useState('');

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'paused':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'offline':
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
      case 'revoked':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      default:
        return 'bg-slate-800 text-slate-400';
    }
  };

  const getTrustBadge = (trust: string) => {
    switch (trust) {
      case 'trusted_lab':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
      case 'airgapped':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      case 'community':
        return 'bg-teal-500/10 text-teal-400 border-teal-500/20';
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    }
  };

  const handleConfirmRevoke = () => {
    if (!revokingNode || !revokeReason.trim()) return;
    onRevoke(revokingNode, revokeReason.trim());
    setRevokingNode(null);
    setRevokeReason('');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Server className="w-5 h-5 text-sky-400" />
            Worker Node Inventory
          </h2>
          <p className="text-xs text-slate-400">
            Hardware capabilities, live telemetry, and zero-trust perimeter status.
          </p>
        </div>
        <button
          onClick={refreshNodes}
          className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
        >
          Refresh Nodes
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {nodes.map((node) => {
          const cap = node.capabilities;
          const isOnline = node.status === 'online';
          const isPaused = node.status === 'paused';
          const isRevoked = node.status === 'revoked';

          return (
            <div
              key={node.id}
              className={`glass-panel rounded-2xl p-5 relative flex flex-col justify-between transition-all duration-200 border ${
                isRevoked
                  ? 'border-rose-900/40 opacity-70'
                  : isOnline
                  ? 'hover:border-sky-500/40'
                  : 'border-slate-800'
              }`}
            >
              <div>
                {/* Node Header */}
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <h3 className="font-bold text-base text-white">{node.node_name}</h3>
                    <span className="font-mono text-xs text-slate-400">ID: {node.node_id}</span>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${getStatusBadge(
                        node.status
                      )}`}
                    >
                      {node.status}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${getTrustBadge(
                        node.trust_level
                      )}`}
                    >
                      {node.trust_level.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Telemetry Metrics */}
                <div className="space-y-3 py-3 border-y border-slate-800/80 my-3 text-xs">
                  {/* CPU */}
                  <div>
                    <div className="flex justify-between text-slate-300 mb-1">
                      <span className="flex items-center gap-1">
                        <Cpu className="w-3.5 h-3.5 text-sky-400" /> CPU ({cap.cpu_cores} Cores)
                      </span>
                      <span className="font-mono">{cap.cpu_utilization_pct.toFixed(1)}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-sky-500 to-indigo-500 transition-all duration-300"
                        style={{ width: `${Math.min(100, cap.cpu_utilization_pct)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Memory & VRAM */}
                  <div className="grid grid-cols-2 gap-2 text-slate-300">
                    <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Available RAM</span>
                      <span className="font-semibold text-slate-200">
                        {(cap.memory_available_mb / 1024).toFixed(1)} / {(cap.memory_mb / 1024).toFixed(1)} GB
                      </span>
                    </div>
                    <div className="p-2 rounded-lg bg-slate-900/60 border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">VRAM (GPU)</span>
                      <span className="font-semibold text-purple-300">
                        {((cap.vram_available_mb || 0) / 1024).toFixed(1)} GB
                      </span>
                    </div>
                  </div>

                  {/* Power & Network */}
                  <div className="flex items-center justify-between text-slate-400 pt-1">
                    <div className="flex items-center gap-1.5">
                      {cap.is_charging ? (
                        <BatteryCharging className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Battery className="w-3.5 h-3.5 text-amber-400" />
                      )}
                      <span>
                        {cap.battery_level !== null ? `${cap.battery_level}%` : 'AC Power'}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Wifi className="w-3.5 h-3.5 text-sky-400" />
                      <span>{cap.network_mbps} Mbps</span>
                    </div>
                    <div className="flex items-center gap-1.5 font-mono text-[11px]">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      <span>{cap.clock_skew_ms.toFixed(0)}ms</span>
                    </div>
                  </div>
                </div>

                {/* Cached Models */}
                <div className="mb-4">
                  <span className="text-[11px] font-semibold text-slate-400 block mb-1.5">
                    Preloaded Model Cache:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {cap.cached_models.map((m) => (
                      <span
                        key={m}
                        className="px-2 py-0.5 rounded text-[11px] font-mono bg-purple-950/40 text-purple-300 border border-purple-800/40"
                      >
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Controls */}
              {!isRevoked && (
                <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800/60">
                  {isOnline && (
                    <button
                      onClick={() => onPause(node.node_id)}
                      className="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 border border-amber-500/20 flex items-center gap-1 transition"
                    >
                      <Pause className="w-3.5 h-3.5" />
                      <span>Pause</span>
                    </button>
                  )}
                  {isPaused && (
                    <button
                      onClick={() => onResume(node.node_id)}
                      className="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 flex items-center gap-1 transition"
                    >
                      <Play className="w-3.5 h-3.5" />
                      <span>Resume</span>
                    </button>
                  )}
                  {user?.role === 'admin' && (
                    <button
                      onClick={() => setRevokingNode(node.node_id)}
                      className="px-2.5 py-1.5 rounded-lg text-xs font-medium bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/20 flex items-center gap-1 transition"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      <span>Revoke</span>
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Revocation Gated Modal */}
      {revokingNode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-md w-full border border-rose-500/30">
            <h3 className="text-lg font-bold text-white flex items-center gap-2 mb-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              Request Node Revocation
            </h3>
            <p className="text-xs text-slate-300 mb-4">
              Revocation permanently un-registers the node from the compute grid. This action requires approval from the authorization committee.
            </p>
            <div className="space-y-3">
              <label className="text-xs font-semibold text-slate-300 block">
                Administrative Reason:
              </label>
              <textarea
                value={revokeReason}
                onChange={(e) => setRevokeReason(e.target.value)}
                placeholder="Specify security incident, decommission rationale, or audit finding..."
                rows={3}
                className="w-full p-3 rounded-xl bg-slate-900 border border-slate-700 text-sm text-white focus:outline-none focus:border-rose-500"
              />
            </div>
            <div className="flex items-center justify-end gap-3 mt-5">
              <button
                onClick={() => setRevokingNode(null)}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              >
                Cancel
              </button>
              <button
                disabled={!revokeReason.trim()}
                onClick={handleConfirmRevoke}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-rose-600 hover:bg-rose-500 text-white transition disabled:opacity-50"
              >
                Submit for Approval
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
