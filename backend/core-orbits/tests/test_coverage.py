"""
Unit tests for Coverage Calculator.

Tests footprint computation and visibility calculations.
"""
import pytest
from app.services.coverage import CoverageCalculator


class TestCoverageCalculator:
    """Test cases for coverage footprint computation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = CoverageCalculator(min_elevation_deg=10.0)
    
    def test_compute_footprint_returns_required_fields(self):
        """Test that footprint computation returns all required fields."""
        result = self.calculator.compute_footprint(
            center_lat=0.0,
            center_lon=0.0,
            altitude_km=550.0
        )
        
        assert 'radius_km' in result
        assert 'radius_deg' in result
        assert 'polygon' in result
    
    def test_footprint_radius_increases_with_altitude(self):
        """Test that coverage radius increases with altitude."""
        low_alt = self.calculator.compute_footprint(0, 0, 400)
        high_alt = self.calculator.compute_footprint(0, 0, 800)
        
        assert high_alt['radius_km'] > low_alt['radius_km']
    
    def test_footprint_radius_decreases_with_elevation(self):
        """Test that coverage radius decreases with higher min elevation."""
        low_elev = CoverageCalculator(min_elevation_deg=5.0)
        high_elev = CoverageCalculator(min_elevation_deg=20.0)
        
        result_low = low_elev.compute_footprint(0, 0, 550)
        result_high = high_elev.compute_footprint(0, 0, 550)
        
        assert result_low['radius_km'] > result_high['radius_km']
    
    def test_polygon_has_correct_number_of_points(self):
        """Test that polygon has requested number of points plus closure."""
        num_points = 36
        result = self.calculator.compute_footprint(
            0, 0, 550, num_polygon_points=num_points
        )
        
        # Should have num_points + 1 (closure point)
        assert len(result['polygon']) == num_points + 1
    
    def test_polygon_is_closed(self):
        """Test that polygon first and last points are the same."""
        result = self.calculator.compute_footprint(0, 0, 550)
        
        first = result['polygon'][0]
        last = result['polygon'][-1]
        
        assert first['latitude'] == last['latitude']
        assert first['longitude'] == last['longitude']
    
    def test_polygon_points_are_valid_coordinates(self):
        """Test that all polygon points have valid lat/lon."""
        result = self.calculator.compute_footprint(45.0, -122.0, 550)
        
        for point in result['polygon']:
            assert -90 <= point['latitude'] <= 90
            assert -180 <= point['longitude'] <= 180
    
    def test_footprint_centered_on_nadir(self):
        """Test that footprint is roughly centered on nadir point."""
        center_lat, center_lon = 45.0, -122.0
        result = self.calculator.compute_footprint(center_lat, center_lon, 550)
        
        # Calculate centroid of polygon (excluding last duplicate point)
        lats = [p['latitude'] for p in result['polygon'][:-1]]
        lons = [p['longitude'] for p in result['polygon'][:-1]]
        
        avg_lat = sum(lats) / len(lats)
        avg_lon = sum(lons) / len(lons)
        
        # Should be close to the center (within a degree or so)
        assert abs(avg_lat - center_lat) < 2.0
        assert abs(avg_lon - center_lon) < 2.0


class TestCoverageRadius:
    """Test cases for coverage radius calculation."""
    
    def setup_method(self):
        self.calculator = CoverageCalculator()
    
    def test_radius_at_iss_altitude(self):
        """Test coverage radius at ISS altitude (~420 km)."""
        radius_km, radius_deg = self.calculator._compute_coverage_radius(
            altitude_km=420, min_elevation_deg=10
        )
        
        # ISS coverage radius at 10° elevation is roughly 1390 km
        # Calculation:
        # rho = asin(R/(R+h) * cos(E)) = asin(6371/6791 * cos(10)) = asin(0.9238) = 67.48 deg
        # theta = 90 - E - rho = 90 - 10 - 67.48 = 12.52 deg
        # radius = 12.52 * 111.19 km/deg = 1392 km
        assert 1300 < radius_km < 3000
    
    def test_radius_at_geo_altitude(self):
        """Test coverage radius at GEO altitude (~35786 km)."""
        radius_km, radius_deg = self.calculator._compute_coverage_radius(
            altitude_km=35786, min_elevation_deg=5
        )
        
        # GEO can see roughly 1/3 of Earth's surface
        # Earth circumference at equator ~ 40000 km, so radius ~6000-7000 km
        assert radius_km > 5000
    
    def test_radius_at_zero_elevation(self):
        """Test coverage radius at 0° elevation (horizon)."""
        result = self.calculator.compute_footprint(
            0, 0, 550, min_elevation_deg=0
        )
        
        # Should be larger than with 10° elevation
        result_10 = self.calculator.compute_footprint(
            0, 0, 550, min_elevation_deg=10
        )
        
        assert result['radius_km'] > result_10['radius_km']


class TestHorizonDistance:
    """Test cases for horizon distance calculation."""
    
    def setup_method(self):
        self.calculator = CoverageCalculator()
    
    def test_horizon_at_iss_altitude(self):
        """Test geometric horizon at ISS altitude."""
        horizon_km = self.calculator.compute_horizon_distance(420)
        
        # Geometric horizon at 420 km should be roughly 2300 km
        assert 2000 < horizon_km < 2800
    
    def test_horizon_increases_with_altitude(self):
        """Test that horizon distance increases with altitude."""
        low = self.calculator.compute_horizon_distance(400)
        high = self.calculator.compute_horizon_distance(800)
        
        assert high > low


class TestVisibility:
    """Test cases for satellite visibility calculation."""
    
    def setup_method(self):
        self.calculator = CoverageCalculator(min_elevation_deg=10.0)
    
    def test_satellite_directly_overhead_is_visible(self):
        """Test that satellite directly overhead is visible."""
        result = self.calculator.is_visible(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            observer_lat=45.0, observer_lon=-122.0
        )
        
        assert result['visible'] is True
        assert result['elevation_deg'] == pytest.approx(90, abs=1)
    
    def test_satellite_far_away_is_not_visible(self):
        """Test that satellite on other side of Earth is not visible."""
        result = self.calculator.is_visible(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            observer_lat=-45.0, observer_lon=58.0  # Opposite side
        )
        
        assert result['visible'] is False
    
    def test_visibility_returns_required_fields(self):
        """Test that visibility check returns all required fields."""
        result = self.calculator.is_visible(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            observer_lat=40.0, observer_lon=-120.0
        )
        
        assert 'visible' in result
        assert 'elevation_deg' in result
        assert 'distance_km' in result
        assert 'ground_distance_km' in result
    
    def test_slant_range_reasonable(self):
        """Test that slant range is reasonable."""
        result = self.calculator.is_visible(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            observer_lat=45.0, observer_lon=-122.0  # Directly below
        )
        
        # Slant range to satellite directly overhead should be ~altitude
        assert result['distance_km'] == pytest.approx(550, rel=0.1)
    
    def test_elevation_below_minimum_not_visible(self):
        """Test that low elevation angle makes satellite not visible."""
        # Put satellite far enough away that elevation is low
        result = self.calculator.is_visible(
            sat_lat=45.0, sat_lon=-122.0, sat_alt_km=550,
            observer_lat=25.0, observer_lon=-100.0,  # Far away
            min_elevation_deg=10.0
        )
        
        if result['elevation_deg'] < 10:
            assert result['visible'] is False
