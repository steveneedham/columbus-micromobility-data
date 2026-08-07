import { useState } from 'react';
import { InputForm } from './components/InputForm.jsx';
import { ResultsCard } from './components/ResultsCard.jsx';
import { Ticker } from './components/Ticker.jsx';
import { SubmissionsGauge } from './components/SubmissionsGauge.jsx';
import { useGBFS } from './hooks/useGBFS.js';
import { useCostCalculator } from './hooks/useCostCalculator.js';
import { COPY } from './constants/messages.js';
import { trackAnalyzeCosts } from './utils/analytics.js';

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
        const nearby = loc.lat != null && loc.lon != null ? getNearbyCount(loc.lat, loc.lon, { spin, veo }) : null;
        return {
          name: loc.name,
          lat: loc.lat,
          lon: loc.lon,
          spinCount: nearby?.spinCount ?? 0,
          veoCount: nearby?.veoCount ?? 0,
          scooterCount: nearby?.scooterCount ?? 0,
          bikeCount: nearby?.bikeCount ?? 0,
        };
      });

    const dataAgeMin = spin.age ? (Date.now() - spin.age) / 60000 : 999;
    const recommendation = getRecommendation(spinCost, veoCost, data, dataAgeMin);

    trackAnalyzeCosts({ formData: data, recommendation });
    setResults({ spin: spinCost, veo: veoCost, recommendation, locationData });
  };

  const handleReset = () => {
    setFormData(null);
    setResults(null);
    setGbfsError(null);
  };

  return (
    <div className="min-h-screen bg-paper text-ink">
      <Ticker />
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-8">
        <header className="mb-8">
          <p className="font-mono text-xs uppercase tracking-wide text-river">🧪 Urban Transit Mobility Lab</p>
          <h1 className="mt-1 font-display text-3xl text-ink">Curb Your Spending</h1>
          <p className="mt-2 text-note">{COPY.tagline}</p>
          {!results && <p className="mt-2 text-sm text-note">{COPY.intro}</p>}
        </header>

        <div className="mb-8">
          <SubmissionsGauge />
        </div>

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
