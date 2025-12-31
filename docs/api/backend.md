# Backend API Reference

## Core Orbits Service (Port 8001)

### Constellations

#### List Constellations
```http
GET /constellations
```

Response:
```json
{
  "data": [
    {
      "id": 1,
      "name": "LEO-NET",
      "description": "Low Earth Orbit Network",
      "satellite_count": 24
    }
  ],
  "total": 1
}
```

#### Get Constellation Satellites
```http
GET /constellations/{id}/satellites
```

### Satellites

#### List Satellites
```http
GET /satellites?constellation_id=1
```

#### Create Satellite
```http
POST /satellites
Content-Type: application/json

{
  "name": "SAT-001",
  "norad_id": "25544",
  "constellation_id": 1,
  "tle_data": {
    "line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9025",
    "line2": "2 25544  51.6400 208.9163 0006703 280.7808  79.2154 15.49815776 20000"
  }
}
```

#### Get Satellite Position
```http
GET /satellites/{id}/position?time=2024-01-15T12:00:00Z
```

Response:
```json
{
  "satellite_id": 1,
  "satellite_name": "SAT-001",
  "timestamp": "2024-01-15T12:00:00Z",
  "latitude": 45.234,
  "longitude": -122.456,
  "altitude_km": 550.5,
  "velocity": {
    "vx": -1.234,
    "vy": 5.678,
    "vz": 3.456,
    "speed_kms": 7.66
  }
}
```

## Ground Scheduler Service (Port 8003)

### Ground Stations

#### Create Ground Station
```http
POST /ground-stations
Content-Type: application/json

{
  "name": "GS-Alpha",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "elevation_m": 10,
  "min_elevation_deg": 10,
  "capabilities": ["S-band", "X-band"],
  "cost_per_minute": 1.5
}
```

### Passes

#### Compute Passes
```http
POST /passes/compute
Content-Type: application/json

{
  "satellite_ids": [1, 2, 3],
  "station_ids": [1, 2],
  "start_time": "2024-01-15T00:00:00Z",
  "end_time": "2024-01-16T00:00:00Z"
}
```

### Schedules

#### Generate Schedule
```http
POST /schedule/generate
Content-Type: application/json

{
  "name": "Daily Schedule",
  "start_time": "2024-01-15T00:00:00Z",
  "end_time": "2024-01-16T00:00:00Z",
  "prefer_high_elevation": true
}
```

## AI Agents Service (Port 8004)

### Pass Scheduler

#### Optimize Schedule
```http
POST /ai/pass-scheduler/optimize
Content-Type: application/json

{
  "passes": [...],
  "data_queues": [...],
  "stations": [...],
  "constraints": {
    "max_passes_per_satellite": 10
  }
}
```

### Ops Co-Pilot

#### Analyze Events
```http
POST /ai/ops-copilot/analyze
Content-Type: application/json

{
  "events": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "event_type": "missed_pass",
      "severity": "warning",
      "source": "ground_scheduler",
      "message": "Pass SAT-012 to GS-Beta missed",
      "satellite_id": 12,
      "station_id": 2
    }
  ]
}
```

Response:
```json
{
  "summary": "Analysis of 1 event...",
  "key_findings": ["..."],
  "suggested_actions": [
    {
      "id": "uuid",
      "action": "Schedule diagnostic check for GS-Beta",
      "priority": "high",
      "rationale": "Multiple missed passes detected"
    }
  ],
  "confidence": 0.85
}
```
