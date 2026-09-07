"""
LocalCompute Commons - Coordinator Service Main Entrypoint
"""
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from packages.shared.config import settings
from packages.shared.database import init_db
from apps.coordinator.api import (
    auth_router, nodes_router, workloads_router,
    jobs_router, tasks_router, approvals_router,
    audit_router, capacity_router, alerts_router
)
from apps.coordinator.core.recovery_engine import recovery_engine
from apps.coordinator.core.state_machine import InvalidStateTransitionError
from apps.coordinator.core.approval_engine import ApprovalRequiredError
from services.monitoring.metrics import get_metrics_payload, API_REQUEST_LATENCY_SECONDS
from services.monitoring.logger import (
    logger, ctx_request_id, ctx_trace_id
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing LocalCompute Commons Coordinator...")
    await init_db()
    await recovery_engine.start()
    logger.info("Coordinator service initialized successfully.")
    yield
    # Shutdown
    logger.info("Shutting down Coordinator service...")
    await recovery_engine.stop()
    logger.info("Coordinator service shutdown complete.")

app = FastAPI(
    title="LocalCompute Commons Coordinator",
    description="Privacy-aware local AI compute coordination and deterministic scheduling platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware: Request ID, Latency & Security Headers
@app.middleware("http")
async def security_and_tracing_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    trace_id = request.headers.get("X-Trace-ID", req_id)
    ctx_request_id.set(req_id)
    ctx_trace_id.set(trace_id)

    start_time = time.perf_counter()
    response: Response = await call_next(request)
    duration = time.perf_counter() - start_time

    # Record Prometheus Latency
    endpoint = request.url.path
    API_REQUEST_LATENCY_SECONDS.labels(endpoint=endpoint, method=request.method).observe(duration)

    # Security Headers
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    
    return response

# Custom Exception Handlers
@app.exception_handler(InvalidStateTransitionError)
async def state_transition_error_handler(request: Request, exc: InvalidStateTransitionError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "invalid_state_transition", "detail": str(exc)}
    )

@app.exception_handler(ApprovalRequiredError)
async def approval_required_error_handler(request: Request, exc: ApprovalRequiredError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "approval_required",
            "approval_id": exc.approval_id,
            "detail": str(exc)
        }
    )

# Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(nodes_router, prefix=settings.API_V1_PREFIX)
app.include_router(workloads_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(tasks_router, prefix=settings.API_V1_PREFIX)
app.include_router(approvals_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)
app.include_router(capacity_router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts_router, prefix=settings.API_V1_PREFIX)

@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "service": "coordinator",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/metrics")
async def prometheus_metrics():
    return Response(
        content=get_metrics_payload(),
        media_type="text/plain; version=0.0.4; charset=utf-8"
    )

@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_PREFIX
    }
