"""
TLE (Two-Line Element) parsing utilities.

TLE Format Reference:
Line 1: 
  - Columns 01-01: Line number (1)
  - Columns 03-07: Satellite catalog number
  - Column 08: Classification (U=Unclassified)
  - Columns 10-11: Launch year (last 2 digits)
  - Columns 12-14: Launch number of the year
  - Columns 15-17: Piece of the launch
  - Columns 19-20: Epoch year (last 2 digits)
  - Columns 21-32: Epoch day and fractional day
  - Columns 34-43: First derivative of mean motion / 2
  - Columns 45-52: Second derivative of mean motion / 6
  - Columns 54-61: B* drag term
  - Column 63: Ephemeris type
  - Columns 65-68: Element set number
  - Column 69: Checksum

Line 2:
  - Columns 01-01: Line number (2)
  - Columns 03-07: Satellite catalog number
  - Columns 09-16: Inclination (degrees)
  - Columns 18-25: Right Ascension of Ascending Node (degrees)
  - Columns 27-33: Eccentricity (leading decimal assumed)
  - Columns 35-42: Argument of Perigee (degrees)
  - Columns 44-51: Mean Anomaly (degrees)
  - Columns 53-63: Mean Motion (revolutions per day)
  - Columns 64-68: Revolution number at epoch
  - Column 69: Checksum
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import re


class TLEParser:
    """
    Parser for Two-Line Element sets.
    Validates TLE format and extracts orbital parameters.
    """
    
    # Earth's gravitational parameter (km^3/s^2)
    MU = 398600.4418
    
    def __init__(self):
        pass
    
    def parse(self, line1: str, line2: str) -> Dict[str, Any]:
        """
        Parse TLE lines and extract orbital elements.
        
        Args:
            line1: First line of TLE
            line2: Second line of TLE
            
        Returns:
            Dictionary containing parsed orbital elements
            
        Raises:
            ValueError: If TLE format is invalid
        """
        self._validate_format(line1, line2)
        
        # Parse Line 1
        catalog_number = line1[2:7].strip()
        classification = line1[7:8]
        launch_year = line1[9:11]
        launch_number = line1[11:14].strip()
        launch_piece = line1[14:17].strip()
        epoch_year = int(line1[18:20])
        epoch_day = float(line1[20:32])
        mean_motion_dot = float(line1[33:43].strip() or '0')
        mean_motion_ddot = self._parse_exponential(line1[44:52])
        bstar = self._parse_exponential(line1[53:61])
        ephemeris_type = int(line1[62:63] or '0')
        element_set = int(line1[64:68].strip() or '0')
        
        # Parse Line 2
        inclination = float(line2[8:16])
        raan = float(line2[17:25])
        eccentricity = float('0.' + line2[26:33].strip())
        arg_perigee = float(line2[34:42])
        mean_anomaly = float(line2[43:51])
        mean_motion = float(line2[52:63])
        rev_number = int(line2[63:68].strip() or '0')
        
        # Convert epoch
        epoch = self._epoch_to_datetime(epoch_year, epoch_day)
        
        # Calculate derived values
        n = mean_motion * 2 * 3.14159265358979 / 86400  # rad/s
        a = (self.MU / (n * n)) ** (1/3)  # Semi-major axis in km
        
        return {
            'catalog_number': catalog_number,
            'classification': classification,
            'launch_year': launch_year,
            'launch_number': launch_number,
            'launch_piece': launch_piece,
            'epoch': epoch,
            'mean_motion_dot': mean_motion_dot,
            'mean_motion_ddot': mean_motion_ddot,
            'bstar': bstar,
            'ephemeris_type': ephemeris_type,
            'element_set': element_set,
            'inclination_deg': inclination,
            'raan_deg': raan,
            'eccentricity': eccentricity,
            'arg_perigee_deg': arg_perigee,
            'mean_anomaly_deg': mean_anomaly,
            'mean_motion_rev_day': mean_motion,
            'rev_number': rev_number,
            'semi_major_axis_km': a,
        }
    
    def _validate_format(self, line1: str, line2: str) -> None:
        """Validate TLE line format and checksums."""
        if len(line1) != 69:
            raise ValueError(f"Line 1 must be 69 characters, got {len(line1)}")
        if len(line2) != 69:
            raise ValueError(f"Line 2 must be 69 characters, got {len(line2)}")
        
        if line1[0] != '1':
            raise ValueError("Line 1 must start with '1'")
        if line2[0] != '2':
            raise ValueError("Line 2 must start with '2'")
        
        # Verify catalog numbers match
        if line1[2:7] != line2[2:7]:
            raise ValueError("Catalog numbers do not match between lines")
        
        # Verify checksums
        if not self._verify_checksum(line1):
            raise ValueError("Line 1 checksum invalid")
        if not self._verify_checksum(line2):
            raise ValueError("Line 2 checksum invalid")
    
    def _verify_checksum(self, line: str) -> bool:
        """Verify TLE line checksum."""
        checksum = 0
        for char in line[:-1]:
            if char.isdigit():
                checksum += int(char)
            elif char == '-':
                checksum += 1
        checksum = checksum % 10
        
        try:
            return checksum == int(line[-1])
        except ValueError:
            return False
    
    def _parse_exponential(self, value: str) -> float:
        """Parse TLE exponential format (e.g., ' 12345-4' -> 0.12345e-4)."""
        value = value.strip()
        if not value or value == '00000-0':
            return 0.0
        
        # Handle format like ' 12345-4' or '-12345-4'
        match = re.match(r'([+-]?)(\d+)([+-])(\d)', value)
        if match:
            sign = -1 if match.group(1) == '-' else 1
            mantissa = float('0.' + match.group(2))
            exp_sign = -1 if match.group(3) == '-' else 1
            exponent = int(match.group(4)) * exp_sign
            return sign * mantissa * (10 ** exponent)
        
        return 0.0
    
    def _epoch_to_datetime(self, year: int, day: float) -> datetime:
        """Convert TLE epoch (year + fractional day) to datetime."""
        # Handle 2-digit year (assume 1957-2056 range)
        if year < 57:
            year += 2000
        else:
            year += 1900
        
        # Convert day of year to datetime
        jan1 = datetime(year, 1, 1, tzinfo=timezone.utc)
        epoch = jan1 + (day - 1) * 86400 * 1e-6  # Convert to timedelta
        
        # Actually, let's do this properly
        from datetime import timedelta
        epoch = jan1 + timedelta(days=day - 1)
        
        return epoch


def parse_tle(line1: str, line2: str) -> Dict[str, Any]:
    """Convenience function to parse TLE."""
    parser = TLEParser()
    return parser.parse(line1, line2)
