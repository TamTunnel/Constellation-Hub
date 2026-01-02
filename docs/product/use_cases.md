# Use Cases

## Demo Scenario

**Goal**: See Constellation Hub in action in 2 minutes without manual setup.

When you run `make demo`, you get a fully populated system with:

- **6 Demo Satellites**: ISS + 5 Starlink satellites with realistic TLEs
- **3 Ground Stations**: Located in US (San Francisco), Europe (Netherlands), and Asia (Tokyo)
- **Pre-computed Data**: Sample passes, schedules, and data queues already loaded
- **3 Demo Users**: One for each role (viewer, operator, admin)

**What You Can Explore**:

1. **3D Globe View** (`/`)
   - See all 6 satellites visualized on the Earth
   - View ground station locations with coverage circles
   - Watch satellite positions update in real-time

2. **Satellite List** (`/satellites`)
   - Browse the demo constellation
   - View orbital parameters and TLE data
   - Check satellite status and metrics

3. **Ground Stations** (`/ground-stations`)
   - See all three stations and their capabilities
   - View antenna configurations
   - Check operational status

4. **Pass Scheduling** (`/scheduling`)
   - View pre-computed passes for the next 24 hours
   - See when each satellite will be visible from each station
   - Explore schedule optimization options

5. **TLE Admin** (`/tle-admin`)
   - Check TLE ingestion status
   - View the 6 satellites in the TLE database
   - Trigger manual TLE refresh (operator+ role required)

**Try Different Roles**:
- Log in as `demo_viewer` to see read-only access
- Log in as `demo_ops` to test operator capabilities (schedule management, TLE refresh)
- Log in as `demo_admin` to explore full system access

This demo provides a realistic, interactive showcase without requiring any satellite operations expertise or manual data entry.

---

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
