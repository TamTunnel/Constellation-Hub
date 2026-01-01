# Local Development Guide

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for frontend)
- Python 3.11+ (for backend)

## Quick Start with Docker

```bash
cd constellation-hub/infra/docker
docker-compose up -d
```

Access:
- Frontend: http://localhost:3000
- Core Orbits API: http://localhost:8001/docs
- Routing API: http://localhost:8002/docs
- Ground Scheduler API: http://localhost:8003/docs
- AI Agents API: http://localhost:8004/docs

---

## Authentication Setup

### Development Mode (No Auth)

For local development without authentication, set:

```bash
AUTH_DISABLED=true
```

All endpoints will be accessible without tokens.

### Creating a Demo Admin User

When the database is empty, use the bootstrap endpoint:

```bash
curl -X POST http://localhost:8001/auth/bootstrap \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "name": "Admin User",
    "password": "securepassword123"
  }'
```

This creates an admin user. The endpoint is disabled after the first user is created.

### Logging In

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using Tokens

Include the access token in API requests:

```bash
curl http://localhost:8001/constellations \
  -H "Authorization: Bearer eyJ..."
```

---

## Database Migrations

### Running Migrations

Before starting services, run database migrations:

```bash
cd backend

# Upgrade to latest schema
python scripts/run_migrations.py upgrade head

# Or just run without arguments (defaults to upgrade head)
python scripts/run_migrations.py
```

### Migration Commands

```bash
# Show current database revision
python scripts/run_migrations.py current

# Show migration history
python scripts/run_migrations.py history

# Downgrade one step
python scripts/run_migrations.py downgrade -1

# Create a new migration
python scripts/run_migrations.py revision -m "Add new_table"

# Auto-generate migration from model changes
python scripts/run_migrations.py revision -m "Add fields" --autogenerate
```

### Docker Compose with Migrations

Migrations run automatically on container startup. To manually run:

```bash
docker-compose exec core-orbits python /app/scripts/run_migrations.py
```

---

## Backend Development

### Running a Single Service

```bash
cd backend/core-orbits
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --port 8001
```

### Running Tests

```bash
cd backend/core-orbits
pytest -v
```

### Database Setup

The services use PostgreSQL. Start it with Docker:

```bash
docker run -d \
  --name constellation-postgres \
  -e POSTGRES_USER=constellation \
  -e POSTGRES_PASSWORD=constellation \
  -e POSTGRES_DB=constellation_hub \
  -p 5432:5432 \
  postgres:15-alpine
```

---

## Frontend Development

```bash
cd frontend/web
npm install
npm run dev
```

Access at http://localhost:3000

### Building for Production

```bash
npm run build
```

---

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

### Core Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `AUTH_DISABLED` | Disable auth for dev | `false` |
| `JWT_SECRET_KEY` | Secret for JWT signing | (required in prod) |
| `LLM_PROVIDER` | AI provider (mock, openai, anthropic) | `mock` |
| `LLM_API_KEY` | API key for LLM provider | (optional) |
| `LOG_FORMAT` | Log format (`json` or `text`) | `json` |
| `METRICS_ENABLED` | Enable Prometheus metrics | `true` |

See `.env.example` for the complete list.

---

## Health & Observability

### Health Checks

Each service exposes:
- `/healthz` - Liveness probe (is the service running?)
- `/readyz` - Readiness probe (is the DB connected?)
- `/metrics` - Prometheus metrics

### Viewing Logs

With `LOG_FORMAT=text` for readable local logs:

```bash
docker-compose logs -f core-orbits
```

### Prometheus Metrics

Access metrics at http://localhost:8001/metrics

To run Prometheus locally:

```bash
docker run -d -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```
