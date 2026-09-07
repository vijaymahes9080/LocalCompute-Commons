import React from 'react';
import { Layers, Clock, Server, CheckCircle2 } from 'lucide-react';
import { JobTask } from '../types';

interface LiveGanttTimelineProps {
  tasks: JobTask[];
}

export const LiveGanttTimeline: React.FC<LiveGanttTimelineProps> = ({ tasks }) => {
  if (!tasks || tasks.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel p-5 rounded-2xl space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-sm text-white flex items-center gap-2">
          <Layers className="w-4 h-4 text-sky-400" />
          Parallel Execution Gantt Timeline
        </h3>
        <span className="text-[11px] font-mono text-slate-400">
          {tasks.filter((t) => t.state === 'succeeded').length} / {tasks.length} Chunks Finished
        </span>
      </div>

      <div className="space-y-2">
        {tasks.map((task) => {
          const isDone = task.state === 'succeeded';
          const isRunning = task.state === 'running';

          return (
            <div
              key={task.id}
              className="p-2.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-slate-400 w-16">Task #{task.sequence_num}</span>
                <span className="text-slate-200 font-semibold truncate max-w-xs">
                  {task.assigned_node_name || 'Worker Assignment Pending'}
                </span>
              </div>

              {/* Progress representation */}
              <div className="flex items-center gap-3">
                <div className="w-36 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-300 ${
                      isDone
                        ? 'bg-emerald-500 w-full'
                        : isRunning
                        ? 'bg-sky-500 w-3/4 animate-pulse'
                        : 'bg-amber-500 w-1/4'
                    }`}
                  ></div>
                </div>

                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    isDone
                      ? 'bg-emerald-500/10 text-emerald-400'
                      : isRunning
                      ? 'bg-sky-500/10 text-sky-400'
                      : 'bg-amber-500/10 text-amber-400'
                  }`}
                >
                  {task.state}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
