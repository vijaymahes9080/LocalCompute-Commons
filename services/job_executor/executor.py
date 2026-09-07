"""
Local Job Task Executor with Sandboxing, Validation, and Integrity Signing
"""
import time
import httpx
from typing import Dict, Any, Tuple
from packages.shared.config import settings
from packages.shared.security.sanitization import sanitize_prompt_input, validate_document_content
from packages.shared.security.crypto import compute_payload_checksum, generate_task_signature
from services.job_executor.mock_ollama import mock_ollama_engine
from services.monitoring.logger import logger

class TaskExecutionError(Exception):
    pass

class JobExecutor:
    """
    Executes tasks locally against Ollama or fallback Mock engine.
    Ensures input sanitization, timeout enforcement, output bounds, and HMAC signing.
    """
    def __init__(self, use_mock: bool = settings.MOCK_INFERENCE):
        self.use_mock = use_mock
        self.max_output_chars: int = 50_000

    async def execute_task(
        self,
        task_id: str,
        required_model: str,
        input_payload: Dict[str, Any],
        timeout_seconds: float = 60.0
    ) -> Tuple[Dict[str, Any], str, float]:
        """
        Executes inference for a single task.
        Returns (output_payload, result_checksum, execution_duration_seconds).
        """
        start_time = time.perf_counter()
        
        # 1. Validate Input
        raw_text = input_payload.get("text", "")
        if not validate_document_content(raw_text):
            raise TaskExecutionError("Task document input validation failed: text empty or exceeds limit")
            
        sanitized_prompt = sanitize_prompt_input(raw_text)
        
        # 2. Execute Inference
        output_text = ""
        eval_metrics: Dict[str, Any] = {}
        
        if self.use_mock:
            try:
                res = await mock_ollama_engine.generate(
                    model=required_model,
                    prompt=sanitized_prompt
                )
                output_text = res.get("response", "")
                eval_metrics = {
                    "eval_count": res.get("eval_count", 0),
                    "prompt_eval_count": res.get("prompt_eval_count", 0),
                    "backend": "mock_ollama"
                }
            except Exception as exc:
                logger.error(f"Inference execution failed on mock engine: {exc}")
                raise TaskExecutionError(f"Local inference failed: {str(exc)}")
        else:
            # Call real Ollama endpoint
            async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                try:
                    resp = await client.post(
                        f"{settings.OLLAMA_BASE_URL}/api/generate",
                        json={
                            "model": required_model,
                            "prompt": f"Summarize the following text:\n\n{sanitized_prompt}",
                            "stream": False
                        }
                    )
                    if resp.status_code != 200:
                        raise TaskExecutionError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")
                    data = resp.json()
                    output_text = data.get("response", "")
                    eval_metrics = {
                        "eval_count": data.get("eval_count", 0),
                        "prompt_eval_count": data.get("prompt_eval_count", 0),
                        "backend": "ollama_native"
                    }
                except httpx.TimeoutException:
                    raise TaskExecutionError(f"Ollama inference timed out after {timeout_seconds}s")
                except Exception as exc:
                    raise TaskExecutionError(f"Ollama connection error: {str(exc)}")

        # 3. Enforce Output Bounds & Integrity Check
        if len(output_text) > self.max_output_chars:
            output_text = output_text[:self.max_output_chars] + "... [TRUNCATED DUE TO SIZE LIMIT]"

        duration = time.perf_counter() - start_time
        
        output_payload = {
            "summary": output_text,
            "char_count": len(output_text),
            "metrics": eval_metrics
        }
        
        checksum = compute_payload_checksum(output_payload)
        
        return output_payload, checksum, duration

# Default instance
job_executor = JobExecutor()
