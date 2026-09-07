"""
Structured JSON Logging with Distributed Context Propagation
"""
import logging
import json
import sys
from datetime import datetime
from contextvars import ContextVar
from typing import Any, Dict, Optional

# Context Variables for distributed tracing
ctx_request_id: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
ctx_job_id: ContextVar[Optional[str]] = ContextVar("job_id", default=None)
ctx_task_id: ContextVar[Optional[str]] = ContextVar("task_id", default=None)
ctx_worker_id: ContextVar[Optional[str]] = ContextVar("worker_id", default=None)
ctx_trace_id: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)

class StructuredJsonFormatter(logging.Formatter):
    """Formats log records as strict JSON objects for observability ingest."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
            "request_id": ctx_request_id.get(),
            "job_id": ctx_job_id.get(),
            "task_id": ctx_task_id.get(),
            "worker_id": ctx_worker_id.get(),
            "trace_id": ctx_trace_id.get(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_structured_logging(level: int = logging.INFO) -> logging.Logger:
    root_logger = logging.getLogger("localcompute")
    root_logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        root_logger.addHandler(handler)
        
    return root_logger

logger = setup_structured_logging()
