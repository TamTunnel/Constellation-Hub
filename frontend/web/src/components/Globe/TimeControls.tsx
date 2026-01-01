/**
 * TimeControls - Controls for globe animation and time scrubbing.
 */
import { useState, useCallback } from 'react';
import { Play, Pause, SkipBack, SkipForward, FastForward, Clock } from 'lucide-react';
import { format } from 'date-fns';

interface TimeControlsProps {
    currentTime?: Date;
    isPlaying?: boolean;
    speed?: number;
    onPlayPause?: () => void;
    onSpeedChange?: (speed: number) => void;
    onTimeOffset?: (offsetSeconds: number) => void;
    onReset?: () => void;
}

const SPEED_OPTIONS = [
    { value: 1, label: '1x' },
    { value: 10, label: '10x' },
    { value: 60, label: '60x' },
    { value: 600, label: '10min/s' },
    { value: 3600, label: '1hr/s' },
];

export default function TimeControls({
    currentTime = new Date(),
    isPlaying = true,
    speed = 1,
    onPlayPause,
    onSpeedChange,
    onTimeOffset,
    onReset,
}: TimeControlsProps) {
    const [sliderValue, setSliderValue] = useState(50); // 0-100, 50 = now

    const handleSliderChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseInt(e.target.value, 10);
        setSliderValue(value);

        // Convert slider to time offset (-12 hours to +12 hours)
        const offsetHours = (value - 50) * 0.24; // ±12 hours
        const offsetSeconds = offsetHours * 3600;

        if (onTimeOffset) {
            onTimeOffset(offsetSeconds);
        }
    }, [onTimeOffset]);

    const handleSkipBack = useCallback(() => {
        setSliderValue(prev => Math.max(0, prev - 5));
        if (onTimeOffset) {
            onTimeOffset((sliderValue - 55) * 0.24 * 3600);
        }
    }, [sliderValue, onTimeOffset]);

    const handleSkipForward = useCallback(() => {
        setSliderValue(prev => Math.min(100, prev + 5));
        if (onTimeOffset) {
            onTimeOffset((sliderValue - 45) * 0.24 * 3600);
        }
    }, [sliderValue, onTimeOffset]);

    const handleReset = useCallback(() => {
        setSliderValue(50);
        if (onTimeOffset) {
            onTimeOffset(0);
        }
        if (onReset) {
            onReset();
        }
    }, [onTimeOffset, onReset]);

    // Calculate display time based on slider
    const displayTime = sliderValue === 50
        ? currentTime
        : new Date(currentTime.getTime() + ((sliderValue - 50) * 0.24 * 3600 * 1000));

    return (
        <div className="bg-space-800/90 backdrop-blur rounded-lg p-4">
            {/* Current time display */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-cosmic-400" />
                    <span className="text-sm text-white/60">Simulation Time</span>
                </div>
                <div className="font-mono text-white">
                    {format(displayTime, 'yyyy-MM-dd HH:mm:ss')} UTC
                </div>
            </div>

            {/* Time slider */}
            <div className="mb-4">
                <input
                    type="range"
                    min="0"
                    max="100"
                    value={sliderValue}
                    onChange={handleSliderChange}
                    className="w-full h-2 bg-space-600 rounded-lg appearance-none cursor-pointer
                        [&::-webkit-slider-thumb]:appearance-none
                        [&::-webkit-slider-thumb]:w-4
                        [&::-webkit-slider-thumb]:h-4
                        [&::-webkit-slider-thumb]:bg-cosmic-500
                        [&::-webkit-slider-thumb]:rounded-full
                        [&::-webkit-slider-thumb]:cursor-pointer
                        [&::-webkit-slider-thumb]:hover:bg-cosmic-400"
                />
                <div className="flex justify-between text-xs text-white/40 mt-1">
                    <span>-12h</span>
                    <span className={sliderValue === 50 ? 'text-cosmic-400 font-semibold' : ''}>Now</span>
                    <span>+12h</span>
                </div>
            </div>

            {/* Playback controls */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleSkipBack}
                        className="p-2 rounded-lg bg-space-700 text-white/60 hover:bg-space-600 hover:text-white transition-all"
                        title="Skip Back 1 Hour"
                    >
                        <SkipBack className="w-4 h-4" />
                    </button>

                    <button
                        onClick={onPlayPause}
                        className={`p-3 rounded-lg transition-all ${isPlaying
                            ? 'bg-cosmic-500 text-white hover:bg-cosmic-400'
                            : 'bg-space-700 text-white/60 hover:bg-space-600 hover:text-white'
                            }`}
                        title={isPlaying ? 'Pause' : 'Play'}
                    >
                        {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                    </button>

                    <button
                        onClick={handleSkipForward}
                        className="p-2 rounded-lg bg-space-700 text-white/60 hover:bg-space-600 hover:text-white transition-all"
                        title="Skip Forward 1 Hour"
                    >
                        <SkipForward className="w-4 h-4" />
                    </button>

                    <button
                        onClick={handleReset}
                        className="p-2 rounded-lg bg-space-700 text-white/60 hover:bg-space-600 hover:text-white transition-all ml-2"
                        title="Reset to Now"
                    >
                        <Clock className="w-4 h-4" />
                    </button>
                </div>

                {/* Speed selector */}
                <div className="flex items-center gap-2">
                    <FastForward className="w-4 h-4 text-white/40" />
                    <select
                        value={speed}
                        onChange={(e) => onSpeedChange?.(parseInt(e.target.value, 10))}
                        className="bg-space-700 text-white text-sm rounded-lg px-3 py-2 border border-space-600 focus:border-cosmic-500 focus:outline-none"
                    >
                        {SPEED_OPTIONS.map(opt => (
                            <option key={opt.value} value={opt.value}>
                                {opt.label}
                            </option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
}
