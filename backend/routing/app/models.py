"""
Database models for Routing service.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, Enum
import enum

from .db import Base


class LinkType(str, enum.Enum):
    """Type of communication link."""
    SATELLITE_GROUND = "satellite_ground"
    INTER_SATELLITE = "inter_satellite"


class LinkORM(Base):
    """Communication link database model."""
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    link_type = Column(String(30), nullable=False)
    source_type = Column(String(30), nullable=False)  # satellite, ground_station
    source_id = Column(Integer, nullable=False, index=True)
    target_type = Column(String(30), nullable=False)
    target_id = Column(Integer, nullable=False, index=True)
    
    # Link characteristics
    latency_ms = Column(Float, nullable=True)
    bandwidth_mbps = Column(Float, nullable=True)
    cost = Column(Float, default=1.0)
    
    is_active = Column(Boolean, default=True)
    metadata_ = Column("metadata", JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PolicyORM(Base):
    """Routing policy database model."""
    __tablename__ = "routing_policies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    
    # Policy weights (higher = more important to minimize)
    latency_weight = Column(Float, default=1.0)
    cost_weight = Column(Float, default=0.5)
    hop_weight = Column(Float, default=0.3)
    
    # Constraints
    max_latency_ms = Column(Float, nullable=True)
    max_hops = Column(Integer, nullable=True)
    max_cost = Column(Float, nullable=True)
    
    # Preferences
    preferred_ground_stations = Column(JSON, default=list)  # List of station IDs
    avoided_ground_stations = Column(JSON, default=list)
    
    is_default = Column(Boolean, default=False)
    metadata_ = Column("metadata", JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
