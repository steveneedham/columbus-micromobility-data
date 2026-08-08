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

  // Real Tesseract output (via `tesseract <image> stdout`) from an actual
  // Veo receipt screenshot attached to issue #37. This exact text is why
  // the fix exists: the receipt never prints "Veo" anywhere, and OCR read
  // "Total paid $7.37" as "Total paid S7.37" while every other line's "$"
  // came through fine.
  it('extracts cost and a written-month date from a real scanned Veo receipt (#37)', () => {
    const text = `
      < Back

      Receipt

      Charge $6.85

      Ride #1017538 (15 min) $6.85
      Subtotal $6.85
      Tax $0.52
      Total paid S7.37
      Charge date July 29, 2026

      Payment method Mix
    `;
    const fields = parseReceiptText(text);
    expect(fields.operator).toBeUndefined(); // genuinely not present in this receipt -- not a bug to "fix"
    expect(fields.durationMin).toBe(15);
    expect(fields.costUSD).toBeCloseTo(7.37, 2); // not 0.52 (Tax) or unset
    expect(fields.date).toBe('2026-07-29');
  });

  it('parses "Month D, YYYY" and abbreviated "Mon D, YYYY" dates', () => {
    expect(parseReceiptText('Charge date July 29, 2026').date).toBe('2026-07-29');
    expect(parseReceiptText('Date: Jul 4, 2026').date).toBe('2026-07-04');
    expect(parseReceiptText('Mar 1 2026').date).toBe('2026-03-01');
  });

  it('prefers a "Total" line over an earlier larger dollar amount', () => {
    const text = 'Ride deposit $9.00 hold, Total paid $2.10';
    expect(parseReceiptText(text).costUSD).toBeCloseTo(2.1, 2);
  });
});
