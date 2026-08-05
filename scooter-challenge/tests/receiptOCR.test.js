import { describe, it, expect } from 'vitest';
import { parseReceiptText } from '../src/utils/receiptOCR.js';

describe('parseReceiptText', () => {
  it('extracts operator, duration, cost, and date from a Spin-style receipt', () => {
    const text = `
      Spin
      Ride complete
      Duration: 13 minutes
      Unlock fee $1.00
      Total $2.39
      7/1/2026
    `;
    const fields = parseReceiptText(text);
    expect(fields).toEqual({
      operator: 'spin',
      durationMin: 13,
      costUSD: 2.39,
      date: '2026-07-01',
    });
  });

  it('extracts fields from a Veo-style receipt with a two-digit year', () => {
    const text = `
      Veo Ride Receipt
      15 min ride
      Base fare $1.00 + $2.25 = $3.25
      Date: 7/2/26
    `;
    const fields = parseReceiptText(text);
    expect(fields.operator).toBe('veo');
    expect(fields.durationMin).toBe(15);
    expect(fields.costUSD).toBeCloseTo(3.25, 2);
    expect(fields.date).toBe('2026-07-02');
  });

  it('picks the last dollar amount as the total when several appear', () => {
    const text = 'Spin ride: unlock $1.00, per-min $1.39, total $3.78';
    const fields = parseReceiptText(text);
    expect(fields.costUSD).toBeCloseTo(3.78, 2);
  });

  it('returns only the fields it can confidently find', () => {
    const text = 'blurry unreadable receipt';
    const fields = parseReceiptText(text);
    expect(fields).toEqual({});
  });
});
