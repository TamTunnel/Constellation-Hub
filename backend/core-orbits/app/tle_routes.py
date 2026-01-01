"""
TLE Feed Management Routes.

Provides endpoints for TLE ingestion status and manual refresh.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from pydantic import BaseModel

from .db import get_db
from .services.tle_ingestion import (
    TLEIngestionService, 
    TLESource, 
    TLERecord, 
    CelesTrakCatalog,
    fetch_sample_satellites
)

# Try to import auth (optional)
try:
    from common.auth import require_auth, require_role, Role, TokenData
except ImportError:
    # Fallback for testing without auth
    def require_auth():
        pass
    def require_role(role):
        return require_auth
    class Role:
        OPERATOR = "operator"
        VIEWER = "viewer"
    class TokenData:
        pass


router = APIRouter(prefix="/tle", tags=["TLE Feeds"])

# Global service instance for status tracking
_tle_service = TLEIngestionService()


# ============ Schemas ============

class TLEStatusResponse(BaseModel):
    """TLE ingestion status."""
    last_refresh: Optional[str] = None
    satellite_count: int = 0
    refresh_interval_hours: int
    sources: dict


class TLESatelliteResponse(BaseModel):
    """TLE satellite record."""
    norad_id: str
    name: str
    tle_line1: str
    tle_line2: str
    source: str
    epoch: Optional[str] = None
    fetched_at: Optional[str] = None


class TLERefreshRequest(BaseModel):
    """Request to refresh TLE data."""
    catalogs: Optional[List[str]] = None  # List of catalog names
    force: bool = False  # Force refresh even if recent


class TLERefreshResponse(BaseModel):
    """Response from TLE refresh."""
    status: str
    satellites_fetched: int
    satellites_stored: int
    message: str


# ============ Database Model ============

# TLE records are stored in the tle_records table
# (schema defined in migrations)

try:
    from sqlalchemy import Column, Integer, String, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from .db import Base
    
    class TLERecordORM(Base):
        __tablename__ = "tle_records"
        
        id = Column(Integer, primary_key=True, index=True)
        norad_id = Column(String(50), nullable=False, index=True)
        name = Column(String(255), nullable=True)
        tle_line1 = Column(String(70), nullable=False)
        tle_line2 = Column(String(70), nullable=False)
        source = Column(String(50), nullable=False, default="celestrak")
        epoch = Column(DateTime(timezone=True), nullable=True)
        fetched_at = Column(DateTime(timezone=True), nullable=False)
except Exception:
    TLERecordORM = None


# ============ Routes ============

@router.get("/status", response_model=TLEStatusResponse)
async def get_tle_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Get TLE ingestion status.
    
    Returns:
    - Last refresh timestamp
    - Number of satellites in database
    - Refresh interval configuration
    - Source availability
    """
    # Get count from database
    count = 0
    last_fetched = None
    
    if TLERecordORM is not None:
        try:
            result = await db.execute(select(func.count(TLERecordORM.id)))
            count = result.scalar() or 0
            
            # Get most recent fetch time
            result = await db.execute(
                select(TLERecordORM.fetched_at)
                .order_by(TLERecordORM.fetched_at.desc())
                .limit(1)
            )
            row = result.scalar_one_or_none()
            if row:
                last_fetched = row.isoformat()
        except Exception:
            pass
    
    status = _tle_service.get_status()
    
    return TLEStatusResponse(
        last_refresh=last_fetched or status.get("last_refresh"),
        satellite_count=count,
        refresh_interval_hours=status.get("refresh_interval_hours", 6),
        sources=status.get("sources", {})
    )


@router.get("/satellites", response_model=List[TLESatelliteResponse])
async def list_tle_satellites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List satellites with TLE data.
    
    Args:
        skip: Pagination offset
        limit: Maximum records to return
        source: Filter by source (celestrak, spacetrack)
    """
    if TLERecordORM is None:
        raise HTTPException(
            status_code=500,
            detail="TLE records table not configured"
        )
    
    query = select(TLERecordORM).offset(skip).limit(limit)
    
    if source:
        query = query.where(TLERecordORM.source == source)
    
    query = query.order_by(TLERecordORM.name)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    return [
        TLESatelliteResponse(
            norad_id=r.norad_id,
            name=r.name or "",
            tle_line1=r.tle_line1,
            tle_line2=r.tle_line2,
            source=r.source,
            epoch=r.epoch.isoformat() if r.epoch else None,
            fetched_at=r.fetched_at.isoformat() if r.fetched_at else None
        )
        for r in records
    ]


@router.post("/refresh", response_model=TLERefreshResponse)
async def refresh_tle_data(
    request: TLERefreshRequest = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    # user: TokenData = Depends(require_role(Role.OPERATOR))  # Enable when auth is active
):
    """
    Trigger TLE data refresh from external sources.
    
    Requires: Operator role or higher.
    
    Args:
        request.catalogs: Optional list of catalogs to refresh
        request.force: Force refresh even if data is recent
    """
    if request is None:
        request = TLERefreshRequest()
    
    # Determine which catalogs to fetch
    if request.catalogs:
        catalogs = [CelesTrakCatalog(c) for c in request.catalogs if c in [e.value for e in CelesTrakCatalog]]
    else:
        catalogs = [CelesTrakCatalog.ACTIVE]  # Default to active satellites
    
    # Fetch TLE data
    async with TLEIngestionService() as service:
        try:
            all_records = await service.fetch_multiple_catalogs(catalogs)
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch TLE data: {str(e)}"
            )
    
    # Store in database
    stored_count = 0
    if TLERecordORM is not None and all_records:
        try:
            # Clear existing records for refreshed catalogs
            # (In production, you might want to keep history)
            for record in all_records:
                # Check if exists
                existing = await db.execute(
                    select(TLERecordORM).where(TLERecordORM.norad_id == record.norad_id)
                )
                existing_record = existing.scalar_one_or_none()
                
                if existing_record:
                    # Update existing
                    existing_record.name = record.name
                    existing_record.tle_line1 = record.tle_line1
                    existing_record.tle_line2 = record.tle_line2
                    existing_record.source = record.source.value
                    existing_record.epoch = record.epoch
                    existing_record.fetched_at = record.fetched_at
                else:
                    # Insert new
                    db_record = TLERecordORM(
                        norad_id=record.norad_id,
                        name=record.name,
                        tle_line1=record.tle_line1,
                        tle_line2=record.tle_line2,
                        source=record.source.value,
                        epoch=record.epoch,
                        fetched_at=record.fetched_at
                    )
                    db.add(db_record)
                
                stored_count += 1
            
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store TLE data: {str(e)}"
            )
    
    # Update service status
    _tle_service.last_refresh = datetime.now(timezone.utc)
    _tle_service.last_count = stored_count
    
    return TLERefreshResponse(
        status="success",
        satellites_fetched=len(all_records),
        satellites_stored=stored_count,
        message=f"Refreshed TLE data from {len(catalogs)} catalog(s)"
    )


@router.get("/catalogs")
async def list_catalogs():
    """
    List available TLE catalogs.
    
    Returns catalog names that can be used with the refresh endpoint.
    """
    return {
        "catalogs": [
            {"name": c.value, "description": c.name.replace("_", " ").title()}
            for c in CelesTrakCatalog
        ]
    }


@router.get("/satellites/{norad_id}", response_model=TLESatelliteResponse)
async def get_satellite_tle(
    norad_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get TLE data for a specific satellite by NORAD ID.
    """
    if TLERecordORM is None:
        raise HTTPException(
            status_code=500,
            detail="TLE records table not configured"
        )
    
    result = await db.execute(
        select(TLERecordORM).where(TLERecordORM.norad_id == norad_id)
    )
    record = result.scalar_one_or_none()
    
    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"TLE not found for NORAD ID {norad_id}"
        )
    
    return TLESatelliteResponse(
        norad_id=record.norad_id,
        name=record.name or "",
        tle_line1=record.tle_line1,
        tle_line2=record.tle_line2,
        source=record.source,
        epoch=record.epoch.isoformat() if record.epoch else None,
        fetched_at=record.fetched_at.isoformat() if record.fetched_at else None
    )
