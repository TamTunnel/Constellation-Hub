"""
Pydantic schemas for AI Agents service API.
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


class EventSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class ActionStatus(str, Enum):
    PENDING = "pending"
    APPLIED = "applied"
    DISMISSED = "dismissed"


# ============ Pass Scheduler Schemas ============

class PassInfo(BaseModel):
    """Pass information for scheduling."""
    id: int
    satellite_id: int
    station_id: int
    aos: datetime
    los: datetime
    max_elevation_deg: float
    duration_seconds: float
    priority: Priority = Priority.MEDIUM
    is_scheduled: bool = False


class DataQueueInfo(BaseModel):
    """Satellite data queue information."""
    satellite_id: int
    critical_volume_mb: float = 0
    high_volume_mb: float = 0
    medium_volume_mb: float = 0
    low_volume_mb: float = 0
    total_volume_mb: float = 0


class StationInfo(BaseModel):
    """Ground station information."""
    id: int
    name: str
    cost_per_minute: float = 1.0
    capabilities: List[str] = Field(default_factory=list)


class OptimizeRequest(BaseModel):
    """Request for schedule optimization."""
    schedule_id: Optional[int] = None
    passes: List[PassInfo]
    data_queues: List[DataQueueInfo] = Field(default_factory=list)
    stations: List[StationInfo] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class OptimizeResponse(BaseModel):
    """Response from schedule optimization."""
    original_pass_ids: List[int]
    optimized_pass_ids: List[int]
    passes_added: List[int]
    passes_removed: List[int]
    improvement_metrics: Dict[str, float]
    optimization_strategy: str
    computation_time_ms: float
    recommendations: List[str] = Field(default_factory=list)


# ============ Ops Co-Pilot Schemas ============

class Event(BaseModel):
    """System event for analysis."""
    id: Optional[int] = None
    timestamp: datetime
    event_type: str
    severity: EventSeverity
    source: str
    message: str
    satellite_id: Optional[int] = None
    station_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SuggestedAction(BaseModel):
    """Suggested action from ops co-pilot."""
    id: str
    action: str
    rationale: str
    priority: Priority
    estimated_impact: str
    status: ActionStatus = ActionStatus.PENDING


class AnalyzeRequest(BaseModel):
    """Request for ops co-pilot analysis."""
    events: List[Event]
    context: Dict[str, Any] = Field(default_factory=dict)
    focus_areas: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    """Response from ops co-pilot analysis."""
    summary: str
    key_findings: List[str]
    suggested_actions: List[SuggestedAction]
    risk_level: str
    affected_satellites: List[int]
    affected_stations: List[int]
    confidence: float = Field(..., ge=0, le=1)
    analyzed_at: datetime


class ActionUpdateRequest(BaseModel):
    """Request to update action status."""
    action_id: str
    status: ActionStatus
    notes: Optional[str] = None
