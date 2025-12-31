"""
Unit tests for TLE Parser.

Tests the parsing and validation of Two-Line Element sets.
"""
import pytest
from app.services.tle_parser import TLEParser, parse_tle


# Valid TLE for ISS (ZARYA)
# Source: Historical ISS TLE
VALID_TLE_LINE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
VALID_TLE_LINE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"


class TestTLEParser:
    """Test cases for TLE parsing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = TLEParser()
    
    def test_parse_valid_tle(self):
        """Test parsing a valid TLE set."""
        result = self.parser.parse(VALID_TLE_LINE1, VALID_TLE_LINE2)
        
        assert result['catalog_number'] == '25544'
        assert result['classification'] == 'U'
        assert result['inclination_deg'] == pytest.approx(51.64, rel=0.01)
        assert result['eccentricity'] == pytest.approx(0.0006703, rel=0.01)
        assert result['mean_motion_rev_day'] == pytest.approx(15.721, rel=0.01)
    
    def test_parse_extracts_orbital_elements(self):
        """Test that all orbital elements are extracted."""
        result = self.parser.parse(VALID_TLE_LINE1, VALID_TLE_LINE2)
        
        required_fields = [
            'catalog_number', 'classification', 'epoch',
            'inclination_deg', 'raan_deg', 'eccentricity',
            'arg_perigee_deg', 'mean_anomaly_deg', 'mean_motion_rev_day',
            'semi_major_axis_km'
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_semi_major_axis_calculation(self):
        """Test semi-major axis is calculated correctly."""
        result = self.parser.parse(VALID_TLE_LINE1, VALID_TLE_LINE2)
        
        # ISS orbit is approximately 420 km altitude = 6371 + 420 = ~6791 km semi-major axis
        assert 6700 < result['semi_major_axis_km'] < 6900
    
    def test_epoch_conversion(self):
        """Test epoch is converted to datetime correctly."""
        result = self.parser.parse(VALID_TLE_LINE1, VALID_TLE_LINE2)
        
        # Epoch 08264.51782528 -> Year 2008, Day 264
        assert result['epoch'].year == 2008
        # Day 264 in leap year 2008 is Sept 20
        assert result['epoch'].month == 9
        assert result['epoch'].day == 20
    
    def test_invalid_line1_length(self):
        """Test that incorrect line 1 length raises error."""
        short_line = "1 25544U 98067A"
        
        with pytest.raises(ValueError, match="Line 1 must be 69 characters"):
            self.parser.parse(short_line, VALID_TLE_LINE2)
    
    def test_invalid_line2_length(self):
        """Test that incorrect line 2 length raises error."""
        short_line = "2 25544"
        
        with pytest.raises(ValueError, match="Line 2 must be 69 characters"):
            self.parser.parse(VALID_TLE_LINE1, short_line)
    
    def test_invalid_line_number(self):
        """Test that wrong line numbers raise error."""
        bad_line1 = "2" + VALID_TLE_LINE1[1:]
        
        with pytest.raises(ValueError, match="Line 1 must start with '1'"):
            self.parser.parse(bad_line1, VALID_TLE_LINE2)
    
    def test_catalog_number_mismatch(self):
        """Test that mismatched catalog numbers raise error."""
        different_catalog = "2 99999  51.6400 208.9163 0006703 280.7808  79.2154 15.49815776    24"
        
        with pytest.raises(ValueError, match="Catalog numbers do not match"):
            self.parser.parse(VALID_TLE_LINE1, different_catalog)
    
    def test_convenience_function(self):
        """Test the parse_tle convenience function."""
        result = parse_tle(VALID_TLE_LINE1, VALID_TLE_LINE2)
        
        assert result['catalog_number'] == '25544'
        assert 'inclination_deg' in result


class TestTLEParserExponential:
    """Test cases for exponential notation parsing."""
    
    def setup_method(self):
        self.parser = TLEParser()
    
    def test_parse_positive_exponent(self):
        """Test parsing positive exponential values."""
        # B* drag term like ' 12345+4' = 0.12345e+4
        result = self.parser._parse_exponential(" 12345+4")
        assert result == pytest.approx(1234.5, rel=0.01)
    
    def test_parse_negative_exponent(self):
        """Test parsing negative exponential values."""
        # B* drag term like ' 12345-4' = 0.12345e-4
        result = self.parser._parse_exponential(" 12345-4")
        assert result == pytest.approx(0.000012345, rel=0.01)
    
    def test_parse_zero_value(self):
        """Test parsing zero/empty exponential values."""
        result = self.parser._parse_exponential("00000-0")
        assert result == 0.0
    
    def test_parse_negative_mantissa(self):
        """Test parsing negative mantissa values."""
        # '-12345-4' = -0.12345e-4
        result = self.parser._parse_exponential("-12345-4")
        assert result == pytest.approx(-0.000012345, rel=0.01)


class TestTLEParserChecksum:
    """Test cases for TLE checksum validation."""
    
    def setup_method(self):
        self.parser = TLEParser()
    
    def test_valid_checksum(self):
        """Test that valid checksums pass validation."""
        # This should not raise
        self.parser._validate_format(VALID_TLE_LINE1, VALID_TLE_LINE2)
    
    def test_checksum_calculation(self):
        """Test checksum verification algorithm."""
        # Manually verify checksum for line 1
        assert self.parser._verify_checksum(VALID_TLE_LINE1)
        assert self.parser._verify_checksum(VALID_TLE_LINE2)
