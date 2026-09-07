import React, { useState } from 'react';
import {
  FileText, CheckCircle2, Clock, XCircle, AlertCircle,
  Eye, HelpCircle, X, ChevronRight, Download, RefreshCw
} from 'lucide-react';
import { Job, JobTask, SchedulingExplanation } from '../types';
import { SchedulingExplanationModal } from './SchedulingExplanationModal';

interface JobQueueProps {
  jobs: Job[];
  onCancelJob: (jobId: string) => void;
  onRefresh: () => void;
  onSelectJob: (jobId: string) => Promise<Job>;
}

export const JobQueue: React.FC<JobQueueProps> = ({
  jobs,
  onCancelJob,
  onRefresh,
  onSelectJob,
}) => {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [activeExplanation, setActiveExplanation] = useState<SchedulingExplanation | null>(null);
  const [viewingResult, setViewingResult] = useState<string | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const handleOpenDetail = async (jobId: string) => {
    setLoadingDetail(true);
    try {
      const detailed = await onSelectJob(jobId);
      setSelectedJob(detailed);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetail(false);
    }
  };

  const getStatusBadge = (state: string) => {
    switch (state) {
      case 'succeeded':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'running':
        return 'bg-sky-500/10 text-sky-400 border-sky-500/20 animate-pulse';
      case 'queued':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      case 'failed':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      case 'cancelled':
        return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
      default:
        return 'bg-slate-800 text-slate-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-sky-400" />
            Distributed Job Queue
          </h2>
          <p className="text-xs text-slate-400">
            Real-time batch progress, state machine transitions, and task attempt recovery.
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </button>
      </div>

      {/* Jobs Table */}
      <div className="glass-panel rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="px-5 py-3.5 font-semibold">Job Title & Model</th>
                <th className="px-5 py-3.5 font-semibold">State</th>
                <th className="px-5 py-3.5 font-semibold">Privacy</th>
                <th className="px-5 py-3.5 font-semibold">Progress</th>
                <th className="px-5 py-3.5 font-semibold">Submitted</th>
                <th className="px-5 py-3.5 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {jobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-slate-500">
                    No active or past workloads found. Submit a batch to start.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => {
                  const progressPct =
                    job.total_tasks > 0
                      ? Math.round((job.succeeded_tasks / job.total_tasks) * 100)
                      : 0;

                  return (
                    <tr key={job.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-4">
                        <div className="font-bold text-sm text-white">{job.title}</div>
                        <div className="flex items-center gap-2 mt-0.5 font-mono text-[11px] text-slate-400">
                          <span>{job.required_model}</span>
                          <span>•</span>
                          <span>Priority {job.priority}</span>
                        </div>
                      </td>
                      <td className="px-5 py-4">
                        <span
                          className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${getStatusBadge(
                            job.state
                          )}`}
                        >
                          {job.state}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="font-mono text-xs text-sky-400 bg-sky-950/30 px-2 py-0.5 rounded border border-sky-800/40">
                          {job.privacy_class}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <div className="w-32">
                          <div className="flex justify-between text-[11px] text-slate-300 mb-1 font-mono">
                            <span>
                              {job.succeeded_tasks}/{job.total_tasks}
                            </span>
                            <span>{progressPct}%</span>
                          </div>
                          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-sky-500 to-emerald-500"
                              style={{ width: `${progressPct}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4 text-slate-400 font-mono text-[11px]">
                        {new Date(job.created_at).toLocaleTimeString()}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {job.scheduling_explanation && (
                            <button
                              onClick={() =>
                                setActiveExplanation(job.scheduling_explanation as SchedulingExplanation)
                              }
                              title="Inspect Deterministic Scheduling Explanation"
                              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-purple-400 transition"
                            >
                              <HelpCircle className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleOpenDetail(job.id)}
                            className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-sky-400 transition"
                          >
                            <Eye className="w-3.5 h-3.5" />
                            <span>Tasks</span>
                          </button>
                          {job.aggregated_result && (
                            <button
                              onClick={() => setViewingResult(job.aggregated_result || '')}
                              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 transition"
                            >
                              <span>Summary</span>
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Task Breakdown Drawer / Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <FileText className="w-4 h-4 text-sky-400" />
                  Task Breakdown: {selectedJob.title}
                </h3>
                <p className="text-xs text-slate-400 font-mono">Job ID: {selectedJob.id}</p>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto py-4 space-y-3 flex-1 pr-1">
              {selectedJob.tasks?.map((task) => (
                <div
                  key={task.id}
                  className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white">
                      Task #{task.sequence_num}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] text-slate-400">
                        Node: {task.assigned_node_name || 'Queued / Scheduler Pending'}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded-full text-[11px] font-bold uppercase border ${getStatusBadge(
                          task.state
                        )}`}
                      >
                        {task.state}
                      </span>
                    </div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950 text-slate-300 font-mono text-[11px]">
                    <span className="text-slate-500 block mb-0.5">Input Text Chunk:</span>
                    {task.input_payload?.text || JSON.stringify(task.input_payload)}
                  </div>

                  {task.output_payload && (
                    <div className="p-2.5 rounded-lg bg-sky-950/30 border border-sky-800/40 text-sky-200">
                      <span className="text-sky-400 font-semibold block mb-0.5">
                        Inference Output:
                      </span>
                      {task.output_payload?.summary}
                    </div>
                  )}

                  {task.error_message && (
                    <div className="p-2.5 rounded-lg bg-rose-950/40 border border-rose-800/40 text-rose-300">
                      <span className="text-rose-400 font-semibold block mb-0.5">
                        Failure Reason:
                      </span>
                      {task.error_message}
                    </div>
                  )}

                  <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1">
                    <span>Attempts: {task.attempt_count}/{task.max_retries}</span>
                    {task.result_checksum && (
                      <span>SHA-256: {task.result_checksum.substring(0, 16)}...</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedJob(null)}
                className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
              >
                Close Breakdown
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Aggregated Summary Modal */}
      {viewingResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-panel p-6 rounded-2xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Aggregated Workload Summary
              </h3>
              <button
                onClick={() => setViewingResult(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="overflow-y-auto py-4 whitespace-pre-wrap text-sm text-slate-200 font-sans leading-relaxed flex-1">
              {viewingResult}
            </div>
            <div className="pt-3 border-t border-slate-800 flex justify-end gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(viewingResult);
                  alert('Summary copied to clipboard!');
                }}
                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300"
              >
                Copy Text
              </button>
              <button
                onClick={() => setViewingResult(null)}
                className="px-4 py-1.5 rounded-lg text-xs font-medium bg-sky-600 hover:bg-sky-500 text-white"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Scheduling Explanation Modal */}
      {activeExplanation && (
        <SchedulingExplanationModal
          explanation={activeExplanation}
          onClose={() => setActiveExplanation(null)}
        />
      )}
    </div>
  );
};
