# System Description

*Technical architecture of Constellation Hub for architects, integrators, and engineering teams.*

---

## Overview

Constellation Hub is a modular, cloud-native platform for satellite constellation management. It provides the software infrastructure between satellites in orbit and the mission systems that use their data.

This document describes the major system components, their responsibilities, and how they interact.

---

## Where Constellation Hub Fits

In a typical ground segment architecture, Constellation Hub sits between low-level TT&C (Telemetry, Tracking & Command) systems and high-level mission applications:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Mission Applications                         │
│     (Customer Portals, Analytics, Imagery Processing)           │
└────────────────────────────┬────────────────────────────────────┘
                             │ Tasking, Data, Status
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                                                                  │
│                     CONSTELLATION HUB                            │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Orbit   │  │ Routing  │  │  Ground  │  │    AI    │        │
│  │  Engine  │  │ Service  │  │ Scheduler│  │  Agents  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │ Pass Plans, Commands, Telemetry
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Ground Network / TT&C                         │
│     (Antennas, Modems, Front-End Processors, GSaaS APIs)        │
└────────────────────────────┬────────────────────────────────────┘
                             │ RF / Baseband
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Satellite Constellation                      │
│              (Spacecraft in LEO, MEO, GEO, etc.)                │
└─────────────────────────────────────────────────────────────────┘
```

**Key insight:** Constellation Hub does not directly control satellites or process raw RF signals. It orchestrates *when* and *how* to communicate with satellites, leaving the actual communication to TT&C systems.

---

## Major Components

### 1. Orbit Engine (core-orbits)

**Purpose:** Compute where satellites are and where they will be.

**Responsibilities:**
- Parse TLE (Two-Line Element) data—the standard format for describing satellite orbits
- Propagate orbits forward in time using the SGP4 algorithm
- Calculate ground coverage footprints (what areas a satellite can "see")
- Provide position queries for any satellite at any time

**Key concepts:**
- *TLE (Two-Line Element):* A compact text format that describes a satellite's orbit. Published by organizations like NORAD.
- *SGP4:* A mathematical model that predicts satellite positions based on TLE data.
- *Ephemeris:* A table of satellite positions over time.

**Interfaces:**
- REST API for querying satellite positions and coverage
- Database storage for satellite and constellation metadata

---

### 2. Routing Service

**Purpose:** Model communication paths and find optimal data routes.

**Responsibilities:**
- Maintain a graph of possible links (satellite-to-ground, satellite-to-satellite)
- Calculate link characteristics (latency, bandwidth, cost)
- Find best paths using Dijkstra's algorithm with configurable policies
- Support constraints like maximum latency, preferred stations, or avoided links

**Key concepts:**
- *Inter-Satellite Link (ISL):* A direct communication link between two satellites, allowing data relay without ground stations.
- *Link budget:* The calculation of signal strength from transmitter to receiver, determining if a link is viable.

**Interfaces:**
- REST API for path queries
- Database storage for link definitions and routing policies

---

### 3. Ground Scheduler

**Purpose:** Manage ground stations and schedule satellite passes.

**Responsibilities:**
- Store ground station definitions (location, capabilities, costs)
- Compute visibility windows—when each satellite can communicate with each station
- Generate baseline schedules using heuristic algorithms
- Track satellite data queues for prioritization

**Key concepts:**
- *Pass:* A time window when a satellite is visible from a ground station (typically 5–15 minutes for LEO satellites).
- *AOS/LOS:* Acquisition of Signal / Loss of Signal—the start and end of a pass.
- *Elevation angle:* How high above the horizon the satellite appears. Higher is better for link quality.

**Interfaces:**
- REST API for station management, pass computation, and scheduling
- Database storage for stations, passes, and schedules

---

### 4. AI Agents

**Purpose:** Provide intelligent optimization and operational assistance.

**Components:**

**Pass Scheduler (optimization)**
- Takes a baseline schedule and improves it
- Uses heuristic scoring (data priority, pass quality, cost)
- Designed with a "strategy pattern" so different algorithms (heuristic, ML-based) can be swapped in

**Ops Co-Pilot (assistance)**
- Analyzes operational events and anomalies
- Generates natural-language summaries
- Suggests actions (e.g., "reschedule to alternate station")
- Uses an abstracted LLM (Large Language Model) client that can connect to various providers

**Key concepts:**
- *LLM (Large Language Model):* An AI system trained on text that can summarize, analyze, and generate language. Examples: GPT, Claude, Llama.
- *Strategy pattern:* A software design that allows swapping algorithms at runtime.

**Interfaces:**
- REST API for optimization and analysis requests
- Can be configured to use mock AI (for testing) or production LLMs

---

### 5. Web Dashboard (Frontend)

**Purpose:** Provide a visual interface for operators.

**Capabilities:**
- 3D globe visualization showing satellite positions and coverage
- Fleet status overview with health indicators
- Schedule management with timeline views
- Ops Co-Pilot panel for AI-assisted analysis

**Technology:** React, TypeScript, CesiumJS (3D mapping library)

---

## Data Flows

### Satellite Tracking Flow

```
TLE Data Source (e.g., Space-Track.org)
          │
          ▼
    Orbit Engine
    (parse, propagate)
          │
          ▼
    Position/Coverage Queries
          │
          ▼
    Frontend Globe / Scheduling Service
```

### Pass Planning Flow

```
Satellites + Ground Stations
          │
          ▼
    Ground Scheduler
    (compute visibility)
          │
          ▼
    Baseline Schedule
          │
          ▼
    AI Agents (optimize)
          │
          ▼
    Final Schedule → Ground Network
```

### Incident Analysis Flow

```
Operational Events (missed pass, link failure, etc.)
          │
          ▼
    AI Agents (Ops Co-Pilot)
          │
          ▼
    Summary + Recommended Actions
          │
          ▼
    Operator Review → Action
```

---

## Deployment Architecture

Constellation Hub can be deployed in various configurations:

### Development / Demo
- All services run on a single machine via Docker Compose
- PostgreSQL database in a container
- Suitable for evaluation and development

### Production / Cloud
- Services deployed as containers in Kubernetes
- Managed PostgreSQL (or equivalent)
- Horizontal scaling for high availability
- API gateway for authentication and rate limiting

### Air-Gapped / Sovereign
- All components deployed within a controlled network
- AI agents configured for local LLM (no external API calls)
- Additional hardening per organizational security policies

---

## Integration Points

Constellation Hub is designed to integrate with:

| System Type | Integration Method |
|-------------|-------------------|
| **TT&C Systems** | REST API for pass plans, command scheduling |
| **GSaaS Providers** | REST API for station availability, contact booking |
| **Mission Databases** | REST API for tasking, data delivery status |
| **SIEM / Logging** | Standard log output, optional syslog/Splunk integration |
| **Identity Providers** | OAuth 2.0 / OIDC for authentication |

---

## Summary

Constellation Hub provides a modular, API-driven platform for constellation operations. Its four core services—Orbit Engine, Routing, Ground Scheduler, and AI Agents—work together to give operators visibility, automation, and intelligence across their satellite fleet.

The system is designed to be:
- **Extensible:** Add new services or replace components as needed
- **Integratable:** Connect to existing ground systems via APIs
- **Deployable:** Run anywhere from a laptop to a secure cloud environment
