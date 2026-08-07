import SUBMISSIONS from '../constants/submissions.json';

const GOAL = 100;
const RADIUS = 90;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

function formatLastUpdated(iso) {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
  });
}

export function SubmissionsGauge() {
  const count = SUBMISSIONS.count || 0;
  const pct = Math.min(100, Math.round((count / GOAL) * 100));
  const fillLength = (Math.min(count, GOAL) / GOAL) * CIRCUMFERENCE;
  const lastUpdated = formatLastUpdated(SUBMISSIONS.generated_at);

  return (
    <div className="rounded-sheet border border-rule bg-sheet p-5 text-center">
      <p className="font-mono text-xs uppercase tracking-wide text-river">🧪 Community progress</p>
      <h3 className="mt-1 font-display text-lg text-ink">Data collection status</h3>

      <div className="relative mx-auto mt-4 h-40 w-40">
        <svg viewBox="0 0 200 200" className="h-40 w-40 -rotate-90">
          <circle cx="100" cy="100" r={RADIUS} fill="none" className="stroke-rule" strokeWidth="8" />
          <circle
            cx="100"
            cy="100"
            r={RADIUS}
            fill="none"
            className="stroke-river"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={CIRCUMFERENCE - fillLength}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <p className="font-display text-3xl text-ink">{pct}%</p>
          <p className="mt-1 font-mono text-xs text-note">
            {count.toLocaleString()} submission{count === 1 ? '' : 's'}
          </p>
        </div>
      </div>

      <p className="mt-3 font-mono text-xs uppercase tracking-wide text-note">Goal: {GOAL.toLocaleString()} submissions</p>
      {lastUpdated && (
        <p className="mt-2 font-mono text-xs text-note">
          Last updated {lastUpdated} — new submissions are anonymized and pulled in on a schedule, not shown live, so
          this count can lag by up to ~6 hours.
        </p>
      )}
      <p className="mt-3 text-sm text-note">
        Help riders make smarter operator choices — every anonymized "Analyze my costs" run adds to this count.
      </p>
    </div>
  );
}
