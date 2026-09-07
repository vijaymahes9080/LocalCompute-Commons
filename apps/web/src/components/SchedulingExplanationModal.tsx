import React from 'react';
import { X, CheckCircle, AlertTriangle, ShieldCheck, Cpu } from 'lucide-react';
import { SchedulingExplanation } from '../types';

interface SchedulingExplanationModalProps {
  explanation: SchedulingExplanation;
  onClose: () => void;
}

export const SchedulingExplanationModal: React.FC<SchedulingExplanationModalProps> = ({
  explanation,
  onClose,
}) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
      <div className="glass-panel p-6 rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col border border-purple-500/30">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-purple-400" />
              Deterministic Scheduling Explanation
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Policy Version: {explanation.policy_version}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Selected Node Summary */}
        <div className="overflow-y-auto py-4 space-y-4 flex-1">
          <div className="p-4 rounded-xl bg-purple-950/30 border border-purple-800/40 flex items-center justify-between">
            <div>
              <span className="text-[11px] font-semibold text-purple-300 uppercase tracking-wider block">
                Selected Placement:
              </span>
              <span className="text-lg font-extrabold text-white">
                {explanation.selected_node_name || 'None Eligible'}
              </span>
              <span className="text-xs font-mono text-slate-400 block">
                ID: {explanation.selected_node_id || 'N/A'}
              </span>
            </div>
            <div className="text-right">
              <span className="text-[11px] font-semibold text-purple-300 uppercase tracking-wider block">
                Total Score:
              </span>
              <span className="text-2xl font-black text-purple-400 font-mono">
                {explanation.total_score.toFixed(1)} / 100
              </span>
            </div>
          </div>

          {/* Scoring Factors Breakdown */}
          <div>
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
              Multi-Factor Score Composition:
            </h4>
            <div className="space-y-2.5">
              {explanation.factors.map((f, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-white">{f.factor_name}</span>
                    <span
                      className={`font-mono font-bold ${
                        f.contribution >= 0 ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {f.contribution >= 0 ? `+${f.contribution}` : f.contribution} pts
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] mb-1">{f.description}</p>
                  <span className="text-[10px] font-mono text-slate-500">
                    Raw Telemetry: {f.raw_value}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Hard Constraint Exclusions */}
          {explanation.excluded_nodes.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" /> Excluded Candidate Nodes:
              </h4>
              <div className="space-y-2">
                {explanation.excluded_nodes.map((ex, idx) => (
                  <div
                    key={idx}
                    className="p-3 rounded-xl bg-rose-950/20 border border-rose-900/40 text-xs"
                  >
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="font-semibold text-slate-200">{ex.node_name}</span>
                      <span className="text-[10px] font-mono text-rose-400">
                        {ex.violates_constraint}
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px]">{ex.reason}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
};
