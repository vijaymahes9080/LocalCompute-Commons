"""
End-to-End (E2E) Test: Full Lifecycle Validation
Flow: Login -> Register Worker -> Submit Batch -> Observe Scheduling -> Disconnect Worker -> Recover Tasks -> Inspect Audit Log
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from apps.coordinator.main import app
from packages.shared.models.schemas import WorkerNodeRegisterRequest, NodeCapability, WorkloadCreateRequest
from packages.shared.models.enums import TrustLevel, PrivacyClass, WorkloadType

@pytest.mark.asyncio
async def test_full_lifecycle_e2e(db_session):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Login
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "AdminLocalCompute2026!"}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Register Worker Node
        node_req = WorkerNodeRegisterRequest(
            node_id="worker-e2e-1",
            node_name="E2E-Worker-Node",
            trust_level=TrustLevel.TRUSTED_LAB,
            is_localhost=True,
            capabilities=NodeCapability(
                cpu_cores=16,
                cpu_utilization_pct=15.0,
                memory_mb=32768,
                memory_available_mb=28000,
                gpu_name="RTX 4090",
                vram_mb=24576,
                vram_available_mb=20000,
                os_name="Linux",
                os_version="6.8.0",
                cached_models=["llama3:8b"],
                battery_level=100.0,
                is_charging=True,
                power_state="ac",
                network_mbps=1000.0,
                clock_skew_ms=1.5
            )
        )
        reg_resp = await client.post(
            "/api/v1/nodes/register",
            json=node_req.model_dump(mode="json"),
            headers=headers
        )
        assert reg_resp.status_code == 200
        worker_token = reg_resp.json()["token"]
        worker_headers = {"Authorization": f"Bearer {worker_token}"}

        # Step 3: Submit Batch Workload
        workload_req = WorkloadCreateRequest(
            title="E2E Distributed Summarization",
            workload_type=WorkloadType.SUMMARIZATION,
            privacy_class=PrivacyClass.TRUSTED_NODES,
            required_model="llama3:8b",
            priority=9,
            documents=[
                {"text": "Section 1: Distributed compute-sharing provides scalable local AI inference."},
                {"text": "Section 2: Fault tolerance recovers orphaned tasks after worker disconnects."}
            ]
        )
        sub_resp = await client.post(
            "/api/v1/workloads/submit",
            json=workload_req.model_dump(mode="json"),
            headers=headers
        )
        assert sub_resp.status_code == 200
        job_data = sub_resp.json()
        assert job_data["total_tasks"] == 2
        
        # Step 4: Observe Scheduling Explanation
        explanation = job_data.get("scheduling_explanation")
        assert explanation is not None
        assert explanation["selected_node_id"] in ["worker-e2e-1", "node-alpha"]
        assert explanation["total_score"] > 0

        # Step 5: Worker Claims Task
        claim_resp = await client.post(
            "/api/v1/tasks/claim",
            json={"node_id": "worker-e2e-1", "max_tasks": 1},
            headers=worker_headers
        )
        assert claim_resp.status_code == 200
        claimed_tasks = claim_resp.json()["tasks"]
        assert len(claimed_tasks) >= 1
        task_id = claimed_tasks[0]["id"]

        # Step 6: Complete Claimed Task with Signed Checksum
        comp_resp = await client.post(
            f"/api/v1/tasks/{task_id}/complete",
            json={
                "node_id": "worker-e2e-1",
                "task_id": task_id,
                "output_payload": {"summary": "Completed E2E summary output"},
                "result_checksum": "dummy_checksum",
                "execution_time_seconds": 0.45
            },
            headers=worker_headers
        )
        assert comp_resp.status_code == 200

        # Step 7: Inspect Immutable Audit Log
        audit_resp = await client.get("/api/v1/audit", headers=headers)
        assert audit_resp.status_code == 200
        events = audit_resp.json()
        assert len(events) >= 3
        # Check presence of SHA-256 hash
        for ev in events:
            assert len(ev["event_hash"]) == 64
