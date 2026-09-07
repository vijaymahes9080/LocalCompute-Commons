"""
Strict Tool Definitions and Handlers for Model Context Protocol (MCP) Server
"""
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Tool Input Schemas
# ---------------------------------------------------------
class ListAvailableNodesInput(BaseModel):
    status_filter: Optional[str] = Field("online", description="Filter by status: online | paused | all")

class InspectNodeCapabilitiesInput(BaseModel):
    node_id: str = Field(..., description="Unique node identifier or UUID")

class SubmitWorkloadInput(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Workload title")
    documents: List[str] = Field(..., min_length=1, description="List of document text chunks to summarize")
    required_model: str = Field("llama3:8b", description="Model identifier e.g. llama3:8b or mistral:7b")
    privacy_class: str = Field("standard", description="Privacy class: local_only | trusted_nodes | standard")
    priority: int = Field(5, ge=1, le=10, description="Priority 1-10")

class GetJobStatusInput(BaseModel):
    job_id: str = Field(..., description="Job identifier")

class GetTaskStatusInput(BaseModel):
    task_id: str = Field(..., description="Task identifier")

class RebalanceJobInput(BaseModel):
    job_id: str = Field(..., description="Job identifier to re-evaluate and rebalance")

class PauseNodeInput(BaseModel):
    node_id: str = Field(..., description="Node ID to pause")
    duration_minutes: int = Field(30, ge=1, le=1440, description="Duration to pause in minutes")

class RevokeNodeInput(BaseModel):
    node_id: str = Field(..., description="Node ID to revoke")
    reason: str = Field(..., min_length=5, description="Administrative reason for revocation")

class GenerateCapacityReportInput(BaseModel):
    include_offline: bool = Field(False, description="Whether to include offline nodes in summary")

class GetAuditEventsInput(BaseModel):
    limit: int = Field(20, ge=1, le=100, description="Number of audit records to return")
    event_type: Optional[str] = Field(None, description="Filter by event type")

# ---------------------------------------------------------
# MCP Tool Registry Metadata
# ---------------------------------------------------------
TOOL_DEFINITIONS = [
    {
        "name": "list_available_nodes",
        "description": "Lists active local compute nodes, their current utilization, and cached models.",
        "classification": "read-only",
        "inputSchema": ListAvailableNodesInput.model_json_schema()
    },
    {
        "name": "inspect_node_capabilities",
        "description": "Returns in-depth hardware telemetry (CPU, RAM, GPU, VRAM, battery, network) for a specific node.",
        "classification": "read-only",
        "inputSchema": InspectNodeCapabilitiesInput.model_json_schema()
    },
    {
        "name": "submit_workload",
        "description": "Submits a privacy-aware batch text summarization workload for deterministic scheduling.",
        "classification": "operational",
        "inputSchema": SubmitWorkloadInput.model_json_schema()
    },
    {
        "name": "get_job_status",
        "description": "Retrieves the progress, task breakdown, scheduling explanation, and aggregated summary of a job.",
        "classification": "read-only",
        "inputSchema": GetJobStatusInput.model_json_schema()
    },
    {
        "name": "get_task_status",
        "description": "Retrieves execution details and attempt history for an individual job task.",
        "classification": "read-only",
        "inputSchema": GetTaskStatusInput.model_json_schema()
    },
    {
        "name": "rebalance_job",
        "description": "Re-evaluates and schedules unassigned or retrying tasks across the worker cluster.",
        "classification": "operational",
        "inputSchema": RebalanceJobInput.model_json_schema()
    },
    {
        "name": "pause_node",
        "description": "Pauses a worker node. Pauses exceeding 60 minutes require administrative approval.",
        "classification": "administrative",
        "inputSchema": PauseNodeInput.model_json_schema()
    },
    {
        "name": "revoke_node",
        "description": "Initiates node revocation workflow. Strictly gated behind multi-party authorization.",
        "classification": "administrative",
        "inputSchema": RevokeNodeInput.model_json_schema()
    },
    {
        "name": "generate_capacity_report",
        "description": "Generates a cluster-wide compute and memory snapshot report.",
        "classification": "read-only",
        "inputSchema": GenerateCapacityReportInput.model_json_schema()
    },
    {
        "name": "get_audit_events",
        "description": "Retrieves immutable audit event history for security and scheduling compliance.",
        "classification": "read-only",
        "inputSchema": GetAuditEventsInput.model_json_schema()
    }
]
