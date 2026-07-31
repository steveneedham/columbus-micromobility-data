import { SkillExporter } from './SkillExporter.jsx';
import { LocationMap } from './LocationMap.jsx';

function ConfidenceBar({ score }) {
  const color = score >= 80 ? 'bg-river' : score >= 50 ? 'bg-brick-dim' : 'bg-note';
  return (
    <div className="h-2 w-full rounded-full bg-panel">
      <div className={`h-2 rounded-full ${color}`} style={{ width: `${score}%` }} />
    </div>
  );
}

export function ResultsCard({ results, formData, onReset }) {
  const { spin, veo, recommendation, locationData = [] } = results;
  const winnerLabel = recommendation.winner === 'spin' ? 'Spin' : 'Veo';

  return (
    <div className="space-y-6">
      <div className="rounded-sheet border-l-4 border-river bg-sheet p-5">
        <p className="font-mono text-xs uppercase tracking-wide text-note">Recommendation</p>
        <p className="mt-1 font-display text-2xl text-ink">
          🏆 {winnerLabel} saves you ${recommendation.savings.toFixed(2)}/month
        </p>
        <p className="mt-2 text-sm text-note">{recommendation.reasoning}</p>

        <div className="mt-4">
          <div className="flex items-center justify-between text-xs text-note">
            <span>Confidence</span>
            <span>{recommendation.confidenceScore}%</span>
          </div>
          <div className="mt-1">
            <ConfidenceBar score={recommendation.confidenceScore} />
          </div>
        </div>
      </div>

      <div className="overflow-x-auto rounded-sheet border border-rule">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="bg-panel text-left font-mono text-xs uppercase tracking-wide text-note">
              <th className="px-4 py-2">Operator</th>
              <th className="px-4 py-2">Per ride (avg)</th>
              <th className="px-4 py-2">Monthly total</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-t border-rule">
              <td className="px-4 py-2 text-ink">
                <div>Spin 99¢ Club</div>
                <div className="mt-0.5 font-mono text-xs text-note">
                  ${spin.breakdown.subscription.toFixed(2)}/mo pass + ${spin.breakdown.perRide.toFixed(2)}/ride
                </div>
              </td>
              <td className="px-4 py-2 text-ink">${spin.perRideAvg.toFixed(2)}</td>
              <td className="px-4 py-2 text-ink">${spin.monthlyTotal.toFixed(2)}</td>
            </tr>
            <tr className="border-t border-rule">
              <td className="px-4 py-2 text-ink">
                <div>Veo Premium</div>
                <div className="mt-0.5 font-mono text-xs text-note">
                  ${veo.breakdown.subscription.toFixed(2)}/mo pass + ${veo.breakdown.perMinute.toFixed(2)}/min
                </div>
              </td>
              <td className="px-4 py-2 text-ink">${veo.perRideAvg.toFixed(2)}</td>
              <td className="px-4 py-2 text-ink">${veo.monthlyTotal.toFixed(2)}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {locationData.length > 0 && (
        <div className="rounded-sheet border border-rule bg-sheet p-5">
          <h3 className="font-display text-lg text-ink">Vehicle density by location</h3>
          <div className="mt-3">
            <LocationMap locations={locationData} />
          </div>
          <div className="mt-3 space-y-2">
            {locationData.map((loc) => (
              <div key={loc.name} className="flex items-center justify-between text-sm">
                <span className="text-ink">{loc.name}</span>
                <span className="font-mono text-note">
                  Spin: {loc.spinCount} · Veo: {loc.veoCount}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <SkillExporter results={results} formData={formData} />

      <button
        type="button"
        onClick={onReset}
        className="font-mono text-xs uppercase tracking-wide text-note hover:underline"
      >
        ← Start over
      </button>
    </div>
  );
}
