import { useEffect, useRef, useState } from 'react';
import { Satellite, Radio, Layers, Eye, EyeOff } from 'lucide-react';

// Note: In production, this would use actual CesiumJS
// For the MVP, we create a simulated globe visualization

interface GlobeViewerProps {
    satellites?: Array<{
        id: number;
        name: string;
        latitude: number;
        longitude: number;
        altitude_km: number;
    }>;
    groundStations?: Array<{
        id: number;
        name: string;
        latitude: number;
        longitude: number;
    }>;
    showCoverage?: boolean;
    showOrbits?: boolean;
}

export default function GlobeViewer({
    satellites = [],
    groundStations = [],
    showCoverage = true,
    showOrbits = true,
}: GlobeViewerProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [coverageVisible, setCoverageVisible] = useState(showCoverage);
    const [orbitsVisible, setOrbitsVisible] = useState(showOrbits);

    useEffect(() => {
        // Simulate loading CesiumJS
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 1500);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div ref={containerRef} className="relative w-full h-full bg-space-900 rounded-xl overflow-hidden">
            {/* Loading state */}
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-space-900">
                    <div className="text-center">
                        <div className="w-16 h-16 border-4 border-cosmic-500/30 border-t-cosmic-500 rounded-full animate-spin mb-4 mx-auto" />
                        <p className="text-white/60">Loading 3D Globe...</p>
                    </div>
                </div>
            )}

            {/* Globe placeholder (in production, this would be CesiumJS) */}
            {!isLoading && (
                <>
                    {/* Simulated globe background */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <div
                            className="w-[500px] h-[500px] rounded-full relative animate-orbit"
                            style={{
                                background: 'radial-gradient(circle at 30% 30%, #1e3a5f, #0a1628)',
                                boxShadow: `
                  inset -30px -30px 60px rgba(0, 0, 0, 0.5),
                  inset 30px 30px 60px rgba(30, 58, 95, 0.3),
                  0 0 100px rgba(99, 102, 241, 0.2)
                `,
                            }}
                        >
                            {/* Grid lines */}
                            <div className="absolute inset-0 rounded-full overflow-hidden opacity-30">
                                {[...Array(6)].map((_, i) => (
                                    <div
                                        key={`lat-${i}`}
                                        className="absolute w-full border-t border-white/20"
                                        style={{ top: `${(i + 1) * 14.28}%` }}
                                    />
                                ))}
                                {[...Array(12)].map((_, i) => (
                                    <div
                                        key={`lon-${i}`}
                                        className="absolute h-full border-l border-white/20"
                                        style={{ left: `${(i + 1) * 8.33}%` }}
                                    />
                                ))}
                            </div>

                            {/* Simulated satellites */}
                            {satellites.map((sat, index) => (
                                <div
                                    key={sat.id}
                                    className="absolute w-3 h-3 bg-cosmic-400 rounded-full glow-cosmic"
                                    style={{
                                        top: `${30 + index * 15}%`,
                                        left: `${40 + index * 10}%`,
                                        animation: `pulse 2s ease-in-out ${index * 0.3}s infinite`,
                                    }}
                                    title={sat.name}
                                />
                            ))}

                            {/* Coverage circles */}
                            {coverageVisible && satellites.map((sat, index) => (
                                <div
                                    key={`coverage-${sat.id}`}
                                    className="absolute w-24 h-24 border-2 border-cosmic-400/30 rounded-full"
                                    style={{
                                        top: `${25 + index * 15}%`,
                                        left: `${35 + index * 10}%`,
                                        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%)',
                                    }}
                                />
                            ))}

                            {/* Ground stations */}
                            {groundStations.map((gs, index) => (
                                <div
                                    key={gs.id}
                                    className="absolute w-4 h-4"
                                    style={{
                                        top: `${60 + index * 10}%`,
                                        left: `${25 + index * 20}%`,
                                    }}
                                    title={gs.name}
                                >
                                    <Radio className="w-4 h-4 text-aurora-400" />
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Controls overlay */}
                    <div className="absolute top-4 right-4 flex flex-col gap-2">
                        <button
                            onClick={() => setCoverageVisible(!coverageVisible)}
                            className={`
                p-2 rounded-lg transition-all duration-200
                ${coverageVisible ? 'bg-cosmic-500 text-white' : 'bg-space-700 text-white/60 hover:bg-space-600'}
              `}
                            title="Toggle Coverage"
                        >
                            {coverageVisible ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                        </button>
                        <button
                            onClick={() => setOrbitsVisible(!orbitsVisible)}
                            className={`
                p-2 rounded-lg transition-all duration-200
                ${orbitsVisible ? 'bg-cosmic-500 text-white' : 'bg-space-700 text-white/60 hover:bg-space-600'}
              `}
                            title="Toggle Orbits"
                        >
                            <Layers className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Stats overlay */}
                    <div className="absolute bottom-4 left-4 glass rounded-lg p-3">
                        <div className="flex gap-4 text-sm">
                            <div className="flex items-center gap-2">
                                <Satellite className="w-4 h-4 text-cosmic-400" />
                                <span>{satellites.length} Satellites</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Radio className="w-4 h-4 text-aurora-400" />
                                <span>{groundStations.length} Ground Stations</span>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
