import { useState } from 'react';
import { LocationInput } from './LocationInput.jsx';
import { ReceiptInput } from './ReceiptInput.jsx';
import { validateReceipt } from '../utils/receiptParser.js';

const MAX_LOCATIONS = 4;
const MAX_RECEIPTS = 10;

function emptyLocation(name) {
  return { name, address: '', lat: null, lon: null };
}

function emptyReceipt() {
  return { operator: 'spin', durationMin: 13, costUSD: 2.39, date: new Date().toISOString().slice(0, 10) };
}

export function InputForm({ onSubmit }) {
  const [locations, setLocations] = useState([emptyLocation('Home')]);
  const [receipts, setReceipts] = useState([emptyReceipt()]);
  const [frequency, setFrequency] = useState(25);
  const [errors, setErrors] = useState([]);

  const updateLocation = (index, updated) => {
    setLocations((prev) => prev.map((loc, i) => (i === index ? updated : loc)));
  };

  const addLocation = () => {
    if (locations.length >= MAX_LOCATIONS) return;
    const names = ['Home', 'Work', 'Grocery store', 'Frequent stop'];
    setLocations((prev) => [...prev, emptyLocation(names[prev.length] ?? 'Stop')]);
  };

  const removeLocation = (index) => {
    setLocations((prev) => prev.filter((_, i) => i !== index));
  };

  const updateReceipt = (index, updated) => {
    setReceipts((prev) => prev.map((r, i) => (i === index ? updated : r)));
  };

  const addReceipt = () => {
    if (receipts.length >= MAX_RECEIPTS) return;
    setReceipts((prev) => [...prev, emptyReceipt()]);
  };

  const removeReceipt = (index) => {
    setReceipts((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const receiptErrors = receipts.flatMap((r, i) => {
      const { valid, errors: rErrors } = validateReceipt(r);
      return valid ? [] : rErrors.map((msg) => `Ride ${i + 1}: ${msg}`);
    });

    const home = locations[0];
    const locationErrors = [];
    if (!home.address && (home.lat == null || home.lon == null)) {
      locationErrors.push('Home needs an address or coordinates.');
    }

    const allErrors = [...receiptErrors, ...locationErrors];
    setErrors(allErrors);
    if (allErrors.length) return;

    onSubmit({ locations, receipts, frequency });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8">
      <section>
        <h2 className="font-display text-xl text-ink">Where do you ride?</h2>
        <p className="mt-1 text-sm text-note">Home is required. Add up to 3 more frequent stops.</p>
        <div className="mt-3 space-y-3">
          {locations.map((location, i) => (
            <LocationInput
              key={i}
              location={location}
              index={i}
              removable={i > 0}
              onChange={(updated) => updateLocation(i, updated)}
              onRemove={() => removeLocation(i)}
            />
          ))}
        </div>
        {locations.length < MAX_LOCATIONS && (
          <button
            type="button"
            onClick={addLocation}
            className="-mx-1 mt-1 px-1 py-2 font-mono text-xs text-river hover:underline"
          >
            + Add another location
          </button>
        )}
      </section>

      <section>
        <h2 className="font-display text-xl text-ink">Your recent rides</h2>
        <p className="mt-1 text-sm text-note">Enter operator, duration, and cost from recent receipts.</p>
        <div className="mt-3 space-y-3">
          {receipts.map((receipt, i) => (
            <ReceiptInput
              key={i}
              receipt={receipt}
              removable={receipts.length > 1}
              onChange={(updated) => updateReceipt(i, updated)}
              onRemove={() => removeReceipt(i)}
            />
          ))}
        </div>
        {receipts.length < MAX_RECEIPTS && (
          <button
            type="button"
            onClick={addReceipt}
            className="-mx-1 mt-1 px-1 py-2 font-mono text-xs text-river hover:underline"
          >
            + Add another ride
          </button>
        )}
      </section>

      <section>
        <label className="font-display text-xl text-ink">
          About {frequency} rides per month
        </label>
        <input
          type="range"
          min="5"
          max="50"
          value={frequency}
          onChange={(e) => setFrequency(parseInt(e.target.value, 10))}
          className="mt-3 w-full accent-river"
        />
      </section>

      {errors.length > 0 && (
        <div className="rounded-sheet border border-brick-dim bg-sheet p-4 text-sm text-brick">
          <ul className="list-inside list-disc space-y-1">
            {errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <button
        type="submit"
        className="w-full rounded-sheet bg-river px-6 py-3 font-mono text-sm uppercase tracking-wide text-sheet hover:opacity-90"
      >
        Analyze my costs
      </button>
    </form>
  );
}
