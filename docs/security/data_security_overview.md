# Data Handling & Security Overview

*How Constellation Hub protects operational data and supports secure deployments.*

---

## Purpose

This document explains what types of data Constellation Hub handles, how that data should be protected in production deployments, and the security measures built into the platform.

It is written for security officers, system administrators, and decision-makers evaluating Constellation Hub for their missions.

---

## What Data Does Constellation Hub Handle?

Constellation Hub is primarily an **operations management platform**. It orchestrates *when* and *how* to communicate with satellites, but it typically does not process raw mission payloads (imagery, sensor data, etc.) directly.

### Data Types

| Category | Description | Sensitivity |
|----------|-------------|-------------|
| **Orbital Data** | Satellite positions derived from TLE (Two-Line Element) sets | Generally unclassified; TLEs are often publicly available |
| **Constellation Metadata** | Satellite names, IDs, operational status | Internal/operational |
| **Ground Station Information** | Station locations, capabilities, availability | Internal/operational |
| **Pass Schedules** | When each satellite contacts each ground station | Operational; may indicate collection priorities |
| **Telemetry Summaries** | High-level health indicators (not raw telemetry streams) | Operational |
| **Scheduling Decisions** | AI recommendations and operator approvals | Operational |
| **User Accounts & Access Logs** | Who accessed what, when | Sensitive; audit trail |

### What Constellation Hub Does NOT Handle (by default)

- Raw mission payloads (imagery, signals intelligence, etc.)
- Detailed command sequences for spacecraft control
- Encryption keys or credentials for TT&C authentication

These remain within dedicated mission data systems and TT&C infrastructure.

---

## How Data Should Be Protected

For production deployments, the following security measures should be implemented:

### Encryption in Transit

- **All network communication uses TLS 1.2 or higher**
- Frontend-to-API, service-to-service, and database connections are encrypted
- Certificates should be issued by a trusted CA (or an internal PKI for air-gapped environments)

### Encryption at Rest

- Database storage should use encrypted volumes (AES-256)
- Backups must also be encrypted
- Container images do not contain secrets; secrets are injected at runtime

### Authentication and Authorization

| Layer | Method |
|-------|--------|
| **User access** | OAuth 2.0 / OpenID Connect with modern identity provider (IdP) |
| **API access** | API keys or OAuth tokens with scopes |
| **Service-to-service** | Mutual TLS or internal service tokens |
| **Database** | Role-based access with least-privilege accounts |

### Role-Based Access Control (RBAC)

Constellation Hub implements three-tier RBAC:

| Role | Permissions | Typical Users |
|------|-------------|---------------|
| **Viewer** | Read-only access to all data, dashboards, and schedules | Analysts, management, stakeholders |
| **Operator** | Can execute schedules, trigger TLE refresh, run AI optimizations, approve AI actions | Satellite operators, mission control |
| **Admin** | Full system access including user and ground station management | System administrators, senior operators |

**Key RBAC Features**:
- JWT-based authentication with bcrypt password hashing
- API key support for service-to-service authentication
- Frontend conditional rendering based on user role
- Backend endpoint protection via FastAPI dependencies
- All privileged actions (operator+) logged for audit trails

**AI Action Restrictions**:
- AI optimization requests: open to all authenticated users
- AI-generated action execution ("apply"): requires **operator role or higher**
- This ensures human-in-the-loop approval for all AI recommendations

[See full permission matrix →](roles_and_permissions.md)

### Logging and Audit Trails

- All API requests are logged with timestamp, user identity, action, and result
- Logs should be shipped to a centralized log management system (SIEM)
- Retention policies should meet organizational and regulatory requirements
- Logs are append-only; tampering should be detectable

---

## AI Agent Security Considerations

Constellation Hub includes AI agents for schedule optimization and operational assistance. These agents have specific security properties:

### What AI Agents See

| Agent | Data Access |
|-------|-------------|
| **Pass Scheduler** | Pass opportunities, satellite priorities, ground station costs |
| **Ops Co-Pilot** | Operational events, alerts, and contextual metadata |

Neither agent has access to raw mission payloads, cryptographic keys, or direct command capabilities.

### AI Agents Are Advisory

> **The AI agents are assistive, not autonomous.** They provide recommendations, but actions require human approval by default.

This "human-in-the-loop" design ensures that:
- Operators review and approve AI suggestions before execution
- No irreversible critical commands are issued by AI without authorization
- Audit trails capture both AI recommendations and human decisions

### LLM Configuration Options

For the Ops Co-Pilot, which can use Large Language Models (LLMs):

| Mode | Description |
|------|-------------|
| **Mock** | No external API calls; template-based responses |
| **On-Premise LLM** | Connect to locally hosted models (e.g., Ollama, vLLM) |
| **Cloud LLM** | Connect to external providers (OpenAI, Anthropic) with API key |

For sensitive environments, operators can:
- Disable external LLM calls entirely
- Use only on-premise or government-approved AI services
- Configure network policies to block outbound AI traffic

---

## Secure Deployment Recommendations

### Network Segmentation

- Place Constellation Hub in a dedicated network zone
- Use firewalls to restrict inbound access to necessary ports only
- Outbound access should be limited and monitored

### Container Security

- Use minimal base images (e.g., distroless, Alpine)
- Scan images for vulnerabilities before deployment
- Do not run containers as root
- Use read-only file systems where possible

### Secrets Management

- Store secrets in a dedicated secrets manager (Vault, AWS Secrets Manager, etc.)
- Do not commit secrets to version control
- Rotate secrets regularly

### Vulnerability Management

- Subscribe to security advisories for dependencies
- Regularly update dependencies and rebuild images
- Use automated scanning in CI/CD pipeline

---

## Data Residency and Sovereignty

Constellation Hub can be deployed:

- **In public cloud** (AWS, Azure, GCP, etc.)
- **In government cloud** (AWS GovCloud, Azure Government, etc.)
- **On-premise / air-gapped** within controlled facilities

Data remains within the deployment boundary; Constellation Hub does not "phone home" or require external connectivity for core functionality (except for optional LLM features, which can be disabled).

---

## Summary

Constellation Hub is designed with security as a core principle:

| Principle | Implementation |
|-----------|----------------|
| **Defense in depth** | Multiple layers of protection (network, application, data) |
| **Least privilege** | Users and services have only necessary permissions |
| **Transparency** | Open-source code is auditable |
| **Human oversight** | AI agents are advisory, not autonomous |
| **Flexibility** | Deploy anywhere from cloud to air-gapped environments |

For production deployments, organizations should apply their standard security policies and conduct appropriate risk assessments.
