/**
 * CesiumGlobe - Production-grade 3D globe visualization using CesiumJS.
 * 
 * Uses open-source imagery (OpenStreetMap) instead of Cesium Ion.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import {
    Viewer,
    Cartesian3,
    Cartesian2,
    Color,
    Ion,
    ScreenSpaceEventHandler,
    ScreenSpaceEventType,
    defined,
    ClockRange,
    ClockStep,
    OpenStreetMapImageryProvider,
    NearFarScalar,
    VerticalOrigin,
    HeightReference,
} from 'cesium';
import 'cesium/Build/Cesium/Widgets/widgets.css';
import { Satellite, Radio, Layers, Eye, EyeOff, Play, Pause, RotateCcw } from 'lucide-react';


// Disable Cesium Ion - we use open-source tiles
Ion.defaultAccessToken = '';

interface SatelliteData {
    id: number | string;
    name: string;
    latitude: number;
    longitude: number;
    altitude_km: number;
    norad_id?: string;
}

interface GroundStationData {
    id: number | string;
    name: string;
    latitude: number;
    longitude: number;
    elevation_m?: number;
}

interface OrbitPoint {
    time: Date;
    latitude: number;
    longitude: number;
    altitude_km: number;
}

interface CesiumGlobeProps {
    satellites?: SatelliteData[];
    groundStations?: GroundStationData[];
    orbitTracks?: Map<string, OrbitPoint[]>;
    showCoverage?: boolean;
    showOrbits?: boolean;
    onSatelliteSelect?: (satellite: SatelliteData) => void;
    onGroundStationSelect?: (station: GroundStationData) => void;
    timeOffset?: number; // Seconds offset from current time
    animationSpeed?: number; // 1x, 10x, 60x
}

export default function CesiumGlobe({
    satellites = [],
    groundStations = [],
    orbitTracks: _orbitTracks,
    showCoverage = true,
    showOrbits = true,
    onSatelliteSelect,
    onGroundStationSelect: _onGroundStationSelect,
    timeOffset: _timeOffset = 0,
    animationSpeed = 1,
}: CesiumGlobeProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const viewerRef = useRef<Viewer | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [coverageVisible, setCoverageVisible] = useState(showCoverage);
    const [orbitsVisible, setOrbitsVisible] = useState(showOrbits);
    const [isPlaying, setIsPlaying] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Initialize Cesium viewer
    useEffect(() => {
        if (!containerRef.current) return;

        const initViewer = async () => {
            try {
                // Create viewer with OpenStreetMap imagery
                const viewer = new Viewer(containerRef.current!, {
                    // Use OpenStreetMap instead of Cesium Ion
                    // @ts-expect-error - Cesium types issue with imageryProvider
                    imageryProvider: new OpenStreetMapImageryProvider({
                        url: 'https://tile.openstreetmap.org/',
                    }),
                    // Disable Cesium Ion-dependent features
                    baseLayerPicker: false,
                    geocoder: false,
                    // Enable other controls
                    animation: true,
                    timeline: true,
                    fullscreenButton: true,
                    vrButton: false,
                    homeButton: true,
                    sceneModePicker: true,
                    navigationHelpButton: false,
                    infoBox: true,
                    selectionIndicator: true,
                    // Performance
                    requestRenderMode: false,
                    maximumRenderTimeChange: Infinity,
                });

                // Configure clock for animation
                viewer.clock.shouldAnimate = true;
                viewer.clock.clockRange = ClockRange.UNBOUNDED;
                viewer.clock.clockStep = ClockStep.SYSTEM_CLOCK_MULTIPLIER;
                viewer.clock.multiplier = animationSpeed;

                // Set initial camera position
                viewer.camera.flyTo({
                    destination: Cartesian3.fromDegrees(-98.0, 35.0, 20000000),
                    duration: 0,
                });

                // Style the atmosphere
                viewer.scene.globe.enableLighting = true;
                viewer.scene.globe.showGroundAtmosphere = true;

                // Store viewer reference
                viewerRef.current = viewer;
                setIsLoading(false);
                setError(null);
            } catch (err) {
                console.error('Failed to initialize Cesium:', err);
                setError('Failed to initialize 3D globe');
                setIsLoading(false);
            }
        };

        initViewer();

        // Cleanup
        return () => {
            if (viewerRef.current) {
                viewerRef.current.destroy();
                viewerRef.current = null;
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [animationSpeed]);

    // Update animation speed
    useEffect(() => {
        if (viewerRef.current) {
            viewerRef.current.clock.multiplier = animationSpeed;
        }
    }, [animationSpeed]);

    // Update play/pause state
    useEffect(() => {
        if (viewerRef.current) {
            viewerRef.current.clock.shouldAnimate = isPlaying;
        }
    }, [isPlaying]);

    // Add satellites to the globe
    useEffect(() => {
        const viewer = viewerRef.current;
        if (!viewer || isLoading) return;

        // Remove existing satellite entities
        viewer.entities.values
            .filter(e => e.id?.startsWith('satellite-'))
            .forEach(e => viewer.entities.remove(e));

        // Add satellites
        satellites.forEach(sat => {
            const position = Cartesian3.fromDegrees(
                sat.longitude,
                sat.latitude,
                sat.altitude_km * 1000 // Convert to meters
            );

            viewer.entities.add({
                id: `satellite-${sat.id}`,
                name: sat.name,
                position: position,
                point: {
                    pixelSize: 10,
                    color: Color.fromCssColorString('#6366f1'),
                    outlineColor: Color.WHITE,
                    outlineWidth: 2,
                    heightReference: HeightReference.NONE,
                },
                label: {
                    text: sat.name,
                    font: '12px sans-serif',
                    fillColor: Color.WHITE,
                    outlineColor: Color.BLACK,
                    outlineWidth: 2,
                    verticalOrigin: VerticalOrigin.BOTTOM,
                    pixelOffset: new Cartesian3(0, -15, 0),
                    scaleByDistance: new NearFarScalar(1e6, 1, 1e8, 0.3),
                },
                description: `
                    <div style="padding: 10px;">
                        <h3>${sat.name}</h3>
                        <p>NORAD ID: ${sat.norad_id || 'N/A'}</p>
                        <p>Altitude: ${sat.altitude_km.toFixed(1)} km</p>
                        <p>Position: ${sat.latitude.toFixed(2)}°, ${sat.longitude.toFixed(2)}°</p>
                    </div>
                `,
            });

            // Add coverage footprint if enabled
            if (coverageVisible) {
                // Simple coverage circle (approximate)
                const radiusKm = calculateCoverageRadius(sat.altitude_km);
                viewer.entities.add({
                    id: `coverage-${sat.id}`,
                    name: `${sat.name} Coverage`,
                    position: Cartesian3.fromDegrees(sat.longitude, sat.latitude),
                    ellipse: {
                        semiMajorAxis: radiusKm * 1000,
                        semiMinorAxis: radiusKm * 1000,
                        material: Color.fromCssColorString('#6366f1').withAlpha(0.15),
                        outline: true,
                        outlineColor: Color.fromCssColorString('#6366f1').withAlpha(0.5),
                        outlineWidth: 2,
                        height: 0,
                    },
                });
            }
        });

        // Handle click events
        const handler = new ScreenSpaceEventHandler(viewer.scene.canvas);
        handler.setInputAction((click: { position: Cartesian2 }) => {
            const pickedObject = viewer.scene.pick(click.position);
            if (defined(pickedObject) && pickedObject.id) {
                const entity = pickedObject.id;
                if (entity.id?.startsWith('satellite-') && onSatelliteSelect) {
                    const satId = entity.id.replace('satellite-', '');
                    const sat = satellites.find(s => String(s.id) === satId);
                    if (sat) onSatelliteSelect(sat);
                }
            }
        }, ScreenSpaceEventType.LEFT_CLICK);

        return () => {
            handler.destroy();
        };
    }, [satellites, isLoading, coverageVisible, onSatelliteSelect]);

    // Add ground stations
    useEffect(() => {
        const viewer = viewerRef.current;
        if (!viewer || isLoading) return;

        // Remove existing ground station entities
        viewer.entities.values
            .filter(e => e.id?.startsWith('gs-'))
            .forEach(e => viewer.entities.remove(e));

        // Add ground stations
        groundStations.forEach(gs => {
            const position = Cartesian3.fromDegrees(
                gs.longitude,
                gs.latitude,
                (gs.elevation_m || 0)
            );

            viewer.entities.add({
                id: `gs-${gs.id}`,
                name: gs.name,
                position: position,
                point: {
                    pixelSize: 12,
                    color: Color.fromCssColorString('#22c55e'),
                    outlineColor: Color.WHITE,
                    outlineWidth: 2,
                    heightReference: HeightReference.CLAMP_TO_GROUND,
                },
                label: {
                    text: gs.name,
                    font: '11px sans-serif',
                    fillColor: Color.WHITE,
                    outlineColor: Color.BLACK,
                    outlineWidth: 2,
                    verticalOrigin: VerticalOrigin.BOTTOM,
                    pixelOffset: new Cartesian3(0, -15, 0),
                    scaleByDistance: new NearFarScalar(1e5, 1, 1e7, 0.3),
                },
                description: `
                    <div style="padding: 10px;">
                        <h3>${gs.name}</h3>
                        <p>Location: ${gs.latitude.toFixed(2)}°, ${gs.longitude.toFixed(2)}°</p>
                        <p>Elevation: ${gs.elevation_m || 0} m</p>
                    </div>
                `,
            });
        });
    }, [groundStations, isLoading]);

    // Toggle coverage visibility
    useEffect(() => {
        const viewer = viewerRef.current;
        if (!viewer) return;

        viewer.entities.values
            .filter(e => e.id?.startsWith('coverage-'))
            .forEach(e => {
                e.show = coverageVisible;
            });
    }, [coverageVisible]);

    const handleReset = useCallback(() => {
        if (viewerRef.current) {
            viewerRef.current.camera.flyTo({
                destination: Cartesian3.fromDegrees(-98.0, 35.0, 20000000),
                duration: 1.5,
            });
        }
    }, []);

    const togglePlay = useCallback(() => {
        setIsPlaying(prev => !prev);
    }, []);

    if (error) {
        return (
            <div className="relative w-full h-full bg-space-900 rounded-xl overflow-hidden flex items-center justify-center">
                <div className="text-center text-red-400">
                    <p className="text-xl mb-2">⚠️</p>
                    <p>{error}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="relative w-full h-full bg-space-900 rounded-xl overflow-hidden">
            {/* Cesium container */}
            <div ref={containerRef} className="absolute inset-0" />

            {/* Loading overlay */}
            {isLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-space-900 z-10">
                    <div className="text-center">
                        <div className="w-16 h-16 border-4 border-cosmic-500/30 border-t-cosmic-500 rounded-full animate-spin mb-4 mx-auto" />
                        <p className="text-white/60">Initializing 3D Globe...</p>
                    </div>
                </div>
            )}

            {/* Controls overlay */}
            {!isLoading && (
                <>
                    <div className="absolute top-4 right-4 flex flex-col gap-2 z-20">
                        <button
                            onClick={() => setCoverageVisible(!coverageVisible)}
                            className={`
                                p-2 rounded-lg transition-all duration-200
                                ${coverageVisible ? 'bg-cosmic-500 text-white' : 'bg-space-700/80 text-white/60 hover:bg-space-600'}
                            `}
                            title="Toggle Coverage"
                        >
                            {coverageVisible ? <Eye className="w-5 h-5" /> : <EyeOff className="w-5 h-5" />}
                        </button>
                        <button
                            onClick={() => setOrbitsVisible(!orbitsVisible)}
                            className={`
                                p-2 rounded-lg transition-all duration-200
                                ${orbitsVisible ? 'bg-cosmic-500 text-white' : 'bg-space-700/80 text-white/60 hover:bg-space-600'}
                            `}
                            title="Toggle Orbits"
                        >
                            <Layers className="w-5 h-5" />
                        </button>
                        <button
                            onClick={togglePlay}
                            className="p-2 rounded-lg bg-space-700/80 text-white/60 hover:bg-space-600 transition-all"
                            title={isPlaying ? 'Pause' : 'Play'}
                        >
                            {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                        </button>
                        <button
                            onClick={handleReset}
                            className="p-2 rounded-lg bg-space-700/80 text-white/60 hover:bg-space-600 transition-all"
                            title="Reset View"
                        >
                            <RotateCcw className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Stats overlay */}
                    <div className="absolute bottom-20 left-4 bg-space-800/80 backdrop-blur rounded-lg p-3 z-20">
                        <div className="flex gap-4 text-sm">
                            <div className="flex items-center gap-2">
                                <Satellite className="w-4 h-4 text-cosmic-400" />
                                <span className="text-white">{satellites.length} Satellites</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Radio className="w-4 h-4 text-aurora-400" />
                                <span className="text-white">{groundStations.length} Ground Stations</span>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}

/**
 * Calculate approximate coverage radius for a satellite at given altitude.
 * Uses 10-degree minimum elevation angle.
 */
function calculateCoverageRadius(altitudeKm: number, minElevationDeg: number = 10): number {
    const earthRadiusKm = 6371;
    const elevationRad = minElevationDeg * Math.PI / 180;

    // Geometry calculation for ground coverage
    const rho = Math.asin(earthRadiusKm / (earthRadiusKm + altitudeKm) * Math.cos(elevationRad));
    const lambda = Math.PI / 2 - elevationRad - rho;
    const coverageRadiusKm = earthRadiusKm * lambda;

    return coverageRadiusKm;
}
