"""
Batch Workload Result Aggregation and Synthesis Engine
"""
from typing import List, Dict, Any

class BatchResultAggregator:
    """
    Combines individual task chunk summaries into an overall cohesive synthesis.
    """
    @staticmethod
    def aggregate_summaries(tasks: List[Dict[str, Any]], job_title: str) -> str:
        """
        Aggregates multiple completed task outputs into a unified multi-section document.
        """
        if not tasks:
            return "No task outputs available for aggregation."

        # Sort tasks deterministically by sequence_num
        sorted_tasks = sorted(tasks, key=lambda t: t.get("sequence_num", 0))
        
        sections = []
        sections.append(f"# Consolidated Summary: {job_title}\n")
        sections.append(f"**Total Processed Sections:** {len(sorted_tasks)}\n")
        sections.append("---\n")
        
        for idx, task in enumerate(sorted_tasks, 1):
            out = task.get("output_payload") or {}
            summary = out.get("summary", "No summary produced.")
            task_id = task.get("id", f"task-{idx}")
            node_name = task.get("assigned_node_name", "Local Node")
            
            sections.append(f"### Section {idx} (Node: {node_name} | Ref: {task_id[:8]}...)\n")
            sections.append(f"{summary}\n")
            
        sections.append("---\n")
        sections.append("*Generated automatically by LocalCompute Commons distributed aggregator.*")
        
        return "\n".join(sections)
