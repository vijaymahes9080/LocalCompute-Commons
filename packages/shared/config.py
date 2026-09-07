"""
Configuration management via pydantic-settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App General
    APP_NAME: str = "LocalCompute Commons"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Server Binding
    COORDINATOR_HOST: str = "0.0.0.0"
    COORDINATOR_PORT: int = 8000
    MCP_SERVER_PORT: int = 8001
    
    # Database (Defaults to SQLite for instant local zero-dependency run, switchable to asyncpg for Postgres)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./localcompute.db",
        description="Async SQLAlchemy database connection string"
    )
    
    # Redis / Queue
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_QUEUE: bool = True  # Allows running without external Redis if desired
    
    # Security & Auth
    SECRET_KEY: str = Field(
        default="localcompute-commons-insecure-dev-secret-key-change-in-production-12345",
        description="Secret key for JWT and HMAC signing"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    NODE_TOKEN_EXPIRE_HOURS: int = 24
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    
    # Default Admin Initializer
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_EMAIL: str = "admin@localcompute.local"
    DEFAULT_ADMIN_PASSWORD: str = "AdminLocalCompute2026!"
    
    # Distributed Worker & Lease Settings
    LEASE_TIMEOUT_SECONDS: int = 60
    HEARTBEAT_TIMEOUT_SECONDS: int = 30
    DEFAULT_TASK_MAX_RETRIES: int = 3
    CLOCK_SKEW_THRESHOLD_MS: float = 5000.0
    
    # Inference / Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    MOCK_INFERENCE: bool = True  # Enables high-speed deterministic mock inference for local dev & tests
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
