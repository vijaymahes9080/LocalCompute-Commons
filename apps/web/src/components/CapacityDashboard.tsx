import React from 'react';
import { Cpu, Server, HardDrive, Database, Layers, Clock, Activity } from 'lucide-react';
import { CapacitySnapshot } from '../types';

interface CapacityDashboardProps {
  snapshot: CapacitySnapshot | null;
  loading: boolean;
}

export const CapacityDashboard: React.FC<CapacityDashboardProps> = ({ snapshot, loading }) => {
  if (loading && !snapshot) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 rounded-xl bg-slate-800/40 border border-slate-700/50"></div>
        ))}
      </div>
    );
  }

  if (!snapshot) {
    return (
      <div className="p-8 rounded-xl glass-panel text-center text-slate-400">
        No capacity telemetry available. Start worker nodes to view cluster metrics.
      </div>
    );
  }

  const cards = [
    {
      title: 'Online Worker Nodes',
      value: `${snapshot.online_nodes} / ${snapshot.total_nodes}`,
      sub: `${snapshot.paused_nodes} paused`,
      icon: Server,
      color: 'from-emerald-500 to-teal-600',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    },
    {
      title: 'Available CPU Compute',
      value: `${snapshot.available_cpu_cores} Cores`,
      sub: `of ${snapshot.total_cpu_cores} total cores`,
      icon: Cpu,
      color: 'from-sky-500 to-blue-600',
      badgeColor: 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    },
    {
      title: 'Available RAM',
      value: `${snapshot.available_memory_gb} GB`,
      sub: `of ${snapshot.total_memory_gb} GB cluster memory`,
      icon: Database,
      color: 'from-indigo-500 to-purple-600',
      badgeColor: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    },
    {
      title: 'Available VRAM (GPU)',
      value: `${snapshot.available_vram_gb} GB`,
      sub: `of ${snapshot.total_vram_gb} GB across nodes`,
      icon: HardDrive,
      color: 'from-fuchsia-500 to-pink-600',
      badgeColor: 'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/20',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map((card, idx) => {
          const Icon = card.icon;
          return (
            <div
              key={idx}
              className="glass-panel p-5 rounded-2xl relative overflow-hidden transition-all duration-200 hover:border-slate-600/80 group"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  {card.title}
                </span>
                <div
                  className={`w-9 h-9 rounded-xl bg-gradient-to-tr ${card.color} flex items-center justify-center text-white shadow-md`}
                >
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="mt-4">
                <div className="text-2xl font-black tracking-tight text-white">{card.value}</div>
                <div className="text-xs text-slate-400 mt-1">{card.sub}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Cluster Queue & Cached Models Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Queue Health */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-1">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-200 flex items-center gap-2">
              <Activity className="w-4 h-4 text-sky-400" />
              Queue & Workload State
            </h3>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              Avg Wait: {snapshot.avg_queue_wait_seconds}s
            </span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-sm text-slate-400">Active Jobs</span>
              <span className="text-base font-bold text-white">{snapshot.active_jobs}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-sm text-amber-400 flex items-center gap-2">
                <Clock className="w-4 h-4" /> Pending In Queue
              </span>
              <span className="text-base font-bold text-amber-400">{snapshot.pending_tasks}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-900/80 border border-slate-800">
              <span className="text-sm text-sky-400 flex items-center gap-2">
                <Layers className="w-4 h-4 animate-spin" /> Actively Running
              </span>
              <span className="text-base font-bold text-sky-400">{snapshot.running_tasks}</span>
            </div>
          </div>
        </div>

        {/* Pre-cached LLM Models on Nodes */}
        <div className="glass-panel p-6 rounded-2xl lg:col-span-2">
          <h3 className="font-bold text-slate-200 mb-2 flex items-center gap-2">
            <Database className="w-4 h-4 text-purple-400" />
            Distributed Model Cache Distribution
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Tasks scheduled to nodes with warm model caches execute immediately with zero model load latency.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.keys(snapshot.cached_models_summary).length > 0 ? (
              Object.entries(snapshot.cached_models_summary).map(([model, count]) => (
                <div
                  key={model}
                  className="flex items-center justify-between p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/90"
                >
                  <div>
                    <span className="font-mono text-sm font-semibold text-slate-200">{model}</span>
                    <p className="text-xs text-slate-500">Ollama-compatible local weight</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {count} {count === 1 ? 'node' : 'nodes'}
                  </span>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-900/40 text-xs text-slate-400 col-span-2 text-center">
                No model caches reported by registered workers.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
