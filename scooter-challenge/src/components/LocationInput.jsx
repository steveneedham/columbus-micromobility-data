import { useState } from 'react';
import { LANDMARKS } from '../constants/landmarks.js';

export function LocationInput({ location, onChange, onRemove, index, removable }) {
  const [showCoordinates, setShowCoordinates] = useState(false);
  const [locating, setLocating] = useState(false);
  const [locateError, setLocateError] = useState(null);

  const hasCoords = location.lat != null && location.lon != null;

  const useMyLocation = () => {
    if (!navigator.geolocation) {
      setLocateError('Geolocation is not available in this browser.');
      return;
    }
    setLocating(true);
    setLocateError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        onChange({
          ...location,
          address: location.address || 'Current location',
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
        });
        setLocating(false);
      },
      (err) => {
        setLocateError(err.message || 'Unable to get your location.');
        setLocating(false);
      },
      { timeout: 10000 }
    );
  };

  const useLandmark = (e) => {
    const landmark = LANDMARKS.find((l) => l.name === e.target.value);
    if (!landmark) return;
    setLocateError(null);
    onChange({ ...location, address: landmark.name, lat: landmark.lat, lon: landmark.lon });
    e.target.value = '';
  };

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

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
        <button
          type="button"
          onClick={useMyLocation}
          disabled={locating}
          className="font-mono text-xs text-river hover:underline disabled:opacity-50"
        >
          {locating ? 'Locating…' : '📍 Use my location'}
        </button>

        <select
          defaultValue=""
          onChange={useLandmark}
          className="rounded border-none bg-transparent font-mono text-xs text-river underline"
        >
          <option value="" disabled>
            📌 Jump to a landmark…
          </option>
          {LANDMARKS.map((landmark) => (
            <option key={landmark.name} value={landmark.name}>
              {landmark.name}
            </option>
          ))}
        </select>

        <button
          type="button"
          onClick={() => setShowCoordinates((prev) => !prev)}
          className="font-mono text-xs text-note hover:underline"
        >
          {showCoordinates ? 'Use address instead' : 'Enter coordinates instead'}
        </button>
      </div>

      {locateError && <p className="mt-1 font-mono text-xs text-brick">{locateError}</p>}
      {hasCoords && (
        <p className="mt-1 font-mono text-xs text-note">
          → {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
        </p>
      )}
    </div>
  );
}
