"""
TLE (Two-Line Element) Feed Ingestion Service.

Fetches TLE data from external sources and stores it in the database.
Supports:
- CelesTrak (free, no auth required)
- Space-Track (requires credentials, for future implementation)
"""
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

import httpx

try:
    from common.logger import get_logger
    from common.config import get_settings
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    class get_settings:
        celestrak_base_url = "https://celestrak.org"
        tle_refresh_interval_hours = 6

logger = get_logger("tle-ingestion")


class TLESource(str, Enum):
    """Supported TLE data sources."""
    CELESTRAK = "celestrak"
    SPACETRACK = "spacetrack"


@dataclass
class TLERecord:
    """Container for TLE data."""
    norad_id: str
    name: str
    tle_line1: str
    tle_line2: str
    source: TLESource
    epoch: Optional[datetime] = None
    fetched_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "norad_id": self.norad_id,
            "name": self.name,
            "tle_line1": self.tle_line1,
            "tle_line2": self.tle_line2,
            "source": self.source.value,
            "epoch": self.epoch.isoformat() if self.epoch else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }


class CelesTrakCatalog(str, Enum):
    """CelesTrak satellite catalogs."""
    ACTIVE = "active"
    STATIONS = "stations"  # Space stations (ISS, Tiangong)
    STARLINK = "starlink"
    ONEWEB = "oneweb"
    IRIDIUM = "iridium"
    GLOBALSTAR = "globalstar"
    PLANET = "planet"
    SPIRE = "spire"
    GPS = "gps-ops"
    GLONASS = "glo-ops"
    GALILEO = "galileo"
    WEATHER = "weather"
    RESOURCE = "resource"
    SCIENCE = "science"
    LAST_30_DAYS = "tle-new"


class TLEIngestionService:
    """
    Service for fetching and managing TLE data.
    
    Usage:
        service = TLEIngestionService()
        records = await service.fetch_celestrak(CelesTrakCatalog.ACTIVE)
        count = await service.update_database(records, db_session)
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.last_refresh: Optional[datetime] = None
        self.last_count: int = 0
        self.http_client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.http_client = httpx.AsyncClient(timeout=60.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.http_client:
            await self.http_client.aclose()
    
    def _get_celestrak_url(self, catalog: CelesTrakCatalog) -> str:
        """Build CelesTrak URL for given catalog."""
        base_url = self.settings.celestrak_base_url
        return f"{base_url}/NORAD/elements/gp.php?GROUP={catalog.value}&FORMAT=tle"
    
    def _parse_tle_text(self, tle_text: str, source: TLESource) -> List[TLERecord]:
        """
        Parse TLE text format into TLERecord objects.
        
        TLE format (3 lines per satellite):
        Line 0: Satellite name
        Line 1: TLE line 1 (starts with '1 ')
        Line 2: TLE line 2 (starts with '2 ')
        """
        records = []
        lines = tle_text.strip().split('\n')
        now = datetime.now(timezone.utc)
        
        i = 0
        while i < len(lines) - 2:
            # Look for name line followed by TLE lines
            name_line = lines[i].strip()
            line1 = lines[i + 1].strip() if i + 1 < len(lines) else ""
            line2 = lines[i + 2].strip() if i + 2 < len(lines) else ""
            
            # Check if this looks like a valid TLE set
            if (line1.startswith('1 ') and 
                line2.startswith('2 ') and
                len(line1) >= 69 and 
                len(line2) >= 69):
                
                # Extract NORAD ID from line 1 (columns 3-7)
                norad_id = line1[2:7].strip()
                
                # Parse epoch from line 1
                epoch = self._parse_epoch(line1)
                
                record = TLERecord(
                    norad_id=norad_id,
                    name=name_line,
                    tle_line1=line1,
                    tle_line2=line2,
                    source=source,
                    epoch=epoch,
                    fetched_at=now
                )
                records.append(record)
                i += 3  # Skip to next satellite
            else:
                i += 1  # Move to next line and try again
        
        return records
    
    def _parse_epoch(self, tle_line1: str) -> Optional[datetime]:
        """
        Parse epoch from TLE line 1.
        
        Epoch format in columns 19-32: YYDDD.DDDDDDDD
        - YY: 2-digit year (00-56 = 2000-2056, 57-99 = 1957-1999)
        - DDD.DDDDDDDD: Day of year with fractional part
        """
        try:
            epoch_str = tle_line1[18:32].strip()
            year_str = epoch_str[:2]
            day_str = epoch_str[2:]
            
            year = int(year_str)
            if year < 57:
                year += 2000
            else:
                year += 1900
            
            day = float(day_str)
            
            # Convert to datetime
            jan1 = datetime(year, 1, 1, tzinfo=timezone.utc)
            from datetime import timedelta
            epoch = jan1 + timedelta(days=day - 1)
            
            return epoch
        except (ValueError, IndexError):
            return None
    
    async def fetch_celestrak(
        self, 
        catalog: CelesTrakCatalog = CelesTrakCatalog.ACTIVE
    ) -> List[TLERecord]:
        """
        Fetch TLE data from CelesTrak.
        
        Args:
            catalog: Which satellite catalog to fetch
            
        Returns:
            List of TLERecord objects
        """
        url = self._get_celestrak_url(catalog)
        logger.info(f"Fetching TLE data from CelesTrak: {catalog.value}")
        
        try:
            if not self.http_client:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.get(url)
            else:
                response = await self.http_client.get(url)
            
            response.raise_for_status()
            tle_text = response.text
            
            records = self._parse_tle_text(tle_text, TLESource.CELESTRAK)
            logger.info(f"Parsed {len(records)} TLE records from CelesTrak {catalog.value}")
            
            return records
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch from CelesTrak: {e}")
            raise
    
    async def fetch_spacetrack(
        self,
        norad_ids: Optional[List[str]] = None
    ) -> List[TLERecord]:
        """
        Fetch TLE data from Space-Track.org.
        
        NOTE: This is a placeholder for future implementation.
        Requires Space-Track account credentials.
        
        Args:
            norad_ids: Optional list of specific NORAD IDs to fetch
            
        Returns:
            List of TLERecord objects
        """
        # TODO: Implement Space-Track integration
        # Requires:
        # 1. Login with credentials (SPACETRACK_USERNAME, SPACETRACK_PASSWORD)
        # 2. Request TLE data via their API
        # 3. Handle rate limiting
        
        logger.warning("Space-Track integration not yet implemented")
        return []
    
    async def fetch_multiple_catalogs(
        self,
        catalogs: List[CelesTrakCatalog]
    ) -> List[TLERecord]:
        """
        Fetch TLE data from multiple catalogs.
        
        Args:
            catalogs: List of catalogs to fetch
            
        Returns:
            Combined list of TLERecord objects (deduplicated by NORAD ID)
        """
        all_records = []
        seen_norad_ids = set()
        
        for catalog in catalogs:
            try:
                records = await self.fetch_celestrak(catalog)
                for record in records:
                    if record.norad_id not in seen_norad_ids:
                        all_records.append(record)
                        seen_norad_ids.add(record.norad_id)
            except Exception as e:
                logger.error(f"Failed to fetch catalog {catalog.value}: {e}")
                continue
        
        return all_records
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ingestion status."""
        return {
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None,
            "last_count": self.last_count,
            "refresh_interval_hours": self.settings.tle_refresh_interval_hours,
            "sources": {
                "celestrak": {
                    "base_url": self.settings.celestrak_base_url,
                    "status": "configured"
                },
                "spacetrack": {
                    "status": "not_configured"  # Future
                }
            }
        }


# Convenience function for one-off fetches
async def fetch_active_satellites() -> List[TLERecord]:
    """Fetch TLE data for all active satellites."""
    async with TLEIngestionService() as service:
        return await service.fetch_celestrak(CelesTrakCatalog.ACTIVE)


async def fetch_sample_satellites() -> List[TLERecord]:
    """Fetch TLE data for common demo satellites (ISS, Starlink sample)."""
    async with TLEIngestionService() as service:
        records = []
        
        # Fetch space stations (includes ISS)
        try:
            stations = await service.fetch_celestrak(CelesTrakCatalog.STATIONS)
            records.extend(stations[:5])  # Just first 5
        except Exception:
            pass
        
        # Fetch some Starlink
        try:
            starlink = await service.fetch_celestrak(CelesTrakCatalog.STARLINK)
            records.extend(starlink[:20])  # Just first 20
        except Exception:
            pass
        
        return records
