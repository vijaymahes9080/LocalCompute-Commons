"""
Deterministic Scheduling Policy Constants and Weights
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class SchedulerWeights:
    # Maximum component scores
    MAX_RESOURCE_FIT_SCORE: float = 25.0
    MAX_MODEL_CACHE_SCORE: float = 25.0
    MAX_LOCALITY_NETWORK_SCORE: float = 25.0
    MAX_POWER_BATTERY_SCORE: float = 25.0
    
    # Penalties
    ACTIVE_LEASE_PENALTY_PER_TASK: float = 5.0
    HIGH_UTILIZATION_PENALTY_WEIGHT: float = 0.15
    CLOCK_SKEW_PENALTY_WEIGHT: float = 0.002
    
    # Thresholds
    MIN_BATTERY_PCT_ON_BATTERY: float = 20.0
    MIN_FREE_MEMORY_MB: int = 512
    MAX_TOLERABLE_CLOCK_SKEW_MS: float = 5000.0

DEFAULT_SCHEDULER_WEIGHTS = SchedulerWeights()
