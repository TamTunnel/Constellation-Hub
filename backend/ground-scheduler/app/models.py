"""
Database models for Ground Scheduler service.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from .db import Base


class GroundStationORM(Base):
    """Ground station database model."""
    __tablename__ = "ground_stations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, default=0)
    min_elevation_deg = Column(Float, default=10.0)
    
    # Capabilities (e.g., ["S-band", "X-band", "Ka-band"])
    capabilities = Column(JSON, default=list)
    
    # Status
    health_status = Column(String(20), default="unknown")
    is_active = Column(Boolean, default=True)
    
    # Cost per contact (for optimization)
    cost_per_minute = Column(Float, default=1.0)
    
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    passes = relationship("PassORM", back_populates="station")


class PassORM(Base):
    """Satellite pass (visibility window) database model."""
    __tablename__ = "passes"

    id = Column(Integer, primary_key=True, index=True)
    satellite_id = Column(Integer, nullable=False, index=True)
    station_id = Column(Integer, ForeignKey("ground_stations.id"), nullable=False, index=True)
    
    # Pass timing
    aos = Column(DateTime, nullable=False)  # Acquisition of Signal
    los = Column(DateTime, nullable=False)  # Loss of Signal
    max_elevation_time = Column(DateTime, nullable=True)
    
    # Pass quality
    max_elevation_deg = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    
    # Scheduling status
    is_scheduled = Column(Boolean, default=False)
    priority = Column(String(20), default="medium")
    
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    station = relationship("GroundStationORM", back_populates="passes")


class ScheduleORM(Base):
    """Downlink schedule database model."""
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Schedule status
    is_active = Column(Boolean, default=True)
    is_optimized = Column(Boolean, default=False)
    
    # Scheduled passes (list of pass IDs)
    scheduled_passes = Column(JSON, default=list)
    
    # Statistics
    total_contact_minutes = Column(Float, default=0)
    total_data_volume_mb = Column(Float, default=0)
    
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataQueueORM(Base):
    """Satellite data queue for scheduling prioritization."""
    __tablename__ = "data_queues"

    id = Column(Integer, primary_key=True, index=True)
    satellite_id = Column(Integer, nullable=False, index=True)
    
    # Data volume by priority
    critical_volume_mb = Column(Float, default=0)
    high_volume_mb = Column(Float, default=0)
    medium_volume_mb = Column(Float, default=0)
    low_volume_mb = Column(Float, default=0)
    
    # Total volume
    total_volume_mb = Column(Float, default=0)
    
    # Customer/mission allocation
    customer_allocations = Column(JSON, default=dict)  # {customer_id: volume_mb}
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
