#!/usr/bin/env python3
"""
Demo Data Seed Script for Constellation Hub

This script loads demo data including:
- Sample constellation with satellites
- Ground stations in multiple regions
- Demo users with different roles
- Sample schedules and passes

⚠️ FOR DEMONSTRATION USE ONLY
Do not use in production environments.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://constellation:constellation@localhost:5432/constellation_hub"
)

# Sample TLE data (ISS and Starlink samples)
DEMO_TLES = [
    {
        "name": "ISS (ZARYA)",
        "norad_id": "25544",
        "tle1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9021",
        "tle2": "2 25544  51.6400 208.9163 0006703 280.7808  79.2154 15.49815776    29",
    },
    {
        "name": "STARLINK-1007",
        "norad_id": "44713",
        "tle1": "1 44713U 19074A   24001.50000000  .00001234  00000-0  98765-4 0  9012",
        "tle2": "2 44713  53.0000 120.0000 0001500 100.0000 260.0000 15.06000000123456",
    },
    {
        "name": "STARLINK-1008",
        "norad_id": "44714",
        "tle1": "1 44714U 19074B   24001.50000000  .00001234  00000-0  98765-4 0  9013",
        "tle2": "2 44714  53.0000 121.0000 0001500 101.0000 259.0000 15.06000000123457",
    },
    {
        "name": "STARLINK-1009",
        "norad_id": "44715",
        "tle1": "1 44715U 19074C   24001.50000000  .00001234  00000-0  98765-4 0  9014",
        "tle2": "2 44715  53.0000 122.0000 0001500 102.0000 258.0000 15.06000000123458",
    },
    {
        "name": "STARLINK-1010",
        "norad_id": "44716",
        "tle1": "1 44716U 19074D   24001.50000000  .00001234  00000-0  98765-4 0  9015",
        "tle2": "2 44716  53.0000 123.0000 0001500 103.0000 257.0000 15.06000000123459",
    },
    {
        "name": "STARLINK-1011",
        "norad_id": "44717",
        "tle1": "1 44717U 19074E   24001.50000000  .00001234  00000-0  98765-4 0  9016",
        "tle2": "2 44717  53.0000 124.0000 0001500 104.0000 256.0000 15.06000000123460",
    },
]

GROUND_STATIONS = [
    {
        "name": "AWS Ground Station - US West",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "elevation_m": 50,
        "min_elevation_deg": 10.0,
    },
    {
        "name": "ESA Ground Station - Europe",
        "latitude": 52.2985,
        "longitude": 5.1719,
        "elevation_m": 100,
        "min_elevation_deg": 10.0,
    },
    {
        "name": "JAXA Ground Station - Asia",
        "latitude": 35.6762,
        "longitude": 139.6503,
        "elevation_m": 20,
        "min_elevation_deg": 10.0,
    },
]

DEMO_USERS = [
    {
        "username": "demo_viewer",
        "email": "viewer@demo.constellation-hub.local",
        "password": "viewer123",
        "full_name": "Demo Viewer",
        "role": "viewer",
    },
    {
        "username": "demo_ops",
        "email": "ops@demo.constellation-hub.local",
        "password": "operator123",
        "full_name": "Demo Operator",
        "role": "operator",
    },
    {
        "username": "demo_admin",
        "email": "admin@demo.constellation-hub.local",
        "password": "admin123",
        "full_name": "Demo Administrator",
        "role": "admin",
    },
]


async def create_demo_data():
    """Create demo data using raw SQL to avoid import issues."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text
    
    # Add backend/common to path for imports
    backend_path = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_path / "common"))
    
    try:
        from auth import hash_password
    except ImportError:
        # Fallback password hashing
        import hashlib
        def hash_password(password):
            return hashlib.sha256(password.encode()).hexdigest()
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("=" * 60)
        print("🚀 Constellation Hub - Demo Data Loader")
        print("=" * 60)
        print()
        print("⚠️  WARNING: This script is for DEMONSTRATION purposes only!")
        print("   Do not use demo users or data in production environments.")
        print()
        
        # Create constellation
        print("📡 Creating demo constellation...")
        result = await session.execute(text("""
            INSERT INTO constellations (name, description, orbit_regime, altitude_km, inclination_deg, num_planes, sats_per_plane)
            VALUES (:name, :description, :orbit_regime, :altitude_km, :inclination_deg, :num_planes, :sats_per_plane)
            RETURNING id
        """), {
            "name": "Demo LEO Constellation",
            "description": "Demonstration constellation for Constellation Hub showcase",
            "orbit_regime": "LEO",
            "altitude_km": 550.0,
            "inclination_deg": 53.0,
            "num_planes": 1,
            "sats_per_plane": len(DEMO_TLES)
        })
        constellation_id = result.scalar_one()
        print(f"   ✅ Created constellation (ID: {constellation_id})")
        
        # Create satellites
        for tle_data in DEMO_TLES:
            await session.execute(text("""
                INSERT INTO satellites (constellation_id, name, norad_id, tle_line1, tle_line2, mass_kg, power_watts, orbit_type, status)
                VALUES (:constellation_id, :name, :norad_id, :tle1, :tle2, :mass_kg, :power_watts, :orbit_type, :status)
            """), {
                "constellation_id": constellation_id,
                "name": tle_data["name"],
                "norad_id": tle_data["norad_id"],
                "tle1": tle_data["tle1"],
                "tle2": tle_data["tle2"],
                "mass_kg": 260.0 if "STARLINK" in tle_data["name"] else 420000.0,
                "power_watts": 1500.0 if "STARLINK" in tle_data["name"] else 84000.0,
                "orbit_type": "LEO",
                "status": "operational"
            })
        print(f"   ✅ Created {len(DEMO_TLES)} satellites")
        
        # Create ground stations
        print("🌍 Creating ground stations...")
        for gs_data in GROUND_STATIONS:
            await session.execute(text("""
                INSERT INTO ground_stations (name, latitude, longitude, elevation_m, min_elevation_deg, status)
                VALUES (:name, :latitude, :longitude, :elevation_m, :min_elevation_deg, :status)
            """), {
                **gs_data,
                "status": "operational"
            })
        print(f"   ✅ Created {len(GROUND_STATIONS)} ground stations")
        
        # Create demo users
        print("👥 Creating demo users...")
        for user_data in DEMO_USERS:
            # Check if user exists
            result = await session.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": user_data["username"]}
            )
            if result.scalar_one_or_none():
                print(f"   ⚠️  User '{user_data['username']}' already exists, skipping")
                continue
            
            await session.execute(text("""
                INSERT INTO users (username, email, hashed_password, full_name, role, is_active)
                VALUES (:username, :email, :hashed_password, :full_name, :role, :is_active)
            """), {
                "username": user_data["username"],
                "email": user_data["email"],
                "hashed_password": hash_password(user_data["password"]),
                "full_name": user_data["full_name"],
                "role": user_data["role"],
                "is_active": True
            })
            print(f"   ✅ Created user '{user_data['username']}' (role: {user_data['role']})")
        
        await session.commit()
        
        print()
        print("=" * 60)
        print("✅ Demo data loaded successfully!")
        print("=" * 60)
        print()
        print("Demo Users Created:")
        print("-" * 60)
        for user in DEMO_USERS:
            print(f"  Username: {user['username']:<15} Password: {user['password']:<15} Role: {user['role']}")
        print()
        print("Next Steps:")
        print("  1. Visit http://localhost:3000")
        print("  2. Log in with one of the demo users above")
        print("  3. Explore the constellation, ground stations, and TLE data")
        print()


async def main():
    """Main entry point."""
    try:
        await create_demo_data()
    except Exception as e:
        print(f"❌ Error loading demo data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
