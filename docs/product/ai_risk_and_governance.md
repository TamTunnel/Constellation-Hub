# AI Risk & Governance

*Guidelines for safe, responsible, and auditable use of AI agents in Constellation Hub.*

---

## Purpose

Constellation Hub includes AI-powered agents that assist operators with schedule optimization and incident analysis. This document clarifies the role of these agents, the safeguards in place, and best practices for governing AI-influenced decisions.

It is written for mission managers, security officers, and executives who need to understand the boundaries and oversight mechanisms for AI in satellite operations.

---

## AI Agents in Constellation Hub

### Pass Scheduler (Optimization Agent)

**What it does:**
- Analyzes pass opportunities, satellite priorities, and ground station availability
- Suggests an optimized schedule that maximizes data throughput or minimizes cost
- Uses heuristic algorithms (rule-based optimization); future versions may incorporate machine learning

**What it does NOT do:**
- Directly send commands to satellites
- Override operator decisions
- Access raw mission payload data

### Ops Co-Pilot (Assistance Agent)

**What it does:**
- Analyzes operational events (alerts, anomalies, missed passes)
- Generates natural-language summaries of incidents
- Suggests actions for operators to consider

**What it does NOT do:**
- Execute actions automatically
- Access systems beyond the operational data it's configured to see
- Make irreversible decisions

---

## Core Principle: Human-in-the-Loop

> **All AI suggestions require human approval before execution for safety-critical actions.**

This design principle ensures that:

1. **Operators remain in control.** AI provides recommendations; humans make decisions.

2. **Errors can be caught.** If the AI suggests something incorrect, the operator can reject or modify it before any action is taken.

3. **Accountability is clear.** The audit log captures both what the AI recommended and what the operator approved.

### Approval Workflow

```
AI Agent generates recommendation
           ↓
Recommendation presented to operator
           ↓
Operator reviews (accepts, modifies, or rejects)
           ↓
If accepted → Action is executed
           ↓
Decision is logged (AI suggestion + operator action)
```

---

## AI Decision Boundaries

The following boundaries are built into the system:

| Boundary | Description |
|----------|-------------|
| **No direct commanding** | AI agents cannot send commands to satellites; they produce schedules that humans approve and TT&C systems execute |
| **No critical parameter changes** | AI cannot modify system configuration or security settings |
| **No autonomous escalation** | AI cannot escalate incidents or engage external parties without operator action |
| **Limited data access** | AI agents only see operational data (schedules, passes, events), not payloads or cryptographic material |

---

## LLM Configuration and Isolation

For the Ops Co-Pilot, which can use Large Language Models:

### Available Modes

| Mode | Description | External Calls |
|------|-------------|----------------|
| **Mock** | Template-based responses, no AI model | None |
| **On-Premise** | Locally hosted LLM (Ollama, vLLM, etc.) | None |
| **Cloud API** | External LLM provider (OpenAI, Anthropic) | Yes |

### Recommendations by Environment

| Environment | Recommended Mode |
|-------------|------------------|
| Development / Demo | Mock or Cloud API |
| Commercial Production | On-premise or Cloud API (with data review) |
| Government / Defense | On-premise only; disable external LLM calls |
| Classified Networks | Disable Ops Co-Pilot LLM features |

### Data Sent to LLMs

When using cloud LLMs, the following data may be sent:
- Event descriptions (type, severity, timestamp)
- Satellite and ground station identifiers (not coordinates by default)
- Error messages and status summaries

The following is NOT sent:
- Mission payloads or imagery
- Cryptographic keys or credentials
- Raw telemetry streams
- Personally identifiable information (PII)

> Operators should review their LLM provider's data handling policies and ensure compliance with organizational requirements.

---

## Audit and Logging

All AI-influenced decisions are logged:

| Log Entry | Contents |
|-----------|----------|
| **AI Recommendation** | Timestamp, agent type, recommendation details |
| **Operator Action** | Accept/reject/modify, operator ID, reason (optional) |
| **Execution Result** | What was executed, success/failure |

Logs are:
- Immutable (append-only)
- Exportable to external systems (SIEM, compliance tools)
- Retained according to organizational policy

### Example Log Entry

```json
{
  "timestamp": "2024-01-15T14:32:00Z",
  "event_type": "ai_recommendation",
  "agent": "pass_scheduler",
  "recommendation_id": "opt-20240115-001",
  "summary": "Optimized schedule: +12% contact efficiency",
  "passes_added": [45, 46, 48],
  "passes_removed": [41, 43]
}

{
  "timestamp": "2024-01-15T14:35:00Z",
  "event_type": "operator_decision",
  "recommendation_id": "opt-20240115-001",
  "operator_id": "jsmith",
  "action": "accepted_with_modification",
  "modification": "Retained pass 41 for customer SLA",
  "final_passes_added": [45, 46, 48],
  "final_passes_removed": [43]
}
```

---

## Best Practices for AI Governance

### 1. Separation of Environments

- Use separate instances for development/training and production
- Do not train on production operational data without review
- Test AI changes in non-production before deployment

### 2. Regular Review of AI Behavior

- Monitor AI recommendation acceptance rates
- Investigate patterns where operators frequently reject AI suggestions
- Conduct periodic audits of AI decision logs

### 3. Configuration Control

- Document AI configuration (model version, parameters, allowed data)
- Require change management for AI settings modifications
- Maintain baseline configurations for rollback

### 4. Training and Awareness

- Ensure operators understand AI limitations
- Provide guidance on when to trust vs. question AI recommendations
- Train operators to document rationale when overriding AI

### 5. Incident Response

- Include AI behavior in incident investigation when relevant
- Have procedures for disabling AI agents if misbehavior is detected
- Report AI-related safety events to the development team

---

## Disabling AI Features

Operators can disable AI features entirely if desired:

| Setting | Effect |
|---------|--------|
| `SCHEDULER_STRATEGY=heuristic` | Uses rule-based optimizer (default) |
| `SCHEDULER_STRATEGY=none` | Disables automatic optimization |
| `LLM_PROVIDER=mock` | Disables real LLM calls for Ops Co-Pilot |
| AI service not deployed | Ops Co-Pilot and AI scheduler unavailable |

The platform functions normally without AI features; scheduling and analysis can be done manually.

---

## Summary

| Governance Principle | Implementation |
|----------------------|----------------|
| **Human oversight** | All AI recommendations require operator approval |
| **Bounded access** | AI agents only see operational data, not payloads or commands |
| **Full auditability** | Every AI recommendation and operator decision is logged |
| **Configurable trust** | Operators can disable external LLMs or AI features entirely |
| **Transparency** | Open-source code enables review of AI behavior |

Constellation Hub's AI agents are designed to augment operator capabilities, not replace operator judgment. They reduce workload and surface insights, while keeping humans firmly in control of safety-critical decisions.
