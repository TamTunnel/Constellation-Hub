# Constellation Hub

**Open-source constellation management and AI-assisted operations for modern satellite fleets.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![CI](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/ci-backend.yml/badge.svg)](https://github.com/TamTunnel/Constellation-Hub/actions)
[![CI - Frontend](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/ci-frontend.yml/badge.svg)](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/ci-frontend.yml)
[![Docker Build](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/docker-build.yml/badge.svg)](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/docker-build.yml)
[![Deploy to Dev](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/deploy-dev.yml/badge.svg)](https://github.com/TamTunnel/Constellation-Hub/actions/workflows/deploy-dev.yml)

---

## One-line summary (Tagline)
Open‑source satellite constellation “brain” for fleet visualization, pass scheduling, data routing, and AI‑assisted operations.

- Simple analogy:
Think of Constellation Hub as an air‑traffic control system and network router combined, but for satellites instead of airplanes. It gives operators one place to see every satellite, plan when they talk to the ground, and let AI suggest smarter ways to move data across the fleet

## The Problem

Operating a modern satellite constellation is hard—and it's only getting harder.

Today's satellite operators face mounting challenges:

- **Manual, labor-intensive planning.** Scheduling downlink passes across dozens or hundreds of satellites requires specialized expertise and hours of coordination, often using spreadsheets or legacy tools.

- **Proprietary, siloed systems.** Most ground software is vendor-locked, expensive, and doesn't integrate well with other tools. Switching costs are high, and customization is limited.

- **Scaling is painful.** What works for 5 satellites breaks at 50. What works for 50 breaks at 500. Teams struggle to scale operations without proportionally scaling headcount.

- **Data overload, not insight.** Operators are drowning in telemetry and alerts, but lack intelligent systems to synthesize information and recommend actions.

- **No open standard.** There's no widely adopted, open-source foundation that new-space companies, government programs, and research missions can build upon.

---

## How Constellation Hub Helps

**Constellation Hub is a unified control plane for satellite constellation operations.**

Think of it as a single dashboard where you can:

- **See your satellites** — Visualize your entire fleet on a 3D globe. Know where each satellite is, where it's going, and what it can see.

- **Plan your passes** — Automatically compute when each satellite can talk to each ground station. Generate optimized downlink schedules with one click.

- **Route your data** — Model the links between satellites and ground stations. Find the best path to move data from orbit to your data center.

- **Get AI assistance** — Let intelligent agents suggest schedule improvements, analyze incidents, and summarize operational status—so your team can focus on decisions, not data entry.

**What makes Constellation Hub different:**

| | Traditional Tools | Constellation Hub |
|---|---|---|
| **Open Source** | ❌ Proprietary | ✅ Apache 2.0, fully open |
| **Vendor Neutral** | ❌ Locked to one vendor | ✅ Works with any ground network |
| **AI-Native** | ❌ Bolt-on analytics | ✅ AI agents built-in from day one |
| **Modern Stack** | ❌ Legacy architectures | ✅ Cloud-native, API-first, containerized |

---

## Competitor Landscape

The satellite ground software market includes established, proprietary platforms from aerospace primes and specialized vendors. These tools are capable but often:

- Require significant licensing fees
- Lock operators into specific ground networks or hardware
- Offer limited customization or integration options

**Constellation Hub complements this ecosystem as an open-core alternative.** It provides a foundation that operators can adopt, extend, and integrate—whether as a primary system for lean missions or as a layer that connects existing investments.

We believe the industry benefits from open standards and shared tooling, and we invite operators, integrators, and developers to build with us.

---

## Key Use Cases

- **Run a 20–100 satellite IoT constellation with a small ops team** — Automate pass planning and scheduling so a team of 2–3 can operate what previously required 10+.

- **Optimize downlinks across owned and commercial ground stations** — Mix your own antennas with Ground-Station-as-a-Service (GSaaS) providers. Let AI find the best allocation.

- **Give operators an AI co-pilot for incident analysis** — When something goes wrong, get plain-language summaries and recommended actions—not just raw alerts.

- **Provide visibility across civil, commercial, and defense missions** — A unified view regardless of mission type, satellite bus, or orbit regime.

- **Accelerate development with an API-first platform** — Integrate Constellation Hub into your existing C2, data processing, or analytics pipelines via REST APIs.

- **Reduce vendor lock-in and total cost of ownership** — Start with open source, customize as needed, and avoid proprietary dependencies.

---

## Who Is This For?

| Audience | How They Benefit |
|----------|------------------|
| **New-Space Startups** | Get to orbit faster with ready-to-use ops tooling |
| **Commercial Constellation Operators** | Scale operations without scaling headcount |
| **Government & Defense Integrators** | Open-source foundation for mission-specific solutions |
| **Research & Academic Missions** | No licensing fees, full transparency, community support |
| **Ground Network Providers** | Offer value-added services on top of an open platform |

---

## Quick Demo

**See Constellation Hub in action in 2 minutes:**

```bash
# Clone the repository
git clone https://github.com/TamTunnel/Constellation-Hub.git
cd constellation-hub

# Start services and load demo data
docker compose up -d
make demo

# Visit the dashboard
open http://localhost:3000
```

**Demo includes:**
- ✅ 6 sample satellites with realistic orbits
- ✅ 3 ground stations (US, Europe, Asia)
- ✅ Pre-computed passes and schedules
- ✅ Demo users for each role (viewer, operator, admin)

[See demo credentials and details →](docs/ops/local_dev.md#demo-setup)

---

## Current Limitations (MVP)

Constellation Hub is an early-stage, production-ready MVP. Please be aware of these limitations:

> [!NOTE]
> **Single-Tenant Focus**  
> Not designed yet for hard multi-tenant isolation. Suitable for single-tenant or trusted environments only.

> [!NOTE]
> **AI is Assistive, Not Autonomous**  
> AI agents propose actions; **human operators must approve** before execution. AI does not take autonomous actions.

> [!WARNING]
> **Not Certified for Classified Environments**  
> Not yet hardened or certified for classified/high-security government use. Any such deployment would require additional security controls and review.

> [!NOTE]
> **Simulation Not Implemented**  
> Tier 3 feature. Current focus is live operations logic and visualization, not constellation design simulation.

[Read full limitations documentation →](docs/product/limitations.md)

---

## Roles & Permissions

Constellation Hub implements role-based access control (RBAC) with three roles:

| Role | Permissions | Demo User |
|------|-------------|-----------|
| **Viewer** | Read-only access to data and visualizations | `demo_viewer` / `viewer123` |
| **Operator** | Can generate schedules, optimize routes, trigger TLE refresh | `demo_ops` / `operator123` |
| **Admin** | Full system access including user management | `demo_admin` / `admin123` |

**Key Restrictions:**
- AI "apply" actions require `operator` role or higher
- User management requires `admin` role
- All demo credentials are for **local/demo use only**

[See full permission matrix →](docs/security/roles_and_permissions.md)

---

## Architecture Overview

Constellation Hub is built as a set of cooperating microservices:

```
┌────────────────────────────────────────────────────────────┐
│                     Web Dashboard                           │
│        (3D Globe • Fleet View • Scheduling • AI Panel)      │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│                      API Gateway                            │
└───┬──────────────┬──────────────┬──────────────┬───────────┘
    │              │              │              │
┌───▼───┐    ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
│ Orbit │    │  Routing  │  │  Ground   │  │    AI     │
│ Engine│    │  Service  │  │ Scheduler │  │  Agents   │
└───────┘    └───────────┘  └───────────┘  └───────────┘
    ↓              ↓              ↓              ↓
                    PostgreSQL Database
```

| Service | What It Does |
|---------|--------------|
| **Orbit Engine** | Computes satellite positions and ground coverage from orbital data |
| **Routing Service** | Finds optimal paths for data flow through the constellation |
| **Ground Scheduler** | Manages ground stations and generates pass schedules |
| **AI Agents** | Provides intelligent schedule optimization and operational assistance |

### Production Features

| Feature | Description |
|---------|-------------|
| **JWT Authentication** | Role-based access control (viewer, operator, admin) |
| **API Key Support** | Service-to-service authentication |
| **Prometheus Metrics** | Request count, latency, error tracking at `/metrics` |
| **Structured Logging** | JSON-formatted logs with request ID tracing |
| **Health Probes** | Kubernetes-compatible `/healthz` and `/readyz` endpoints |
| **Database Migrations** | Alembic for schema versioning |
| **TLE Ingestion** | Automated satellite data from CelesTrak |
| **3D Globe** | CesiumJS visualization with OpenStreetMap tiles |

---


## Quickstart

### Prerequisites

- Docker and Docker Compose
- Git

### Run the Demo

```bash
# Clone the repository
git clone https://github.com/TamTunnel/Constellation-Hub.git
cd constellation-hub

# Start all services
cd infra/docker
docker-compose up -d

# Access the dashboard
open http://localhost:3000
```

### Explore the APIs

Each service exposes interactive API documentation:

- **Orbit Engine:** http://localhost:8001/docs
- **Routing:** http://localhost:8002/docs
- **Ground Scheduler:** http://localhost:8003/docs
- **AI Agents:** http://localhost:8004/docs

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/architecture/overview.md) | System design and component relationships |
| [System Description](docs/architecture/system_description.md) | Detailed technical architecture |
| [Concept of Operations](docs/product/conops.md) | Typical missions, roles, and workflows |
| [API Reference](docs/api/backend.md) | REST API endpoints and examples |
| [Local Development](docs/ops/local_dev.md) | Setting up a dev environment |
| [Observability Guide](docs/ops/observability.md) | Logging, metrics, and health probes |
| [TLE Feeds](docs/product/tle_feeds.md) | Satellite TLE data ingestion |
| [CI/CD Guide](docs/ops/ci_cd.md) | Build and deployment pipelines |
| [Security Overview](docs/security/data_security_overview.md) | Data handling and protection |
| [Compliance Guide](docs/security/compliance_and_assurance.md) | Regulatory alignment roadmap |
| [AI Governance](docs/product/ai_risk_and_governance.md) | AI safety and oversight practices |


---

## Contributing

We welcome contributions from the community! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Submitting issues and feature requests
- Making pull requests
- Code style and testing requirements

---

## License

Constellation Hub is released under the [Apache 2.0 License](LICENSE).

---

## Contact

- **GitHub Issues:** [Report bugs or request features](https://github.com/TamTunnel/Constellation-Hub/issues)
- **Discussions:** [Join the community](https://github.com/TamTunnel/Constellation-Hub/discussions)
- **Security:** See [SECURITY.md](SECURITY.md) for responsible disclosure

---

*Constellation Hub is a community-driven project. We're building the foundation for the next generation of satellite operations—together.*
