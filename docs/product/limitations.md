# Current Limitations & Scope

This document outlines the current scope, known gaps, and limitations of Constellation Hub's MVP release.

---

## Project Scope

Constellation Hub is designed as a **unified control plane for satellite constellation operations**. The current MVP focuses on:

✅ **Core Operations**: Fleet visualization, pass scheduling, ground network management  
✅ **AI-Assisted Planning**: Intelligent schedule optimization and operational assistance  
✅ **Production-Ready Foundation**: Authentication, observability, database migrations, TLE ingestion  
✅ **Modern Stack**: Cloud-native architecture, API-first design, containerized deployment  

---

## Current Limitations (MVP)

### 1. Multi-Tenancy & Isolation

**Current State**: Single-tenant or trusted environment only

- ✅ Supports one organization/constellation at a time
- ✅ User roles (viewer, operator, admin) within single tenant
- ❌ No hard multi-tenant data isolation
- ❌ No tenant-specific resource limits or quotas

**Use Cases**:
- ✅ Single constellation operator (startup, research mission)
- ✅ Internal tools for a single organization
- ⚠️ Multi-customer SaaS (requires additional isolation)

**Tier 3 Roadmap**: Add tenant isolation, per-tenant databases, resource quotas

---

### 2. AI Safety & Human-in-the-Loop

**Current State**: AI agents are assistive tools, not autonomous operators

- ✅ AI provides schedule optimization recommendations
- ✅ AI analyzes operational events and suggests actions
- ✅ **Human approval required** before executing AI recommendations
- ❌ AI does not execute commands autonomously

**Guardrails**:
- AI "apply" actions restricted to `operator` role or higher
- All AI actions logged for audit
- Operators review AI proposals before execution

**Philosophy**: AI augments human expertise but does not replace operator judgment.

---

### 3. Security & Compliance Posture

**Current State**: Not certified for classified or high-security environments

- ✅ JWT authentication with bcrypt password hashing
- ✅ Role-based access control (RBAC)
- ✅ Structured logging with request tracing
- ✅ Health probes for operational monitoring
- ❌ Not FIPS 140-2/3 certified
- ❌ Not cleared for classified data (SECRET/TS)
- ❌ No multi-factor authentication (MFA) yet
- ❌ No hardware security module (HSM) integration

**Use Cases**:
- ✅ Commercial satellite operations (unclassified data)
- ✅ Research and academic missions
- ✅ Internal dev/test environments
- ⚠️ Government classified missions (requires hardening review)
- ⚠️ Financial or healthcare data (requires compliance audit)

**Deployment Guidance**:
- For classified environments: conduct security review, add controls (MFA, HSM, network isolation)
- For regulated industries: perform compliance assessment (GDPR, HIPAA, etc.)
- For production: change default secrets, enable audit logging, restrict network access

---

### 4. Simulation & Emulation

**Current State**: Live operations logic and visualization; simulation not yet implemented

- ✅ Real-time satellite position visualization (via TLE propagation)
- ✅ Pass prediction and scheduling for live constellations
- ❌ No physics-based orbital simulator
- ❌ No constellation design/simulation mode
- ❌ No "what-if" scenario analysis for future constellations

**Use Cases**:
- ✅ Operating existing satellites in orbit
- ✅ Planning passes for deployed constellations
- ⚠️ Pre-launch constellation design (requires simulation)
- ⚠️ Trade studies for new missions (requires modeling)

**Tier 3+ Roadmap**: Add simulation mode for constellation design and trade studies

---

### 5. Ground Network Capabilities

**Current State**: Supports ground station management and pass scheduling

- ✅ Multi-ground-station network modeling
- ✅ Pass prediction with elevation constraints
- ✅ Schedule generation and conflict resolution
- ⚠️ Limited antenna pattern modeling (assumes omnidirectional)
- ❌ No real-time antenna pointing control
- ❌ No signal link budget calculations
- ❌ No weather/atmospheric effects modeling

**Future Enhancements**:
- Antenna pointing automation
- Link budget and margin analysis
- Weather-aware scheduling
- Integration with commercial GSaaS providers (AWS Ground Station, Azure Orbital, etc.)

---

### 6. Data Routing & ISL Modeling

**Current State**: Basic inter-satellite link (ISL) routing logic

- ✅ Graph-based routing of data through constellation
- ✅ Shortest-path and capacity-aware algorithms
- ⚠️ Simplified link capacity models
- ❌ No optical ISL power/pointing constraints
- ❌ No realistic RF link budgets for ISLs
- ❌ No dynamic topology updates as satellites move

**Use Cases**:
- ✅ Logical data routing for small constellations
- ⚠️ High-fidelity ISL performance modeling (requires enhancement)

---

### 7. Scalability & Performance

**Current State**: Designed for small-to-medium constellations (10–500 satellites)

- ✅ Handles 10–100 satellites efficiently
- ✅ Horizontal scaling via microservices
- ⚠️ Not yet tested with 1,000+ satellites
- ⚠️ Globe visualization may degrade with very large constellations

**Performance Notes**:
- Pass computation can be CPU-intensive for large constellations
- Consider caching or pre-computation for mega-constellations
- Frontend globe rendering limited by browser WebGL performance

---

### 8. External Integrations

**Current State**: Limited integrations; extensible via APIs

**Available**:
- ✅ CelesTrak TLE ingestion
- ✅ REST APIs for all services
- ✅ Prometheus metrics export

**Not Yet Integrated**:
- ❌ Space-Track.org (TLE source, requires credentials)
- ❌ AWS Ground Station
- ❌ Azure Orbital
- ❌ Satellite command and control (C2) systems
- ❌ Mission planning tools (STK, GMAT, etc.)

**Integration Path**: Use REST APIs to connect Constellation Hub with external systems

---

## Development & Testing Gaps

### Testing Coverage

- ✅ Unit tests for backend services
- ✅ Integration tests for API endpoints
- ⚠️ Limited end-to-end (E2E) tests
- ❌ No load/stress testing results published
- ❌ No chaos engineering or resilience testing

### CI/CD Maturity

- ✅ Automated linting and tests on every commit
- ✅ Docker image builds
- ⚠️ No automated deployment pipelines to staging/production
- ❌ No blue/green or canary deployment strategies
- ❌ No automated rollback mechanisms

---

## Deployment & Operations Gaps

### Infrastructure as Code

- ✅ Docker Compose for local dev
- ⚠️ No Kubernetes deployment manifests yet
- ❌ No Terraform or Pulumi infrastructure definitions
- ❌ No Helm charts for easy K8s deployment

### Observability

- ✅ Structured logging (JSON)
- ✅ Prometheus metrics endpoints
- ✅ Health and readiness probes
- ⚠️ No pre-built Grafana dashboards
- ❌ No distributed tracing (OpenTelemetry, Jaeger)
- ❌ No alerting rules defined

### Backup & Disaster Recovery

- ❌ No automated database backup solution
- ❌ No disaster recovery (DR) plan documented
- ❌ No multi-region deployment guidance

---

## Comparison with Commercial Alternatives

Constellation Hub is an **open-core alternative** to proprietary satellite operations platforms.

| Feature | Constellation Hub (MVP) | Commercial Platforms |
|---------|------------------------|----------------------|
| **Licensing** | Open-source (Apache 2.0) | Proprietary, licensed per seat |
| **Cost** | Free to use | High licensing fees |
| **Customization** | Fully customizable | Limited or none |
| **Vendor Lock-In** | None | High |
| **AI-Assisted Ops** | ✅ Built-in | ❌ Bolt-on or none |
| **Multi-Tenant SaaS** | ❌ Not yet | ✅ Often yes |
| **Classified Support** | ⚠️ Requires review | ✅ Some vendors certified |
| **Simulation** | ❌ Not yet | ✅ Often included |
| **GSaaS Integration** | ❌ Not yet | ✅ AWS, Azure, etc. |

**When to Choose Constellation Hub**:
- You want full control and customization
- You need to avoid vendor lock-in
- You're operating a small-to-medium constellation (10–500 satellites)
- You value open-source transparency and community-driven development

**When Commercial Tools May Be Better**:
- You need pre-certified solutions for classified environments
- You require comprehensive simulation/modeling capabilities
- You need extensive GSaaS integrations out-of-the-box
- You prefer vendor support and SLAs

---

## Roadmap to Address Limitations

### Tier 3 (Near-Term)

- [ ] Multi-tenant isolation and per-tenant configs
- [ ] Kubernetes deployment manifests and Helm charts
- [ ] Grafana dashboard templates
- [ ] Space-Track.org integration
- [ ] Basic constellation simulation mode

### Tier 4 (Mid-Term)

- [ ] Multi-factor authentication (MFA)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] AWS Ground Station integration
- [ ] Advanced ISL modeling (optical links, realistic budgets)
- [ ] Automated backup and DR procedures

### Future Considerations

- [ ] FIPS compliance and HSM integration
- [ ] Government security clearance pathways
- [ ] Mega-constellation optimization (1,000+ satellites)
- [ ] Real-time C2 integration
- [ ] Physics-based orbital propagation (beyond TLE)

---

## Feedback & Contributions

Constellation Hub is a community-driven project. If you encounter limitations or have enhancement requests:

- 📝 **File an Issue**: [GitHub Issues](https://github.com/TamTunnel/Constellation-Hub/issues)
- 💬 **Join Discussions**: [GitHub Discussions](https://github.com/TamTunnel/Constellation-Hub/discussions)
- 🔧 **Contribute**: See [CONTRIBUTING.md](../../CONTRIBUTING.md)

We welcome contributions to address these limitations and expand Constellation Hub's capabilities.
