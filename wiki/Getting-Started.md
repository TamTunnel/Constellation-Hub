# Getting Started

This guide will help you get Constellation Hub up and running in minutes.

## Prerequisites

- **Docker** and **Docker Compose** (v2.0+)
- **Git**
- **Make** (optional, for convenience commands)

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/TamTunnel/Constellation-Hub.git
   cd Constellation-Hub
   ```

2. **Start Services**:

   ```bash
   docker compose up -d
   ```

   This will start:
   - Frontend (localhost:3000)
   - Core Services (API ports 8001-8004)
   - PostgreSQL Database
   - Prometheus & Grafana (if enabled)

## Quick Demo

The fastest way to explore Constellation Hub is using the **Demo Mode**.

### Option 1: CLI Setup

Run the following command to seed the database with realistic sample data:

```bash
make demo
```

This script:

1. Runs database migrations
2. Creates a "Demo LEO Constellation"
3. Adds 6 satellites (ISS + 5 Starlink)
4. Adds 3 ground stations (US, Europe, Asia)
5. Generates sample passes and schedules
6. Creates demo user accounts

### Option 2: GUI Setup

1. Navigate to http://localhost:3000/login
2. Click **"Initialize Demo Data"** below the login form
3. Wait for the success message

## Accessing the Dashboard

Once setup is complete:

1. Open http://localhost:3000
2. Login with one of the demo accounts:

| Role         | Username      | Password      | Access Level          |
| ------------ | ------------- | ------------- | --------------------- |
| **Viewer**   | `demo_viewer` | `viewer123`   | Read-only             |
| **Operator** | `demo_ops`    | `operator123` | Can schedule & manage |
| **Admin**    | `demo_admin`  | `admin123`    | Full system access    |

> [!TIP]
> Use the **Quick Login** buttons on the login page to instantly switch between roles.

## Troubleshooting

- **Database Connection Error**: Ensure the postgres container is healthy (`docker compose ps`).
- **Map Not Loading**: Check if you have internet access (CesiumJS requires access to Bing Maps/OSM servers by default).
- **Login Failed**: Verify you ran `make demo` or clicked "Initialize Demo Data".
