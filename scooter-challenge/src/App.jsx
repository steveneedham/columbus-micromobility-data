import { useState } from 'react';
import { InputForm } from './components/InputForm.jsx';
import { ResultsCard } from './components/ResultsCard.jsx';
import { useGBFS } from './hooks/useGBFS.js';
import { useCostCalculator } from './hooks/useCostCalculator.js';
import { COPY } from './constants/messages.js';

export default function App() {
  const [formData, setFormData] = useState(null);
  const [results, setResults] = useState(null);
  const [gbfsError, setGbfsError] = useState(null);
  const { fetchVehicles, getNearbyCount } = useGBFS();
  const { calculateCosts, getRecommendation } = useCostCalculator();

  const handleFormSubmit = async (data) => {
    setFormData(data);

    const { spin, veo } = await fetchVehicles();
    const anyError = spin.error || veo.error;
    setGbfsError(anyError ? COPY.gbfsError : null);

    const spinCost = calculateCosts('spin', data);
    const veoCost = calculateCosts('veo', data);

    const locationData = data.locations
      .filter((loc) => (loc.address || (loc.lat != null && loc.lon != null)))
      .map((loc) => {
        const nearby = loc.lat != null && loc.lon != null ? getNearbyCount(loc.lat, loc.lon) : null;
        return {
          name: loc.name,
          spinCount: nearby?.spinCount ?? 0,
          veoCount: nearby?.veoCount ?? 0,
        };
      });

    const dataAgeMin = spin.age ? (Date.now() - spin.age) / 60000 : 999;
    const recommendation = getRecommendation(spinCost, veoCost, data, dataAgeMin);

    setResults({ spin: spinCost, veo: veoCost, recommendation, locationData });
  };

  const handleReset = () => {
    setFormData(null);
    setResults(null);
    setGbfsError(null);
  };

  return (
    <div className="min-h-screen bg-paper px-4 py-10 text-ink sm:px-8">
      <div className="mx-auto max-w-2xl">
        <header className="mb-8">
          <p className="font-mono text-xs uppercase tracking-wide text-river">🛴 Research tool</p>
          <h1 className="mt-1 font-display text-3xl text-ink">Scooter Challenge</h1>
          <p className="mt-2 text-note">{COPY.tagline}</p>
          {!results && <p className="mt-2 text-sm text-note">{COPY.intro}</p>}
        </header>

        <main>
          {gbfsError && (
            <div className="mb-4 rounded-sheet border border-brick-dim bg-sheet p-3 text-sm text-brick">
              {gbfsError}
            </div>
          )}

          {!results ? (
            <InputForm onSubmit={handleFormSubmit} />
          ) : (
            <ResultsCard results={results} formData={formData} onReset={handleReset} />
          )}
        </main>

        <footer className="mt-10 border-t border-rule pt-4">
          <p className="font-mono text-xs text-note">{COPY.privacyNote}</p>
        </footer>
      </div>
    </div>
  );
}
