# Docker Deployment Guide

LocalCompute Commons is fully packaged for one-command local and server cluster deployment via Docker Compose.

---

## 1. Services Overview

| Container | Image / Dockerfile | Internal Port | Host Port | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `lc-postgres` | `postgres:16-alpine` | `5432` | `5432` | PostgreSQL metadata & audit DB |
| `lc-redis` | `redis:7-alpine` | `6379` | `6379` | Task dispatch & queue |
| `lc-coordinator` | `Dockerfile.coordinator` | `8000` | `8000` | Core FastAPI Control Plane |
| `lc-worker-alpha` | `Dockerfile.worker` | - | - | Lab Worker Node 1 (RTX 4090 mock) |
| `lc-worker-beta` | `Dockerfile.worker` | - | - | Lab Worker Node 2 (A100 mock) |
| `lc-worker-gamma` | `Dockerfile.worker` | - | - | Community Worker Node 3 |
| `lc-web` | `Dockerfile.web` | `80` | `5173` | Nginx + React Dashboard |
| `lc-mcp-server` | `Dockerfile.mcp` | - | - | Model Context Protocol Service |
| `lc-prometheus` | `prom/prometheus` | `9090` | `9090` | Prometheus Metrics Scraper |
| `lc-n8n` | `n8nio/n8n:latest` | `5678` | `5678` | n8n Hourly Alerting Engine |

---

## 2. Booting the Cluster

```bash
docker compose -f infra/docker/docker-compose.yml up -d --build
```

To view logs:
```bash
docker compose -f infra/docker/docker-compose.yml logs -f coordinator
```

To tear down:
```bash
docker compose -f infra/docker/docker-compose.yml down -v
```
