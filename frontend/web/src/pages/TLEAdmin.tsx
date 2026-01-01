/**
 * TLEAdmin - Admin page for TLE feed management.
 */
import { useState } from 'react';
import { RefreshCw, Database, Clock, CheckCircle, AlertCircle, Satellite } from 'lucide-react';
import { useTLEStatus, useRefreshTLE } from '../hooks/useSatellitePositions';
import { useQuery } from '@tanstack/react-query';
import { coreOrbitsClient } from '../api/client';

const CATALOGS = [
    { value: 'active', label: 'Active Satellites', description: 'All operational satellites' },
    { value: 'stations', label: 'Space Stations', description: 'ISS, Tiangong, etc.' },
    { value: 'starlink', label: 'Starlink', description: 'SpaceX Starlink constellation' },
    { value: 'oneweb', label: 'OneWeb', description: 'OneWeb constellation' },
    { value: 'gps-ops', label: 'GPS', description: 'GPS navigation satellites' },
    { value: 'galileo', label: 'Galileo', description: 'EU navigation satellites' },
    { value: 'weather', label: 'Weather', description: 'Weather satellites' },
];

export default function TLEAdmin() {
    const [selectedCatalogs, setSelectedCatalogs] = useState<string[]>(['active']);
    const { data: status, isLoading: statusLoading, refetch: refetchStatus } = useTLEStatus();
    const { refresh, isRefreshing, error: refreshError } = useRefreshTLE();
    const [lastResult, setLastResult] = useState<{ satellites_fetched: number; satellites_stored: number } | null>(null);

    // Fetch TLE satellites
    const { data: tleSatellites, isLoading: satellitesLoading } = useQuery({
        queryKey: ['tleSatellites'],
        queryFn: async () => {
            const response = await coreOrbitsClient.get('/tle/satellites?limit=20');
            return response.data;
        },
    });

    const handleRefresh = async () => {
        try {
            const result = await refresh(selectedCatalogs);
            setLastResult(result);
            refetchStatus();
        } catch {
            // Error handled by hook
        }
    };

    const toggleCatalog = (catalog: string) => {
        setSelectedCatalogs(prev =>
            prev.includes(catalog)
                ? prev.filter(c => c !== catalog)
                : [...prev, catalog]
        );
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">TLE Feed Administration</h1>
                <p className="text-white/60 mt-1">
                    Manage Two-Line Element data from external sources
                </p>
            </div>

            {/* Status Card */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-cosmic-500/20 rounded-lg">
                            <Database className="w-6 h-6 text-cosmic-400" />
                        </div>
                        <div>
                            <p className="text-white/60 text-sm">Satellites Tracked</p>
                            <p className="text-2xl font-bold">
                                {statusLoading ? '...' : status?.satellite_count || 0}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-aurora-500/20 rounded-lg">
                            <Clock className="w-6 h-6 text-aurora-400" />
                        </div>
                        <div>
                            <p className="text-white/60 text-sm">Last Refresh</p>
                            <p className="text-lg font-semibold">
                                {status?.last_refresh
                                    ? new Date(status.last_refresh).toLocaleString()
                                    : 'Never'}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-nebula-500/20 rounded-lg">
                            <RefreshCw className="w-6 h-6 text-nebula-400" />
                        </div>
                        <div>
                            <p className="text-white/60 text-sm">Refresh Interval</p>
                            <p className="text-lg font-semibold">
                                {status?.refresh_interval_hours || 6} hours
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Refresh Controls */}
            <div className="card">
                <h2 className="text-lg font-semibold mb-4">Refresh TLE Data</h2>

                {/* Catalog Selection */}
                <div className="mb-4">
                    <p className="text-white/60 text-sm mb-2">Select catalogs to refresh:</p>
                    <div className="flex flex-wrap gap-2">
                        {CATALOGS.map(catalog => (
                            <button
                                key={catalog.value}
                                onClick={() => toggleCatalog(catalog.value)}
                                className={`
                                    px-3 py-2 rounded-lg text-sm transition-all
                                    ${selectedCatalogs.includes(catalog.value)
                                        ? 'bg-cosmic-500 text-white'
                                        : 'bg-space-700 text-white/60 hover:bg-space-600'}
                                `}
                                title={catalog.description}
                            >
                                {catalog.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Refresh Button */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleRefresh}
                        disabled={isRefreshing || selectedCatalogs.length === 0}
                        className={`
                            btn-primary flex items-center gap-2
                            ${isRefreshing ? 'opacity-50 cursor-not-allowed' : ''}
                        `}
                    >
                        <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                        {isRefreshing ? 'Refreshing...' : 'Refresh Now'}
                    </button>

                    {/* Result message */}
                    {lastResult && (
                        <div className="flex items-center gap-2 text-aurora-400">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm">
                                Fetched {lastResult.satellites_fetched} satellites,
                                stored {lastResult.satellites_stored}
                            </span>
                        </div>
                    )}

                    {refreshError && (
                        <div className="flex items-center gap-2 text-red-400">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-sm">{refreshError}</span>
                        </div>
                    )}
                </div>
            </div>

            {/* Recent TLE Records */}
            <div className="card">
                <h2 className="text-lg font-semibold mb-4">Recent TLE Records</h2>

                {satellitesLoading ? (
                    <div className="text-center py-8 text-white/60">
                        Loading...
                    </div>
                ) : tleSatellites && tleSatellites.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-white/60 text-sm border-b border-white/10">
                                    <th className="pb-3">Name</th>
                                    <th className="pb-3">NORAD ID</th>
                                    <th className="pb-3">Source</th>
                                    <th className="pb-3">Epoch</th>
                                    <th className="pb-3">Fetched</th>
                                </tr>
                            </thead>
                            <tbody>
                                {tleSatellites.map((sat: Record<string, unknown>, index: number) => (
                                    <tr
                                        key={index}
                                        className="border-b border-white/5 hover:bg-white/5"
                                    >
                                        <td className="py-3 flex items-center gap-2">
                                            <Satellite className="w-4 h-4 text-cosmic-400" />
                                            {sat.name as string}
                                        </td>
                                        <td className="py-3 font-mono text-sm text-white/60">
                                            {sat.norad_id as string}
                                        </td>
                                        <td className="py-3">
                                            <span className="px-2 py-1 bg-cosmic-500/20 text-cosmic-400 rounded text-xs">
                                                {sat.source as string}
                                            </span>
                                        </td>
                                        <td className="py-3 text-sm text-white/60">
                                            {sat.epoch
                                                ? new Date(sat.epoch as string).toLocaleDateString()
                                                : 'N/A'}
                                        </td>
                                        <td className="py-3 text-sm text-white/60">
                                            {sat.fetched_at
                                                ? new Date(sat.fetched_at as string).toLocaleString()
                                                : 'N/A'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="text-center py-8 text-white/60">
                        <p>No TLE records yet.</p>
                        <p className="text-sm mt-1">Click "Refresh Now" to fetch satellite data.</p>
                    </div>
                )}
            </div>

            {/* Source Status */}
            <div className="card">
                <h2 className="text-lg font-semibold mb-4">Data Sources</h2>
                <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-space-700/50 rounded-lg">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 bg-aurora-500 rounded-full" />
                            <span>CelesTrak</span>
                        </div>
                        <span className="text-aurora-400 text-sm">Configured</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-space-700/50 rounded-lg">
                        <div className="flex items-center gap-3">
                            <div className="w-2 h-2 bg-white/30 rounded-full" />
                            <span>Space-Track.org</span>
                        </div>
                        <span className="text-white/40 text-sm">Not Configured</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
