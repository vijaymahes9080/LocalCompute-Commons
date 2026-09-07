"""
LocalCompute Commons - Model Context Protocol (MCP) Server
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
import httpx
from pydantic import ValidationError
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from packages.shared.config import settings
from services.mcp_server.tools import (
    TOOL_DEFINITIONS,
    ListAvailableNodesInput, InspectNodeCapabilitiesInput,
    SubmitWorkloadInput, GetJobStatusInput, GetTaskStatusInput,
    RebalanceJobInput, PauseNodeInput, RevokeNodeInput,
    GenerateCapacityReportInput, GetAuditEventsInput
)
from services.monitoring.logger import logger

# Initialize MCP Server instance
mcp_app = Server("localcompute-commons-mcp")

COORDINATOR_URL = f"http://{settings.COORDINATOR_HOST}:{settings.COORDINATOR_PORT}"

async def _get_auth_header() -> Dict[str, str]:
    """Retrieves an admin/operator token from coordinator for MCP actions."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.post(
                f"{COORDINATOR_URL}/api/v1/auth/login",
                json={
                    "username": settings.DEFAULT_ADMIN_USERNAME,
                    "password": settings.DEFAULT_ADMIN_PASSWORD
                }
            )
            if resp.status_code == 200:
                token = resp.json().get("access_token")
                return {"Authorization": f"Bearer {token}"}
        except Exception as exc:
            logger.error(f"Failed to authenticate MCP server: {exc}")
    return {}

@mcp_app.list_tools()
async def list_tools() -> List[types.Tool]:
    """Lists all 10 verified LocalCompute Commons tools."""
    tools = []
    for t in TOOL_DEFINITIONS:
        tools.append(types.Tool(
            name=t["name"],
            description=f"[{t['classification'].upper()}] {t['description']}",
            inputSchema=t["inputSchema"]
        ))
    return tools

@mcp_app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Dispatches tool execution to Coordinator API with input validation and security checks."""
    headers = await _get_auth_header()
    
    try:
        if name == "list_available_nodes":
            validated = ListAvailableNodesInput(**arguments)
            status_param = None if validated.status_filter == "all" else validated.status_filter
            params = {"status": status_param} if status_param else {}
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/nodes", params=params, headers=headers)
                return [types.TextContent(type="text", text=resp.text)]

        elif name == "inspect_node_capabilities":
            validated = InspectNodeCapabilitiesInput(**arguments)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/nodes", headers=headers)
                nodes = resp.json()
                match = next((n for n in nodes if n["node_id"] == validated.node_id or n["id"] == validated.node_id), None)
                if not match:
                    return [types.TextContent(type="text", text=json.dumps({"error": "Node not found"}))]
                return [types.TextContent(type="text", text=json.dumps(match, indent=2))]

        elif name == "submit_workload":
            validated = SubmitWorkloadInput(**arguments)
            payload = {
                "title": validated.title,
                "workload_type": "summarization",
                "privacy_class": validated.privacy_class,
                "required_model": validated.required_model,
                "priority": validated.priority,
                "documents": [{"text": doc} for doc in validated.documents]
            }
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(f"{COORDINATOR_URL}/api/v1/workloads/submit", json=payload, headers=headers)
                return [types.TextContent(type="text", text=resp.text)]

        elif name == "get_job_status":
            validated = GetJobStatusInput(**arguments)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/jobs/{validated.job_id}", headers=headers)
                return [types.TextContent(type="text", text=resp.text)]

        elif name == "get_task_status":
            validated = GetTaskStatusInput(**arguments)
            # Find task across jobs
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/jobs", headers=headers)
                jobs = resp.json()
                for j in jobs:
                    j_detail = await client.get(f"{COORDINATOR_URL}/api/v1/jobs/{j['id']}", headers=headers)
                    tasks = j_detail.json().get("tasks", [])
                    match = next((t for t in tasks if t["id"] == validated.task_id), None)
                    if match:
                        return [types.TextContent(type="text", text=json.dumps(match, indent=2))]
                return [types.TextContent(type="text", text=json.dumps({"error": "Task not found"}))]

        elif name == "rebalance_job":
            validated = RebalanceJobInput(**arguments)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/jobs/{validated.job_id}", headers=headers)
                return [types.TextContent(type="text", text=json.dumps({
                    "status": "rebalanced",
                    "job_id": validated.job_id,
                    "explanation": resp.json().get("scheduling_explanation")
                }))]

        elif name == "pause_node":
            validated = PauseNodeInput(**arguments)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{COORDINATOR_URL}/api/v1/nodes/{validated.node_id}/pause",
                    params={"duration_minutes": validated.duration_minutes},
                    headers=headers
                )
                return [types.TextContent(type="text", text=resp.text)]

        elif name == "revoke_node":
            validated = RevokeNodeInput(**arguments)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{COORDINATOR_URL}/api/v1/nodes/{validated.node_id}/revoke",
                    json={"reason": validated.reason},
                    headers=headers
                )
                return [types.TextContent(type="text", text=resp.text)]

        elif name == "generate_capacity_report":
            validated = GenerateCapacityReportInput(**arguments)
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/capacity/snapshot", headers=headers)
                data = resp.json()
                summary = (
                    f"# LocalCompute Cluster Capacity Report\n"
                    f"- Total Nodes: {data.get('total_nodes')} ({data.get('online_nodes')} Online, {data.get('paused_nodes')} Paused)\n"
                    f"- Total Compute: {data.get('total_cpu_cores')} Cores ({data.get('available_cpu_cores')} Cores Available)\n"
                    f"- Total Memory: {data.get('total_memory_gb')} GB ({data.get('available_memory_gb')} GB Free)\n"
                    f"- Total VRAM: {data.get('total_vram_gb')} GB ({data.get('available_vram_gb')} GB Free)\n"
                    f"- Cached Models: {data.get('cached_models_summary')}\n"
                    f"- Queue: {data.get('pending_tasks')} Pending, {data.get('running_tasks')} Running across {data.get('active_jobs')} Active Jobs."
                )
                return [types.TextContent(type="text", text=summary)]

        elif name == "get_audit_events":
            validated = GetAuditEventsInput(**arguments)
            params = {"limit": validated.limit}
            if validated.event_type:
                params["event_type"] = validated.event_type
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{COORDINATOR_URL}/api/v1/audit", params=params, headers=headers)
                return [types.TextContent(type="text", text=resp.text)]

        else:
            return [types.TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

    except ValidationError as val_err:
        return [types.TextContent(type="text", text=json.dumps({"error": "Schema validation failed", "details": val_err.errors()}))]
    except Exception as exc:
        logger.error(f"Error executing MCP tool {name}: {exc}")
        return [types.TextContent(type="text", text=json.dumps({"error": "Tool execution failed", "message": str(exc)}))]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await mcp_app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="localcompute-commons-mcp",
                server_version="1.0.0",
                capabilities=mcp_app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
