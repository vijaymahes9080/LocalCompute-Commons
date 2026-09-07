"""
Prometheus Metrics Instrumentation for LocalCompute Commons
"""
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Counters
TASKS_SUBMITTED_TOTAL = Counter(
    "localcompute_tasks_submitted_total",
    "Total number of workload tasks submitted",
    ["workload_type", "privacy_class"]
)

TASKS_COMPLETED_TOTAL = Counter(
    "localcompute_tasks_completed_total",
    "Total number of tasks successfully completed",
    ["worker_id", "model"]
)

TASKS_FAILED_TOTAL = Counter(
    "localcompute_tasks_failed_total",
    "Total number of task failures",
    ["worker_id", "reason"]
)

TASKS_RETRIED_TOTAL = Counter(
    "localcompute_tasks_retried_total",
    "Total number of task retries triggered",
    ["reason"]
)

DATA_TRANSFERRED_BYTES_TOTAL = Counter(
    "localcompute_data_transferred_bytes_total",
    "Total bytes of task input/output payload transferred",
    ["direction"]
)

# Gauges
ACTIVE_WORKER_NODES = Gauge(
    "localcompute_active_worker_nodes",
    "Number of active online worker nodes",
    ["trust_level"]
)

CLUSTER_TOTAL_CPU_CORES = Gauge(
    "localcompute_cluster_total_cpu_cores",
    "Total CPU cores across active worker nodes"
)

CLUSTER_AVAILABLE_MEMORY_BYTES = Gauge(
    "localcompute_cluster_available_memory_bytes",
    "Total available memory across worker nodes in bytes"
)

CLUSTER_AVAILABLE_VRAM_BYTES = Gauge(
    "localcompute_cluster_available_vram_bytes",
    "Total available VRAM across worker nodes in bytes"
)

QUEUE_PENDING_TASKS = Gauge(
    "localcompute_queue_pending_tasks",
    "Current number of tasks waiting in queue"
)

ACTIVE_RUNNING_TASKS = Gauge(
    "localcompute_active_running_tasks",
    "Current number of tasks actively running on workers"
)

# Histograms
TASK_QUEUE_WAIT_SECONDS = Histogram(
    "localcompute_task_queue_wait_seconds",
    "Time tasks spend waiting in queue before assignment",
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

TASK_EXECUTION_DURATION_SECONDS = Histogram(
    "localcompute_task_execution_duration_seconds",
    "Execution duration of tasks on worker nodes",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0, 120.0, 300.0]
)

API_REQUEST_LATENCY_SECONDS = Histogram(
    "localcompute_api_request_latency_seconds",
    "API endpoint response latency",
    ["endpoint", "method"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

def get_metrics_payload() -> bytes:
    """Returns the Prometheus formatted metrics snapshot."""
    return generate_latest()
