import React from 'react';
import { Lock, EyeOff, CheckCheck } from 'lucide-react';

export const PrivacyBanner: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-sky-950/40 via-slate-900/60 to-emerald-950/40 border-b border-sky-500/20 px-4 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-300">
          <span className="p-1 rounded bg-sky-500/20 text-sky-400">
            <Lock className="w-3.5 h-3.5" />
          </span>
          <span className="font-semibold text-white">Zero-Retention Local Compute:</span>
          <span>Inference runs strictly on peer hardware within university & lab perimeter.</span>
        </div>
        <div className="flex items-center gap-4 text-slate-400">
          <div className="flex items-center gap-1.5">
            <EyeOff className="w-3.5 h-3.5 text-emerald-400" />
            <span>Document Payloads Redacted</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCheck className="w-3.5 h-3.5 text-sky-400" />
            <span>Deterministic SHA-256 Audit Trail</span>
          </div>
        </div>
      </div>
    </div>
  );
};
