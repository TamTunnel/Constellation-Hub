"""
Unit tests for Scheduler.

Tests baseline schedule generation and optimization.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.scheduler import BaselineScheduler

class TestBaselineScheduler:
    """Test cases for BaselineScheduler."""
    
    def setup_method(self):
        self.scheduler = BaselineScheduler()
    
    def test_generate_empty_schedule(self):
        """Test generating schedule with no passes."""
        schedule_ids = self.scheduler.generate_baseline(
            passes=[],
            data_queues={},
            station_costs={}
        )
        
        assert schedule_ids is not None
        assert len(schedule_ids) == 0
    
    def test_generate_single_pass(self):
        """Test scheduling a single pass."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        passes = [{
            "id": 1,
            "satellite_id": 1,
            "station_id": 1,
            "aos": base_time,
            "los": base_time + timedelta(minutes=10),
            "max_elevation_deg": 75.0,
            "duration_seconds": 600
        }]
        
        schedule_ids = self.scheduler.generate_baseline(
            passes=passes,
            data_queues={},
            station_costs={}
        )
        
        assert len(schedule_ids) == 1
        assert 1 in schedule_ids
    
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
                "max_elevation_deg": 75.0,
                "duration_seconds": 900,
                "priority": "medium"
            },
            {
                "id": 2,
                "satellite_id": 2,
                "station_id": 1,
                "aos": base_time + timedelta(minutes=5),  # Overlaps
                "los": base_time + timedelta(minutes=20),
                "max_elevation_deg": 60.0,
                "duration_seconds": 900,
                "priority": "medium"
            }
        ]
        
        # id 1 has better elevation (75 vs 60), so should be picked
        
        schedule_ids = self.scheduler.generate_baseline(
            passes=passes,
            data_queues={},
            station_costs={}
        )
        
        # Should schedule only one (higher elevation wins)
        assert len(schedule_ids) == 1
        assert 1 in schedule_ids
    
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
                "max_elevation_deg": 45.0,
                "duration_seconds": 900,
                "priority": "high"  # Higher priority
            },
            {
                "id": 2,
                "satellite_id": 2,
                "station_id": 1,
                "aos": base_time + timedelta(minutes=5),
                "los": base_time + timedelta(minutes=20),
                "max_elevation_deg": 80.0,  # Better elevation but lower priority
                "duration_seconds": 900,
                "priority": "low"
            }
        ]
        
        schedule_ids = self.scheduler.generate_baseline(
            passes=passes,
            data_queues={},
            station_costs={}
        )
        
        # Should pick the higher priority pass (id 1)
        # Check scores:
        # id 1: High priority (+25), Elev 45 (25 pts), Dur 15 (min 30 cap? No, 900/60*3 = 45 -> cap 30). Total ~ 30 (queue) + 25 (elev) + 30 (dur) + 25 (prio) = 110
        # id 2: Low priority (-10), Elev 80 (44 pts), Dur 15 (30 pts). Total ~ 30 + 44 + 30 - 10 = 94

        assert len(schedule_ids) == 1
        assert 1 in schedule_ids


class TestScheduleMetrics:
    """Test cases for schedule quality metrics."""
    
    def setup_method(self):
        self.scheduler = BaselineScheduler()
    
    def test_contact_time_calculation(self):
        """Test total contact time is calculated correctly."""
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        passes = [
            {
                "id": 1, "satellite_id": 1, "station_id": 1,
                "aos": base_time,
                "los": base_time + timedelta(minutes=10),
                "max_elevation_deg": 75.0,
                "duration_seconds": 600
            },
            {
                "id": 2, "satellite_id": 1, "station_id": 2,
                "aos": base_time + timedelta(hours=1),
                "los": base_time + timedelta(hours=1, minutes=15),
                "max_elevation_deg": 60.0,
                "duration_seconds": 900
            }
        ]
        
        selected_ids = {1, 2}
        
        metrics = self.scheduler.calculate_schedule_metrics(
            passes=passes,
            selected_ids=selected_ids,
            data_queues={}
        )
        
        # Total contact time should be 10 + 15 = 25 minutes
        assert metrics['total_contact_minutes'] == pytest.approx(25, abs=1)
