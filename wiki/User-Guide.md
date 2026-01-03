# User Guide

This guide walks through common operational scenarios in Constellation Hub.

## Core Concepts

- **Constellation**: A group of satellites working together.
- **Satellite**: An orbiting vehicle defined by TLE parameters.
- **Ground Station**: A terrestrial facility for uplink/downlink.
- **Pass**: A time window when a satellite is visible to a ground station.
- **Schedule**: An optimized plan of passes assigned for communication.

## Operational Scenarios

### 1. Planning Passes

**Goal**: Generate a contact schedule for a constellation.

1. Navigate to **Scheduling**.
2. Select your constellation (e.g., "Demo LEO Constellation").
3. Click **"Compute Passes"** to calculate visibility windows for the next 24 hours.
4. Click **"Generate Schedule"** to auto-assign passes to ground stations.
5. Review the timeline and ground tracks on the map.

### 2. Using AI Optimization

**Goal**: Resolve conflicts and prioritize high-value data.

1. In the Scheduling view, open the **AI Assistant** panel.
2. Select **"Optimize Schedule"**.
3. Choose your optimization goal (e.g., "Maximize Data Throughput" or "Minimize Latency").
4. The AI will propose a modified schedule. Review the changes (highlighted in diff view).
5. Click **"Apply"** to finalize (Requires Operator role).

### 3. Incident Analysis (Ops Co-Pilot)

**Goal**: Understand why a pass failed or a satellite is anomalous.

1. Navigate to **Ops Co-Pilot**.
2. Feed in the recent event logs or select a time range.
3. Ask: _"Why did we miss the pass with GS-Europe at 14:00?"_
4. The AI analyzes geometric constraints, ground station status, and system logs to provide a root cause analysis.

### 4. Managing TLEs

**Goal**: Ensure orbital data is up to date.

1. Navigate to **TLE Admin** (Admin/Operator only).
2. Check the "Last Updated" timestamp.
3. If data is stale (>24 hours), click **"Refresh TLEs"**.
4. The system fetches fresh data from CelesTrak and re-propagates orbits.

## Visualizing the Fleet

The **Dashboard** (`/`) provides a real-time 3D view:

- **Green Orbit Lines**: active operational satellites.
- **Cones/Circles**: Ground station coverage masks.
- **Time Slider**: Scrub forward/backward to see future/past positions.
- **Click**: Select any object to view detailed telemetry and state.
