"""
Unit & Contract Tests for MCP Tools and Schemas
"""
import pytest
from pydantic import ValidationError
from services.mcp_server.tools import (
    TOOL_DEFINITIONS,
    SubmitWorkloadInput, PauseNodeInput, RevokeNodeInput,
    InspectNodeCapabilitiesInput
)

def test_mcp_tool_definitions_registry():
    assert len(TOOL_DEFINITIONS) == 10
    tool_names = [t["name"] for t in TOOL_DEFINITIONS]
    
    expected_tools = [
        "list_available_nodes",
        "inspect_node_capabilities",
        "submit_workload",
        "get_job_status",
        "get_task_status",
        "rebalance_job",
        "pause_node",
        "revoke_node",
        "generate_capacity_report",
        "get_audit_events"
    ]
    for exp in expected_tools:
        assert exp in tool_names

def test_submit_workload_schema_validation():
    # Valid input
    valid = SubmitWorkloadInput(
        title="Test Batch",
        documents=["Section 1 text", "Section 2 text"],
        required_model="llama3:8b",
        privacy_class="trusted_nodes",
        priority=6
    )
    assert valid.title == "Test Batch"
    assert len(valid.documents) == 2

    # Invalid empty documents list
    with pytest.raises(ValidationError):
        SubmitWorkloadInput(
            title="Invalid",
            documents=[],
            required_model="llama3:8b"
        )

def test_revoke_node_schema_validation():
    # Valid
    valid = RevokeNodeInput(node_id="node-123", reason="Node decommissioning verified")
    assert valid.node_id == "node-123"

    # Too short reason
    with pytest.raises(ValidationError):
        RevokeNodeInput(node_id="node-123", reason="bad")
