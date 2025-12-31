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

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `LLM_PROVIDER` - AI provider (mock, openai, anthropic)
- `LLM_API_KEY` - API key for LLM provider
