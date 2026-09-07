"""
Capacity Snapshot Calculation and Exporter
"""
from typing import List, Dict, Any
from datetime import datetime
from packages.shared.models.schemas import CapacitySnapshot, WorkerNodeResponse
from packages.shared.models.enums import NodeStatus

def generate_cluster_capacity_snapshot(
    nodes: List[WorkerNodeResponse],
    active_jobs: int,
    pending_tasks: int,
    running_tasks: int,
    avg_queue_wait: float = 0.0
) -> CapacitySnapshot:
    """Computes a real-time capacity and compute availability snapshot."""
    online_nodes = [n for n in nodes if n.status == NodeStatus.ONLINE]
    paused_nodes = [n for n in nodes if n.status == NodeStatus.PAUSED]
    
    total_cpu = sum(n.capabilities.cpu_cores for n in online_nodes)
    # Available CPU approximated by (1 - utilization) * cores
    avail_cpu = sum(
        int(n.capabilities.cpu_cores * max(0.0, 1.0 - (n.capabilities.cpu_utilization_pct / 100.0)))
        for n in online_nodes
    )
    
    total_mem_gb = sum(n.capabilities.memory_mb for n in online_nodes) / 1024.0
    avail_mem_gb = sum(n.capabilities.memory_available_mb for n in online_nodes) / 1024.0
    
    total_vram_gb = sum((n.capabilities.vram_mb or 0) for n in online_nodes) / 1024.0
    avail_vram_gb = sum((n.capabilities.vram_available_mb or 0) for n in online_nodes) / 1024.0
    
    # Model cache summary
    model_counts: Dict[str, int] = {}
    for n in online_nodes:
        for model in n.capabilities.cached_models:
            model_counts[model] = model_counts.get(model, 0) + 1
            
    return CapacitySnapshot(
        total_nodes=len(nodes),
        online_nodes=len(online_nodes),
        paused_nodes=len(paused_nodes),
        total_cpu_cores=total_cpu,
        available_cpu_cores=avail_cpu,
        total_memory_gb=round(total_mem_gb, 2),
        available_memory_gb=round(avail_mem_gb, 2),
        total_vram_gb=round(total_vram_gb, 2),
        available_vram_gb=round(avail_vram_gb, 2),
        cached_models_summary=model_counts,
        active_jobs=active_jobs,
        pending_tasks=pending_tasks,
        running_tasks=running_tasks,
        avg_queue_wait_seconds=round(avg_queue_wait, 2),
        snapshot_time=datetime.utcnow()
    )
