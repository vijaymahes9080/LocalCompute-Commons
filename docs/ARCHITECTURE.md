# System Architecture & Distributed State Machine

LocalCompute Commons coordinates decentralized compute nodes with deterministic scheduling, privacy-preserving placement, and fault-tolerant lease lifecycles.

---

## 1. System Topology

```mermaid
graph TD
    subgraph UI ["User & Agent Layer"]
        Web[React Web UI]
        MCP[MCP Agent Client]
        N8N[n8n Automation]
    end

    subgraph Coordinator ["Coordinator Control Plane (FastAPI)"]
        Router[API Gateway & Auth]
        Scheduler[Deterministic Policy Engine]
        Recovery[Lease Watcher & Recovery Daemon]
        Approval[Multi-Party Approval Gate]
    end

    subgraph DataStore ["Persistence & Messaging"]
        DB[(PostgreSQL / SQLite Metadata)]
        Queue[(Redis Streams / Priority Queue)]
        Metrics[(Prometheus Exporter)]
    end

    subgraph Workers ["Heterogeneous Worker Fleet"]
        WA[Worker Alpha: Lab Rig RTX 4090]
        WB[Worker Beta: Server Node A100]
        WC[Worker Gamma: Community Desktop]
    end

    UI --> Router
    Router --> DB
    Router --> Queue
    Router --> Scheduler
    Router --> Approval
    Recovery --> DB
    Recovery --> Queue
    Workers <--> Router
    Router --> Metrics
```

---

## 2. Job & Task State Machine

### Job Lifecycle States
- `pending`: Workload received, awaiting task decomposition and queue dispatch.
- `queued`: Tasks queued, waiting for worker lease claims.
- `assigned`: Tasks mapped to candidate workers.
- `running`: One or more tasks actively executing on worker hardware.
- `succeeded`: All batch tasks successfully completed and output aggregated.
- `failed`: One or more tasks reached terminal retry limit.
- `cancelled`: Manually aborted by user or administrator.
- `expired`: Workload exceeded maximum allowed execution runtime.

### Task State Transition Diagram
```mermaid
stateDiagram-v2
    [*] --> pending
    pending --> queued
    queued --> assigned
    assigned --> running
    running --> succeeded : result valid
    running --> retrying : lease expired / fail
    retrying --> queued : backoff elapsed
    running --> failed : retries exhausted
    queued --> cancelled : job abort
    running --> cancelled : job abort
    succeeded --> [*]
    failed --> [*]
    cancelled --> [*]
```

---

## 3. Worker Lease & Failure Recovery Protocol

1. **Heartbeat Protocol**: Workers emit telemetry every 5 seconds. Nodes with no heartbeat for $>30\text{s}$ are transitioned to `offline`.
2. **Time-Bounded Leases**: When a worker claims a task, a 60-second lease is recorded in PostgreSQL.
3. **Automated Recovery Loop**: An asynchronous recovery daemon scans for expired leases every 3 seconds.
4. **Idempotent Re-queueing**: Expired tasks have their `attempt_count` incremented. If `attempt_count < max_retries`, the task state is reset to `queued` for assignment to another healthy worker.
5. **Cryptographic Result Signing**: When a worker finishes inference, it computes a canonical SHA-256 checksum and HMAC signature over the output payload.
