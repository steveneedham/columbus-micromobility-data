import { TICKER_EXAMPLES } from '../constants/tickerExamples.js';

const OPERATOR_PATTERN = /\b(Spin|Veo)\b/g;

function renderWithOperatorColors(text) {
  return text.split(OPERATOR_PATTERN).map((part, i) =>
    part === 'Spin' || part === 'Veo' ? (
      <span key={i} className={`font-semibold ${part === 'Spin' ? 'text-spin' : 'text-veo'}`}>
        {part}
      </span>
    ) : (
      part
    )
  );
}

function winnerDotClass(text) {
  const matches = text.match(OPERATOR_PATTERN);
  const winner = matches ? matches[matches.length - 1] : null;
  if (winner === 'Spin') return 'text-spin';
  if (winner === 'Veo') return 'text-veo';
  return 'text-river';
}

export function Ticker() {
  const items = [...TICKER_EXAMPLES, ...TICKER_EXAMPLES];

  return (
    <div
      className="ticker-track overflow-hidden border-y border-rule bg-panel py-2"
      role="marquee"
      aria-label="Illustrative example savings from Curb Your Spending — not live or tracked user data"
    >
      <div className="ticker-content flex w-max gap-8 whitespace-nowrap px-4 font-mono text-xs text-note">
        {items.map((text, i) => (
          <span key={i} className="flex items-center gap-2" aria-hidden={i >= TICKER_EXAMPLES.length}>
            <span className={winnerDotClass(text)}>●</span>
            {renderWithOperatorColors(text)}
          </span>
        ))}
      </div>
    </div>
  );
}
