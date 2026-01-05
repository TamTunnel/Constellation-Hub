# Deployment Guide

This guide covers how to deploy Constellation Hub to production environments.

## Docker Compose Deployment

The root `docker-compose.yml` is production-ready and can be used with Docker Swarm, Coolify, or Portainer.

### Environment Variables

Configure these variables in your deployment environment (e.g., `.env` file or CI/CD secrets).

#### Database Configuration

| Variable            | Default             | Description       |
| ------------------- | ------------------- | ----------------- |
| `POSTGRES_USER`     | `constellation`     | Database username |
| `POSTGRES_PASSWORD` | `constellation`     | Database password |
| `POSTGRES_DB`       | `constellation_hub` | Database name     |

#### Security & App Settings

| Variable         | Default                   | Description                                                        |
| ---------------- | ------------------------- | ------------------------------------------------------------------ |
| `JWT_SECRET_KEY` | `change-me-in-production` | **Required.** Secret for signing auth tokens.                      |
| `DEMO_MODE`      | `true`                    | Set to `false` to disable the `/demo/seed` endpoint in production. |
| `DEBUG`          | `false`                   | Set to `true` for verbose logging.                                 |

#### Frontend Configuration (Build Time)

These variables must be set when building the frontend container or passed to the runtime if using the provided Docker image which handles env injection.

| Variable                    | Default                 | Description                   |
| --------------------------- | ----------------------- | ----------------------------- |
| `VITE_CORE_ORBITS_URL`      | `http://localhost:8001` | Public URL of Core Orbits API |
| `VITE_ROUTING_URL`          | `http://localhost:8002` | Public URL of Routing API     |
| `VITE_GROUND_SCHEDULER_URL` | `http://localhost:8003` | Public URL of Scheduler API   |
| `VITE_AI_AGENTS_URL`        | `http://localhost:8004` | Public URL of AI Agents API   |

### Coolify Deployment

1. **Source**: Connect your GitHub repository.
2. **Configuration**:
   - **Base Directory**: `/`
   - **Docker Compose Location**: `/docker-compose.yml`
3. **Environment Variables**:
   Add the variables listed above. Ensure `VITE_*_URL` point to the actual domains (e.g., `https://api.yourdomain.com`).

## Kubernetes Deployment

_(Coming soon. See `infra/helm` for experimental charts.)_
