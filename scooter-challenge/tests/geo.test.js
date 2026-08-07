import { describe, it, expect } from 'vitest';
import { haversineDistance, huntTimeEstimate, validateCoordinates, nearbyVehicles } from '../src/utils/geo.js';

describe('geo utilities', () => {
  it('calculates distance between two Columbus points', () => {
    const dist = haversineDistance(39.9612, -82.9988, 39.9357, -82.9758);
    expect(dist).toBeGreaterThan(1.5);
    expect(dist).toBeLessThan(2.2);
  });

  it('returns 0 for identical coordinates', () => {
    expect(haversineDistance(40, -83, 40, -83)).toBe(0);
  });

  it('estimates hunt time correctly', () => {
    expect(huntTimeEstimate(0.25)).toBe(6);
    expect(huntTimeEstimate(0.5)).toBe(11);
  });

  it('validates coordinates', () => {
    expect(validateCoordinates(40, -83).valid).toBe(true);
    expect(validateCoordinates(200, -83).valid).toBe(false);
    expect(validateCoordinates(40, 400).valid).toBe(false);
  });

  it('finds nearby vehicles by operator within radius, sorted by distance', () => {
    const home = { lat: 39.9612, lon: -82.9988 };
    const vehicles = [
      { operator: 'spin', lat: 39.9613, lon: -82.9989, type: 'scooter' }, // ~15m away
      { operator: 'spin', lat: 39.9625, lon: -82.9988, type: 'bike' }, // ~0.09mi, within 0.25mi
      { operator: 'veo', lat: 39.9614, lon: -82.999, type: 'scooter' }, // close
      { operator: 'veo', lat: 40.05, lon: -83.05, type: 'scooter' }, // far away, excluded
    ];
    const result = nearbyVehicles(home.lat, home.lon, vehicles, 0.25);
    expect(result.spin).toHaveLength(2);
    expect(result.veo).toHaveLength(1);
    expect(result.spin[0].distanceMiles).toBeLessThanOrEqual(result.spin[1].distanceMiles);
  });

  it('returns empty results when no vehicles are within radius', () => {
    const result = nearbyVehicles(39.9612, -82.9988, [{ operator: 'spin', lat: 40.5, lon: -83.5 }], 0.25);
    expect(result.spin).toHaveLength(0);
    expect(result.veo).toHaveLength(0);
  });
});
