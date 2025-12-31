# Interface Control Document (ICD) Summary

*Overview of external interfaces for integrating Constellation Hub with ground systems, service providers, and mission applications.*

---

## Purpose

This document provides a high-level summary of the external interfaces that Constellation Hub exposes and consumes. It is intended for system integrators, architects, and engineers planning to connect Constellation Hub to other systems.

> **Note:** This is a summary document. A detailed ICD with message formats, timing requirements, and error handling would be developed as part of a formal integration project.

---

## Interface Categories

Constellation Hub interfaces with three main categories of external systems:

1. **TT&C / Ground Network Systems** — The equipment and software that physically communicate with satellites
2. **Ground Station Service Providers (GSaaS)** — Third-party ground station networks available on-demand
3. **Mission Systems / Customer C2** — Higher-level systems that submit tasking and receive data

---

## 1. TT&C / Ground Network Interfaces

### Description

These interfaces connect Constellation Hub to the ground network infrastructure that sends commands to satellites and receives telemetry and data.

### Data Exchanged

| Direction | Data Type | Description |
|-----------|-----------|-------------|
| Hub → TT&C | **Pass Schedule** | When to point each antenna at which satellite, including timing (AOS, LOS) and link parameters |
| Hub → TT&C | **Command Batches** | Pre-built command sequences to upload during scheduled passes |
| TT&C → Hub | **Pass Status** | Confirmation of pass execution (completed, partial, failed) |
| TT&C → Hub | **Telemetry Summary** | High-level health indicators extracted from spacecraft telemetry |
| TT&C → Hub | **Link Metrics** | Signal quality, data volume transferred, error rates |

### Protocol Assumptions

- **REST API (preferred):** JSON over HTTPS for schedule delivery and status reporting
- **File-based (alternative):** Schedule files in JSON or XML format via SFTP for legacy systems
- **Real-time updates (optional):** WebSocket or Server-Sent Events for live pass status

### Integration Notes

- Constellation Hub pushes schedules; TT&C systems pull or receive via API callback
- Time synchronization is critical—all times in UTC
- Authentication via API keys or mutual TLS

---

## 2. Ground Station Service Provider (GSaaS) Interfaces

### Description

These interfaces allow Constellation Hub to book and manage contacts with commercial ground station networks such as AWS Ground Station, Azure Orbital, KSAT, SSC, Leaf Space, and others.

### Data Exchanged

| Direction | Data Type | Description |
|-----------|-----------|-------------|
| Hub → GSaaS | **Contact Request** | Satellite ID, time window, ground station preferences, link requirements |
| GSaaS → Hub | **Availability Response** | Available time slots, pricing, station capabilities |
| Hub → GSaaS | **Booking Confirmation** | Selected time slot and configuration |
| GSaaS → Hub | **Contact Status** | Execution status, data delivery confirmation |
| GSaaS → Hub | **Usage/Billing Data** | Contact minutes used, cost summary |

### Protocol Assumptions

- **REST API:** JSON over HTTPS (most GSaaS providers offer REST APIs)
- **OAuth 2.0:** Token-based authentication for API access
- **Webhooks:** For asynchronous status updates from providers

### Integration Notes

- Each GSaaS provider has a unique API; Constellation Hub uses adapter modules
- Availability queries may be cached to reduce API calls
- Failover logic: if one provider is unavailable, attempt alternate providers

---

## 3. Mission Systems / Customer C2 Interfaces

### Description

These interfaces connect Constellation Hub to higher-level mission management systems, customer portals, and command-and-control (C2) applications.

### Data Exchanged

| Direction | Data Type | Description |
|-----------|-----------|-------------|
| C2 → Hub | **Tasking Requests** | Collection requests, data delivery requirements, priority levels |
| Hub → C2 | **Feasibility Response** | Whether tasking can be fulfilled, estimated delivery time |
| Hub → C2 | **Execution Status** | Task accepted, in progress, completed, failed |
| Hub → C2 | **Data Delivery Notification** | Confirmation that data has been delivered to the specified endpoint |
| Hub → C2 | **Operational Alerts** | Anomalies, missed passes, capacity warnings |

### Protocol Assumptions

- **REST API:** JSON over HTTPS for structured data exchange
- **gRPC (optional):** For high-throughput, low-latency integrations
- **Message Queue (optional):** RabbitMQ, Kafka, or similar for event-driven architectures

### Integration Notes

- Tasking requests should include priority (critical, high, medium, low)
- SLA management: Hub tracks deadlines and alerts if at risk
- Data delivery is typically via separate data plane (not through Constellation Hub)

---

## Interface Summary Table

| Interface | Direction | Protocol | Authentication | Data Format |
|-----------|-----------|----------|----------------|-------------|
| TT&C Schedule Delivery | Hub → Ground | REST/HTTPS | API Key, mTLS | JSON |
| TT&C Status Reporting | Ground → Hub | REST/HTTPS, Webhook | API Key | JSON |
| GSaaS Availability Query | Hub → Provider | REST/HTTPS | OAuth 2.0 | JSON |
| GSaaS Booking | Hub → Provider | REST/HTTPS | OAuth 2.0 | JSON |
| GSaaS Status | Provider → Hub | Webhook | OAuth 2.0 | JSON |
| Mission Tasking | C2 → Hub | REST/HTTPS | OAuth 2.0, API Key | JSON |
| Mission Status | Hub → C2 | REST/HTTPS, Webhook | OAuth 2.0 | JSON |
| Operational Alerts | Hub → External | Webhook, Email, SMS | Varies | JSON, Text |

---

## API Standards

Constellation Hub APIs follow these conventions:

- **OpenAPI 3.0:** All APIs are documented with OpenAPI specifications
- **Versioning:** API paths include version (e.g., `/v1/passes`)
- **Error Responses:** Standard HTTP status codes with JSON error bodies
- **Pagination:** Large result sets use cursor-based pagination
- **Rate Limiting:** Configurable rate limits per client

---

## Security Considerations

- All external interfaces require TLS 1.2 or higher
- Authentication is mandatory; anonymous access is not supported
- API keys should be rotated regularly
- Sensitive fields (e.g., command content) can be encrypted at the application level

---

## Extending the ICD

For a production integration, this summary should be expanded into a full ICD that includes:

- Detailed message schemas (JSON Schema or Protocol Buffers)
- Sequence diagrams for key workflows
- Timing and latency requirements
- Error handling and retry policies
- Security threat model for each interface
- Test cases and compliance verification

---

## Conclusion

Constellation Hub provides well-defined interfaces for integration with ground networks, service providers, and mission systems. By using standard protocols (REST, OAuth, WebSockets) and open formats (JSON), it minimizes integration complexity and maximizes interoperability.
