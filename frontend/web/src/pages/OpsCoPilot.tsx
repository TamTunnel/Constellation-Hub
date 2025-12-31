import { Bot, Send, CheckCircle, XCircle, Clock } from 'lucide-react';

const mockAnalysis = {
    summary: "Analysis of 5 events over the review period. Pattern detected: 2 missed passes may indicate ground station issues.",
    findings: [
        "Satellite SAT-012 has 2 critical events requiring investigation.",
        "Ground station GS-Beta involved in 3 events. Consider maintenance."
    ],
    actions: [
        { id: '1', action: 'Review telemetry for SAT-012', priority: 'critical', status: 'pending' },
        { id: '2', action: 'Schedule diagnostic check for GS-Beta', priority: 'high', status: 'pending' },
        { id: '3', action: 'Review weather data at affected stations', priority: 'medium', status: 'pending' },
    ]
};

export default function OpsCoPilot() {
    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Ops Co-Pilot</h1>
                    <p className="text-white/60 mt-1">AI-powered operations assistant</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Send className="w-4 h-4" />
                    Analyze Events
                </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Analysis Summary */}
                <div className="card">
                    <div className="flex items-center gap-2 mb-4">
                        <Bot className="w-5 h-5 text-cosmic-400" />
                        <h3 className="text-lg font-semibold">Analysis Summary</h3>
                    </div>
                    <p className="text-white/80 mb-4">{mockAnalysis.summary}</p>
                    <div className="space-y-2">
                        {mockAnalysis.findings.map((finding, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm">
                                <span className="text-cosmic-400">•</span>
                                <span>{finding}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Suggested Actions */}
                <div className="card">
                    <h3 className="text-lg font-semibold mb-4">Suggested Actions</h3>
                    <div className="space-y-3">
                        {mockAnalysis.actions.map((action) => (
                            <div key={action.id} className="p-3 bg-space-700 rounded-lg">
                                <div className="flex items-center justify-between mb-2">
                                    <span className={`px-2 py-1 rounded text-xs ${action.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                                            action.priority === 'high' ? 'bg-yellow-500/20 text-yellow-400' :
                                                'bg-cosmic-500/20 text-cosmic-400'
                                        }`}>
                                        {action.priority}
                                    </span>
                                    <div className="flex gap-2">
                                        <button className="p-1 hover:bg-aurora-500/20 rounded" title="Apply">
                                            <CheckCircle className="w-4 h-4 text-aurora-400" />
                                        </button>
                                        <button className="p-1 hover:bg-red-500/20 rounded" title="Dismiss">
                                            <XCircle className="w-4 h-4 text-red-400" />
                                        </button>
                                    </div>
                                </div>
                                <p className="text-sm">{action.action}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
