# Deterministic Scheduling Policy Specification

## 1. Design Philosophy
LocalCompute Commons intentionally enforces a **strictly deterministic, explainable scoring policy** implemented in Python. The LLM / Agent layer is used exclusively to translate explanations for human operators and cannot override hard safety constraints or alter node assignments.

---

## 2. Hard Constraint Filtering (Pre-Scoring Stage)

Before candidate nodes are scored, they must pass 5 hard validation filters:

1. **Status Constraint**: `node.status == NodeStatus.ONLINE`
2. **Privacy Perimeter Match**:
   - `local_only`: Requires `node.is_localhost == True` or `node.is_airgapped == True`.
   - `trusted_nodes`: Requires `node.trust_level IN [TRUSTED_LAB, AIRGAPPED]`.
   - `standard`: Requires `node.trust_level != UNTRUSTED`.
3. **Memory Availability**: `node.memory_available_mb >= 512 MB`.
4. **Battery Threshold**: If discharging (not on AC), `node.battery_level >= 20.0%`.
5. **Clock Skew Bound**: $|node.\text{clock\_skew\_ms}| \le 5000\text{ ms}$.

Any candidate failing any rule is appended to `excluded_nodes` with the violated constraint recorded.

---

## 3. Mathematical Scoring Function

For each eligible node $N$ and required model $M$, the total score is computed as:

$$\text{TotalScore}(N, M) = S_{\text{Resource}}(N) + S_{\text{Cache}}(N, M) + S_{\text{Locality}}(N) + S_{\text{Power}}(N) - P_{\text{Load}}(N)$$

### Component Breakdowns:
1. **Resource Fit ($0 \le S_{\text{Resource}} \le 25$)**:
   $$S_{\text{Resource}} = 25 \times \left(0.4 \times \min\left(1.0, \frac{\text{Cores}}{16}\right) + 0.6 \times \min\left(1.0, \frac{\text{FreeRAM MB}}{16384}\right)\right)$$

2. **Model Cache ($S_{\text{Cache}} \in \{0, 25\}$)**:
   $$S_{\text{Cache}} = 25.0 \quad \text{if } M \in N.\text{cached\_models} \quad \text{else } 0.0$$

3. **Data Locality & Network ($0 \le S_{\text{Locality}} \le 25$)**:
   $$S_{\text{Locality}} = (15.0 \text{ if } N.\text{is\_localhost} \text{ else } 0.0) + \min\left(10.0, \frac{\text{Throughput Mbps}}{1000} \times 10\right)$$

4. **Power & Battery ($0 \le S_{\text{Power}} \le 25$)**:
   $$S_{\text{Power}} = 25.0 \quad \text{if AC/Charging} \quad \text{else } 25.0 \times \left(\frac{\text{Battery \%}}{100}\right)$$

5. **Load & Lease Penalty ($P_{\text{Load}} \ge 0$)**:
   $$P_{\text{Load}} = 5.0 \times \text{ActiveLeases} + 0.15 \times \text{CPU Utilization \%}$$

---

## 4. Structured Output Format

```json
{
  "job_id": "job-8921-uuid",
  "task_id": "task-001",
  "selected_node_id": "node-alpha",
  "selected_node_name": "Lab-Alpha-RTX4090",
  "total_score": 88.5,
  "factors": [
    {
      "factor_name": "ResourceFit",
      "raw_value": "16 cores, 24576MB RAM",
      "weight": 25.0,
      "contribution": 25.0,
      "description": "Hardware compute and free memory availability"
    },
    {
      "factor_name": "ModelCache",
      "raw_value": "cached=True",
      "weight": 25.0,
      "contribution": 25.0,
      "description": "Zero-download instant inference execution when model is preloaded"
    }
  ],
  "excluded_nodes": [],
  "policy_version": "v1.2.0-deterministic",
  "requires_approval": false,
  "generated_at": "2026-09-07T20:00:00Z"
}
```
