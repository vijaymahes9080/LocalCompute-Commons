"""
Deterministic Scheduler Engine for LocalCompute Commons
"""
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from packages.shared.models.schemas import (
    WorkerNodeResponse, JobResponse, JobTaskResponse,
    SchedulingExplanation, ScoreFactor, ExcludedNode
)
from packages.shared.models.enums import NodeStatus, TrustLevel, PrivacyClass
from services.scheduler.policies import DEFAULT_SCHEDULER_WEIGHTS, SchedulerWeights

class DeterministicScheduler:
    """
    Deterministic scoring and constraint-based scheduling engine.
    Ensures that scheduling decisions are 100% reproducible, verifiable, and auditable.
    """
    def __init__(self, weights: SchedulerWeights = DEFAULT_SCHEDULER_WEIGHTS):
        self.weights = weights
        self.policy_version = "v1.2.0-deterministic"

    def filter_and_score_nodes(
        self,
        job_id: str,
        privacy_class: PrivacyClass,
        required_model: str,
        nodes: List[WorkerNodeResponse],
        task: Optional[JobTaskResponse] = None
    ) -> SchedulingExplanation:
        """
        Applies hard constraint filters, then computes deterministic multi-factor scores
        for all eligible worker nodes. Returns a comprehensive SchedulingExplanation.
        """
        eligible_nodes: List[WorkerNodeResponse] = []
        excluded_nodes: List[ExcludedNode] = []
        
        # 1. Apply Hard Constraints
        for node in nodes:
            # Status check
            if node.status != NodeStatus.ONLINE:
                excluded_nodes.append(ExcludedNode(
                    node_id=node.node_id,
                    node_name=node.node_name,
                    reason=f"Node status is {node.status.value}, not online",
                    violates_constraint="NodeStatus == ONLINE"
                ))
                continue
                
            # Privacy Class Filter
            if privacy_class == PrivacyClass.LOCAL_ONLY:
                if not (node.is_localhost or node.is_airgapped):
                    excluded_nodes.append(ExcludedNode(
                        node_id=node.node_id,
                        node_name=node.node_name,
                        reason="Workload is local_only but node is remote network worker",
                        violates_constraint="is_localhost == True OR is_airgapped == True"
                    ))
                    continue
            elif privacy_class == PrivacyClass.TRUSTED_NODES:
                if node.trust_level not in [TrustLevel.TRUSTED_LAB, TrustLevel.AIRGAPPED]:
                    excluded_nodes.append(ExcludedNode(
                        node_id=node.node_id,
                        node_name=node.node_name,
                        reason=f"Workload requires trusted_nodes but node trust is {node.trust_level.value}",
                        violates_constraint="trust_level IN [TRUSTED_LAB, AIRGAPPED]"
                    ))
                    continue
            elif privacy_class == PrivacyClass.STANDARD:
                if node.trust_level == TrustLevel.UNTRUSTED:
                    excluded_nodes.append(ExcludedNode(
                        node_id=node.node_id,
                        node_name=node.node_name,
                        reason="Node is explicitly marked UNTRUSTED",
                        violates_constraint="trust_level != UNTRUSTED"
                    ))
                    continue

            # Memory threshold
            if node.capabilities.memory_available_mb < self.weights.MIN_FREE_MEMORY_MB:
                excluded_nodes.append(ExcludedNode(
                    node_id=node.node_id,
                    node_name=node.node_name,
                    reason=f"Available RAM ({node.capabilities.memory_available_mb}MB) < required ({self.weights.MIN_FREE_MEMORY_MB}MB)",
                    violates_constraint=f"memory_available_mb >= {self.weights.MIN_FREE_MEMORY_MB}"
                ))
                continue

            # Battery threshold
            if not node.capabilities.is_charging and node.capabilities.battery_level is not None:
                if node.capabilities.battery_level < self.weights.MIN_BATTERY_PCT_ON_BATTERY:
                    excluded_nodes.append(ExcludedNode(
                        node_id=node.node_id,
                        node_name=node.node_name,
                        reason=f"Node on battery at {node.capabilities.battery_level}% (threshold is {self.weights.MIN_BATTERY_PCT_ON_BATTERY}%)",
                        violates_constraint=f"battery_level >= {self.weights.MIN_BATTERY_PCT_ON_BATTERY}"
                    ))
                    continue

            # Clock skew threshold
            if abs(node.capabilities.clock_skew_ms) > self.weights.MAX_TOLERABLE_CLOCK_SKEW_MS:
                excluded_nodes.append(ExcludedNode(
                    node_id=node.node_id,
                    node_name=node.node_name,
                    reason=f"Clock skew of {node.capabilities.clock_skew_ms}ms exceeds threshold ({self.weights.MAX_TOLERABLE_CLOCK_SKEW_MS}ms)",
                    violates_constraint=f"|clock_skew_ms| <= {self.weights.MAX_TOLERABLE_CLOCK_SKEW_MS}"
                ))
                continue

            eligible_nodes.append(node)

        # If no eligible nodes remain
        if not eligible_nodes:
            return SchedulingExplanation(
                job_id=job_id,
                task_id=task.id if task else None,
                selected_node_id=None,
                selected_node_name=None,
                total_score=0.0,
                factors=[],
                excluded_nodes=excluded_nodes,
                policy_version=self.policy_version,
                requires_approval=False,
                generated_at=datetime.utcnow()
            )

        # 2. Score Eligible Nodes
        scored_candidates: List[Tuple[float, WorkerNodeResponse, List[ScoreFactor]]] = []
        
        for node in eligible_nodes:
            factors: List[ScoreFactor] = []
            
            # Factor A: Resource Fit (0 - 25)
            # Higher CPU cores and available memory yield higher score
            cpu_factor = min(1.0, node.capabilities.cpu_cores / 16.0)
            mem_factor = min(1.0, node.capabilities.memory_available_mb / 16384.0)
            res_score = round(self.weights.MAX_RESOURCE_FIT_SCORE * (0.4 * cpu_factor + 0.6 * mem_factor), 2)
            factors.append(ScoreFactor(
                factor_name="ResourceFit",
                raw_value=f"{node.capabilities.cpu_cores} cores, {node.capabilities.memory_available_mb}MB RAM",
                weight=self.weights.MAX_RESOURCE_FIT_SCORE,
                contribution=res_score,
                description="Hardware compute and free memory availability"
            ))
            
            # Factor B: Model Cached (0 or 25)
            is_cached = required_model.lower() in [m.lower() for m in node.capabilities.cached_models]
            model_score = self.weights.MAX_MODEL_CACHE_SCORE if is_cached else 0.0
            factors.append(ScoreFactor(
                factor_name="ModelCache",
                raw_value=f"cached={is_cached}",
                weight=self.weights.MAX_MODEL_CACHE_SCORE,
                contribution=model_score,
                description="Zero-download instant inference execution when model is preloaded"
            ))
            
            # Factor C: Data Locality & Network Quality (0 - 25)
            locality_points = 15.0 if node.is_localhost else 0.0
            net_points = min(10.0, (node.capabilities.network_mbps / 1000.0) * 10.0)
            net_score = round(locality_points + net_points, 2)
            factors.append(ScoreFactor(
                factor_name="LocalityAndNetwork",
                raw_value=f"local={node.is_localhost}, {node.capabilities.network_mbps} Mbps",
                weight=self.weights.MAX_LOCALITY_NETWORK_SCORE,
                contribution=net_score,
                description="Localhost data locality and network throughput speed"
            ))
            
            # Factor D: Power & Battery State (0 - 25)
            if node.capabilities.is_charging or node.capabilities.power_state == "ac":
                power_score = self.weights.MAX_POWER_BATTERY_SCORE
            else:
                battery_pct = node.capabilities.battery_level or 50.0
                power_score = round(self.weights.MAX_POWER_BATTERY_SCORE * (battery_pct / 100.0), 2)
            factors.append(ScoreFactor(
                factor_name="PowerAndBattery",
                raw_value=f"state={node.capabilities.power_state}, charging={node.capabilities.is_charging}",
                weight=self.weights.MAX_POWER_BATTERY_SCORE,
                contribution=power_score,
                description="AC power stability vs battery discharge level"
            ))
            
            # Factor E: Load & Lease Penalties
            lease_penalty = -1.0 * round(node.active_leases_count * self.weights.ACTIVE_LEASE_PENALTY_PER_TASK, 2)
            util_penalty = -1.0 * round(node.capabilities.cpu_utilization_pct * self.weights.HIGH_UTILIZATION_PENALTY_WEIGHT, 2)
            load_penalty = lease_penalty + util_penalty
            factors.append(ScoreFactor(
                factor_name="LoadPenalty",
                raw_value=f"{node.active_leases_count} active leases, {node.capabilities.cpu_utilization_pct}% CPU",
                weight=-30.0,
                contribution=load_penalty,
                description="Penalizes busy nodes to load-balance across the cluster"
            ))
            
            # Total score
            total_score = round(res_score + model_score + net_score + power_score + load_penalty, 2)
            scored_candidates.append((total_score, node, factors))
            
        # Deterministic sort: highest score first, ties broken by node_id ascending
        scored_candidates.sort(key=lambda item: (-item[0], item[1].node_id))
        
        best_score, best_node, best_factors = scored_candidates[0]
        
        return SchedulingExplanation(
            job_id=job_id,
            task_id=task.id if task else None,
            selected_node_id=best_node.node_id,
            selected_node_name=best_node.node_name,
            total_score=best_score,
            factors=best_factors,
            excluded_nodes=excluded_nodes,
            policy_version=self.policy_version,
            requires_approval=False,
            generated_at=datetime.utcnow()
        )

# Singleton default scheduler instance
deterministic_scheduler = DeterministicScheduler()
