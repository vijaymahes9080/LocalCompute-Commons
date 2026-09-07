# n8n Automation & Monitoring Setup

LocalCompute Commons includes an importable workflow in `workflows/n8n/capacity_and_outage_monitoring.json` designed for n8n Community Edition.

---

## 1. Importing the Workflow

1. Open your n8n web dashboard at `http://localhost:5678`.
2. Go to **Workflows** > **Add Workflow**.
3. Click the **...** menu in the top right and select **Import from File**.
4. Choose `workflows/n8n/capacity_and_outage_monitoring.json`.

---

## 2. Workflow Logic

1. **Hourly Schedule Trigger**: Fires once every 60 minutes.
2. **HTTP Request**: Queries `GET /api/v1/capacity/snapshot` on the Coordinator.
3. **Condition Check**: Evaluates if `online_nodes < 1` (cluster outage) or `avg_queue_wait_seconds > 60.0` (severe queue latency).
4. **Alert Ingestion**: If triggered, issues `POST /api/v1/alerts` to create an actionable system alert in the Coordinator.
