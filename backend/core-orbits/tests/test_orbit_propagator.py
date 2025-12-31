"""
Unit tests for Orbit Propagator.

Tests SGP4-based orbit propagation and coordinate transformations.
"""
import pytest
from datetime import datetime, timezone
from app.services.orbit_propagator import OrbitPropagator


# Valid TLE for ISS (ZARYA)
VALID_TLE_LINE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9025"
VALID_TLE_LINE2 = "2 25544  51.6400 208.9163 0006703 280.7808  79.2154 15.49815776    20"


class TestOrbitPropagator:
    """Test cases for orbit propagation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.propagator = OrbitPropagator()
    
    def test_compute_position_returns_required_fields(self):
        """Test that position computation returns all required fields."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        required_fields = ['latitude', 'longitude', 'altitude_km', 'velocity', 'position_eci']
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_latitude_in_valid_range(self):
        """Test that latitude is within -90 to 90 degrees."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        assert -90 <= result['latitude'] <= 90
    
    def test_longitude_in_valid_range(self):
        """Test that longitude is within -180 to 180 degrees."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        assert -180 <= result['longitude'] <= 180
    
    def test_iss_altitude_reasonable(self):
        """Test that ISS altitude is in expected range (~400-430 km)."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        # ISS altitude should be approximately 400-430 km
        assert 350 < result['altitude_km'] < 500
    
    def test_velocity_reasonable(self):
        """Test that velocity is in expected range for LEO satellite."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        # LEO orbital velocity is approximately 7.5-7.8 km/s
        assert 7.0 < result['velocity']['speed_kms'] < 8.5
    
    def test_velocity_components_exist(self):
        """Test that velocity vector components are present."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        assert 'vx' in result['velocity']
        assert 'vy' in result['velocity']
        assert 'vz' in result['velocity']
        assert 'speed_kms' in result['velocity']
    
    def test_position_eci_components_exist(self):
        """Test that ECI position components are present."""
        target_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        assert 'x' in result['position_eci']
        assert 'y' in result['position_eci']
        assert 'z' in result['position_eci']
    
    def test_position_changes_over_time(self):
        """Test that satellite position changes over time."""
        time1 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        time2 = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)
        
        result1 = self.propagator.compute_position(VALID_TLE_LINE1, VALID_TLE_LINE2, time1)
        result2 = self.propagator.compute_position(VALID_TLE_LINE1, VALID_TLE_LINE2, time2)
        
        # Position should change significantly over 30 minutes
        assert result1['latitude'] != result2['latitude'] or result1['longitude'] != result2['longitude']
    
    def test_handles_naive_datetime(self):
        """Test that naive datetime is handled (assumed UTC)."""
        target_time = datetime(2024, 1, 1, 12, 0, 0)  # No timezone
        
        # Should not raise
        result = self.propagator.compute_position(
            VALID_TLE_LINE1, VALID_TLE_LINE2, target_time
        )
        
        assert 'latitude' in result


class TestOrbitPropagatorTimeSeries:
    """Test cases for time series position computation."""
    
    def setup_method(self):
        self.propagator = OrbitPropagator()
    
    def test_positions_over_time_returns_list(self):
        """Test that compute_positions_over_time returns a list."""
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 10, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_positions_over_time(
            VALID_TLE_LINE1, VALID_TLE_LINE2, start, end, step_seconds=60
        )
        
        assert isinstance(result, list)
        assert len(result) == 11  # 0, 1, 2, ..., 10 minutes
    
    def test_positions_include_timestamps(self):
        """Test that each position includes a timestamp."""
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_positions_over_time(
            VALID_TLE_LINE1, VALID_TLE_LINE2, start, end, step_seconds=60
        )
        
        for pos in result:
            assert 'timestamp' in pos
    
    def test_positions_are_sequential(self):
        """Test that positions are in chronological order."""
        start = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
        
        result = self.propagator.compute_positions_over_time(
            VALID_TLE_LINE1, VALID_TLE_LINE2, start, end, step_seconds=60
        )
        
        timestamps = [pos['timestamp'] for pos in result]
        assert timestamps == sorted(timestamps)


class TestOrbitPropagatorEpoch:
    """Test cases for TLE epoch extraction."""
    
    def setup_method(self):
        self.propagator = OrbitPropagator()
    
    def test_get_tle_epoch(self):
        """Test extraction of TLE epoch."""
        epoch = self.propagator.get_tle_epoch(VALID_TLE_LINE1, VALID_TLE_LINE2)
        
        assert isinstance(epoch, datetime)
        assert epoch.year == 2024
        assert epoch.month == 1


class TestCoordinateConversion:
    """Test cases for coordinate conversion functions."""
    
    def setup_method(self):
        self.propagator = OrbitPropagator()
    
    def test_datetime_to_jd_j2000(self):
        """Test Julian date conversion for J2000 epoch."""
        j2000 = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = self.propagator._datetime_to_jd(j2000)
        
        # J2000 epoch is JD 2451545.0
        assert jd == pytest.approx(2451545.0, abs=0.001)
    
    def test_jd_to_datetime_roundtrip(self):
        """Test that datetime -> JD -> datetime roundtrip works."""
        original = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        jd = self.propagator._datetime_to_jd(original)
        recovered = self.propagator._jd_to_datetime(jd)
        
        # Should be within a few seconds
        diff = abs((recovered - original).total_seconds())
        assert diff < 5
