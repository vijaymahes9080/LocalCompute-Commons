"""
Example Worker Node Daemon Runner
"""
import asyncio
import os
import signal
import sys

from packages.shared.models.enums import TrustLevel
from services.worker_agent.agent import WorkerAgent
from services.monitoring.logger import logger

async def main():
    node_name = os.environ.get("NODE_NAME", "Alpha-Lab-Worker")
    coord_url = os.environ.get("COORDINATOR_URL", "http://localhost:8000")
    trust_raw = os.environ.get("TRUST_LEVEL", "trusted_lab")
    models_raw = os.environ.get("CACHED_MODELS", "llama3:8b,mistral:7b")
    
    trust_level = TrustLevel(trust_raw)
    cached_models = [m.strip() for m in models_raw.split(",") if m.strip()]

    agent = WorkerAgent(
        node_name=node_name,
        coordinator_url=coord_url,
        trust_level=trust_level,
        cached_models=cached_models,
        is_localhost=True
    )

    logger.info(f"Starting Worker Agent '{node_name}' connecting to {coord_url}...")
    
    # Run loop
    try:
        await agent.start()
    except (KeyboardInterrupt, asyncio.CancelledError):
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
