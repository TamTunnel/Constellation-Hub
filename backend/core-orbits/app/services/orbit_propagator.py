"""
Orbit Propagator using SGP4 algorithm.

SGP4 (Simplified General Perturbations 4) is the standard algorithm
for propagating TLE-based satellite orbits. It accounts for:
- Earth's oblateness (J2, J3, J4 terms)
- Atmospheric drag
- Solar/lunar gravitational perturbations (simplified)

This module wraps the sgp4 library to provide position and velocity
at any given time.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import math

from sgp4.api import Satrec, jday
from sgp4.api import SGP4_ERRORS


class OrbitPropagator:
    """
    Propagates satellite orbits using SGP4/SDP4.
    
    Given TLE data, computes satellite position and velocity
    at any specified time.
    """
    
    # Earth parameters
    EARTH_RADIUS_KM = 6371.0
    
    def __init__(self):
        """Initialize the orbit propagator."""
        pass
    
    def compute_position(
        self,
        tle_line1: str,
        tle_line2: str,
        target_time: datetime
    ) -> Dict[str, Any]:
        """
        Compute satellite position at a specific time.
        
        Args:
            tle_line1: First line of TLE
            tle_line2: Second line of TLE
            target_time: Time at which to compute position
            
        Returns:
            Dictionary with position data:
                - latitude (degrees, -90 to 90)
                - longitude (degrees, -180 to 180)
                - altitude_km (km above Earth surface)
                - velocity (optional velocity vector)
                - position_eci (ECI coordinates in km)
                
        Raises:
            ValueError: If TLE is invalid or propagation fails
        """
        # Ensure time is UTC
        if target_time.tzinfo is None:
            target_time = target_time.replace(tzinfo=timezone.utc)
        
        # Create satellite object from TLE
        satellite = Satrec.twoline2rv(tle_line1, tle_line2)
        
        # Convert datetime to Julian date
        jd, fr = jday(
            target_time.year,
            target_time.month,
            target_time.day,
            target_time.hour,
            target_time.minute,
            target_time.second + target_time.microsecond / 1e6
        )
        
        # Propagate to get position and velocity in ECI coordinates
        error_code, position_eci, velocity_eci = satellite.sgp4(jd, fr)
        
        if error_code != 0:
            error_msg = SGP4_ERRORS.get(error_code, f"Unknown error {error_code}")
            raise ValueError(f"SGP4 propagation failed: {error_msg}")
        
        # position_eci and velocity_eci are in km and km/s respectively
        x, y, z = position_eci
        vx, vy, vz = velocity_eci
        
        # Convert ECI to geodetic (lat, lon, alt)
        lat, lon, alt = self._eci_to_geodetic(x, y, z, target_time)
        
        # Calculate velocity magnitude
        speed = math.sqrt(vx**2 + vy**2 + vz**2)
        
        return {
            'latitude': lat,
            'longitude': lon,
            'altitude_km': alt,
            'velocity': {
                'vx': vx,
                'vy': vy,
                'vz': vz,
                'speed_kms': speed
            },
            'position_eci': {
                'x': x,
                'y': y,
                'z': z
            }
        }
    
    def compute_positions_over_time(
        self,
        tle_line1: str,
        tle_line2: str,
        start_time: datetime,
        end_time: datetime,
        step_seconds: int = 60
    ) -> list:
        """
        Compute satellite positions over a time range.
        
        Args:
            tle_line1: First line of TLE
            tle_line2: Second line of TLE
            start_time: Start of time range
            end_time: End of time range
            step_seconds: Time step between positions (default: 60s)
            
        Returns:
            List of position dictionaries with timestamps
        """
        from datetime import timedelta
        
        positions = []
        current = start_time
        
        while current <= end_time:
            try:
                pos = self.compute_position(tle_line1, tle_line2, current)
                pos['timestamp'] = current.isoformat()
                positions.append(pos)
            except ValueError:
                pass  # Skip failed propagations
            
            current += timedelta(seconds=step_seconds)
        
        return positions
    
    def get_tle_epoch(self, tle_line1: str, tle_line2: str) -> datetime:
        """
        Extract epoch datetime from TLE.
        
        Args:
            tle_line1: First line of TLE
            tle_line2: Second line of TLE
            
        Returns:
            Epoch as datetime in UTC
        """
        satellite = Satrec.twoline2rv(tle_line1, tle_line2)
        
        # satellite.jdsatepoch and satellite.jdsatepochF contain the epoch
        jd = satellite.jdsatepoch + satellite.jdsatepochF
        
        # Convert Julian date to datetime
        return self._jd_to_datetime(jd)
    
    def _eci_to_geodetic(
        self,
        x: float,
        y: float,
        z: float,
        time: datetime
    ) -> Tuple[float, float, float]:
        """
        Convert Earth-Centered Inertial (ECI) to geodetic coordinates.
        
        Uses a simplified ECEF conversion accounting for Earth's rotation.
        For more precision, use a proper geodetic library.
        
        Args:
            x, y, z: ECI position in km
            time: Time of observation for Earth rotation angle
            
        Returns:
            Tuple of (latitude_deg, longitude_deg, altitude_km)
        """
        # Earth rotation rate (rad/s)
        omega_earth = 7.2921150e-5
        
        # Calculate Greenwich Mean Sidereal Time (GMST)
        # This is a simplified calculation
        jd = self._datetime_to_jd(time)
        d = jd - 2451545.0  # Days since J2000.0
        
        # GMST in degrees
        gmst = 280.46061837 + 360.98564736629 * d
        gmst = gmst % 360
        if gmst < 0:
            gmst += 360
        gmst_rad = math.radians(gmst)
        
        # Rotate ECI to ECEF
        x_ecef = x * math.cos(gmst_rad) + y * math.sin(gmst_rad)
        y_ecef = -x * math.sin(gmst_rad) + y * math.cos(gmst_rad)
        z_ecef = z
        
        # Convert ECEF to geodetic (simple spherical Earth)
        r = math.sqrt(x_ecef**2 + y_ecef**2 + z_ecef**2)
        
        # Latitude
        lat = math.degrees(math.asin(z_ecef / r))
        
        # Longitude
        lon = math.degrees(math.atan2(y_ecef, x_ecef))
        
        # Altitude above spherical Earth
        alt = r - self.EARTH_RADIUS_KM
        
        return lat, lon, alt
    
    def _datetime_to_jd(self, dt: datetime) -> float:
        """Convert datetime to Julian date."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        y = dt.year
        m = dt.month
        d = dt.day + (dt.hour + dt.minute / 60 + dt.second / 3600) / 24
        
        if m <= 2:
            y -= 1
            m += 12
        
        a = int(y / 100)
        b = 2 - a + int(a / 4)
        
        jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5
        
        return jd
    
    def _jd_to_datetime(self, jd: float) -> datetime:
        """Convert Julian date to datetime."""
        z = int(jd + 0.5)
        f = jd + 0.5 - z
        
        if z < 2299161:
            a = z
        else:
            alpha = int((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - int(alpha / 4)
        
        b = a + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        
        day = b - d - int(30.6001 * e) + f
        
        if e < 14:
            month = e - 1
        else:
            month = e - 13
        
        if month > 2:
            year = c - 4716
        else:
            year = c - 4715
        
        # Extract time from fractional day
        day_int = int(day)
        frac = day - day_int
        hour = int(frac * 24)
        frac = frac * 24 - hour
        minute = int(frac * 60)
        frac = frac * 60 - minute
        second = int(frac * 60)
        
        return datetime(year, month, day_int, hour, minute, second, tzinfo=timezone.utc)
