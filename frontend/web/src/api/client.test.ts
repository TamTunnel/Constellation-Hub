import { describe, it, expect } from 'vitest';
import { api } from '../api/client';

describe('API Client', () => {
    it('should have constellation methods', () => {
        expect(api.getConstellations).toBeDefined();
        expect(api.getSatellites).toBeDefined();
        expect(api.getSatellitePosition).toBeDefined();
    });

    it('should have ground station methods', () => {
        expect(api.getGroundStations).toBeDefined();
        expect(api.getPasses).toBeDefined();
        expect(api.getSchedule).toBeDefined();
    });

    it('should have AI agent methods', () => {
        expect(api.optimizeSchedule).toBeDefined();
        expect(api.analyzeEvents).toBeDefined();
    });
});
