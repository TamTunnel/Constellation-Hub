# Development Guide

## Local Development Setup

### Requirements

- Docker Desktop / Docker Engine
- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)

### Quick Start

1. **Start entire stack**:

   ```bash
   make up
   ```

2. **Run Demo Setup**:

   ```bash
   make demo
   ```

3. **View Logs**:
   ```bash
   make logs
   ```

### Backend Development

The backend is composed of multiple FastAPI services in `backend/`.

**Running Tests**:

```bash
make test
```

**Linting**:

```bash
make lint
```

**Database Migrations**:
To generate a new migration after changing models:

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend Development

The frontend is in `frontend/web`.

**Install Dependencies**:

```bash
cd frontend/web
npm install
```

**Run Dev Server** (if not using Docker):

```bash
npm run dev
```

### Contributing

1. Fork the repo.
2. Create a feature branch.
3. Commit your changes (please include tests).
4. Run `make lint` and `make test`.
5. Submit a Pull Request.

## Architecture Decisions

- **Why FastAPI?** High performance, async support, and auto-generated OpenAPI docs.
- **Why CesiumJS?** Industry standard for high-fidelity geospatial visualization.
- **Why PostgreSQL?** Robust, with PostGIS support for spatial queries.
