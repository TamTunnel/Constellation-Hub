"""
Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============ TLE Schemas ============

class TLEInput(BaseModel):
    """Input schema for TLE data."""
    line1: str = Field(..., min_length=69, max_length=69, description="TLE line 1")
    line2: str = Field(..., min_length=69, max_length=69, description="TLE line 2")


class TLEData(BaseModel):
    """TLE data with optional epoch."""
    line1: str
    line2: str
    epoch: Optional[datetime] = None


# ============ Constellation Schemas ============

class ConstellationCreate(BaseModel):
    """Schema for creating a constellation."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConstellationResponse(BaseModel):
    """Response schema for a constellation."""
    id: int
    name: str
    description: Optional[str]
    metadata: Dict[str, Any]
    satellite_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConstellationList(BaseModel):
    """Response schema for list of constellations."""
    data: List[ConstellationResponse]
    total: int


# ============ Satellite Schemas ============

class SatelliteCreate(BaseModel):
    """Schema for creating a satellite."""
    name: str = Field(..., min_length=1, max_length=100)
    norad_id: Optional[str] = Field(None, max_length=10)
    constellation_id: Optional[int] = None
    tle_data: Optional[TLEInput] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SatelliteResponse(BaseModel):
    """Response schema for a satellite."""
    id: int
    name: str
    norad_id: Optional[str]
    constellation_id: Optional[int]
    tle_data: Optional[TLEData]
    health_status: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SatelliteList(BaseModel):
    """Response schema for list of satellites."""
    data: List[SatelliteResponse]
    total: int


# ============ Position Schemas ============

class VelocityData(BaseModel):
    """Velocity vector data."""
    vx: float = Field(..., description="Velocity X (km/s)")
    vy: float = Field(..., description="Velocity Y (km/s)")
    vz: float = Field(..., description="Velocity Z (km/s)")
    speed_kms: float = Field(..., description="Total speed (km/s)")


class PositionResponse(BaseModel):
    """Response schema for satellite position."""
    satellite_id: int
    satellite_name: str
    timestamp: datetime
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude_km: float = Field(..., ge=0)
    velocity: Optional[VelocityData] = None


# ============ Coverage Schemas ============

class PolygonPoint(BaseModel):
    """Point in coverage polygon."""
    latitude: float
    longitude: float


class CoverageResponse(BaseModel):
    """Response schema for satellite coverage footprint."""
    satellite_id: int
    satellite_name: str
    timestamp: datetime
    center_latitude: float
    center_longitude: float
    altitude_km: float
    radius_km: float = Field(..., description="Coverage radius in km")
    polygon: Optional[List[PolygonPoint]] = Field(None, description="Footprint polygon points")
