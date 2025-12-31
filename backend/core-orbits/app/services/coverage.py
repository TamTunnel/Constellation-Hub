"""
Coverage footprint computation.

A satellite's coverage footprint is the area on Earth's surface
that can communicate with the satellite. This depends on:
- Satellite altitude
- Minimum elevation angle (antenna/reception constraints)
- Earth's curvature

For a first approximation, we use a simple circular footprint
based on the geometric horizon visible from the satellite.
"""
import math
from typing import Dict, Any, List, Optional


class CoverageCalculator:
    """
    Computes satellite ground coverage footprints.
    
    The coverage radius is calculated based on the satellite's altitude
    and a minimum elevation angle constraint.
    """
    
    # Earth parameters
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self, min_elevation_deg: float = 10.0):
        """
        Initialize coverage calculator.
        
        Args:
            min_elevation_deg: Minimum elevation angle in degrees.
                               Objects below this angle from the ground
                               station's horizon are not visible.
        """
        self.min_elevation_deg = min_elevation_deg
    
    def compute_footprint(
        self,
        center_lat: float,
        center_lon: float,
        altitude_km: float,
        min_elevation_deg: Optional[float] = None,
        num_polygon_points: int = 36
    ) -> Dict[str, Any]:
        """
        Compute the coverage footprint for a satellite.
        
        Args:
            center_lat: Satellite nadir latitude (degrees)
            center_lon: Satellite nadir longitude (degrees)  
            altitude_km: Satellite altitude above Earth surface (km)
            min_elevation_deg: Override default minimum elevation
            num_polygon_points: Number of points for polygon approximation
            
        Returns:
            Dictionary containing:
                - radius_km: Coverage radius in kilometers
                - radius_deg: Coverage radius in degrees of arc
                - polygon: List of {lat, lon} points forming the footprint boundary
        """
        min_elev = min_elevation_deg if min_elevation_deg is not None else self.min_elevation_deg
        
        # Calculate coverage radius
        radius_km, radius_deg = self._compute_coverage_radius(altitude_km, min_elev)
        
        # Generate polygon points
        polygon = self._generate_polygon(
            center_lat, center_lon, radius_deg, num_polygon_points
        )
        
        return {
            'radius_km': radius_km,
            'radius_deg': radius_deg,
            'polygon': polygon
        }
    
    def _compute_coverage_radius(
        self,
        altitude_km: float,
        min_elevation_deg: float
    ) -> tuple:
        """
        Calculate the coverage radius based on geometry.
        
        The coverage radius is the ground distance from the nadir point
        to the edge of the coverage area, where the satellite appears
        at the minimum elevation angle.
        
        Geometry:
        - Earth radius: R
        - Satellite altitude: h
        - Minimum elevation angle: E
        - Earth central angle (coverage): θ
        - Slant range: d
        
        From spherical geometry:
        cos(θ + E) = R * cos(E) / (R + h)
        
        Args:
            altitude_km: Satellite altitude
            min_elevation_deg: Minimum elevation angle
            
        Returns:
            Tuple of (radius_km, radius_deg)
        """
        R = self.EARTH_RADIUS_KM
        h = altitude_km
        E = math.radians(min_elevation_deg)
        
        # Calculate Earth central angle to coverage edge
        # Using law of sines and geometry
        rho = math.asin(R * math.cos(E) / (R + h))  # nadir angle
        
        # Earth central angle
        theta = math.pi/2 - E - rho
        
        # Convert to radius
        radius_deg = math.degrees(theta)
        radius_km = theta * R
        
        return radius_km, radius_deg
    
    def _generate_polygon(
        self,
        center_lat: float,
        center_lon: float,
        radius_deg: float,
        num_points: int
    ) -> List[Dict[str, float]]:
        """
        Generate polygon points approximating the circular footprint.
        
        Uses a simple spherical Earth approximation for calculating
        points on the coverage boundary.
        
        Args:
            center_lat: Center latitude (degrees)
            center_lon: Center longitude (degrees)
            radius_deg: Radius in degrees of arc
            num_points: Number of polygon vertices
            
        Returns:
            List of {latitude, longitude} dictionaries
        """
        polygon = []
        center_lat_rad = math.radians(center_lat)
        center_lon_rad = math.radians(center_lon)
        radius_rad = math.radians(radius_deg)
        
        for i in range(num_points):
            # Bearing from center (0 to 2π)
            bearing = 2 * math.pi * i / num_points
            
            # Calculate destination point using spherical geometry
            # (Haversine inverse)
            lat2 = math.asin(
                math.sin(center_lat_rad) * math.cos(radius_rad) +
                math.cos(center_lat_rad) * math.sin(radius_rad) * math.cos(bearing)
            )
            
            lon2 = center_lon_rad + math.atan2(
                math.sin(bearing) * math.sin(radius_rad) * math.cos(center_lat_rad),
                math.cos(radius_rad) - math.sin(center_lat_rad) * math.sin(lat2)
            )
            
            # Convert back to degrees
            lat_deg = math.degrees(lat2)
            lon_deg = math.degrees(lon2)
            
            # Normalize longitude to -180 to 180
            while lon_deg > 180:
                lon_deg -= 360
            while lon_deg < -180:
                lon_deg += 360
            
            polygon.append({
                'latitude': lat_deg,
                'longitude': lon_deg
            })
        
        # Close the polygon
        if polygon:
            polygon.append(polygon[0].copy())
        
        return polygon
    
    def compute_horizon_distance(self, altitude_km: float) -> float:
        """
        Calculate the geometric horizon distance for a satellite.
        
        This is the maximum distance at which an observer on Earth
        could theoretically see the satellite (at 0° elevation).
        
        Args:
            altitude_km: Satellite altitude
            
        Returns:
            Horizon distance in km
        """
        R = self.EARTH_RADIUS_KM
        h = altitude_km
        
        # Geometric horizon: sqrt((R+h)^2 - R^2) = sqrt(h^2 + 2*R*h)
        return math.sqrt(h * h + 2 * R * h)
    
    def is_visible(
        self,
        sat_lat: float,
        sat_lon: float,
        sat_alt_km: float,
        observer_lat: float,
        observer_lon: float,
        observer_alt_m: float = 0,
        min_elevation_deg: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Check if a satellite is visible from an observer location.
        
        Args:
            sat_lat, sat_lon, sat_alt_km: Satellite position
            observer_lat, observer_lon: Observer position (degrees)
            observer_alt_m: Observer altitude above sea level (meters)
            min_elevation_deg: Minimum elevation angle
            
        Returns:
            Dictionary with:
                - visible: bool
                - elevation_deg: Elevation angle (if visible)
                - distance_km: Slant range to satellite
        """
        min_elev = min_elevation_deg if min_elevation_deg is not None else self.min_elevation_deg
        
        # Calculate ground distance using haversine
        R = self.EARTH_RADIUS_KM
        lat1, lon1 = math.radians(observer_lat), math.radians(observer_lon)
        lat2, lon2 = math.radians(sat_lat), math.radians(sat_lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        ground_distance = R * c
        
        # Calculate elevation angle
        # Using spherical geometry: satellite height h, earth central angle c
        # tan(elevation) = (cos(c) - R/(R+h)) / sin(c)
        h = sat_alt_km
        
        if ground_distance < 0.001:  # Nearly overhead
            elevation = 90.0
        else:
            # More accurate calculation
            _sin_c = math.sin(c)  # noqa: F841
            cos_c = math.cos(c)
            
            # Slant range
            slant_range = R * math.sqrt(1 + ((R + h) / R)**2 - 2 * (R + h) / R * cos_c)
            
            # Elevation angle
            sin_elev = ((R + h) * cos_c - R) / slant_range
            elevation = math.degrees(math.asin(max(-1, min(1, sin_elev))))
        
        visible = elevation >= min_elev
        
        # Calculate slant range
        slant_range = math.sqrt(
            ground_distance**2 + 
            (h - observer_alt_m/1000)**2 + 
            2 * R * (1 - math.cos(c)) * h
        )
        
        return {
            'visible': visible,
            'elevation_deg': elevation,
            'distance_km': slant_range,
            'ground_distance_km': ground_distance
        }
