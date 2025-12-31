# Architecture Overview

This document describes the high-level architecture of Constellation Hub.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Frontend (React + CesiumJS)                       │
│         3D Globe  │  Satellite List  │  Schedule  │  Ops Co-Pilot   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ REST API (HTTP/JSON)
                                 │
┌────────────────────────────────▼────────────────────────────────────┐
│                         Nginx (API Gateway)                          │
│                    Routing, Load Balancing, SSL                      │
└─────┬─────────────────┬───────────────────┬───────────────────┬─────┘
      │                 │                   │                   │
┌─────▼─────┐   ┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│ core-     │   │   routing     │   │   ground-     │   │   ai-agents   │
│ orbits    │   │   service     │   │   scheduler   │   │   service     │
│ Port:8001 │   │   Port:8002   │   │   Port:8003   │   │   Port:8004   │
│           │   │               │   │               │   │               │
│ TLE Parse │   │ Graph Build   │   │ Visibility    │   │ Pass Sched    │
│ SGP4 Prop │   │ Path Finding  │   │ Scheduling    │   │ Ops Co-Pilot  │
│ Coverage  │   │ Policies      │   │ Data Queues   │   │ LLM Client    │
└─────┬─────┘   └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
      │                 │                   │                   │
      └─────────────────┴─────────┬─────────┴───────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    PostgreSQL Database     │
                    │    (Shared Data Store)     │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Redis Cache (Optional)  │
                    └───────────────────────────┘
```

## Services

### Core Orbits Service (Port 8001)

**Purpose**: Orbital mechanics and satellite tracking.

**Responsibilities**:
- Parse TLE (Two-Line Element) data
- Propagate satellite positions using SGP4
- Compute ground coverage footprints
- Manage constellation and satellite metadata

**Key Endpoints**:
- `GET /constellations` - List constellations
- `GET /satellites/{id}/position` - Get position at time
- `GET /satellites/{id}/coverage` - Get coverage footprint

### Routing Service (Port 8002)

**Purpose**: Link modeling and path computation.

**Responsibilities**:
- Model satellite-ground and inter-satellite links
- Build network graphs from link data
- Compute optimal paths using Dijkstra's algorithm
- Apply routing policies (latency, cost, hop limits)

**Key Endpoints**:
- `POST /routing/paths` - Compute optimal route
- `GET /links` - List communication links

### Ground Scheduler Service (Port 8003)

**Purpose**: Ground station management and scheduling.

**Responsibilities**:
- Manage ground station definitions
- Compute satellite visibility windows
- Generate baseline downlink schedules
- Track satellite data queues

**Key Endpoints**:
- `POST /ground-stations` - Register station
- `POST /passes/compute` - Compute passes
- `POST /schedule/generate` - Generate schedule

### AI Agents Service (Port 8004)

**Purpose**: AI-powered optimization and operations assistance.

**Components**:
1. **Pass Scheduler**: Optimizes schedules using heuristics or ML
2. **Ops Co-Pilot**: Analyzes events and suggests actions

**Key Endpoints**:
- `POST /ai/pass-scheduler/optimize` - Optimize schedule
- `POST /ai/ops-copilot/analyze` - Analyze events

## Data Flow

### TLE Ingestion
```
TLE Source → Core Orbits Service → PostgreSQL
                    ↓
            SGP4 Propagation
                    ↓
            Position/Coverage Calculation
```

### Pass Scheduling
```
Satellites → Ground Scheduler → Visibility Computation
                    ↓
            Baseline Schedule
                    ↓
            AI Agents → Optimized Schedule
```

### Ops Analysis
```
Events → AI Agents → LLM Client → Analysis
                         ↓
                 Suggested Actions
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, TypeScript, Vite, CesiumJS, TailwindCSS |
| Backend | Python 3.11, FastAPI |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Orbital Math | SGP4, Skyfield |
| Containers | Docker, docker-compose |
| CI/CD | GitHub Actions |
