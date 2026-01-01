# Observability Guide

This document describes the observability infrastructure for Constellation Hub.

## Overview

Constellation Hub implements a comprehensive observability stack:

- **Structured Logging** - JSON-formatted logs with request tracing
- **Prometheus Metrics** - HTTP request metrics and custom business metrics
- **Health Probes** - Kubernetes-compatible liveness and readiness checks

---

## Structured Logging

### Log Format

All services output structured JSON logs with consistent fields:

```json
{
  "timestamp": "2026-01-01T12:00:00.000000+00:00",
  "level": "INFO",
  "service": "core-orbits",
  "message": "Computed visibility window for satellite 12345",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "logger": "constellation.core-orbits"
}
```

### Log Fields

| Field | Description |
|-------|-------------|
| `timestamp` | ISO8601 timestamp in UTC |
| `level` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `service` | Service name (core-orbits, routing, ground-scheduler, ai-agents) |
| `message` | Human-readable log message |
| `request_id` | Unique ID for request tracing across services |
| `logger` | Python logger name |
| `exception` | Stack trace (only present on errors) |
| `extra_fields` | Additional context fields |

### Request ID Tracing

Every HTTP request is assigned a unique request ID:

1. If the client sends `X-Request-ID` header, that value is used
2. Otherwise, a UUID is generated
3. The request ID is included in all log messages during that request
4. The response includes the `X-Request-ID` header

This enables end-to-end tracing across services.

### Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `LOG_LEVEL` | INFO | Minimum log level |
| `LOG_FORMAT` | json | Log format: `json` or `text` |

For local development, use `LOG_FORMAT=text` for human-readable output.

### Integration with Log Aggregators

#### AWS CloudWatch

```yaml
# docker-compose override for CloudWatch
services:
  core-orbits:
    logging:
      driver: awslogs
      options:
        awslogs-region: us-east-1
        awslogs-group: constellation-hub
        awslogs-stream: core-orbits
```

#### Elastic/Logstash

JSON logs can be ingested directly by Logstash:

```yaml
input {
  file {
    path => "/var/log/constellation/*.log"
    codec => json
  }
}
```

---

## Prometheus Metrics

### Endpoints

Each service exposes metrics at `GET /metrics`:

- core-orbits: http://localhost:8001/metrics
- routing: http://localhost:8002/metrics
- ground-scheduler: http://localhost:8003/metrics
- ai-agents: http://localhost:8004/metrics

### Standard Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | service, method, endpoint, status_code | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | service, method, endpoint | Request latency |
| `errors_total` | Counter | service, error_type | Total errors |

### Custom Business Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `satellites_tracked_total` | Counter | constellation | Satellites being tracked |
| `passes_computed_total` | Counter | service | Visibility passes computed |
| `schedules_generated_total` | Counter | service, optimizer | Schedules generated |

### Prometheus Configuration

Create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'constellation-hub'
    static_configs:
      - targets:
        - 'core-orbits:8001'
        - 'routing:8002'
        - 'ground-scheduler:8003'
        - 'ai-agents:8004'
```

### Grafana Dashboard

A sample Grafana dashboard is available at `infra/grafana/dashboards/constellation.json`.

Key panels:
- Request rate by service
- Error rate
- P50/P95/P99 latency
- Active satellites
- Schedule generation rate

---

## Health Probes

### Endpoints

Each service exposes health check endpoints:

| Endpoint | Purpose | Auth Required |
|----------|---------|---------------|
| `/healthz` | Liveness probe | No |
| `/readyz` | Readiness probe | No |
| `/health` | Legacy (deprecated) | No |

### Liveness Probe (`/healthz`)

Returns 200 if the service process is running.

```json
{
  "status": "ok",
  "timestamp": "2026-01-01T12:00:00.000000+00:00"
}
```

Use for Kubernetes liveness probes - if this fails, the pod should be restarted.

### Readiness Probe (`/readyz`)

Returns 200 if the service can handle requests (database connected, dependencies ready).

```json
{
  "status": "ready",
  "timestamp": "2026-01-01T12:00:00.000000+00:00",
  "checks": {
    "database": "connected"
  }
}
```

Returns 503 if not ready:

```json
{
  "status": "not_ready",
  "timestamp": "2026-01-01T12:00:00.000000+00:00",
  "checks": {
    "database": "error: connection refused"
  }
}
```

### Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: core-orbits
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /readyz
              port: 8001
            initialDelaySeconds: 5
            periodSeconds: 5
```

---

## Docker Compose Setup

To enable full observability stack locally:

```yaml
# docker-compose.observability.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:
```

Run with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.observability.yml up -d
```

---

## Alerting

### Prometheus Alerting Rules

```yaml
groups:
  - name: constellation-hub
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in {{ $labels.service }}"

      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
```

---

## Troubleshooting

### No metrics appearing

1. Check `METRICS_ENABLED=true` in environment
2. Verify `/metrics` endpoint is accessible
3. Check Prometheus target status at http://localhost:9090/targets

### Logs not in JSON format

1. Verify `LOG_FORMAT=json` in environment
2. Check the `common.logger` module is being imported correctly

### Request IDs not appearing

1. Ensure the request ID middleware is registered in `main.py`
2. Check that `set_request_id()` is being called
