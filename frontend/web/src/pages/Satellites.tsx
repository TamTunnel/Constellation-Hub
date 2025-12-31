import { useState } from 'react';
import { Satellite, Plus, Search, Filter, RefreshCw } from 'lucide-react';

const mockSatellites = [
    { id: 1, name: 'SAT-001', noradId: '25544', constellation: 'LEO-NET', status: 'healthy', altitude: 550, inclination: 51.6 },
    { id: 2, name: 'SAT-002', noradId: '25545', constellation: 'LEO-NET', status: 'healthy', altitude: 560, inclination: 51.6 },
    { id: 3, name: 'SAT-003', noradId: '25546', constellation: 'LEO-NET', status: 'degraded', altitude: 545, inclination: 51.6 },
    { id: 4, name: 'SAT-004', noradId: '25547', constellation: 'LEO-NET', status: 'healthy', altitude: 555, inclination: 51.6 },
    { id: 5, name: 'SAT-005', noradId: '25548', constellation: 'LEO-NET', status: 'healthy', altitude: 552, inclination: 51.6 },
];

export default function Satellites() {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredSatellites = mockSatellites.filter(sat =>
        sat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        sat.noradId.includes(searchQuery)
    );

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Satellites</h1>
                    <p className="text-white/60 mt-1">Manage constellation satellites and TLE data</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add Satellite
                </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-4">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/40" />
                    <input
                        type="text"
                        placeholder="Search satellites..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="input w-full pl-10"
                    />
                </div>
                <button className="btn-secondary flex items-center gap-2">
                    <Filter className="w-4 h-4" />
                    Filters
                </button>
                <button className="btn-secondary flex items-center gap-2">
                    <RefreshCw className="w-4 h-4" />
                    Update TLEs
                </button>
            </div>

            {/* Satellites table */}
            <div className="card">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left text-white/60 text-sm border-b border-white/10">
                                <th className="pb-3 pl-4">Satellite</th>
                                <th className="pb-3">NORAD ID</th>
                                <th className="pb-3">Constellation</th>
                                <th className="pb-3">Altitude (km)</th>
                                <th className="pb-3">Inclination</th>
                                <th className="pb-3">Status</th>
                                <th className="pb-3">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredSatellites.map((sat) => (
                                <tr key={sat.id} className="table-row">
                                    <td className="py-4 pl-4">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 bg-cosmic-500/20 rounded-lg flex items-center justify-center">
                                                <Satellite className="w-4 h-4 text-cosmic-400" />
                                            </div>
                                            <span className="font-medium">{sat.name}</span>
                                        </div>
                                    </td>
                                    <td className="py-4 font-mono text-sm text-white/70">{sat.noradId}</td>
                                    <td className="py-4">{sat.constellation}</td>
                                    <td className="py-4">{sat.altitude}</td>
                                    <td className="py-4">{sat.inclination}°</td>
                                    <td className="py-4">
                                        <span className={`px-2 py-1 rounded text-xs ${sat.status === 'healthy'
                                                ? 'bg-aurora-500/20 text-aurora-400'
                                                : sat.status === 'degraded'
                                                    ? 'bg-yellow-500/20 text-yellow-400'
                                                    : 'bg-red-500/20 text-red-400'
                                            }`}>
                                            {sat.status}
                                        </span>
                                    </td>
                                    <td className="py-4">
                                        <button className="text-cosmic-400 hover:text-cosmic-300 text-sm">
                                            View Details
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
