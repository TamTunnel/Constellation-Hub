/**
 * Demo constellation data for showcasing the globe.
 * These are sample satellites and ground stations for demo purposes.
 */

export interface DemoSatellite {
    id: number;
    name: string;
    norad_id: string;
    latitude: number;
    longitude: number;
    altitude_km: number;
    constellation?: string;
}

export interface DemoGroundStation {
    id: number;
    name: string;
    latitude: number;
    longitude: number;
    elevation_m: number;
    provider?: string;
}

// Sample satellites including ISS and some Starlink-like positions
export const DEMO_SATELLITES: DemoSatellite[] = [
    // ISS
    {
        id: 1,
        name: 'ISS (ZARYA)',
        norad_id: '25544',
        latitude: 41.2,
        longitude: -73.5,
        altitude_km: 420,
        constellation: 'Space Station',
    },
    // Starlink-like satellites
    {
        id: 2,
        name: 'STARLINK-1234',
        norad_id: '48123',
        latitude: 35.5,
        longitude: -120.3,
        altitude_km: 550,
        constellation: 'Starlink',
    },
    {
        id: 3,
        name: 'STARLINK-2345',
        norad_id: '48234',
        latitude: 52.1,
        longitude: 4.5,
        altitude_km: 550,
        constellation: 'Starlink',
    },
    {
        id: 4,
        name: 'STARLINK-3456',
        norad_id: '48345',
        latitude: -15.8,
        longitude: 145.2,
        altitude_km: 550,
        constellation: 'Starlink',
    },
    {
        id: 5,
        name: 'STARLINK-4567',
        norad_id: '48456',
        latitude: 28.3,
        longitude: 77.2,
        altitude_km: 550,
        constellation: 'Starlink',
    },
    // GPS satellites
    {
        id: 6,
        name: 'GPS IIF-12',
        norad_id: '40730',
        latitude: 55.0,
        longitude: -95.0,
        altitude_km: 20200,
        constellation: 'GPS',
    },
    {
        id: 7,
        name: 'GPS III-03',
        norad_id: '48859',
        latitude: -55.0,
        longitude: 35.0,
        altitude_km: 20200,
        constellation: 'GPS',
    },
    // Weather satellite
    {
        id: 8,
        name: 'GOES-18',
        norad_id: '51850',
        latitude: 0.0,
        longitude: -137.2,
        altitude_km: 35786,
        constellation: 'Weather',
    },
    // More LEO satellites
    {
        id: 9,
        name: 'ONEWEB-0045',
        norad_id: '48925',
        latitude: 62.5,
        longitude: -142.0,
        altitude_km: 1200,
        constellation: 'OneWeb',
    },
    {
        id: 10,
        name: 'ONEWEB-0078',
        norad_id: '48956',
        latitude: -45.2,
        longitude: 28.5,
        altitude_km: 1200,
        constellation: 'OneWeb',
    },
    {
        id: 11,
        name: 'PLANET DOVE-123',
        norad_id: '49123',
        latitude: 22.5,
        longitude: -58.2,
        altitude_km: 475,
        constellation: 'Planet',
    },
    {
        id: 12,
        name: 'SPIRE LEMUR-89',
        norad_id: '49189',
        latitude: -12.3,
        longitude: 78.9,
        altitude_km: 500,
        constellation: 'Spire',
    },
];

// Sample ground stations
export const DEMO_GROUND_STATIONS: DemoGroundStation[] = [
    {
        id: 1,
        name: 'Svalbard (SvalSat)',
        latitude: 78.23,
        longitude: 15.41,
        elevation_m: 464,
        provider: 'KSAT',
    },
    {
        id: 2,
        name: 'Fairbanks (NOAA)',
        latitude: 64.97,
        longitude: -147.52,
        elevation_m: 136,
        provider: 'NOAA',
    },
    {
        id: 3,
        name: 'Wallops Island',
        latitude: 37.94,
        longitude: -75.47,
        elevation_m: 3,
        provider: 'NASA',
    },
    {
        id: 4,
        name: 'McMurdo Station',
        latitude: -77.85,
        longitude: 166.67,
        elevation_m: 10,
        provider: 'NSF',
    },
    {
        id: 5,
        name: 'Canberra DSN',
        latitude: -35.40,
        longitude: 148.98,
        elevation_m: 680,
        provider: 'NASA DSN',
    },
    {
        id: 6,
        name: 'Madrid DSN',
        latitude: 40.43,
        longitude: -4.25,
        elevation_m: 780,
        provider: 'NASA DSN',
    },
    {
        id: 7,
        name: 'Goldstone DSN',
        latitude: 35.43,
        longitude: -116.89,
        elevation_m: 1031,
        provider: 'NASA DSN',
    },
    {
        id: 8,
        name: 'Singapore',
        latitude: 1.35,
        longitude: 103.82,
        elevation_m: 15,
        provider: 'AWS Ground Station',
    },
];

// Example orbit track (ISS-like)
export function generateOrbitTrack(
    satellite: DemoSatellite,
    durationMinutes: number = 90,
    stepMinutes: number = 1
): Array<{ time: Date; latitude: number; longitude: number; altitude_km: number }> {
    const points = [];
    const now = new Date();
    const orbitalPeriodMinutes = 90; // ISS-like
    const inclination = 51.6; // degrees

    for (let t = 0; t <= durationMinutes; t += stepMinutes) {
        const time = new Date(now.getTime() + t * 60 * 1000);
        const orbitFraction = (t / orbitalPeriodMinutes) * 2 * Math.PI;

        // Simplified orbit calculation
        const lat = inclination * Math.sin(orbitFraction);
        const lon = satellite.longitude + (t * 4); // ~4 degrees per minute for LEO

        points.push({
            time,
            latitude: lat,
            longitude: ((lon + 180) % 360) - 180, // Normalize to -180 to 180
            altitude_km: satellite.altitude_km,
        });
    }

    return points;
}

// Get demo data based on mode
export function getDemoData(mode: 'full' | 'minimal' | 'empty' = 'full') {
    switch (mode) {
        case 'full':
            return {
                satellites: DEMO_SATELLITES,
                groundStations: DEMO_GROUND_STATIONS,
            };
        case 'minimal':
            return {
                satellites: DEMO_SATELLITES.slice(0, 3),
                groundStations: DEMO_GROUND_STATIONS.slice(0, 3),
            };
        case 'empty':
            return {
                satellites: [],
                groundStations: [],
            };
    }
}
