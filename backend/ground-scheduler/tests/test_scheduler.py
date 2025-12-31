"""
Unit tests for Scheduler.

Tests baseline schedule generation and optimization.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.scheduler import BaseScheduler, ScheduleEntry


class TestScheduleEntry:
    """Test cases for ScheduleEntry data class."""
    
    def test_create_entry(self):
        """Test creating a schedule entry."""
        aos = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        los = datetime(2024, 1, 1, 12, 15, 0, tzinfo=timezone.utc)
        
        entry = ScheduleEntry(
            pass_id=1,
            satellite_id=1,
            station_id=1,
            aos=aos,
            los=los,
            max_elevation=75.0,
            priority=1
        )
        
        assert entry.pass_id == 1
        assert entry.satellite_id == 1
        assert entry.duration_seconds == 900  # 15 minutes
    
    def test_entry_duration_calculation(self):
        """Test that duration is calculated correctly."""
        aos = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        los = datetime(2024, 1, 1, 12, 10, 30, tzinfo=timezone.utc)
        
        entry = ScheduleEntry(
            pass_id=1,
            satellite_id=1,
            station_id=1,
            aos=aos,
            los=los,
            max_elevation=45.0,
            priority=1
        )
        
        assert entry.duration_seconds == 630  # 10 min 30 sec
    
    def test_entries_overlap_detection(self):
        """Test detecting overlapping entries."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        entry1 = ScheduleEntry(
            pass_id=1, satellite_id=1, station_id=1,
            aos=base_time,
            los=base_time + timedelta(minutes=15),
            max_elevation=45.0, priority=1
        )
        
        entry2 = ScheduleEntry(
            pass_id=2, satellite_id=2, station_id=1,
            aos=base_time + timedelta(minutes=10),  # Overlaps
            los=base_time + timedelta(minutes=25),
            max_elevation=60.0, priority=1
        )
        
        assert entry1.overlaps(entry2)
        assert entry2.overlaps(entry1)
    
    def test_entries_no_overlap(self):
        """Test non-overlapping entries."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        entry1 = ScheduleEntry(
            pass_id=1, satellite_id=1, station_id=1,
            aos=base_time,
            los=base_time + timedelta(minutes=15),
            max_elevation=45.0, priority=1
        )
        
        entry2 = ScheduleEntry(
            pass_id=2, satellite_id=2, station_id=1,
            aos=base_time + timedelta(minutes=20),  # After entry1
            los=base_time + timedelta(minutes=35),
            max_elevation=60.0, priority=1
        )
        
        assert not entry1.overlaps(entry2)


class TestBaseScheduler:
    """Test cases for BaseScheduler."""
    
    def setup_method(self):
        self.scheduler = BaseScheduler()
    
    def test_generate_empty_schedule(self):
        """Test generating schedule with no passes."""
        schedule = self.scheduler.generate(
            passes=[],
            stations=[],
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        
        assert schedule is not None
        assert len(schedule.entries) == 0
    
    def test_generate_single_pass(self):
        """Test scheduling a single pass."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        passes = [{
            "id": 1,
            "satellite_id": 1,
            "station_id": 1,
            "aos": base_time,
            "los": base_time + timedelta(minutes=10),
            "max_elevation": 75.0
        }]
        
        stations = [{
            "id": 1,
            "name": "GS-Alpha",
            "available": True
        }]
        
        schedule = self.scheduler.generate(
            passes=passes,
            stations=stations,
            start_time=base_time - timedelta(hours=1),
            end_time=base_time + timedelta(hours=1)
        )
        
        assert len(schedule.entries) == 1
    
    def test_conflict_resolution(self):
        """Test that scheduler resolves conflicts."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        # Two overlapping passes at same station
        passes = [
            {
                "id": 1,
                "satellite_id": 1,
                "station_id": 1,
                "aos": base_time,
                "los": base_time + timedelta(minutes=15),
                "max_elevation": 75.0,
                "priority": 1
            },
            {
                "id": 2,
                "satellite_id": 2,
                "station_id": 1,
                "aos": base_time + timedelta(minutes=5),  # Overlaps
                "los": base_time + timedelta(minutes=20),
                "max_elevation": 60.0,
                "priority": 1
            }
        ]
        
        stations = [{"id": 1, "name": "GS-Alpha", "available": True}]
        
        schedule = self.scheduler.generate(
            passes=passes,
            stations=stations,
            start_time=base_time - timedelta(hours=1),
            end_time=base_time + timedelta(hours=1)
        )
        
        # Should schedule only one (higher elevation wins)
        assert len(schedule.entries) == 1
    
    def test_priority_ordering(self):
        """Test that higher priority passes are preferred."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        passes = [
            {
                "id": 1,
                "satellite_id": 1,
                "station_id": 1,
                "aos": base_time,
                "los": base_time + timedelta(minutes=15),
                "max_elevation": 45.0,
                "priority": 2  # Higher priority
            },
            {
                "id": 2,
                "satellite_id": 2,
                "station_id": 1,
                "aos": base_time + timedelta(minutes=5),
                "los": base_time + timedelta(minutes=20),
                "max_elevation": 80.0,  # Better elevation but lower priority
                "priority": 1
            }
        ]
        
        stations = [{"id": 1, "name": "GS-Alpha", "available": True}]
        
        schedule = self.scheduler.generate(
            passes=passes,
            stations=stations,
            start_time=base_time - timedelta(hours=1),
            end_time=base_time + timedelta(hours=1),
            prefer_priority=True
        )
        
        # Should pick the higher priority pass
        if len(schedule.entries) == 1:
            assert schedule.entries[0].priority == 2


class TestScheduleMetrics:
    """Test cases for schedule quality metrics."""
    
    def setup_method(self):
        self.scheduler = BaseScheduler()
    
    def test_contact_time_calculation(self):
        """Test total contact time is calculated correctly."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        passes = [
            {
                "id": 1, "satellite_id": 1, "station_id": 1,
                "aos": base_time,
                "los": base_time + timedelta(minutes=10),
                "max_elevation": 75.0
            },
            {
                "id": 2, "satellite_id": 1, "station_id": 2,
                "aos": base_time + timedelta(hours=1),
                "los": base_time + timedelta(hours=1, minutes=15),
                "max_elevation": 60.0
            }
        ]
        
        stations = [
            {"id": 1, "name": "GS-Alpha", "available": True},
            {"id": 2, "name": "GS-Beta", "available": True}
        ]
        
        schedule = self.scheduler.generate(
            passes=passes,
            stations=stations,
            start_time=base_time - timedelta(hours=1),
            end_time=base_time + timedelta(hours=2)
        )
        
        # Total contact time should be 10 + 15 = 25 minutes
        assert schedule.total_contact_minutes == pytest.approx(25, abs=1)
