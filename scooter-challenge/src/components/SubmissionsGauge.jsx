import { useState } from 'react';
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
  const [expanded, setExpanded] = useState(false);
  const [showRaw, setShowRaw] = useState(false);
  const count = SUBMISSIONS.count || 0;
  const pct = Math.min(100, Math.round((count / GOAL) * 100));
  const fillLength = (Math.min(count, GOAL) / GOAL) * CIRCUMFERENCE;
  const lastUpdated = formatLastUpdated(SUBMISSIONS.generated_at);

  return (
    <div className="rounded-sheet border border-rule bg-sheet p-4">
      <button
        type="button"
        onClick={() => setExpanded((prev) => !prev)}
        aria-expanded={expanded}
        className="flex w-full items-center justify-between gap-3 text-left"
      >
        <span className="font-mono text-xs uppercase tracking-wide text-river">
          🧪 Community progress — {pct}% ({count.toLocaleString()} of {GOAL.toLocaleString()} submissions)
        </span>
        <span className="shrink-0 font-mono text-xs text-note">{expanded ? '▲ Collapse' : '▼ Expand'}</span>
      </button>

      {expanded && (
        <div className="mt-4 text-center">
          <h3 className="font-display text-lg text-ink">Data collection status</h3>

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

          <button
            type="button"
            onClick={() => setShowRaw((prev) => !prev)}
            aria-expanded={showRaw}
            className="-mx-1 mt-4 px-1 py-2 font-mono text-xs text-river hover:underline"
          >
            {showRaw ? 'Hide' : 'Show'} raw submissions.json
          </button>
          {showRaw && (
            <pre className="mt-2 max-h-64 overflow-auto rounded border border-rule bg-paper p-3 text-left font-mono text-xs text-ink">
              {JSON.stringify(SUBMISSIONS, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
