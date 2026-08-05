import { createWorker } from 'tesseract.js';
import { RECEIPT_PATTERNS } from './receiptParser.js';

// The recognition engine (worker script, wasm core, language data) loads
// from a CDN on first use. If that load stalls -- flaky network, corporate
// proxy, ad blocker -- tesseract.js's promise can hang indefinitely instead
// of rejecting, so every step here is bounded by a timeout rather than
// trusting the underlying promise to settle.
const SCAN_TIMEOUT_MS = 20000;

let workerPromise = null;

function withTimeout(promise, ms, message) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(message)), ms);
    promise.then(
      (value) => { clearTimeout(timer); resolve(value); },
      (err) => { clearTimeout(timer); reject(err); },
    );
  });
}

function getWorker() {
  if (!workerPromise) {
    workerPromise = createWorker('eng').catch((err) => {
      workerPromise = null;
      throw err;
    });
  }
  return withTimeout(workerPromise, SCAN_TIMEOUT_MS, 'Receipt scanner failed to load.').catch((err) => {
    workerPromise = null;
    throw err;
  });
}

// Receipt screenshots often list more than one dollar amount (unlock fee,
// per-minute rate, total) -- the total is almost always the last one printed.
function lastCostMatch(text) {
  const matches = [...text.matchAll(new RegExp(RECEIPT_PATTERNS.cost, 'g'))];
  return matches.length ? matches[matches.length - 1] : null;
}

export function parseReceiptText(text) {
  const fields = {};

  const operatorMatch = text.match(RECEIPT_PATTERNS.operator);
  if (operatorMatch) fields.operator = operatorMatch[1].toLowerCase();

  const durationMatch = text.match(RECEIPT_PATTERNS.duration);
  if (durationMatch) fields.durationMin = parseInt(durationMatch[1], 10);

  const costMatch = lastCostMatch(text);
  if (costMatch) fields.costUSD = parseFloat(costMatch[1]);

  const dateMatch = text.match(RECEIPT_PATTERNS.date);
  if (dateMatch) {
    const [, month, day, year] = dateMatch;
    const fullYear = year.length === 2 ? `20${year}` : year;
    fields.date = `${fullYear.padStart(4, '0')}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
  }

  return fields;
}

// Runs entirely in the browser via WebAssembly -- the image and its text
// never leave the device. See scooter-challenge/src/utils/analytics.js for
// what (if anything) gets logged, which is never the receipt image or text.
export async function scanReceiptImage(file) {
  const worker = await getWorker();
  const { data } = await withTimeout(worker.recognize(file), SCAN_TIMEOUT_MS, 'Receipt scan timed out.');
  return { fields: parseReceiptText(data.text), rawText: data.text };
}
