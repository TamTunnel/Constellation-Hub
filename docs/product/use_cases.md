# Use Cases

## Use Case 1: Plan Passes for an IoT Constellation

**Scenario**: You operate a 20-satellite IoT constellation and need to plan downlink passes for the next 24 hours.

**Steps**:

1. **Add satellites** with TLE data via the API or UI
2. **Register ground stations** with their locations and capabilities
3. **Compute passes** for all satellite-station pairs
4. **Generate baseline schedule** using the Ground Scheduler
5. **Optimize with AI** to maximize data throughput

**API Flow**:
```
POST /satellites (x20)
POST /ground-stations (x3)
POST /passes/compute
POST /schedule/generate
POST /ai/pass-scheduler/optimize
```

## Use Case 2: Analyze a Missed-Pass Incident

**Scenario**: Three consecutive passes with GS-Beta were missed. You want to understand why and what to do.

**Steps**:

1. **Collect events** from the system logs
2. **Send to Ops Co-Pilot** for analysis
3. **Review summary** and suggested actions
4. **Apply or dismiss** recommendations

**API Flow**:
```
POST /ai/ops-copilot/analyze
{
  "events": [
    {"event_type": "missed_pass", "station_id": 2, ...},
    {"event_type": "missed_pass", "station_id": 2, ...},
    {"event_type": "link_failure", "station_id": 2, ...}
  ]
}
```

**Expected Output**:
- Summary identifying the pattern
- Suggestion to check GS-Beta equipment
- Option to reschedule to alternate stations

## Use Case 3: Optimal Routing for a Data Transfer

**Scenario**: You need to route a high-priority data packet from SAT-005 to your data center in Tokyo.

**Steps**:

1. **Query available links** between satellites and ground stations
2. **Request route computation** with latency constraints
3. **Visualize route** on the 3D globe
4. **Execute transfer** using the computed path

**API Flow**:
```
POST /routing/paths
{
  "origin_type": "satellite",
  "origin_id": 5,
  "destination_type": "ground_station",
  "destination_id": 3,
  "priority": "high",
  "max_latency_ms": 200
}
```
