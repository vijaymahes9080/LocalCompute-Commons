import React, { useState } from 'react';
import { Terminal, Lock, ShieldCheck, Globe, Plus, Trash2, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import { PrivacyClass } from '../types';

interface WorkloadFormProps {
  onSubmit: (data: {
    title: string;
    privacy_class: string;
    required_model: string;
    priority: number;
    documents: { text: string }[];
  }) => Promise<void>;
  loading: boolean;
}

export const WorkloadForm: React.FC<WorkloadFormProps> = ({ onSubmit, loading }) => {
  const [title, setTitle] = useState('Research Paper Batch Summarization');
  const [privacyClass, setPrivacyClass] = useState<PrivacyClass>('trusted_nodes');
  const [requiredModel, setRequiredModel] = useState('llama3:8b');
  const [priority, setPriority] = useState(7);
  const [chunks, setChunks] = useState<string[]>([
    'Section 1: Distributed machine learning leverages local edge compute clusters to conduct privacy-safe parallel inference without egress to cloud providers.',
    'Section 2: Mathematical convergence and scheduling proofs demonstrate that deterministic multi-factor scoring reduces tail queue latencies by 42%.',
    'Section 3: Security audit logs verified with SHA-256 hash chaining prevent repudiation and tampering in multi-tenant lab environments.',
  ]);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleAddChunk = () => {
    setChunks([...chunks, `Section ${chunks.length + 1}: Enter additional text chunk for parallel summarization...`]);
  };

  const handleUpdateChunk = (index: number, val: string) => {
    const updated = [...chunks];
    updated[index] = val;
    setChunks(updated);
  };

  const handleRemoveChunk = (index: number) => {
    if (chunks.length <= 1) return;
    setChunks(chunks.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatusMessage(null);
    try {
      await onSubmit({
        title,
        privacy_class: privacyClass,
        required_model: requiredModel,
        priority,
        documents: chunks.map((c) => ({ text: c })),
      });
      setStatusMessage({ type: 'success', text: 'Workload successfully submitted to deterministic scheduler!' });
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Failed to submit workload' });
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <Terminal className="w-5 h-5 text-sky-400" />
          Submit AI Workload Batch
        </h2>
        <p className="text-xs text-slate-400">
          Dispatch parallel text summarization tasks across verified cluster nodes with deterministic routing.
        </p>
      </div>

      {statusMessage && (
        <div
          className={`p-4 rounded-xl flex items-center gap-3 text-xs font-medium ${
            statusMessage.type === 'success'
              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 rounded-2xl space-y-6">
        {/* Title */}
        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-2">
            Workload Title:
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500 font-medium"
          />
        </div>

        {/* Privacy Class Selector */}
        <div>
          <label className="text-xs font-semibold text-slate-300 block mb-2">
            Privacy Perimeter Classification:
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              {
                id: 'local_only',
                label: 'Local-Only',
                desc: 'Restricted strictly to this machine / air-gapped node',
                icon: Lock,
                color: 'text-purple-400',
              },
              {
                id: 'trusted_nodes',
                label: 'Trusted Lab Nodes',
                desc: 'Verified university and lab hardware',
                icon: ShieldCheck,
                color: 'text-sky-400',
              },
              {
                id: 'standard',
                label: 'Standard Community',
                desc: 'Any active community cluster node with PII redaction',
                icon: Globe,
                color: 'text-emerald-400',
              },
            ].map((p) => {
              const Icon = p.icon;
              const isSelected = privacyClass === p.id;
              return (
                <div
                  key={p.id}
                  onClick={() => setPrivacyClass(p.id as PrivacyClass)}
                  className={`cursor-pointer p-4 rounded-xl border transition-all duration-150 ${
                    isSelected
                      ? 'bg-slate-800/90 border-sky-500 ring-1 ring-sky-500'
                      : 'bg-slate-900/40 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Icon className={`w-4 h-4 ${p.color}`} />
                    <span className="font-bold text-sm text-white">{p.label}</span>
                  </div>
                  <p className="text-[11px] text-slate-400">{p.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Model & Priority */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">
              Target Ollama Model:
            </label>
            <select
              value={requiredModel}
              onChange={(e) => setRequiredModel(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-700 text-sm text-white focus:outline-none focus:border-sky-500 font-mono"
            >
              <option value="llama3:8b">llama3:8b (General Summarization)</option>
              <option value="mistral:7b">mistral:7b (Technical Synthesis)</option>
              <option value="phi3:mini">phi3:mini (Ultra Fast Lightweight)</option>
              <option value="qwen2:7b">qwen2:7b (Multi-lingual)</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-300 block mb-2">
              Scheduling Priority (1 = Low, 10 = Urgent):
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="1"
                max="10"
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value))}
                className="w-full accent-sky-500"
              />
              <span className="font-mono text-base font-bold text-sky-400 w-6 text-center">
                {priority}
              </span>
            </div>
          </div>
        </div>

        {/* Document Chunks */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-xs font-semibold text-slate-300">
              Document Chunks ({chunks.length} tasks will be created in parallel):
            </label>
            <button
              type="button"
              onClick={handleAddChunk}
              className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-sky-500/10 text-sky-400 hover:bg-sky-500/20 border border-sky-500/20 transition"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Chunk</span>
            </button>
          </div>

          <div className="space-y-3">
            {chunks.map((chunk, idx) => (
              <div key={idx} className="relative group">
                <textarea
                  value={chunk}
                  onChange={(e) => handleUpdateChunk(idx, e.target.value)}
                  rows={2}
                  required
                  placeholder={`Enter text for chunk ${idx + 1}...`}
                  className="w-full p-3 pr-10 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
                />
                {chunks.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveChunk(idx)}
                    className="absolute top-3 right-3 p-1 rounded-md text-slate-500 hover:text-rose-400 transition opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end pt-4 border-t border-slate-800">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm bg-brand-600 hover:bg-brand-500 text-white transition shadow-lg shadow-brand-500/20 glow-brand disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
            <span>{loading ? 'Submitting...' : 'Dispatch Workload to Grid'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
