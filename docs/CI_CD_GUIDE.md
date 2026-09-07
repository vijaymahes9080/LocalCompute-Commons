# CI/CD & Automated Verification Guide

The LocalCompute Commons repository is protected by automated GitHub Actions CI/CD pipelines defined in `.github/workflows/ci.yml`.

---

## 1. Pipeline Stages

1. **Backend Tests & Coverage**:
   - Executes Pytest unit and integration test suite with code coverage tracking across `packages/`, `apps/coordinator/`, and `services/`.
   - Runs the 40-scenario benchmark evaluation suite.
2. **Frontend Build & Lint**:
   - Runs TypeScript strict compilation and Vite production bundling in `apps/web`.
3. **Docker Compose Linting**:
   - Validates multi-service container orchestration schemas in `infra/docker/docker-compose.yml`.
