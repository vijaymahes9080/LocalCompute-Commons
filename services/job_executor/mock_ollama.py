"""
Mock Ollama Engine for Deterministic Testing and Offline Operation
"""
import re
import asyncio
from typing import Dict, Any, Optional

class MockOllamaInference:
    """
    Simulates local Ollama LLM responses with realistic text summarization,
    deterministic key-point extraction, token timing, and injectable failure modes.
    """
    def __init__(self):
        self.available_models = ["llama3:8b", "mistral:7b", "phi3:mini", "qwen2:7b"]
        self.simulated_latency_ms: float = 20.0
        self.failure_mode: Optional[str] = None  # 'timeout' | 'oom' | 'corrupt' | 'unavailable'

    async def generate(self, model: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulates Ollama /api/generate endpoint."""
        # Check model availability
        if self.failure_mode == "unavailable" or (model.lower() not in [m.lower() for m in self.available_models]):
            raise RuntimeError(f"Model '{model}' not found in local cache")

        # Simulate timeout failure
        if self.failure_mode == "timeout":
            await asyncio.sleep(2.0)
            raise asyncio.TimeoutError("Ollama inference timed out after limit")

        # Simulate OOM failure
        if self.failure_mode == "oom":
            raise MemoryError("CUDA out of memory while loading KV cache")

        # Simulate inference execution latency
        if self.simulated_latency_ms > 0:
            await asyncio.sleep(self.simulated_latency_ms / 1000.0)

        # Extract meaningful summary points from prompt
        cleaned = re.sub(r"[#\*\-_`]", " ", prompt)
        words = [w for w in cleaned.split() if len(w) > 3]
        key_terms = list(dict.fromkeys(words))[:8]  # unique top words
        
        # Produce a structured coherent summary
        summary_text = (
            f"**Executive Summary ({model})**:\n"
            f"- Analyzed input text comprising {len(prompt)} characters and {len(words)} words.\n"
            f"- Key focal themes identified: {', '.join(key_terms) if key_terms else 'General compute'}.\n"
            f"- Findings indicate distributed task execution succeeded under privacy-aware local constraints."
        )

        if self.failure_mode == "corrupt":
            summary_text = "\x00\x01\x02__MALFORMED_OUTPUT__"

        return {
            "model": model,
            "response": summary_text,
            "done": True,
            "total_duration": int(self.simulated_latency_ms * 1_000_000),
            "eval_count": len(summary_text.split()),
            "prompt_eval_count": len(words)
        }

mock_ollama_engine = MockOllamaInference()
