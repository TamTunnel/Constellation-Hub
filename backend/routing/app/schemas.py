"""
Pydantic schemas for Routing service API.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class LinkType(str, Enum):
    SATELLITE_GROUND = "satellite_ground"
    INTER_SATELLITE = "inter_satellite"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============ Link Schemas ============

class LinkCreate(BaseModel):
    """Schema for creating a link."""
    link_type: LinkType
    source_type: str = Field(..., description="satellite or ground_station")
    source_id: int
    target_type: str
    target_id: int
    latency_ms: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    cost: float = 1.0
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LinkResponse(BaseModel):
    """Response schema for a link."""
    id: int
    link_type: str
    source_type: str
    source_id: int
    target_type: str
    target_id: int
    latency_ms: Optional[float]
    bandwidth_mbps: Optional[float]
    cost: float
    is_active: bool
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LinkList(BaseModel):
    """Response schema for list of links."""
    data: List[LinkResponse]
    total: int


# ============ Policy Schemas ============

class PolicyCreate(BaseModel):
    """Schema for creating a routing policy."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    latency_weight: float = 1.0
    cost_weight: float = 0.5
    hop_weight: float = 0.3
    max_latency_ms: Optional[float] = None
    max_hops: Optional[int] = None
    max_cost: Optional[float] = None
    preferred_ground_stations: List[int] = Field(default_factory=list)
    avoided_ground_stations: List[int] = Field(default_factory=list)
    is_default: bool = False


class PolicyResponse(BaseModel):
    """Response schema for a policy."""
    id: int
    name: str
    description: Optional[str]
    latency_weight: float
    cost_weight: float
    hop_weight: float
    max_latency_ms: Optional[float]
    max_hops: Optional[int]
    max_cost: Optional[float]
    preferred_ground_stations: List[int]
    avoided_ground_stations: List[int]
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Route Schemas ============

class RouteRequest(BaseModel):
    """Request for route computation."""
    origin_type: str = Field(..., description="satellite or ground_station")
    origin_id: int
    destination_type: str
    destination_id: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    policy_id: Optional[int] = None
    priority: Priority = Priority.MEDIUM


class RouteHop(BaseModel):
    """Single hop in a route."""
    node_type: str
    node_id: int
    node_name: Optional[str] = None
    latency_ms: Optional[float] = None
    cost: Optional[float] = None


class RouteResponse(BaseModel):
    """Response schema for a computed route."""
    request_id: str
    origin: RouteHop
    destination: RouteHop
    hops: List[RouteHop]
    total_latency_ms: float
    total_cost: float
    total_hops: int
    computed_at: datetime
    policy_name: Optional[str] = None
    feasible: bool = True
    message: Optional[str] = None


class MultiRouteRequest(BaseModel):
    """Request for multiple route computations."""
    routes: List[RouteRequest]
