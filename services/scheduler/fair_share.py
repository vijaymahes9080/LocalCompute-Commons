"""
Multi-Tenant Campus Quota and Dominant Resource Fairness (DRF) Allocator
"""
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class OrganizationQuota:
    org_id: str
    org_name: str
    max_concurrent_tasks: int
    daily_token_quota: int
    used_tokens_today: int = 0
    active_tasks_count: int = 0

class DominantResourceFairnessAllocator:
    """
    Allocates compute slots fairly across student teams, research groups, and labs
    using Dominant Resource Fairness (DRF).
    """
    def __init__(self):
        self._quotas: Dict[str, OrganizationQuota] = {
            "default-lab": OrganizationQuota("default-lab", "Main AI Lab", max_concurrent_tasks=20, daily_token_quota=1_000_000),
            "student-club": OrganizationQuota("student-club", "Student AI Club", max_concurrent_tasks=10, daily_token_quota=500_000),
            "rural-hub": OrganizationQuota("rural-hub", "Rural Tech Hub", max_concurrent_tasks=15, daily_token_quota=750_000),
        }

    def can_admit_task(self, org_id: str) -> bool:
        """Checks if organization has sufficient quota to admit new tasks."""
        quota = self._quotas.get(org_id)
        if not quota:
            return True
        return quota.active_tasks_count < quota.max_concurrent_tasks and quota.used_tokens_today < quota.daily_token_quota

    def calculate_dominant_share(self, org_id: str, total_cluster_slots: int) -> float:
        """Calculates dominant share fraction of cluster resources."""
        quota = self._quotas.get(org_id)
        if not quota or total_cluster_slots == 0:
            return 0.0
        return round(quota.active_tasks_count / total_cluster_slots, 4)

drf_allocator = DominantResourceFairnessAllocator()
