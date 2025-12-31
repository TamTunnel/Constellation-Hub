# CI/CD Guide

## GitHub Actions Workflows

### ci-backend.yml

**Trigger**: Push/PR to `main` or `develop` affecting `backend/`

**Jobs**:
1. Test each service (core-orbits, routing, ground-scheduler, ai-agents)
2. Run linting with ruff
3. Run pytest tests

### ci-frontend.yml

**Trigger**: Push/PR to `main` or `develop` affecting `frontend/`

**Jobs**:
1. Install dependencies
2. Run ESLint
3. Run TypeScript type checking
4. Run Vitest tests
5. Build production bundle

### docker-build.yml

**Trigger**: Push to `main`

**Jobs**:
1. Build Docker images for all services
2. Push to GitHub Container Registry
3. Tag with commit SHA and `latest`

### deploy-dev.yml

**Trigger**: Manual (workflow_dispatch)

**Jobs**:
1. Template for deployment automation
2. Currently outputs instructions; customize for your environment

## Setting Up CI/CD

1. **Enable GitHub Actions** in your repository settings

2. **Configure secrets** (Settings > Secrets):
   - `GITHUB_TOKEN` is automatic
   - Add `KUBE_CONFIG` for Kubernetes deployments

3. **Container Registry**:
   - Images push to `ghcr.io/your-username/constellation-hub/`
   - Ensure packages are public or configure access

## Running Workflows Locally

Use [act](https://github.com/nektos/act) to test workflows locally:

```bash
act -j test-core-orbits
```
