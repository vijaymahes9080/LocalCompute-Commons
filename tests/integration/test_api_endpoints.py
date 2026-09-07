"""
Integration Tests for Coordinator FastAPI REST Endpoints
"""
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_healthz_and_root(async_client: AsyncClient):
    resp = await async_client.get("/healthz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "coordinator"

@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(async_client: AsyncClient):
    resp = await async_client.get("/metrics")
    assert resp.status_code == 200
    assert "localcompute_" in resp.text

@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "AdminLocalCompute2026!"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"
    assert data["user"]["role"] == "admin"

@pytest.mark.asyncio
async def test_auth_login_failure(async_client: AsyncClient):
    resp = await async_client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "WrongPassword"}
    )
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_list_nodes(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get("/api/v1/nodes", headers=headers)
    assert resp.status_code == 200
    nodes = resp.json()
    assert len(nodes) >= 1
    assert nodes[0]["node_id"] == "node-alpha"

@pytest.mark.asyncio
async def test_submit_workload_and_inspect_job(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "title": "Integration Test Workload",
        "workload_type": "summarization",
        "privacy_class": "trusted_nodes",
        "required_model": "llama3:8b",
        "priority": 7,
        "documents": [
            {"text": "Section 1: Distributed compute-sharing enables edge execution."},
            {"text": "Section 2: Deterministic scheduling ensures predictable performance."}
        ]
    }
    
    # Submit
    resp = await async_client.post("/api/v1/workloads/submit", json=payload, headers=headers)
    assert resp.status_code == 200
    job = resp.json()
    assert job["title"] == "Integration Test Workload"
    assert job["total_tasks"] == 2
    assert "scheduling_explanation" in job
    assert job["scheduling_explanation"]["selected_node_id"] == "node-alpha"

    # Get Job Detail
    job_id = job["id"]
    detail_resp = await async_client.get(f"/api/v1/jobs/{job_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["tasks"]) == 2

@pytest.mark.asyncio
async def test_capacity_snapshot(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get("/api/v1/capacity/snapshot", headers=headers)
    assert resp.status_code == 200
    snap = resp.json()
    assert snap["total_nodes"] >= 1
    assert snap["total_cpu_cores"] >= 16

@pytest.mark.asyncio
async def test_audit_log_query(async_client: AsyncClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = await async_client.get("/api/v1/audit", headers=headers)
    assert resp.status_code == 200
    events = resp.json()
    assert isinstance(events, list)
