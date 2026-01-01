# TLE Feed Integration

This document describes the TLE (Two-Line Element) feed integration for Constellation Hub.

## Overview

Constellation Hub ingests TLE data from external sources to track satellite positions. TLE data is the standard format for orbital elements published by organizations like NORAD and CelesTrak.

## Supported Sources

### CelesTrak (Primary)

**Status**: ✅ Fully Implemented

CelesTrak provides free TLE data for most tracked objects.

- **URL**: https://celestrak.org
- **Authentication**: None required
- **Rate Limits**: Fair use policy
- **Update Frequency**: Data updated by CelesTrak every few hours

#### Available Catalogs

| Catalog | Description | Approximate Count |
|---------|-------------|-------------------|
| `active` | All operational satellites | ~8,000 |
| `stations` | Space stations (ISS, Tiangong) | ~5 |
| `starlink` | SpaceX Starlink constellation | ~5,000+ |
| `oneweb` | OneWeb constellation | ~600+ |
| `iridium` | Iridium constellation | ~75 |
| `gps-ops` | GPS satellites | ~30 |
| `galileo` | Galileo navigation | ~30 |
| `weather` | Weather satellites | ~50 |

### Space-Track (Future)

**Status**: 🔜 Planned

Space-Track.org requires a free account for API access.

- **URL**: https://space-track.org
- **Authentication**: Username/password required
- **Rate Limits**: Documented quotas
- **Update Frequency**: Near real-time

Configuration placeholders:
```bash
SPACETRACK_USERNAME=your-username
SPACETRACK_PASSWORD=your-password
```

---

## API Endpoints

### Get TLE Status

```
GET /tle/status
```

Returns current ingestion status:

```json
{
  "last_refresh": "2026-01-01T12:00:00+00:00",
  "satellite_count": 1523,
  "refresh_interval_hours": 6,
  "sources": {
    "celestrak": {"base_url": "https://celestrak.org", "status": "configured"},
    "spacetrack": {"status": "not_configured"}
  }
}
```

### List TLE Satellites

```
GET /tle/satellites?skip=0&limit=100&source=celestrak
```

Returns satellite TLE records:

```json
[
  {
    "norad_id": "25544",
    "name": "ISS (ZARYA)",
    "tle_line1": "1 25544U 98067A   26001.50000000  .00016717  00000+0  30000-3 0  9990",
    "tle_line2": "2 25544  51.6416  21.5410 0001264 233.2354 126.8365 15.49896578484000",
    "source": "celestrak",
    "epoch": "2026-01-01T12:00:00+00:00",
    "fetched_at": "2026-01-01T12:30:00+00:00"
  }
]
```

### Get Satellite TLE by NORAD ID

```
GET /tle/satellites/25544
```

### Refresh TLE Data

```
POST /tle/refresh
Content-Type: application/json

{
  "catalogs": ["active", "stations"],
  "force": false
}
```

**Requires**: Operator role or higher

Response:
```json
{
  "status": "success",
  "satellites_fetched": 8234,
  "satellites_stored": 8234,
  "message": "Refreshed TLE data from 2 catalog(s)"
}
```

### List Available Catalogs

```
GET /tle/catalogs
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TLE_REFRESH_INTERVAL_HOURS` | How often to auto-refresh | `6` |
| `CELESTRAK_BASE_URL` | CelesTrak API base URL | `https://celestrak.org` |
| `SPACETRACK_USERNAME` | Space-Track.org username | (empty) |
| `SPACETRACK_PASSWORD` | Space-Track.org password | (empty) |

---

## Automatic Refresh

TLE data can become stale. For accurate orbit prediction:

- **LEO satellites** (400-2000 km): TLEs good for 1-7 days
- **MEO satellites** (2000-35786 km): TLEs good for 2-4 weeks
- **GEO satellites** (35786 km): TLEs good for weeks to months

### Manual Refresh

Use the admin UI or API to trigger a refresh:

```bash
curl -X POST http://localhost:8001/tle/refresh \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"catalogs": ["active"]}'
```

### Scheduled Refresh

For production, set up a cron job or use the background scheduler:

```bash
# Example crontab entry - refresh every 6 hours
0 */6 * * * curl -X POST http://localhost:8001/tle/refresh -H "Authorization: Bearer $TOKEN"
```

---

## TLE Format

Two-Line Element sets consist of:

```
ISS (ZARYA)
1 25544U 98067A   26001.50000000  .00016717  00000+0  30000-3 0  9990
2 25544  51.6416  21.5410 0001264 233.2354 126.8365 15.49896578484000
```

### Line 0: Satellite Name

### Line 1 Fields:

| Column | Description |
|--------|-------------|
| 1 | Line number (1) |
| 3-7 | NORAD Catalog Number |
| 8 | Classification (U=unclassified) |
| 10-17 | International Designator |
| 19-32 | Epoch (YYDDD.DDDDDDDD) |
| 34-43 | First derivative of mean motion |
| 45-52 | Second derivative of mean motion |
| 54-61 | BSTAR drag term |
| 63 | Ephemeris type |
| 65-68 | Element set number |
| 69 | Checksum |

### Line 2 Fields:

| Column | Description |
|--------|-------------|
| 1 | Line number (2) |
| 3-7 | NORAD Catalog Number |
| 9-16 | Inclination (degrees) |
| 18-25 | Right Ascension (degrees) |
| 27-33 | Eccentricity (decimal point assumed) |
| 35-42 | Argument of Perigee (degrees) |
| 44-51 | Mean Anomaly (degrees) |
| 53-63 | Mean Motion (revolutions/day) |
| 64-68 | Revolution number at epoch |
| 69 | Checksum |

---

## Usage Examples

### Python

```python
from app.services.tle_ingestion import TLEIngestionService, CelesTrakCatalog

async def refresh_tle():
    async with TLEIngestionService() as service:
        records = await service.fetch_celestrak(CelesTrakCatalog.STARLINK)
        print(f"Fetched {len(records)} Starlink satellites")
        return records
```

### Frontend

```typescript
// Fetch TLE status
const status = await fetch('/tle/status').then(r => r.json());
console.log(`Last refresh: ${status.last_refresh}`);
console.log(`Satellites tracked: ${status.satellite_count}`);

// Trigger refresh (requires auth)
await fetch('/tle/refresh', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ catalogs: ['active'] })
});
```

---

## Limitations and Caveats

### Demo vs Production

- **Demo mode**: Uses CelesTrak free tier, suitable for testing
- **Production**: Consider Space-Track for better data quality and licensing

### Data Accuracy

- TLE accuracy degrades over time due to atmospheric drag and perturbations
- For critical applications, refresh TLEs frequently
- Use SGP4 propagator (included) for position prediction

### Legal Considerations

- CelesTrak data is provided under fair use
- Space-Track requires acceptance of their User Agreement
- Some satellite data may have restrictions
