import { useEffect, useRef, useState } from 'react';
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

function hasLocationValue(loc) {
  return Boolean(loc.address) || (loc.lat != null && loc.lon != null);
}

function StepArrow() {
  return (
    <span className="step-arrow mr-1 text-brick" aria-hidden="true">
      ➤
    </span>
  );
}

function StepBox({ number, title, subtitle, active, locked, children }) {
  return (
    <section
      className={`rounded-sheet border p-4 transition-opacity ${
        locked ? 'border-rule opacity-50' : active ? 'border-river' : 'border-rule'
      }`}
    >
      <div className="flex items-baseline gap-2">
        {active && <StepArrow />}
        <span className="font-display text-xl leading-none text-river">{number}</span>
        <h2 className="font-display text-xl text-ink">{title}</h2>
      </div>
      {subtitle && <p className="mt-1 text-sm text-note">{subtitle}</p>}
      <fieldset disabled={locked} className="m-0 mt-3 min-w-0 border-0 p-0">
        {children}
      </fieldset>
      {locked && <p className="mt-2 font-mono text-xs text-note">Complete the step above to unlock this.</p>}
    </section>
  );
}

export function InputForm({ onSubmit }) {
  const [locations, setLocations] = useState([emptyLocation('Home')]);
  const [receipts, setReceipts] = useState([emptyReceipt()]);
  const [frequency, setFrequency] = useState(25);
  const [frequencyTouched, setFrequencyTouched] = useState(false);
  const [receiptsTouched, setReceiptsTouched] = useState(false);
  const [errors, setErrors] = useState([]);

  const step2Ref = useRef(null);
  const step3Ref = useRef(null);
  const step4Ref = useRef(null);
  const prevStepRef = useRef(null);

  const step1Done = locations.filter(hasLocationValue).length >= 2;
  const step2Done = step1Done && receiptsTouched && receipts.some((r) => validateReceipt(r).valid);
  const step3Done = step2Done && frequencyTouched;
  const currentStep = !step1Done ? 1 : !step2Done ? 2 : !step3Done ? 3 : 4;

  useEffect(() => {
    const refs = { 2: step2Ref, 3: step3Ref, 4: step4Ref };
    if (prevStepRef.current != null && currentStep > prevStepRef.current) {
      refs[currentStep]?.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    prevStepRef.current = currentStep;
  }, [currentStep]);

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
    setReceiptsTouched(true);
  };

  const addReceipt = () => {
    if (receipts.length >= MAX_RECEIPTS) return;
    setReceipts((prev) => [...prev, emptyReceipt()]);
    setReceiptsTouched(true);
  };

  const removeReceipt = (index) => {
    setReceipts((prev) => prev.filter((_, i) => i !== index));
    setReceiptsTouched(true);
  };

  const handleFrequencyChange = (e) => {
    setFrequency(parseInt(e.target.value, 10));
    setFrequencyTouched(true);
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
        <p className="font-mono text-xs uppercase tracking-wide text-river">🧪 Start here</p>
        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {/* SITE-GUIDE:START (auto-synced daily by scripts/update_site_guide.py -- see that file's docstring before hand-editing) */}
          {[
            'Add your home + at least one more address.',
            'Add at least 1 receipt — 2+ from different operators (Spin and Veo) preferred for a more accurate comparison.',
            'Set about how many rides you take per month.',
            'Click "Analyze my costs."',
          ]
          /* SITE-GUIDE:END */
          .map((step, i) => (
            <div key={i} className="flex gap-3 rounded-sheet border border-rule bg-sheet p-3">
              <span className="font-display text-xl leading-none text-river">{i + 1}</span>
              <p className="text-sm text-note">{step}</p>
            </div>
          ))}
        </div>
      </section>

      <StepBox number={1} title="Where do you ride?" subtitle="Home is required. Add up to 3 more frequent stops." active={currentStep === 1} locked={false}>
        <div className="space-y-3">
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
      </StepBox>

      <div ref={step2Ref}>
        <StepBox
          number={2}
          title="Your recent rides"
          subtitle="Enter operator, duration, and cost from recent receipts, or scan a screenshot to fill them in."
          active={currentStep === 2}
          locked={currentStep < 2}
        >
          {currentStep === 2 && !receiptsTouched && (
            <p className="mb-2 font-mono text-xs text-note">
              Still showing a placeholder ride — edit a field or scan a screenshot to continue.
            </p>
          )}
          <div className="space-y-3">
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
        </StepBox>
      </div>

      <div ref={step3Ref}>
        <StepBox number={3} title={`About ${frequency} rides per month`} active={currentStep === 3} locked={currentStep < 3}>
          <input
            type="range"
            min="5"
            max="50"
            value={frequency}
            onChange={handleFrequencyChange}
            className="w-full accent-river"
          />
        </StepBox>
      </div>

      {errors.length > 0 && (
        <div className="rounded-sheet border border-brick-dim bg-sheet p-4 text-sm text-brick">
          <ul className="list-inside list-disc space-y-1">
            {errors.map((err) => (
              <li key={err}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      <div ref={step4Ref}>
        <StepBox number={4} title="Analyze" active={currentStep === 4} locked={currentStep < 4}>
          <button
            type="submit"
            className="w-full rounded-sheet bg-river px-6 py-3 font-mono text-sm uppercase tracking-wide text-sheet hover:opacity-90 disabled:opacity-50"
          >
            Analyze my costs
          </button>
        </StepBox>
      </div>
    </form>
  );
}
