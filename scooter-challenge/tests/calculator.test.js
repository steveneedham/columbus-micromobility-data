import { describe, it, expect } from 'vitest';
import { projectCost, compareOperators, confidenceScore, recommend } from '../src/utils/calculator.js';

describe('cost calculator', () => {
  it('projects Spin cost correctly', () => {
    const result = projectCost('spin', { avgRideDurationMin: 13.5, ridesPerMonth: 25 });
    expect(result.monthlyTotal).toBeCloseTo(0.99 + 2.39 * 25, 2);
  });

  it('projects Veo cost correctly', () => {
    const result = projectCost('veo', { avgRideDurationMin: 13.5, ridesPerMonth: 25 });
    expect(result.monthlyTotal).toBeCloseTo(5.99 + 0.475 * 13.5 * 25, 2);
  });

  it('picks the cheaper operator', () => {
    const spinCost = projectCost('spin', { avgRideDurationMin: 13.5, ridesPerMonth: 25 });
    const veoCost = projectCost('veo', { avgRideDurationMin: 13.5, ridesPerMonth: 25 });
    const rec = compareOperators(spinCost, veoCost);
    expect(rec.winner).toBe('spin');
    expect(rec.savings).toBeGreaterThan(0);
  });

  it('scores confidence higher with more receipts and locations', () => {
    const low = confidenceScore({ numReceipts: 1, costConsistency: 0.3, numLocations: 1, gbfsDataAgeMin: 10 });
    const high = confidenceScore({ numReceipts: 4, costConsistency: 0.9, numLocations: 4, gbfsDataAgeMin: 10 });
    expect(high).toBeGreaterThan(low);
  });

  it('produces a full recommendation object', () => {
    const spinCost = projectCost('spin', { avgRideDurationMin: 13.5, ridesPerMonth: 25 });
    const veoCost = projectCost('veo', { avgRideDurationMin: 13.5, ridesPerMonth: 25 });
    const rec = recommend(spinCost, veoCost, { confidence: { numReceipts: 3, numLocations: 2 } });
    expect(rec).toHaveProperty('winner');
    expect(rec).toHaveProperty('confidenceScore');
    expect(rec).toHaveProperty('reasoning');
  });
});
