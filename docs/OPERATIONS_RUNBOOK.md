# Operations Runbook

## 1. Onboarding a New Compute Node

1. Install Python 3.11 and the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables on the node:
   ```bash
   export NODE_NAME="Physics-Lab-GPU-01"
   export COORDINATOR_URL="http://<coordinator-ip>:8000"
   export TRUST_LEVEL="trusted_lab"
   export CACHED_MODELS="llama3:8b,mistral:7b"
   ```
3. Start the worker daemon:
   ```bash
   python examples/run_local_worker.py
   ```
4. Verify registration on the web dashboard at `http://<coordinator-ip>:5173`.

---

## 2. Handling Node Failures

- If a worker crashes, the coordinator's `RecoveryEngine` automatically detects lease expirations within 60 seconds (or 30s missed heartbeats).
- Orphaned tasks are returned to `queued` state and reassigned to active nodes.
- To temporarily take a node down for maintenance without losing tasks, use the **Pause Node** action in the Web UI.

---

## 3. Database Backup & Restore

```bash
# PostgreSQL Backup
docker exec -t lc-postgres pg_dump -U lc_user localcompute > backup_$(date +%Y%m%d).sql

# PostgreSQL Restore
cat backup_20260907.sql | docker exec -i lc-postgres psql -U lc_user -d localcompute
```
