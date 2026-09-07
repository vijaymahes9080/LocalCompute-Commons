# Zero-Retention Privacy Model & Perimeter Classification

## 1. Perimeter Classifications

| Privacy Class | Allowed Nodes | Ingestion Sanitization | Retention Policy | Typical Workload |
| :--- | :--- | :--- | :--- | :--- |
| `local_only` | `is_localhost == True` or `is_airgapped == True` | None (Local execution) | Memory only | Medical records, confidential research, proprietary IP |
| `trusted_nodes` | `trust_level IN [TRUSTED_LAB, AIRGAPPED]` | Sensitive key stripping | Ephemeral batch execution | Departmental papers, student thesis code |
| `standard` | Any node with `trust_level != UNTRUSTED` | Bearer token & PII regex redaction | Ephemeral batch execution | Public datasets, open-access literature |

---

## 2. Zero-Retention Execution Guarantees

1. **No Raw Document Storage**: The Coordinator decomposes incoming batches into in-memory task chunks dispatched across active worker leases. Raw input documents are never written to unencrypted disks.
2. **Ephemeral Inference**: Worker nodes process chunks directly in Ollama memory and dispose of context windows immediately upon task completion.
3. **Automated Metadata Redaction**: In the `standard` privacy class, internal IP addresses, Bearer tokens, passwords, and private API keys are replaced with `[REDACTED]` prior to dispatch.
