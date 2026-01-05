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

#### Security & App Settings (Runtime)

| Variable         | Default                   | Description                                                        |
| ---------------- | ------------------------- | ------------------------------------------------------------------ |
| `JWT_SECRET_KEY` | `change-me-in-production` | **Required.** Secret for signing auth tokens.                      |
| `DEMO_MODE`      | `true`                    | Set to `false` to disable the `/demo/seed` endpoint in production. |
| `DEBUG`          | `false`                   | Set to `true` for verbose logging.                                 |

#### Frontend Configuration (Build Time)

> **Important:** These are **build-time arguments**, not runtime environment variables. Vite bakes these into the static JavaScript bundle during `npm run build`. They must be set before/during the Docker build, not at container startup.

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
   - Add all variables listed above in the **Environment Variables** section.
   - Ensure `VITE_*_URL` variables are set to your actual public domains:
     ```
     VITE_CORE_ORBITS_URL=https://coreorbits.yourapp.com
     VITE_ROUTING_URL=https://routing.yourapp.com
     VITE_GROUND_SCHEDULER_URL=https://scheduler.yourapp.com
     VITE_AI_AGENTS_URL=https://aiagents.yourapp.com
     JWT_SECRET_KEY=your-secure-random-secret
     DEMO_MODE=false
     ```
4. **Deploy**: Click Deploy. The `docker-compose.yml` will build all services.

### Local Development

For local development, the defaults work out of the box:

```bash
docker compose up -d
```

## Kubernetes Deployment

_(Coming soon. See `infra/helm` for experimental charts.)_

## Troubleshooting

### Frontend shows "Network Error" or can't reach APIs

- Ensure `VITE_*_URL` variables were set **before** building the frontend image.
- If you changed these values, you need to rebuild the frontend: `docker compose build frontend --no-cache`

### Database connection errors

- Ensure PostgreSQL container is healthy: `docker compose ps`
- Check credentials match between app and database containers.

### Demo data not loading

- Ensure `DEMO_MODE=true` (default).
- Navigate to `/login` and click "Initialize Demo Data".
