import { describe, it, expect } from 'vitest';
import { haversineDistance, huntTimeEstimate, validateCoordinates } from '../src/utils/geo.js';

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
});
