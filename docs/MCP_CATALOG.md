# Model Context Protocol (MCP) Tool Catalog

LocalCompute Commons exposes **10 official Model Context Protocol (MCP) tools** compliant with the Python MCP SDK.

---

## Tool Reference

### 1. `list_available_nodes`
- **Classification**: `read-only`
- **Description**: Lists active local compute nodes, current CPU/RAM utilization, and cached models.
- **Parameters**: `status_filter` (string: `online` | `paused` | `all`)

### 2. `inspect_node_capabilities`
- **Classification**: `read-only`
- **Description**: Returns hardware telemetry (CPU, RAM, GPU, VRAM, battery, network, clock skew) for a node.
- **Parameters**: `node_id` (string, required)

### 3. `submit_workload`
- **Classification**: `operational`
- **Description**: Submits a batch text summarization workload for deterministic scheduling.
- **Parameters**: `title` (str), `documents` (list of strings), `required_model` (str), `privacy_class` (str), `priority` (int: 1-10)

### 4. `get_job_status`
- **Classification**: `read-only`
- **Description**: Retrieves batch progress, task breakdown, scheduling explanation, and aggregated summary.
- **Parameters**: `job_id` (string, required)

### 5. `get_task_status`
- **Classification**: `read-only`
- **Description**: Retrieves execution details and attempt history for an individual job task.
- **Parameters**: `task_id` (string, required)

### 6. `rebalance_job`
- **Classification**: `operational`
- **Description**: Re-evaluates and schedules unassigned or retrying tasks across the worker cluster.
- **Parameters**: `job_id` (string, required)

### 7. `pause_node`
- **Classification**: `administrative`
- **Description**: Pauses a worker node. Pauses exceeding 60 minutes require administrative approval.
- **Parameters**: `node_id` (string, required), `duration_minutes` (int)

### 8. `revoke_node`
- **Classification**: `administrative`
- **Description**: Initiates node revocation workflow. Strictly gated behind multi-party authorization.
- **Parameters**: `node_id` (string, required), `reason` (string, required)

### 9. `generate_capacity_report`
- **Classification**: `read-only`
- **Description**: Generates a cluster-wide compute and memory snapshot report.
- **Parameters**: `include_offline` (boolean)

### 10. `get_audit_events`
- **Classification**: `read-only`
- **Description**: Retrieves immutable audit event history for security and scheduling compliance.
- **Parameters**: `limit` (int), `event_type` (string)
