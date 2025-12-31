"""
Shared data models for Constellation Hub.
These Pydantic models are used across services for API schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


# Enums
class HealthStatus(str, Enum):
    """Health status for satellites and ground stations."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class LinkType(str, Enum):
    """Type of communication link."""
    SATELLITE_GROUND = "satellite_ground"
    INTER_SATELLITE = "inter_satellite"


class Priority(str, Enum):
    """Priority levels for scheduling."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Base Models
class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Satellite Models
class Position(BaseModel):
    """Geographic position with optional altitude."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    altitude_km: Optional[float] = Field(None, ge=0, description="Altitude in kilometers")


class Velocity(BaseModel):
    """Velocity vector in km/s."""
    vx: float = Field(..., description="Velocity X component (km/s)")
    vy: float = Field(..., description="Velocity Y component (km/s)")
    vz: float = Field(..., description="Velocity Z component (km/s)")


class OrbitalElements(BaseModel):
    """Classical orbital elements."""
    semi_major_axis_km: float = Field(..., description="Semi-major axis in km")
    eccentricity: float = Field(..., ge=0, lt=1, description="Orbital eccentricity")
    inclination_deg: float = Field(..., ge=0, le=180, description="Inclination in degrees")
    raan_deg: float = Field(..., ge=0, lt=360, description="Right ascension of ascending node")
    arg_perigee_deg: float = Field(..., ge=0, lt=360, description="Argument of perigee")
    true_anomaly_deg: float = Field(..., ge=0, lt=360, description="True anomaly")


class TLEData(BaseModel):
    """Two-Line Element set data."""
    line1: str = Field(..., min_length=69, max_length=69, description="TLE line 1")
    line2: str = Field(..., min_length=69, max_length=69, description="TLE line 2")
    epoch: Optional[datetime] = Field(None, description="TLE epoch")


class SatelliteBase(BaseModel):
    """Base satellite model."""
    name: str = Field(..., min_length=1, max_length=100)
    norad_id: Optional[str] = Field(None, max_length=10)
    constellation_id: Optional[int] = None
    tle_data: Optional[TLEData] = None
    metadata: dict = Field(default_factory=dict)


class SatelliteCreate(SatelliteBase):
    """Model for creating a satellite."""
    pass


class Satellite(SatelliteBase, TimestampMixin):
    """Full satellite model with ID."""
    id: int
    health_status: HealthStatus = HealthStatus.UNKNOWN

    class Config:
        from_attributes = True


class SatellitePosition(BaseModel):
    """Satellite position at a specific time."""
    satellite_id: int
    timestamp: datetime
    position: Position
    velocity: Optional[Velocity] = None
    is_sunlit: Optional[bool] = None


# Constellation Models
class ConstellationBase(BaseModel):
    """Base constellation model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class ConstellationCreate(ConstellationBase):
    """Model for creating a constellation."""
    pass


class Constellation(ConstellationBase, TimestampMixin):
    """Full constellation model with ID."""
    id: int
    satellite_count: int = 0

    class Config:
        from_attributes = True


# Coverage Models
class CoverageFootprint(BaseModel):
    """Ground coverage footprint for a satellite."""
    satellite_id: int
    timestamp: datetime
    center: Position
    radius_km: float = Field(..., gt=0, description="Coverage radius in km")
    polygon: Optional[List[Position]] = Field(None, description="Detailed footprint polygon")


# Ground Station Models
class GroundStationBase(BaseModel):
    """Base ground station model."""
    name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation_m: float = Field(0, ge=0, description="Elevation above sea level in meters")
    min_elevation_deg: float = Field(10, ge=0, le=90, description="Minimum elevation angle for passes")
    capabilities: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)


class GroundStationCreate(GroundStationBase):
    """Model for creating a ground station."""
    pass


class GroundStation(GroundStationBase, TimestampMixin):
    """Full ground station model with ID."""
    id: int
    health_status: HealthStatus = HealthStatus.UNKNOWN

    class Config:
        from_attributes = True


# Pass Models
class Pass(BaseModel):
    """Visibility pass between satellite and ground station."""
    id: Optional[int] = None
    satellite_id: int
    station_id: int
    aos: datetime = Field(..., description="Acquisition of Signal time")
    los: datetime = Field(..., description="Loss of Signal time")
    max_elevation_deg: float = Field(..., ge=0, le=90)
    max_elevation_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    class Config:
        from_attributes = True


# Link Models
class Link(BaseModel):
    """Communication link between two nodes."""
    id: Optional[int] = None
    link_type: LinkType
    source_id: int
    target_id: int
    latency_ms: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    cost: Optional[float] = None
    is_active: bool = True


# Routing Models
class RouteRequest(BaseModel):
    """Request for route computation."""
    origin_type: str = Field(..., description="Origin type: satellite, ground_station, region")
    origin_id: int
    destination_type: str
    destination_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    max_latency_ms: Optional[float] = None
    max_hops: Optional[int] = None
    priority: Priority = Priority.MEDIUM


class RouteHop(BaseModel):
    """Single hop in a route."""
    node_type: str
    node_id: int
    node_name: Optional[str] = None
    latency_ms: Optional[float] = None


class Route(BaseModel):
    """Computed route between origin and destination."""
    request_id: str
    origin: RouteHop
    destination: RouteHop
    hops: List[RouteHop]
    total_latency_ms: float
    total_cost: float
    computed_at: datetime = Field(default_factory=datetime.utcnow)


# Schedule Models
class ScheduledPass(BaseModel):
    """A pass scheduled for data downlink."""
    pass_id: int
    satellite_id: int
    station_id: int
    start_time: datetime
    end_time: datetime
    priority: Priority
    data_volume_mb: float = 0
    assigned: bool = False


class Schedule(BaseModel):
    """Complete downlink schedule."""
    id: Optional[int] = None
    name: str
    start_time: datetime
    end_time: datetime
    passes: List[ScheduledPass] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_optimized: bool = False


# AI/Event Models
class Event(BaseModel):
    """System event for analysis."""
    id: Optional[int] = None
    timestamp: datetime
    event_type: str
    severity: str
    source: str
    message: str
    metadata: dict = Field(default_factory=dict)


class Analysis(BaseModel):
    """AI analysis result."""
    summary: str
    suggested_actions: List[str]
    confidence: float = Field(..., ge=0, le=1)
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)


# API Response Models
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    data: any
    meta: dict = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    """Error detail model."""
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: ErrorDetail
