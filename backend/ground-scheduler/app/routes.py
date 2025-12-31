"""
API routes for Ground Scheduler service.
"""
from datetime import datetime, timezone
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .db import get_db
from .models import GroundStationORM, PassORM, ScheduleORM, DataQueueORM
from .schemas import (
    GroundStationCreate, GroundStationResponse, GroundStationList,
    PassResponse, PassList, PassComputeRequest, PassComputeResponse,
    ScheduleCreate, ScheduleResponse, ScheduleGenerateRequest,
    DataQueueUpdate, DataQueueResponse
)
from .services.visibility import VisibilityCalculator
from .services.scheduler import BaselineScheduler

router = APIRouter()


# ============ Ground Station Endpoints ============

@router.get("/ground-stations", response_model=GroundStationList)
async def list_ground_stations(
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List all ground stations."""
    query = select(GroundStationORM)
    if is_active is not None:
        query = query.where(GroundStationORM.is_active == is_active)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    stations = result.scalars().all()
    
    return GroundStationList(
        data=[_station_to_response(s) for s in stations],
        total=len(stations)
    )


@router.post("/ground-stations", response_model=GroundStationResponse, status_code=201)
async def create_ground_station(
    station: GroundStationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ground station."""
    db_station = GroundStationORM(
        name=station.name,
        latitude=station.latitude,
        longitude=station.longitude,
        elevation_m=station.elevation_m,
        min_elevation_deg=station.min_elevation_deg,
        capabilities=station.capabilities,
        cost_per_minute=station.cost_per_minute,
        metadata_=station.metadata
    )
    db.add(db_station)
    await db.commit()
    await db.refresh(db_station)
    
    return _station_to_response(db_station)


@router.get("/ground-stations/{station_id}", response_model=GroundStationResponse)
async def get_ground_station(station_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific ground station."""
    station = await db.get(GroundStationORM, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Ground station not found")
    return _station_to_response(station)


@router.delete("/ground-stations/{station_id}", status_code=204)
async def delete_ground_station(station_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a ground station."""
    station = await db.get(GroundStationORM, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Ground station not found")
    await db.delete(station)
    await db.commit()


# ============ Pass Endpoints ============

@router.get("/passes", response_model=PassList)
async def list_passes(
    satellite_id: Optional[int] = None,
    station_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    is_scheduled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List passes with optional filtering."""
    query = select(PassORM)
    
    conditions = []
    if satellite_id:
        conditions.append(PassORM.satellite_id == satellite_id)
    if station_id:
        conditions.append(PassORM.station_id == station_id)
    if start_time:
        conditions.append(PassORM.aos >= start_time)
    if end_time:
        conditions.append(PassORM.los <= end_time)
    if is_scheduled is not None:
        conditions.append(PassORM.is_scheduled == is_scheduled)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(PassORM.aos).offset(skip).limit(limit)
    result = await db.execute(query)
    passes = result.scalars().all()
    
    # Get station names
    station_names = {}
    station_ids = {p.station_id for p in passes}
    if station_ids:
        stations_result = await db.execute(
            select(GroundStationORM).where(GroundStationORM.id.in_(station_ids))
        )
        for station in stations_result.scalars().all():
            station_names[station.id] = station.name
    
    return PassList(
        data=[_pass_to_response(p, station_names.get(p.station_id)) for p in passes],
        total=len(passes)
    )


@router.post("/passes/compute", response_model=PassComputeResponse)
async def compute_passes(
    request: PassComputeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compute visibility passes for satellite-station pairs.
    
    This is a simplified computation. In production, this would
    query the core-orbits service for TLE data.
    """
    start_time_ms = time.time() * 1000
    
    # Get stations
    if request.station_ids:
        stations_result = await db.execute(
            select(GroundStationORM).where(
                and_(
                    GroundStationORM.id.in_(request.station_ids),
                    GroundStationORM.is_active == True
                )
            )
        )
    else:
        stations_result = await db.execute(
            select(GroundStationORM).where(GroundStationORM.is_active == True)
        )
    stations = stations_result.scalars().all()
    
    if not stations:
        raise HTTPException(status_code=400, detail="No active ground stations found")
    
    # Compute passes for each satellite-station pair
    visibility_calc = VisibilityCalculator()
    passes_created = 0
    
    for sat_id in request.satellite_ids:
        for station in stations:
            min_elev = request.min_elevation_deg or station.min_elevation_deg
            
            # Generate simulated passes (in production, would use actual TLE data)
            computed_passes = visibility_calc.compute_passes_simplified(
                satellite_id=sat_id,
                station_lat=station.latitude,
                station_lon=station.longitude,
                start_time=request.start_time,
                end_time=request.end_time,
                min_elevation_deg=min_elev
            )
            
            for pass_data in computed_passes:
                db_pass = PassORM(
                    satellite_id=sat_id,
                    station_id=station.id,
                    aos=pass_data['aos'],
                    los=pass_data['los'],
                    max_elevation_time=pass_data.get('max_elevation_time'),
                    max_elevation_deg=pass_data['max_elevation_deg'],
                    duration_seconds=pass_data['duration_seconds']
                )
                db.add(db_pass)
                passes_created += 1
    
    await db.commit()
    
    computation_time_ms = time.time() * 1000 - start_time_ms
    time_range_hours = (request.end_time - request.start_time).total_seconds() / 3600
    
    return PassComputeResponse(
        passes_computed=passes_created,
        satellites_processed=len(request.satellite_ids),
        stations_processed=len(stations),
        time_range_hours=time_range_hours,
        computation_time_ms=computation_time_ms
    )


# ============ Schedule Endpoints ============

@router.get("/schedules", response_model=List[ScheduleResponse])
async def list_schedules(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all schedules."""
    query = select(ScheduleORM)
    if is_active is not None:
        query = query.where(ScheduleORM.is_active == is_active)
    query = query.order_by(ScheduleORM.created_at.desc())
    
    result = await db.execute(query)
    schedules = result.scalars().all()
    
    return [_schedule_to_response(s) for s in schedules]


@router.get("/schedule", response_model=Optional[ScheduleResponse])
async def get_current_schedule(db: AsyncSession = Depends(get_db)):
    """Get the current active schedule."""
    result = await db.execute(
        select(ScheduleORM)
        .where(ScheduleORM.is_active == True)
        .order_by(ScheduleORM.created_at.desc())
        .limit(1)
    )
    schedule = result.scalar_one_or_none()
    
    if not schedule:
        return None
    
    return _schedule_to_response(schedule)


@router.post("/schedule/generate", response_model=ScheduleResponse)
async def generate_schedule(
    request: ScheduleGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a baseline downlink schedule.
    
    Uses a greedy heuristic to assign passes based on:
    - Satellite data priority
    - Pass quality (elevation)
    - Ground station cost
    """
    # Get available passes in time range
    query = select(PassORM).where(
        and_(
            PassORM.aos >= request.start_time,
            PassORM.los <= request.end_time,
            PassORM.is_scheduled == False
        )
    )
    
    if request.satellite_ids:
        query = query.where(PassORM.satellite_id.in_(request.satellite_ids))
    if request.station_ids:
        query = query.where(PassORM.station_id.in_(request.station_ids))
    
    query = query.order_by(PassORM.aos)
    result = await db.execute(query)
    available_passes = result.scalars().all()
    
    if not available_passes:
        raise HTTPException(status_code=400, detail="No available passes in time range")
    
    # Get data queues for prioritization
    sat_ids = {p.satellite_id for p in available_passes}
    queue_result = await db.execute(
        select(DataQueueORM).where(DataQueueORM.satellite_id.in_(sat_ids))
    )
    data_queues = {q.satellite_id: q for q in queue_result.scalars().all()}
    
    # Get station costs
    station_ids = {p.station_id for p in available_passes}
    station_result = await db.execute(
        select(GroundStationORM).where(GroundStationORM.id.in_(station_ids))
    )
    station_costs = {s.id: s.cost_per_minute for s in station_result.scalars().all()}
    
    # Generate baseline schedule
    scheduler = BaselineScheduler()
    scheduled_pass_ids = scheduler.generate_baseline(
        passes=[_pass_to_dict(p) for p in available_passes],
        data_queues={sid: _queue_to_dict(q) for sid, q in data_queues.items()},
        station_costs=station_costs,
        prefer_high_elevation=request.prefer_high_elevation,
        max_passes_per_satellite=request.max_passes_per_satellite
    )
    
    # Mark passes as scheduled
    for pass_obj in available_passes:
        if pass_obj.id in scheduled_pass_ids:
            pass_obj.is_scheduled = True
    
    # Calculate statistics
    total_minutes = sum(
        p.duration_seconds / 60 for p in available_passes if p.id in scheduled_pass_ids
    )
    
    # Create schedule
    db_schedule = ScheduleORM(
        name=request.name,
        start_time=request.start_time,
        end_time=request.end_time,
        scheduled_passes=list(scheduled_pass_ids),
        total_contact_minutes=total_minutes,
        is_optimized=False
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    
    return _schedule_to_response(db_schedule)


# ============ Data Queue Endpoints ============

@router.put("/data-queues", response_model=DataQueueResponse)
async def update_data_queue(
    queue: DataQueueUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update or create a satellite's data queue."""
    result = await db.execute(
        select(DataQueueORM).where(DataQueueORM.satellite_id == queue.satellite_id)
    )
    db_queue = result.scalar_one_or_none()
    
    if db_queue:
        db_queue.critical_volume_mb = queue.critical_volume_mb
        db_queue.high_volume_mb = queue.high_volume_mb
        db_queue.medium_volume_mb = queue.medium_volume_mb
        db_queue.low_volume_mb = queue.low_volume_mb
        db_queue.customer_allocations = queue.customer_allocations
    else:
        db_queue = DataQueueORM(
            satellite_id=queue.satellite_id,
            critical_volume_mb=queue.critical_volume_mb,
            high_volume_mb=queue.high_volume_mb,
            medium_volume_mb=queue.medium_volume_mb,
            low_volume_mb=queue.low_volume_mb,
            customer_allocations=queue.customer_allocations
        )
        db.add(db_queue)
    
    db_queue.total_volume_mb = (
        queue.critical_volume_mb + queue.high_volume_mb +
        queue.medium_volume_mb + queue.low_volume_mb
    )
    
    await db.commit()
    await db.refresh(db_queue)
    
    return DataQueueResponse(
        id=db_queue.id,
        satellite_id=db_queue.satellite_id,
        critical_volume_mb=db_queue.critical_volume_mb,
        high_volume_mb=db_queue.high_volume_mb,
        medium_volume_mb=db_queue.medium_volume_mb,
        low_volume_mb=db_queue.low_volume_mb,
        total_volume_mb=db_queue.total_volume_mb,
        customer_allocations=db_queue.customer_allocations or {},
        updated_at=db_queue.updated_at
    )


# ============ Helper Functions ============

def _station_to_response(station: GroundStationORM) -> GroundStationResponse:
    return GroundStationResponse(
        id=station.id,
        name=station.name,
        latitude=station.latitude,
        longitude=station.longitude,
        elevation_m=station.elevation_m,
        min_elevation_deg=station.min_elevation_deg,
        capabilities=station.capabilities or [],
        health_status=station.health_status,
        is_active=station.is_active,
        cost_per_minute=station.cost_per_minute,
        metadata=station.metadata_ or {},
        created_at=station.created_at,
        updated_at=station.updated_at
    )


def _pass_to_response(pass_obj: PassORM, station_name: Optional[str] = None) -> PassResponse:
    return PassResponse(
        id=pass_obj.id,
        satellite_id=pass_obj.satellite_id,
        station_id=pass_obj.station_id,
        station_name=station_name,
        aos=pass_obj.aos,
        los=pass_obj.los,
        max_elevation_time=pass_obj.max_elevation_time,
        max_elevation_deg=pass_obj.max_elevation_deg,
        duration_seconds=pass_obj.duration_seconds,
        is_scheduled=pass_obj.is_scheduled,
        priority=pass_obj.priority,
        metadata=pass_obj.metadata_ or {},
        created_at=pass_obj.created_at
    )


def _pass_to_dict(pass_obj: PassORM) -> dict:
    return {
        'id': pass_obj.id,
        'satellite_id': pass_obj.satellite_id,
        'station_id': pass_obj.station_id,
        'aos': pass_obj.aos,
        'los': pass_obj.los,
        'max_elevation_deg': pass_obj.max_elevation_deg,
        'duration_seconds': pass_obj.duration_seconds,
        'priority': pass_obj.priority
    }


def _queue_to_dict(queue: DataQueueORM) -> dict:
    return {
        'critical_volume_mb': queue.critical_volume_mb,
        'high_volume_mb': queue.high_volume_mb,
        'medium_volume_mb': queue.medium_volume_mb,
        'low_volume_mb': queue.low_volume_mb,
        'total_volume_mb': queue.total_volume_mb
    }


def _schedule_to_response(schedule: ScheduleORM) -> ScheduleResponse:
    return ScheduleResponse(
        id=schedule.id,
        name=schedule.name,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
        is_active=schedule.is_active,
        is_optimized=schedule.is_optimized,
        scheduled_passes=schedule.scheduled_passes or [],
        total_contact_minutes=schedule.total_contact_minutes,
        total_data_volume_mb=schedule.total_data_volume_mb,
        metadata=schedule.metadata_ or {},
        created_at=schedule.created_at,
        updated_at=schedule.updated_at
    )
