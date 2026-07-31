export function ReceiptInput({ receipt, onChange, onRemove, removable }) {
  return (
    <div className="grid grid-cols-2 gap-2 rounded-sheet border border-rule bg-sheet p-4 sm:grid-cols-4">
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
  );
}
