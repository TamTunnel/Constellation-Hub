import {
    Satellite,
    Radio,
    Calendar,
    AlertTriangle,
    TrendingUp,
    Clock
} from 'lucide-react';
import { GlobeViewer } from '../components/Globe';

// Mock data for the dashboard
const mockSatellites = [
    { id: 1, name: 'SAT-001', latitude: 45.2, longitude: -122.3, altitude_km: 550 },
    { id: 2, name: 'SAT-002', latitude: 32.1, longitude: 89.5, altitude_km: 560 },
    { id: 3, name: 'SAT-003', latitude: -15.8, longitude: 45.2, altitude_km: 545 },
];

const mockGroundStations = [
    { id: 1, name: 'GS-Alpha', latitude: 40.7, longitude: -74.0 },
    { id: 2, name: 'GS-Beta', latitude: 51.5, longitude: -0.1 },
];

const stats = [
    {
        label: 'Active Satellites',
        value: 24,
        change: '+2',
        trend: 'up',
        icon: Satellite,
        color: 'cosmic'
    },
    {
        label: 'Ground Stations',
        value: 8,
        change: '0',
        trend: 'neutral',
        icon: Radio,
        color: 'aurora'
    },
    {
        label: 'Scheduled Passes',
        value: 156,
        change: '+12',
        trend: 'up',
        icon: Calendar,
        color: 'nebula'
    },
    {
        label: 'Active Alerts',
        value: 3,
        change: '-2',
        trend: 'down',
        icon: AlertTriangle,
        color: 'yellow'
    },
];

export default function Dashboard() {
    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Dashboard</h1>
                    <p className="text-white/60 mt-1">Constellation overview and real-time status</p>
                </div>
                <div className="flex items-center gap-2 text-sm text-white/60">
                    <Clock className="w-4 h-4" />
                    <span>Last updated: Just now</span>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {stats.map((stat) => {
                    const Icon = stat.icon;
                    const colorClasses = {
                        cosmic: 'bg-cosmic-500/20 text-cosmic-400 border-cosmic-500/30',
                        aurora: 'bg-aurora-500/20 text-aurora-400 border-aurora-500/30',
                        nebula: 'bg-nebula-500/20 text-nebula-400 border-nebula-500/30',
                        yellow: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
                    };

                    return (
                        <div
                            key={stat.label}
                            className="card hover:border-white/20 transition-all duration-200"
                        >
                            <div className="flex items-start justify-between">
                                <div>
                                    <p className="text-white/60 text-sm">{stat.label}</p>
                                    <p className="text-3xl font-bold mt-1">{stat.value}</p>
                                    <div className="flex items-center gap-1 mt-2">
                                        <TrendingUp className={`w-4 h-4 ${stat.trend === 'up' ? 'text-aurora-400' :
                                                stat.trend === 'down' ? 'text-red-400' :
                                                    'text-white/40'
                                            }`} />
                                        <span className={`text-sm ${stat.trend === 'up' ? 'text-aurora-400' :
                                                stat.trend === 'down' ? 'text-red-400' :
                                                    'text-white/40'
                                            }`}>
                                            {stat.change} this week
                                        </span>
                                    </div>
                                </div>
                                <div className={`p-3 rounded-lg border ${colorClasses[stat.color as keyof typeof colorClasses]}`}>
                                    <Icon className="w-6 h-6" />
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Main content grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Globe view */}
                <div className="lg:col-span-2 card p-0 overflow-hidden" style={{ height: '500px' }}>
                    <GlobeViewer
                        satellites={mockSatellites}
                        groundStations={mockGroundStations}
                    />
                </div>

                {/* Activity feed */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                        {[
                            { time: '2 min ago', event: 'Pass completed', details: 'SAT-005 → GS-Alpha', type: 'success' },
                            { time: '15 min ago', event: 'Schedule optimized', details: '+8% efficiency', type: 'info' },
                            { time: '1 hour ago', event: 'Link degradation', details: 'SAT-012 → GS-Beta', type: 'warning' },
                            { time: '2 hours ago', event: 'Pass completed', details: 'SAT-008 → GS-Gamma', type: 'success' },
                            { time: '3 hours ago', event: 'New TLE uploaded', details: '24 satellites updated', type: 'info' },
                        ].map((activity, index) => (
                            <div key={index} className="flex items-start gap-3 table-row p-2 rounded">
                                <div className={`w-2 h-2 rounded-full mt-2 ${activity.type === 'success' ? 'bg-aurora-500' :
                                        activity.type === 'warning' ? 'bg-yellow-500' :
                                            'bg-cosmic-500'
                                    }`} />
                                <div className="flex-1">
                                    <p className="text-sm font-medium">{activity.event}</p>
                                    <p className="text-xs text-white/60">{activity.details}</p>
                                </div>
                                <span className="text-xs text-white/40">{activity.time}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Upcoming passes */}
            <div className="card">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Upcoming Passes</h3>
                    <button className="btn-secondary text-sm">View All</button>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="text-left text-white/60 text-sm">
                                <th className="pb-3">Satellite</th>
                                <th className="pb-3">Ground Station</th>
                                <th className="pb-3">AOS</th>
                                <th className="pb-3">LOS</th>
                                <th className="pb-3">Max Elev</th>
                                <th className="pb-3">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[
                                { sat: 'SAT-001', gs: 'GS-Alpha', aos: '14:32:00', los: '14:44:30', elev: '78°', status: 'Scheduled' },
                                { sat: 'SAT-003', gs: 'GS-Beta', aos: '14:45:15', los: '14:53:20', elev: '45°', status: 'Scheduled' },
                                { sat: 'SAT-005', gs: 'GS-Alpha', aos: '15:12:00', los: '15:24:45', elev: '62°', status: 'Pending' },
                                { sat: 'SAT-002', gs: 'GS-Gamma', aos: '15:30:30', los: '15:41:00', elev: '55°', status: 'Pending' },
                            ].map((pass, index) => (
                                <tr key={index} className="table-row">
                                    <td className="py-3">
                                        <div className="flex items-center gap-2">
                                            <Satellite className="w-4 h-4 text-cosmic-400" />
                                            {pass.sat}
                                        </div>
                                    </td>
                                    <td className="py-3">
                                        <div className="flex items-center gap-2">
                                            <Radio className="w-4 h-4 text-aurora-400" />
                                            {pass.gs}
                                        </div>
                                    </td>
                                    <td className="py-3 font-mono text-sm">{pass.aos}</td>
                                    <td className="py-3 font-mono text-sm">{pass.los}</td>
                                    <td className="py-3">{pass.elev}</td>
                                    <td className="py-3">
                                        <span className={`px-2 py-1 rounded text-xs ${pass.status === 'Scheduled'
                                                ? 'bg-aurora-500/20 text-aurora-400'
                                                : 'bg-cosmic-500/20 text-cosmic-400'
                                            }`}>
                                            {pass.status}
                                        </span>
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
