import { Radio, Plus, MapPin, Signal } from 'lucide-react';

const mockStations = [
    { id: 1, name: 'GS-Alpha', location: 'New York, USA', lat: 40.7, lon: -74.0, status: 'online', capabilities: ['S-band', 'X-band'] },
    { id: 2, name: 'GS-Beta', location: 'London, UK', lat: 51.5, lon: -0.1, status: 'online', capabilities: ['S-band', 'Ka-band'] },
    { id: 3, name: 'GS-Gamma', location: 'Tokyo, Japan', lat: 35.7, lon: 139.7, status: 'maintenance', capabilities: ['X-band'] },
];

export default function GroundStations() {
    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Ground Stations</h1>
                    <p className="text-white/60 mt-1">Manage ground station network</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add Station
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {mockStations.map((station) => (
                    <div key={station.id} className="card hover:border-white/20 transition-all">
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${station.status === 'online' ? 'bg-aurora-500/20' : 'bg-yellow-500/20'
                                    }`}>
                                    <Radio className={station.status === 'online' ? 'text-aurora-400' : 'text-yellow-400'} />
                                </div>
                                <div>
                                    <h3 className="font-semibold">{station.name}</h3>
                                    <div className="flex items-center gap-1 text-sm text-white/60">
                                        <MapPin className="w-3 h-3" />
                                        {station.location}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex gap-2 mt-2">
                            {station.capabilities.map((cap) => (
                                <span key={cap} className="px-2 py-1 bg-space-600 rounded text-xs">{cap}</span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
