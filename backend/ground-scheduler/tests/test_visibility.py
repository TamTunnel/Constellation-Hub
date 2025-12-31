"""
Unit tests for Visibility Calculator.

Tests satellite visibility window computation.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.services.visibility import VisibilityCalculator


class TestVisibilityCalculator:
    """Test cases for visibility computation."""
    
    def setup_method(self):
        self.calculator = VisibilityCalculator()
    
    def test_compute_passes_returns_list(self):
        """Test that compute_passes returns a list."""
        station = {
            "id": 1,
            "latitude": 40.7,
            "longitude": -74.0,
            "elevation_m": 10,
            "min_elevation_deg": 10
        }
        
        satellite = {
            "id": 1,
            "tle_line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9025",
            "tle_line2": "2 25544  51.6400 208.9163 0006703 280.7808  79.2154 15.49815776    20"
        }
        
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        
        passes = self.calculator.compute_passes(
            satellite=satellite,
            station=station,
            start_time=start,
            end_time=end
        )
        
        assert isinstance(passes, list)
    
    def test_pass_structure(self):
        """Test that passes have required fields."""
        station = {
            "id": 1,
            "latitude": 40.7,
            "longitude": -74.0,
            "elevation_m": 10,
            "min_elevation_deg": 5  # Lower threshold for more passes
        }
        
        satellite = {
            "id": 1,
            "tle_line1": "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9025",
            "tle_line2": "2 25544  51.6400 208.9163 0006703 280.7808  79.2154 15.49815776    20"
        }
        
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        
        passes = self.calculator.compute_passes(
            satellite=satellite,
            station=station,
            start_time=start,
            end_time=end
        )
        
        if len(passes) > 0:
            p = passes[0]
            assert "aos" in p  # Acquisition of Signal
            assert "los" in p  # Loss of Signal
            assert "max_elevation" in p
            assert "satellite_id" in p
            assert "station_id" in p


class TestVisibilityHelpers:
    """Test cases for visibility helper functions."""
    
    def setup_method(self):
        self.calculator = VisibilityCalculator()
    
    def test_elevation_angle_calculation(self):
        """Test elevation angle calculation."""
        # Satellite directly overhead
        elevation = self.calculator._compute_elevation(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            obs_lat=45.0, obs_lon=-122.0
        )
        
        # Should be ~90 degrees (directly overhead)
        assert elevation > 80
    
    def test_elevation_angle_horizon(self):
        """Test elevation angle near horizon."""
        # Satellite far from observer
        elevation = self.calculator._compute_elevation(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            obs_lat=30.0, obs_lon=-100.0  # Far away
        )
        
        # Should be lower elevation or negative
        assert elevation < 45


class TestPassFiltering:
    """Test cases for pass filtering."""
    
    def setup_method(self):
        self.calculator = VisibilityCalculator()
    
    def test_filter_by_min_elevation(self):
        """Test filtering passes by minimum elevation."""
        passes = [
            {"max_elevation": 80, "satellite_id": 1, "station_id": 1},
            {"max_elevation": 15, "satellite_id": 1, "station_id": 1},
            {"max_elevation": 5, "satellite_id": 1, "station_id": 1},
            {"max_elevation": 45, "satellite_id": 1, "station_id": 1},
        ]
        
        filtered = self.calculator.filter_passes(passes, min_elevation=10)
        
        assert len(filtered) == 3  # 80, 15, and 45 degrees
    
    def test_filter_by_duration(self):
        """Test filtering passes by minimum duration."""
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        passes = [
            {
                "aos": base,
                "los": base + timedelta(minutes=15),  # 15 min
                "max_elevation": 45
            },
            {
                "aos": base + timedelta(hours=1),
                "los": base + timedelta(hours=1, minutes=3),  # 3 min
                "max_elevation": 60
            },
            {
                "aos": base + timedelta(hours=2),
                "los": base + timedelta(hours=2, minutes=10),  # 10 min
                "max_elevation": 30
            }
        ]
        
        filtered = self.calculator.filter_passes(passes, min_duration_seconds=300)  # 5 min
        
        assert len(filtered) == 2  # 15 min and 10 min passes
