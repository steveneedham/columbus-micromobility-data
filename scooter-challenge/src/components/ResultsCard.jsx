import { SkillExporter } from './SkillExporter.jsx';
import { LocationMap } from './LocationMap.jsx';
import { ShareCard } from './ShareCard.jsx';
import { ScooterIcon, BikeIcon } from './VehicleIcons.jsx';
import { COPY } from '../constants/messages.js';
import { buildReportIssueUrl } from '../utils/reportIssue.js';
import { RATES_UPDATED_AT } from '../constants/operators.js';

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
  const winnerIsSpin = recommendation.winner === 'spin';
  const winnerLabel = winnerIsSpin ? 'Spin' : 'Veo';
  const winnerBorder = winnerIsSpin ? 'border-spin' : 'border-veo';
  const winnerText = winnerIsSpin ? 'text-spin' : 'text-veo';

  return (
    <div className="space-y-6">
      <div className={`rounded-sheet border-l-4 ${winnerBorder} bg-sheet p-5`}>
        <p className="font-mono text-xs uppercase tracking-wide text-note">Recommendation</p>
        <p className="mt-1 font-display text-2xl text-ink">
          🏆 <span className={`font-semibold ${winnerText}`}>{winnerLabel}</span> saves you $
          {recommendation.savings.toFixed(2)}/month
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

        <p className="mt-4 border-t border-rule pt-3 font-mono text-xs text-note">{COPY.disclaimer}</p>
      </div>

      <ShareCard results={results} formData={formData} />

      <p className="font-mono text-xs text-note">Rates as of {RATES_UPDATED_AT}</p>

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
            <tr className="border-l-4 border-t border-spin border-t-rule">
              <td className="px-4 py-2 text-ink">
                <div className="font-semibold text-spin">Spin 99¢ Club</div>
                <div className="mt-0.5 font-mono text-xs text-note">
                  ${spin.breakdown.subscription.toFixed(2)}/mo pass + ${spin.breakdown.perRide.toFixed(2)}/ride
                </div>
              </td>
              <td className="px-4 py-2 text-ink">${spin.perRideAvg.toFixed(2)}</td>
              <td className="px-4 py-2 text-ink">${spin.monthlyTotal.toFixed(2)}</td>
            </tr>
            <tr className="border-l-4 border-t border-veo border-t-rule">
              <td className="px-4 py-2 text-ink">
                <div className="font-semibold text-veo">Veo Premium</div>
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

      <a
        href={buildReportIssueUrl(results)}
        target="_blank"
        rel="noopener noreferrer"
        className="-mx-1 -my-2 inline-flex items-center gap-1 px-1 py-2 font-mono text-xs text-note hover:text-brick hover:underline"
      >
        ⚠️ Report incorrect data or rate
      </a>

      {locationData.length > 0 && (
        <div className="rounded-sheet border border-rule bg-sheet p-5">
          <h3 className="font-display text-lg text-ink">Vehicle density by location</h3>
          <div className="mt-3">
            <LocationMap locations={locationData} />
          </div>
          <div className="mt-3 space-y-2">
            {locationData.map((loc) => (
              <div key={loc.name} className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-sm">
                <span className="text-ink">{loc.name}</span>
                <span className="flex items-center gap-3 font-mono text-note">
                  <span className="text-spin">Spin: {loc.spinCount}</span>
                  <span className="text-veo">Veo: {loc.veoCount}</span>
                  <span className="flex items-center gap-1 text-note" title="Scooters nearby">
                    <ScooterIcon size={14} />
                    {loc.scooterCount}
                  </span>
                  <span className="flex items-center gap-1 text-note" title="Bikes nearby">
                    <BikeIcon size={14} />
                    {loc.bikeCount}
                  </span>
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
        className="-mx-1 -my-2 px-1 py-2 font-mono text-xs uppercase tracking-wide text-note hover:underline"
      >
        ← Start over
      </button>
    </div>
  );
}
