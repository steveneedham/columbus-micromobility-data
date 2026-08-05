export function parseManualEntry(entry) {
  const { operator, durationMin, costUSD, date } = entry;
  const perMinRate = durationMin > 0 ? costUSD / durationMin : null;
  return { operator, durationMin, costUSD, date, perMinRate };
}

export function validateReceipt(receipt) {
  const errors = [];
  if (!receipt.operator || !['spin', 'veo'].includes(receipt.operator)) {
    errors.push('Operator must be "spin" or "veo".');
  }
  if (!receipt.durationMin || receipt.durationMin <= 0) {
    errors.push('Duration must be greater than 0.');
  } else if (receipt.durationMin < 2 || receipt.durationMin > 60) {
    errors.push('Duration looks unusual (expected 2-60 minutes) — double check this ride.');
  }
  if (!receipt.costUSD || receipt.costUSD <= 0) {
    errors.push('Cost must be greater than 0.');
  } else if (receipt.costUSD < 1 || receipt.costUSD > 30) {
    errors.push('Cost looks unusual (expected $1-$30) — double check this ride.');
  }
  if (!receipt.date) errors.push('Date is required.');

  return { valid: errors.length === 0, errors };
}

export const RECEIPT_PATTERNS = {
  operator: /\b(Spin|Veo)\b/i,
  duration: /(\d+)\s*min(?:ute)?s?/i,
  cost: /\$\s?(\d+\.\d{2})/,
  date: /(\d{1,2})\/(\d{1,2})\/(\d{2,4})/,
};
