import { Calendar, Sparkles, Clock } from 'lucide-react';

export default function Scheduling() {
    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Scheduling</h1>
                    <p className="text-white/60 mt-1">Pass scheduling and AI optimization</p>
                </div>
                <div className="flex gap-2">
                    <button className="btn-secondary flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Generate Schedule
                    </button>
                    <button className="btn-primary flex items-center gap-2">
                        <Sparkles className="w-4 h-4" />
                        Optimize with AI
                    </button>
                </div>
            </div>

            {/* Timeline placeholder */}
            <div className="card">
                <h3 className="text-lg font-semibold mb-4">Schedule Timeline</h3>
                <div className="h-64 flex items-center justify-center border border-dashed border-white/20 rounded-lg">
                    <div className="text-center text-white/60">
                        <Clock className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>Gantt-style timeline view</p>
                        <p className="text-sm">Generate a schedule to see passes here</p>
                    </div>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="card text-center">
                    <p className="text-3xl font-bold text-cosmic-400">0</p>
                    <p className="text-white/60 text-sm">Scheduled Passes</p>
                </div>
                <div className="card text-center">
                    <p className="text-3xl font-bold text-aurora-400">0</p>
                    <p className="text-white/60 text-sm">Contact Minutes</p>
                </div>
                <div className="card text-center">
                    <p className="text-3xl font-bold text-nebula-400">0%</p>
                    <p className="text-white/60 text-sm">Optimization Score</p>
                </div>
            </div>
        </div>
    );
}
