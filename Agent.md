# Agent.md - Constellation Hub AI Session Context

This file codifies architectural decisions, conventions, and best practices for the Constellation Hub project. All AI assistants working on this codebase should follow these guidelines to maintain consistency.

---

## Project Identity

- **Product Name**: `constellation-hub`
- **Repository**: `TamTunnel/Constellation-Hub`
- **Purpose**: Open-source AI-enhanced satellite constellation management platform
- **Target Users**: Satellite operators, ground segment teams, constellation planners
- **License**: Apache 2.0 (permissive, enterprise-friendly)

---

## Architecture Principles

### Microservices Design

The platform uses a **modular microservices architecture** with clear boundaries:

| Service | Responsibility | Port |
|---------|---------------|------|
| `core-orbits` | Orbital mechanics, TLE parsing, position/coverage | 8001 |
| `routing` | Link modeling, graph construction, path finding | 8002 |
| `ground-scheduler` | Ground stations, visibility, pass scheduling | 8003 |
| `ai-agents` | AI scheduling optimizer, Ops Co-Pilot | 8004 |
| `frontend (web)` | React UI with CesiumJS visualization | 3000 |

**Key Rules**:
1. Services communicate via REST APIs only (no direct DB sharing between services)
2. Each service has its own Dockerfile and requirements.txt
3. Shared code lives in `backend/common/` (models, config, utilities)
4. Database is shared PostgreSQL (single source of truth)

### Data Flow

```
User → Frontend → API Gateway → Backend Services → PostgreSQL
                                       ↓
                                    Redis (cache)
```

---

## Technology Stack Constraints

### Backend (Python)

| Requirement | Specification |
|-------------|---------------|
| Python Version | 3.11+ |
| Framework | FastAPI |
| Package Manager | pip with requirements.txt |
| Virtual Environment | venv (one per service) |
| Testing | pytest with pytest-asyncio |
| Linting | ruff (replaces flake8 + black) |
| Type Checking | mypy (strict mode) |

**Orbital Libraries**:
- `sgp4` - TLE propagation (SGP4/SDP4 algorithm)
- `skyfield` - High-precision astronomy calculations
- `numpy` - Numerical computations

### Frontend (TypeScript)

| Requirement | Specification |
|-------------|---------------|
| Node Version | 20+ LTS |
| Package Manager | npm |
| Framework | React 18+ with Vite |
| Language | TypeScript (strict mode) |
| 3D Visualization | CesiumJS (Cesium Ion-free mode) |
| UI Framework | shadcn/ui + Tailwind CSS |
| State | React Query (server) + Zustand (client) |
| Testing | Vitest + React Testing Library |
| Linting | ESLint + Prettier |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Containers | Docker (multi-stage builds) |
| Local Dev | docker-compose |
| Production | Kubernetes (manifests provided as skeleton) |
| CI/CD | GitHub Actions |
| Secrets | Environment variables (.env files) |

---

## Naming Conventions

### Files & Directories

| Type | Convention | Example |
|------|------------|---------|
| Python files | snake_case | `orbit_propagator.py` |
| TypeScript files | camelCase or PascalCase for components | `useApi.ts`, `Globe.tsx` |
| Directories | kebab-case | `ground-scheduler/` |
| Test files | `test_*.py` (Python), `*.test.ts` (TS) | `test_visibility.py` |

### Code

| Type | Convention | Example |
|------|------------|---------|
| Python classes | PascalCase | `GroundStation` |
| Python functions | snake_case | `compute_visibility()` |
| Python constants | UPPER_SNAKE | `DEFAULT_ELEVATION_MASK` |
| TypeScript components | PascalCase | `SatelliteList` |
| TypeScript hooks | camelCase with `use` prefix | `useSatellites` |
| API endpoints | lowercase with hyphens | `/ground-stations` |

### Database

| Type | Convention | Example |
|------|------------|---------|
| Table names | plural snake_case | `satellites`, `ground_stations` |
| Column names | snake_case | `created_at`, `max_elevation` |
| Foreign keys | `{table}_id` | `satellite_id`, `station_id` |

---

## API Design Standards

### RESTful Conventions

```
GET    /resources         - List all
GET    /resources/{id}    - Get one
POST   /resources         - Create
PUT    /resources/{id}    - Full update
PATCH  /resources/{id}    - Partial update
DELETE /resources/{id}    - Delete
```

### Response Format

```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T12:00:00Z",
    "request_id": "uuid"
  }
}
```

### Error Format

```json
{
  "error": {
    "code": "SATELLITE_NOT_FOUND",
    "message": "Satellite with ID 123 not found",
    "details": { ... }
  }
}
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | No content (DELETE) |
| 400 | Bad request (validation error) |
| 404 | Not found |
| 422 | Unprocessable entity (business logic error) |
| 500 | Internal server error |

---

## Configuration Management

### Environment Variables

All configuration via environment variables. Never hardcode secrets.

**Required Variables**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/constellation_hub

# Redis (optional)
REDIS_URL=redis://localhost:6379

# AI/LLM (optional)
LLM_PROVIDER=openai|anthropic|local|mock
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4

# Service URLs (for inter-service communication)
CORE_ORBITS_URL=http://core-orbits:8001
ROUTING_URL=http://routing:8002
GROUND_SCHEDULER_URL=http://ground-scheduler:8003
AI_AGENTS_URL=http://ai-agents:8004
```

### Files

- `.env` - Local development (gitignored)
- `.env.example` - Template with dummy values (committed)
- Environment-specific configs via Docker/K8s

---

## Testing Standards

### Coverage Requirements

| Type | Minimum Coverage |
|------|-----------------|
| Unit tests | 80% |
| Integration tests | Key workflows covered |
| E2E tests | Critical user journeys |

### Test Organization

```
backend/core-orbits/
├── app/
│   └── services/
│       └── orbit_propagator.py
└── tests/
    ├── unit/
    │   └── test_orbit_propagator.py
    └── integration/
        └── test_api.py
```

### Test Naming

```python
def test_compute_position_returns_correct_coordinates():
def test_compute_position_raises_for_invalid_tle():
def test_compute_position_handles_future_dates():
```

---

## Git Practices

### Branch Naming

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/<short-description>` | `feature/add-coverage-api` |
| Bugfix | `fix/<short-description>` | `fix/visibility-calculation` |
| Chore | `chore/<short-description>` | `chore/update-deps` |

### Commit Messages

Use conventional commits:

```
feat: add satellite coverage endpoint
fix: correct visibility window calculation
docs: update API documentation
test: add unit tests for routing service
chore: upgrade FastAPI to 0.110
```

### Pull Requests

1. Link to related issues
2. Include description of changes
3. Add screenshots for UI changes
4. Ensure CI passes before merge

---

## AI Agent Integration

### Pass Scheduler

The AI Pass Scheduler uses a **Strategy Pattern**:

```python
class PassSchedulerStrategy(ABC):
    @abstractmethod
    def optimize(self, passes: List[Pass], data_queues: List[DataQueue]) -> Schedule:
        pass

class HeuristicScheduler(PassSchedulerStrategy):
    """Rule-based optimizer (default)"""
    pass

class MLScheduler(PassSchedulerStrategy):
    """Machine learning optimizer (future)"""
    pass
```

**Rules for Adding New Schedulers**:
1. Implement `PassSchedulerStrategy` interface
2. Register in scheduler factory
3. Select via environment variable: `SCHEDULER_STRATEGY=heuristic|ml`

### Ops Co-Pilot

Uses an **LLM Client Abstraction**:

```python
class LLMClient(ABC):
    @abstractmethod
    async def analyze(self, events: List[Event]) -> Analysis:
        pass

class MockLLMClient(LLMClient):
    """Template-based responses for testing"""
    pass

class OpenAIClient(LLMClient):
    """OpenAI API integration"""
    pass
```

**Rules for LLM Integration**:
1. Always use the abstraction, never call APIs directly
2. Provide mock client for testing and demos
3. Configure provider via `LLM_PROVIDER` env var
4. Handle rate limits and errors gracefully

---

## Documentation Requirements

### Code Comments

```python
def compute_visibility_window(
    satellite: Satellite,
    station: GroundStation,
    start_time: datetime,
    end_time: datetime,
    elevation_mask: float = 10.0  # degrees above horizon
) -> List[VisibilityWindow]:
    """
    Compute visibility windows for a satellite-station pair.
    
    The visibility window is the period when the satellite is above
    the elevation mask from the ground station's perspective.
    
    Args:
        satellite: Satellite with TLE data
        station: Ground station with location
        start_time: Start of time window to analyze
        end_time: End of time window to analyze
        elevation_mask: Minimum elevation angle in degrees (default: 10°)
    
    Returns:
        List of VisibilityWindow objects with start, end, and max elevation
    
    Note:
        Uses SGP4 propagator with 60-second resolution for initial pass,
        then refines boundaries to 1-second precision.
    """
```

### README Updates

Update README.md whenever:
- Adding new features
- Changing configuration options
- Modifying API endpoints
- Updating dependencies

---

## Tier System

The project uses a tiered feature system:

| Tier | Scope | Status |
|------|-------|--------|
| Tier 1 | Digital twin + routing | Phase 1 |
| Tier 2 | Ground passes + AI agents | Phase 1 |
| Tier 3 | Simulation & emulation | Future |

**Future Extensibility**:
- Architecture supports adding Tier 3 simulation services
- Database schema is extensible for new data types
- API versioning (v1) allows future breaking changes

---

## Quick Reference Commands

```bash
# Local development
docker-compose up -d              # Start all services
docker-compose logs -f core-orbits # View service logs

# Backend development
cd backend/core-orbits
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest                            # Run tests
ruff check .                      # Lint
uvicorn app.main:app --reload     # Run dev server

# Frontend development
cd frontend/web
npm install
npm run dev                        # Start dev server
npm test                          # Run tests
npm run lint                      # Lint
npm run build                     # Production build
```

---

## Contact & Resources

- **Repository**: https://github.com/TamTunnel/Constellation-Hub
- **Documentation**: `/docs/` directory
- **Issues**: GitHub Issues for bug reports and feature requests
