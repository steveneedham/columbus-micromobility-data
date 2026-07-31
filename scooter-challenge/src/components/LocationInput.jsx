import { useState } from 'react';

export function LocationInput({ location, onChange, onRemove, index, removable }) {
  const [showCoordinates, setShowCoordinates] = useState(false);

  return (
    <div className="rounded-sheet border border-rule bg-sheet p-4">
      <div className="flex items-center justify-between gap-2">
        <label className="font-mono text-xs uppercase tracking-wide text-note">{location.name}</label>
        {removable && (
          <button
            type="button"
            onClick={onRemove}
            className="font-mono text-xs text-brick hover:underline"
          >
            Remove
          </button>
        )}
      </div>

      {!showCoordinates ? (
        <input
          type="text"
          placeholder="Address or intersection"
          value={location.address}
          onChange={(e) => onChange({ ...location, address: e.target.value })}
          className="mt-2 w-full rounded border border-rule bg-paper px-3 py-2 text-ink outline-none focus:border-river"
        />
      ) : (
        <div className="mt-2 grid grid-cols-2 gap-2">
          <input
            type="number"
            step="0.0001"
            placeholder="Latitude"
            value={location.lat ?? ''}
            onChange={(e) => onChange({ ...location, lat: parseFloat(e.target.value) })}
            className="rounded border border-rule bg-paper px-3 py-2 text-ink outline-none focus:border-river"
          />
          <input
            type="number"
            step="0.0001"
            placeholder="Longitude"
            value={location.lon ?? ''}
            onChange={(e) => onChange({ ...location, lon: parseFloat(e.target.value) })}
            className="rounded border border-rule bg-paper px-3 py-2 text-ink outline-none focus:border-river"
          />
        </div>
      )}

      <button
        type="button"
        onClick={() => setShowCoordinates((prev) => !prev)}
        className="mt-2 font-mono text-xs text-river hover:underline"
      >
        {showCoordinates ? 'Use address instead' : 'Enter coordinates instead'}
      </button>
    </div>
  );
}
