"""
Pydantic schemas for Ground Scheduler service API.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============ Ground Station Schemas ============

class GroundStationCreate(BaseModel):
    """Schema for creating a ground station."""
    name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation_m: float = Field(0, ge=0)
    min_elevation_deg: float = Field(10.0, ge=0, le=90)
    capabilities: List[str] = Field(default_factory=list)
    cost_per_minute: float = Field(1.0, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GroundStationResponse(BaseModel):
    """Response schema for a ground station."""
    id: int
    name: str
    latitude: float
    longitude: float
    elevation_m: float
    min_elevation_deg: float
    capabilities: List[str]
    health_status: str
    is_active: bool
    cost_per_minute: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GroundStationList(BaseModel):
    """Response schema for list of ground stations."""
    data: List[GroundStationResponse]
    total: int


# ============ Pass Schemas ============

class PassResponse(BaseModel):
    """Response schema for a pass."""
    id: int
    satellite_id: int
    station_id: int
    station_name: Optional[str] = None
    aos: datetime
    los: datetime
    max_elevation_time: Optional[datetime]
    max_elevation_deg: float
    duration_seconds: float
    is_scheduled: bool
    priority: str
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class PassList(BaseModel):
    """Response schema for list of passes."""
    data: List[PassResponse]
    total: int


class PassComputeRequest(BaseModel):
    """Request to compute passes for satellites."""
    satellite_ids: List[int] = Field(..., min_length=1)
    station_ids: Optional[List[int]] = None  # None = all stations
    start_time: datetime
    end_time: datetime
    min_elevation_deg: Optional[float] = None  # Override station default


class PassComputeResponse(BaseModel):
    """Response from pass computation."""
    passes_computed: int
    satellites_processed: int
    stations_processed: int
    time_range_hours: float
    computation_time_ms: float


# ============ Schedule Schemas ============

class ScheduledPassInfo(BaseModel):
    """Information about a scheduled pass."""
    pass_id: int
    satellite_id: int
    station_id: int
    start_time: datetime
    end_time: datetime
    priority: Priority
    data_volume_mb: float = 0
    assigned: bool = False


class ScheduleCreate(BaseModel):
    """Schema for creating a schedule."""
    name: str = Field(..., min_length=1, max_length=100)
    start_time: datetime
    end_time: datetime


class ScheduleResponse(BaseModel):
    """Response schema for a schedule."""
    id: int
    name: str
    start_time: datetime
    end_time: datetime
    is_active: bool
    is_optimized: bool
    scheduled_passes: List[int]
    total_contact_minutes: float
    total_data_volume_mb: float
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleGenerateRequest(BaseModel):
    """Request to generate a baseline schedule."""
    name: str = Field(..., min_length=1, max_length=100)
    start_time: datetime
    end_time: datetime
    satellite_ids: Optional[List[int]] = None  # None = all satellites
    station_ids: Optional[List[int]] = None  # None = all stations
    max_passes_per_satellite: Optional[int] = None
    prefer_high_elevation: bool = True


# ============ Data Queue Schemas ============

class DataQueueUpdate(BaseModel):
    """Schema for updating a satellite's data queue."""
    satellite_id: int
    critical_volume_mb: float = 0
    high_volume_mb: float = 0
    medium_volume_mb: float = 0
    low_volume_mb: float = 0
    customer_allocations: Dict[str, float] = Field(default_factory=dict)


class DataQueueResponse(BaseModel):
    """Response schema for a data queue."""
    id: int
    satellite_id: int
    critical_volume_mb: float
    high_volume_mb: float
    medium_volume_mb: float
    low_volume_mb: float
    total_volume_mb: float
    customer_allocations: Dict[str, float]
    updated_at: datetime

    class Config:
        from_attributes = True
