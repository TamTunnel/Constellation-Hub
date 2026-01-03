"""
Demo Routes.

Provides endpoints for demo setup and management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from common.config import get_settings
from .services.demo import seed_demo_data

router = APIRouter(prefix="/demo", tags=["Demo"])

@router.post("/seed", status_code=201)
async def seed_demo(
    db: AsyncSession = Depends(get_db),
    settings = Depends(get_settings)
):
    """
    Seed the database with demo data.
    
    Only available if DEMO_MODE is enabled.
    """
    if not settings.demo_mode:
        raise HTTPException(status_code=403, detail="Demo mode is disabled")
        
    try:
        result = await seed_demo_data(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
