"""
Database models for Core Orbits service.
Uses SQLAlchemy ORM for persistence.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum

import sys
sys.path.insert(0, '../..')
from common.database import Base


class HealthStatus(str, enum.Enum):
    """Health status enum for database."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ConstellationORM(Base):
    """Constellation database model."""
    __tablename__ = "constellations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    satellites = relationship("SatelliteORM", back_populates="constellation")


class SatelliteORM(Base):
    """Satellite database model."""
    __tablename__ = "satellites"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    norad_id = Column(String(10), nullable=True, index=True)
    constellation_id = Column(Integer, ForeignKey("constellations.id"), nullable=True)
    
    # TLE data stored as JSON
    tle_line1 = Column(String(69), nullable=True)
    tle_line2 = Column(String(69), nullable=True)
    tle_epoch = Column(DateTime, nullable=True)
    
    health_status = Column(String(20), default="unknown")
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    constellation = relationship("ConstellationORM", back_populates="satellites")
