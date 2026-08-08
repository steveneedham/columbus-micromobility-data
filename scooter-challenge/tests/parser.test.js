import { describe, it, expect } from 'vitest';
import { parseManualEntry, validateReceipt } from '../src/utils/receiptParser.js';

describe('receipt parser', () => {
  it('parses a manual entry and derives per-minute rate', () => {
    const parsed = parseManualEntry({ operator: 'spin', durationMin: 13, costUSD: 2.39, date: '2026-07-01' });
    expect(parsed.perMinRate).toBeCloseTo(2.39 / 13, 4);
  });

  it('validates a normal receipt', () => {
    const { valid } = validateReceipt({ operator: 'spin', durationMin: 13, costUSD: 2.39, date: '2026-07-01' });
    expect(valid).toBe(true);
  });

  it('flags outlier duration and cost', () => {
    const { valid, errors } = validateReceipt({ operator: 'spin', durationMin: 120, costUSD: 50, date: '2026-07-01' });
    expect(valid).toBe(false);
    expect(errors.length).toBeGreaterThan(0);
  });

  it('flags missing required fields', () => {
    const { valid } = validateReceipt({ operator: 'veo', durationMin: 10 });
    expect(valid).toBe(false);
  });
});
