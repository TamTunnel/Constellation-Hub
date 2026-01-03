# Architecture

Constellation Hub utilizes a modern, cloud-native microservices architecture designed for scalability and extensibility.

## System Diagram

```mermaid
graph TD
    Client[Web Client (React/Cesium)] --> Gateway[API Gateway / Nginx]

    Gateway --> CoreOrbits[Core Orbits Service]
    Gateway --> Routing[Routing Service]
    Gateway --> Scheduler[Ground Scheduler]
    Gateway --> AIAgents[AI Agents]

    CoreOrbits --> DB[(PostgreSQL)]
    Routing --> DB
    Scheduler --> DB
    AIAgents --> DB

    subgraph Data Layer
        DB
    end

    subgraph Services Layer
        CoreOrbits
        Routing
        Scheduler
        AIAgents
    end

    subgraph Presentation Layer
        Client
    end
```

## Service Descriptions

### 1. Core Orbits (`core-orbits`)

**Responsibility**: The source of truth for orbital data.

- **Key Functions**:
  - Ingests TLE (Two-Line Element) data from CelesTrak.
  - Propagates satellite positions using SGP4 algorithms.
  - Manages constellation and satellite metadata.
- **Tech Stack**: Python, FastAPI, NumPy, Skyfield/SGP4.

### 2. Ground Scheduler (`ground-scheduler`)

**Responsibility**: Manages the link between space and ground.

- **Key Functions**:
  - Maintains the database of ground station locations.
  - Computes visibility windows (AOS/LOS) for all satellite-station pairs.
  - Generates conflict-free downlink schedules.
- **Tech Stack**: Python, FastAPI, IntervalTree.

### 3. Routing Service (`routing`)

**Responsibility**: Optimizes data flow through the constellation.

- **Key Functions**:
  - Models the network topology (ISLs and downlinks).
  - Computes optimal paths for data packets based on latency and capacity.
- **Tech Stack**: Python, FastAPI, NetworkX.

### 4. AI Agents (`ai-agents`)

**Responsibility**: Provides intelligent oversight and optimization.

- **Key Functions**:
  - **Pass Scheduler Agent**: Analyses schedules and suggests efficiency improvements.
  - **Ops Co-Pilot**: Analyzes system logs and events to provide natural language summaries and recommendations.
- **Tech Stack**: Python, FastAPI, LangChain (optional integration).

## Database Schema

The system uses a unified **PostgreSQL** database with specific schemas/tables for each domain:

- `constellations`, `satellites`: Core orbital entities.
- `ground_stations`, `passes`, `schedules`: Ground segment operations.
- `users`: Authentication and profile data.
- `audit_logs`: Security and operational audit trails.

## Frontend Application

The web dashboard is a Single Page Application (SPA) built with:

- **React 18**: UI component library.
- **CesiumJS**: High-fidelity 3D globe visualization.
- **TailwindCSS**: Styling framework.
- **Vite**: Build tool and dev server.

## Deployment

The system is containerized using **Docker** and orchestrated via **Docker Compose** for local development. It is designed to be deployable on **Kubernetes** for production use cases.
