#!/usr/bin/env python3
"""
Demo Data Seed Script via Service

Wrapper around the core demo service logic.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(backend_path / "core-orbits"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

try:
    from app.services.demo import seed_demo_data
except ImportError:
    # Try alternate import if running from different context
    sys.path.append(str(backend_path / "core-orbits"))
    from app.services.demo import seed_demo_data

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://constellation:constellation@localhost:5432/constellation_hub"
)

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            await seed_demo_data(session)
            await session.commit()
            print("✅ GUI-ready demo data loaded successfully!")
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
