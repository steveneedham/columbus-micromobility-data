import { useRef, useState } from 'react';
import { scanReceiptImage } from '../utils/receiptOCR.js';

const FIELD_LABELS = { operator: 'operator', durationMin: 'duration', costUSD: 'cost', date: 'date' };

const SCAN_STATUS_TEXT = {
  scanning: 'Reading your screenshot…',
  done: 'Filled in from your screenshot — double check the fields before continuing.',
  empty: "Couldn't make out any details in that image — enter the ride manually.",
  error: "Couldn't read that image — enter the ride manually.",
};

function joinWithAnd(items, conjunction) {
  if (items.length <= 1) return items.join('');
  if (items.length === 2) return `${items[0]} ${conjunction} ${items[1]}`;
  return `${items.slice(0, -1).join(', ')}, ${conjunction} ${items[items.length - 1]}`;
}

function partialScanMessage(fields) {
  const found = Object.keys(fields).map((key) => FIELD_LABELS[key]);
  const missing = Object.keys(FIELD_LABELS).filter((key) => !(key in fields)).map((key) => FIELD_LABELS[key]);
  return `Filled in ${joinWithAnd(found, 'and')} from your screenshot — couldn't identify ${joinWithAnd(missing, 'or')}, so please check ${missing.length > 1 ? 'those' : 'that'} yourself.`;
}

export function ReceiptInput({ receipt, onChange, onRemove, removable }) {
  const [scanStatus, setScanStatus] = useState(null);
  const [scanMessage, setScanMessage] = useState(null);
  const fileInputRef = useRef(null);

  const handleFile = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;

    setScanStatus('scanning');
    setScanMessage(null);
    try {
      const { fields } = await scanReceiptImage(file);
      const foundCount = Object.keys(fields).length;
      if (foundCount === 0) {
        setScanStatus('empty');
        return;
      }
      onChange({ ...receipt, ...fields });
      if (foundCount < Object.keys(FIELD_LABELS).length) {
        setScanStatus('partial');
        setScanMessage(partialScanMessage(fields));
      } else {
        setScanStatus('done');
      }
    } catch {
      setScanStatus('error');
    }
  };

  return (
    <div className="rounded-sheet border border-rule bg-sheet p-4">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
      <select
        value={receipt.operator}
        onChange={(e) => onChange({ ...receipt, operator: e.target.value })}
        className={`rounded border-2 bg-paper px-2 py-2 font-semibold ${
          receipt.operator === 'spin' ? 'border-spin text-spin' : 'border-veo text-veo'
        }`}
      >
        <option value="spin">Spin</option>
        <option value="veo">Veo</option>
      </select>

      <input
        type="number"
        min="1"
        placeholder="Duration (min)"
        value={receipt.durationMin}
        onChange={(e) => onChange({ ...receipt, durationMin: parseFloat(e.target.value) })}
        className="rounded border border-rule bg-paper px-2 py-2 text-ink"
      />

      <input
        type="number"
        min="0"
        step="0.01"
        placeholder="Cost ($)"
        value={receipt.costUSD}
        onChange={(e) => onChange({ ...receipt, costUSD: parseFloat(e.target.value) })}
        className="rounded border border-rule bg-paper px-2 py-2 text-ink"
      />

      <div className="flex items-center gap-2">
        <input
          type="date"
          value={receipt.date}
          onChange={(e) => onChange({ ...receipt, date: e.target.value })}
          className="w-full rounded border border-rule bg-paper px-2 py-2 text-ink"
        />
        {removable && (
          <button
            type="button"
            onClick={onRemove}
            className="-my-2 px-2 py-2 font-mono text-xs text-brick hover:underline"
          >
            ✕
          </button>
        )}
      </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-rule pt-3">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={scanStatus === 'scanning'}
          className="rounded border border-rule px-2 py-1.5 font-mono text-xs text-note hover:border-ink hover:text-ink disabled:opacity-50"
        >
          📷 Scan receipt screenshot
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFile}
          className="hidden"
          aria-label="Upload a screenshot of your Spin or Veo receipt"
        />
        {scanStatus && (
          <span className={`font-mono text-xs ${scanStatus === 'done' ? 'text-river' : 'text-note'}`}>
            {scanMessage || SCAN_STATUS_TEXT[scanStatus]}
          </span>
        )}
      </div>
    </div>
  );
}
