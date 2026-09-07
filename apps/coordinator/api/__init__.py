"""
Coordinator API Routers
"""
from apps.coordinator.api.auth import router as auth_router
from apps.coordinator.api.nodes import router as nodes_router
from apps.coordinator.api.workloads import router as workloads_router
from apps.coordinator.api.jobs import router as jobs_router
from apps.coordinator.api.tasks import router as tasks_router
from apps.coordinator.api.approvals import router as approvals_router
from apps.coordinator.api.audit import router as audit_router
from apps.coordinator.api.capacity import router as capacity_router
from apps.coordinator.api.alerts import router as alerts_router
from apps.coordinator.api.pairing import router as pairing_router
