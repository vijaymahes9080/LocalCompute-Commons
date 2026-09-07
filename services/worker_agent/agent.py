"""
Worker Agent Daemon for LocalCompute Commons
"""
import asyncio
import signal
import uuid
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any

from packages.shared.models.schemas import (
    WorkerNodeRegisterRequest, NodeCapability,
    NodeHeartbeatRequest, TaskClaimRequest,
    TaskCompleteRequest, TaskFailRequest, JobTaskResponse
)
from packages.shared.models.enums import TrustLevel, NodeStatus
from services.worker_agent.telemetry import HardwareTelemetryProbe
from services.job_executor.executor import JobExecutor, TaskExecutionError
from services.monitoring.logger import logger

class WorkerAgent:
    """
    Autonomous Worker Agent running on compute nodes.
    Maintains heartbeat loop, claims assigned tasks, executes inference, and handles graceful shutdown.
    """
    def __init__(
        self,
        node_id: Optional[str] = None,
        node_name: str = "Lab-Worker-Alpha",
        coordinator_url: str = "http://localhost:8000",
        trust_level: TrustLevel = TrustLevel.TRUSTED_LAB,
        cached_models: Optional[List[str]] = None,
        is_localhost: bool = True
    ):
        self.node_id = node_id or f"node-{uuid.uuid4().hex[:8]}"
        self.node_name = node_name
        self.coordinator_url = coordinator_url.rstrip("/")
        self.trust_level = trust_level
        self.is_localhost = is_localhost
        self.telemetry_probe = HardwareTelemetryProbe(cached_models=cached_models)
        self.executor = JobExecutor()
        
        self.token: Optional[str] = None
        self.status: NodeStatus = NodeStatus.ONLINE
        self.is_running: bool = False
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self._server_time_offset_ms: float = 0.0

    async def register(self) -> bool:
        """Performs initial node registration handshake."""
        capabilities = self.telemetry_probe.collect_capabilities()
        payload = WorkerNodeRegisterRequest(
            node_id=self.node_id,
            node_name=self.node_name,
            capabilities=capabilities,
            trust_level=self.trust_level,
            is_localhost=self.is_localhost
        )
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.post(
                    f"{self.coordinator_url}/api/v1/nodes/register",
                    json=payload.model_dump(mode="json")
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.token = data.get("token")
                    logger.info(f"Worker '{self.node_name}' ({self.node_id}) registered successfully.")
                    return True
                else:
                    logger.error(f"Registration failed with HTTP {resp.status_code}: {resp.text}")
                    return False
            except Exception as exc:
                logger.error(f"Registration connection error: {exc}")
                return False

    async def send_heartbeat(self) -> bool:
        """Emits telemetry heartbeat to coordinator."""
        if not self.token:
            return False
            
        capabilities = self.telemetry_probe.collect_capabilities()
        payload = NodeHeartbeatRequest(
            node_id=self.node_id,
            capabilities=capabilities,
            active_tasks=list(self.active_tasks.keys())
        )
        
        headers = {"Authorization": f"Bearer {self.token}"}
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.post(
                    f"{self.coordinator_url}/api/v1/nodes/heartbeat",
                    json=payload.model_dump(mode="json"),
                    headers=headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self.status = NodeStatus(data.get("status", "online"))
                    if data.get("token_renewal"):
                        self.token = data["token_renewal"]
                    return True
                return False
            except Exception as exc:
                logger.warning(f"Heartbeat failed: {exc}")
                return False

    async def claim_tasks(self, max_tasks: int = 1) -> List[Dict[str, Any]]:
        """Polls for pending tasks allocated to this worker."""
        if not self.token or self.status != NodeStatus.ONLINE:
            return []
            
        payload = TaskClaimRequest(node_id=self.node_id, max_tasks=max_tasks)
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.post(
                    f"{self.coordinator_url}/api/v1/tasks/claim",
                    json=payload.model_dump(mode="json"),
                    headers=headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("tasks", [])
                return []
            except Exception as exc:
                logger.debug(f"Task claim error: {exc}")
                return []

    async def process_task(self, task_dict: Dict[str, Any]):
        """Executes task inference and posts results back to coordinator."""
        task_id = task_dict["id"]
        input_payload = task_dict.get("input_payload", {})
        required_model = input_payload.get("model", "llama3:8b")
        
        logger.info(f"Worker {self.node_id} processing task {task_id} with model {required_model}")
        
        try:
            output_payload, checksum, duration = await self.executor.execute_task(
                task_id=task_id,
                required_model=required_model,
                input_payload=input_payload,
                timeout_seconds=60.0
            )
            
            # Post completion
            comp_payload = TaskCompleteRequest(
                node_id=self.node_id,
                task_id=task_id,
                output_payload=output_payload,
                result_checksum=checksum,
                execution_time_seconds=duration
            )
            headers = {"Authorization": f"Bearer {self.token}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self.coordinator_url}/api/v1/tasks/{task_id}/complete",
                    json=comp_payload.model_dump(mode="json"),
                    headers=headers
                )
            logger.info(f"Task {task_id} completed successfully in {duration:.2f}s")
            
        except Exception as exc:
            logger.error(f"Task {task_id} execution failed: {exc}")
            fail_payload = TaskFailRequest(
                node_id=self.node_id,
                task_id=task_id,
                error_message=str(exc)
            )
            headers = {"Authorization": f"Bearer {self.token}"}
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    f"{self.coordinator_url}/api/v1/tasks/{task_id}/fail",
                    json=fail_payload.model_dump(mode="json"),
                    headers=headers
                )

    async def start(self):
        """Starts worker heartbeat and polling loop."""
        self.is_running = True
        registered = await self.register()
        if not registered:
            logger.error(f"Worker {self.node_id} failed to initialize registration.")
            return

        hb_interval = 5.0
        poll_interval = 2.0
        
        last_hb = 0.0
        
        while self.is_running:
            now = asyncio.get_event_loop().time()
            if now - last_hb >= hb_interval:
                await self.send_heartbeat()
                last_hb = now
                
            if len(self.active_tasks) < 2 and self.status == NodeStatus.ONLINE:
                tasks = await self.claim_tasks(max_tasks=1)
                for t in tasks:
                    tid = t["id"]
                    fut = asyncio.create_task(self.process_task(t))
                    self.active_tasks[tid] = fut
                    fut.add_done_callback(lambda f, t_id=tid: self.active_tasks.pop(t_id, None))

            await asyncio.sleep(poll_interval)

    async def stop(self):
        """Gracefully shuts down worker agent and cancels pending tasks."""
        logger.info(f"Shutting down worker {self.node_name}...")
        self.is_running = False
        for tid, fut in list(self.active_tasks.items()):
            fut.cancel()
        logger.info(f"Worker {self.node_name} stopped.")
