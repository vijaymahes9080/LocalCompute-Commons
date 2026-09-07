"""
Unit Tests for Deterministic Scheduler Engine
"""
import pytest
from datetime import datetime
from packages.shared.models.schemas import (
    WorkerNodeResponse, NodeCapability
)
from packages.shared.models.enums import NodeStatus, TrustLevel, PrivacyClass
from services.scheduler.engine import DeterministicScheduler

def make_node(
    node_id: str,
    name: str,
    status: NodeStatus = NodeStatus.ONLINE,
    trust: TrustLevel = TrustLevel.TRUSTED_LAB,
    is_localhost: bool = False,
    cached_models=None,
    cpu_cores: int = 8,
    memory_available_mb: int = 8192,
    cpu_util: float = 10.0,
    is_charging: bool = True,
    battery_level: float = 100.0,
    active_leases: int = 0,
    clock_skew_ms: float = 0.0
) -> WorkerNodeResponse:
    return WorkerNodeResponse(
        id=f"uuid-{node_id}",
        node_id=node_id,
        node_name=name,
        status=status,
        trust_level=trust,
        is_localhost=is_localhost,
        is_airgapped=False,
        capabilities=NodeCapability(
            cpu_cores=cpu_cores,
            cpu_utilization_pct=cpu_util,
            memory_mb=16384,
            memory_available_mb=memory_available_mb,
            gpu_name="RTX 3080",
            vram_mb=10240,
            vram_available_mb=8192,
            os_name="Linux",
            os_version="6.5.0",
            cached_models=cached_models or ["llama3:8b"],
            battery_level=battery_level,
            is_charging=is_charging,
            power_state="ac" if is_charging else "battery",
            network_mbps=500.0,
            clock_skew_ms=clock_skew_ms
        ),
        registered_at=datetime.utcnow(),
        active_leases_count=active_leases
    )

def test_deterministic_scoring_reproducibility():
    scheduler = DeterministicScheduler()
    node_a = make_node("node-a", "Node A", cached_models=["llama3:8b"], active_leases=0)
    node_b = make_node("node-b", "Node B", cached_models=["mistral:7b"], active_leases=0)
    
    # Run 10 times, scores and selection must be 100% identical
    results = [
        scheduler.filter_and_score_nodes(
            job_id="job-1",
            privacy_class=PrivacyClass.STANDARD,
            required_model="llama3:8b",
            nodes=[node_a, node_b]
        )
        for _ in range(10)
    ]
    
    for r in results:
        assert r.selected_node_id == "node-a"
        assert r.total_score == results[0].total_score
        assert len(r.factors) == 5

def test_model_cache_weight_advantage():
    scheduler = DeterministicScheduler()
    node_cached = make_node("node-cached", "Cached", cached_models=["llama3:8b"])
    node_uncached = make_node("node-uncached", "Uncached", cached_models=["other:7b"])
    
    explanation = scheduler.filter_and_score_nodes(
        job_id="job-1",
        privacy_class=PrivacyClass.STANDARD,
        required_model="llama3:8b",
        nodes=[node_cached, node_uncached]
    )
    assert explanation.selected_node_id == "node-cached"
    
    # Verify ModelCache factor contribution
    cache_factor = next(f for f in explanation.factors if f.factor_name == "ModelCache")
    assert cache_factor.contribution == 25.0

def test_local_only_privacy_constraint_exclusion():
    scheduler = DeterministicScheduler()
    node_remote = make_node("node-remote", "Remote Node", is_localhost=False)
    node_local = make_node("node-local", "Local Node", is_localhost=True)
    
    explanation = scheduler.filter_and_score_nodes(
        job_id="job-priv",
        privacy_class=PrivacyClass.LOCAL_ONLY,
        required_model="llama3:8b",
        nodes=[node_remote, node_local]
    )
    
    assert explanation.selected_node_id == "node-local"
    assert len(explanation.excluded_nodes) == 1
    assert explanation.excluded_nodes[0].node_id == "node-remote"
    assert "local_only" in explanation.excluded_nodes[0].reason

def test_low_battery_threshold_exclusion():
    scheduler = DeterministicScheduler()
    node_low_batt = make_node("node-batt", "Discharging Node", is_charging=False, battery_level=12.0)
    
    explanation = scheduler.filter_and_score_nodes(
        job_id="job-batt",
        privacy_class=PrivacyClass.STANDARD,
        required_model="llama3:8b",
        nodes=[node_low_batt]
    )
    
    assert explanation.selected_node_id is None
    assert len(explanation.excluded_nodes) == 1
    assert "battery" in explanation.excluded_nodes[0].reason

def test_clock_skew_threshold_exclusion():
    scheduler = DeterministicScheduler()
    node_skewed = make_node("node-skew", "Clock Skew Node", clock_skew_ms=8500.0)
    
    explanation = scheduler.filter_and_score_nodes(
        job_id="job-skew",
        privacy_class=PrivacyClass.STANDARD,
        required_model="llama3:8b",
        nodes=[node_skewed]
    )
    
    assert explanation.selected_node_id is None
    assert len(explanation.excluded_nodes) == 1
    assert "Clock skew" in explanation.excluded_nodes[0].reason
