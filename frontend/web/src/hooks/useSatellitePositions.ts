/**
 * useSatellitePositions - Hook for fetching and updating satellite positions.
 */
import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { coreOrbitsClient } from '../api/client';

interface SatellitePosition {
    id: number;
    name: string;
    norad_id?: string;
    latitude: number;
    longitude: number;
    altitude_km: number;
    velocity_km_s?: number;
}

interface UseSatellitePositionsOptions {
    constellationId?: number;
    pollInterval?: number; // milliseconds
    timeOffset?: number; // seconds from now
    enabled?: boolean;
}

export function useSatellitePositions(options: UseSatellitePositionsOptions = {}) {
    const {
        constellationId,
        pollInterval = 10000, // 10 seconds default
        timeOffset = 0,
        enabled = true,
    } = options;

    const [positions, setPositions] = useState<SatellitePosition[]>([]);

    // Fetch satellites
    const { data: satellites, isLoading, error } = useQuery({
        queryKey: ['satellites', constellationId],
        queryFn: async () => {
            const url = constellationId
                ? `/satellites?constellation_id=${constellationId}`
                : '/satellites';
            const response = await coreOrbitsClient.get(url);
            return response.data.items || response.data;
        },
        enabled,
        refetchInterval: pollInterval,
    });

    // Compute positions with time offset
    useEffect(() => {
        if (!satellites || satellites.length === 0) return;

        // For demo, use static positions from satellite data
        // In production, this would call /satellites/{id}/position?time=...
        const newPositions: SatellitePosition[] = satellites.map((sat: Record<string, unknown>) => {
            // If satellite has TLE data and we have time offset, compute position
            // For now, use stored lat/long or mock positions
            return {
                id: sat.id as number,
                name: sat.name as string,
                norad_id: sat.norad_id as string | undefined,
                latitude: (sat.latitude as number) || Math.random() * 180 - 90,
                longitude: (sat.longitude as number) || Math.random() * 360 - 180,
                altitude_km: (sat.altitude_km as number) || 550,
            };
        });

        setPositions(newPositions);
    }, [satellites, timeOffset]);

    return {
        positions,
        isLoading,
        error,
        satellites,
    };
}

/**
 * useGroundStations - Hook for fetching ground stations.
 */
export function useGroundStations(options: { enabled?: boolean } = {}) {
    const { enabled = true } = options;

    return useQuery({
        queryKey: ['groundStations'],
        queryFn: async () => {
            // Ground stations are in the ground-scheduler service
            try {
                const response = await fetch(
                    import.meta.env.VITE_GROUND_SCHEDULER_URL + '/ground-stations'
                );
                if (!response.ok) throw new Error('Failed to fetch ground stations');
                const data = await response.json();
                return data.items || data;
            } catch {
                // Return mock data for demo
                return [
                    { id: 1, name: 'GS-Alpha', latitude: 40.7, longitude: -74.0, elevation_m: 10 },
                    { id: 2, name: 'GS-Beta', latitude: 51.5, longitude: -0.1, elevation_m: 50 },
                    { id: 3, name: 'GS-Gamma', latitude: 35.7, longitude: 139.7, elevation_m: 40 },
                    { id: 4, name: 'GS-Delta', latitude: -33.9, longitude: 151.2, elevation_m: 5 },
                ];
            }
        },
        enabled,
        staleTime: 60000, // 1 minute
    });
}

/**
 * useTLEStatus - Hook for TLE feed status.
 */
export function useTLEStatus() {
    return useQuery({
        queryKey: ['tleStatus'],
        queryFn: async () => {
            const response = await coreOrbitsClient.get('/tle/status');
            return response.data;
        },
        staleTime: 30000, // 30 seconds
    });
}

/**
 * useRefreshTLE - Mutation hook for triggering TLE refresh.
 */
export function useRefreshTLE() {
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const refresh = useCallback(async (catalogs?: string[]) => {
        setIsRefreshing(true);
        setError(null);

        try {
            const response = await coreOrbitsClient.post('/tle/refresh', {
                catalogs: catalogs || ['active'],
            });
            return response.data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Refresh failed';
            setError(message);
            throw err;
        } finally {
            setIsRefreshing(false);
        }
    }, []);

    return { refresh, isRefreshing, error };
}
