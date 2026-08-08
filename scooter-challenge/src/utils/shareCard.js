// Matches the Field Ledger "project card" pattern already used elsewhere in
// this repo (see ../../demand-forecast-card.svg) — 1200x630, same palette,
// eyebrow/headline/hairline/footer rhythm — so a screenshot or exported PNG
// reads as part of the same publication.
const PALETTE = {
  paper: '#F3F0E8',
  sheet: '#FBFAF6',
  panel: '#E8E4DA',
  rule: '#C8C2B5',
  ink: '#202A2E',
  note: '#5D696D',
  brick: '#A94728',
  river: '#236A73',
};

function esc(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

export function generateShareCardSVG(results, formData) {
  const { spin, veo, recommendation } = results;
  const winnerIsSpin = recommendation.winner === 'spin';
  const winnerLabel = winnerIsSpin ? 'Spin' : 'Veo';
  const winnerHex = winnerIsSpin ? '#E03F23' : '#00B8AA';
  const otherLabel = winnerIsSpin ? 'Veo' : 'Spin';
  const otherHex = winnerIsSpin ? '#00B8AA' : '#E03F23';
  const winnerMonthly = winnerIsSpin ? spin.monthlyTotal : veo.monthlyTotal;
  const otherMonthly = winnerIsSpin ? veo.monthlyTotal : spin.monthlyTotal;

  const locationCount = formData.locations.length;
  const receiptCount = formData.receipts.length;
  const date = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="title desc">
  <title id="title">Curb Your Spending — ${esc(winnerLabel)} wins by $${recommendation.savings.toFixed(2)}/month</title>
  <desc id="desc">A Curb Your Spending cost-comparison result card, styled with the Field Ledger design system.</desc>
  <style>
    .display{font-family:Newsreader,Georgia,'Times New Roman',serif}
    .body{font-family:'IBM Plex Sans',Arial,sans-serif}
    .mono{font-family:'IBM Plex Mono','Courier New',monospace}
  </style>
  <rect width="1200" height="630" fill="${PALETTE.paper}"/>
  <rect x="1" y="1" width="1198" height="628" fill="none" stroke="${PALETTE.rule}" stroke-width="2"/>

  <text x="78" y="82" class="mono" font-size="13" font-weight="600" letter-spacing="1.8" fill="${PALETTE.brick}">🧪 URBAN TRANSIT MOBILITY LAB</text>
  <text x="78" y="104" class="mono" font-size="11" letter-spacing="1.4" fill="${PALETTE.note}">CURB YOUR SPENDING · COLUMBUS, OH</text>

  <line x1="78" y1="142" x2="1122" y2="142" stroke="${PALETTE.rule}" stroke-width="1"/>

  <text x="76" y="222" class="display" font-size="60" font-weight="500" fill="${PALETTE.ink}">🏆 <tspan fill="${winnerHex}" font-weight="600">${esc(winnerLabel)}</tspan> wins by</text>
  <text x="76" y="292" class="display" font-size="72" font-weight="500" fill="${winnerHex}">$${recommendation.savings.toFixed(2)}/month</text>
  <text x="80" y="330" class="body" font-size="19" fill="${PALETTE.note}">${esc(recommendation.reasoning)}</text>

  <line x1="80" y1="366" x2="720" y2="366" stroke="${PALETTE.river}" stroke-width="2"/>
  <g transform="translate(80 402)">
    <text x="0" y="0" class="mono" font-size="11" letter-spacing="1" fill="${PALETTE.note}">${esc(winnerLabel).toUpperCase()} · MONTHLY</text>
    <text x="0" y="47" class="display" font-size="42" font-weight="500" fill="${winnerHex}">$${winnerMonthly.toFixed(0)}</text>
    <text x="220" y="0" class="mono" font-size="11" letter-spacing="1" fill="${PALETTE.note}">${esc(otherLabel).toUpperCase()} · MONTHLY</text>
    <text x="220" y="47" class="display" font-size="42" font-weight="500" fill="${otherHex}">$${otherMonthly.toFixed(0)}</text>
    <text x="440" y="0" class="mono" font-size="11" letter-spacing="1" fill="${PALETTE.note}">CONFIDENCE</text>
    <text x="440" y="47" class="display" font-size="42" font-weight="500" fill="${PALETTE.ink}">${recommendation.confidenceScore}%</text>
  </g>

  <g transform="translate(800 184)">
    <rect x="0" y="0" width="322" height="278" fill="${PALETTE.panel}" stroke="${PALETTE.rule}"/>
    <text x="26" y="38" class="mono" font-size="11" font-weight="600" letter-spacing="1.2" fill="${PALETTE.river}">THIS RESULT IS BASED ON</text>
    <line x1="26" y1="55" x2="296" y2="55" stroke="#9CC6C9"/>
    <g class="body" font-size="16" fill="${PALETTE.ink}">
      <circle cx="34" cy="91" r="5" fill="${PALETTE.river}"/><text x="52" y="97">${formData.frequency} rides/month</text>
      <circle cx="34" cy="132" r="5" fill="${PALETTE.river}"/><text x="52" y="138">${receiptCount} logged ride${receiptCount === 1 ? '' : 's'}</text>
      <circle cx="34" cy="173" r="5" fill="${PALETTE.brick}"/><text x="52" y="179">${locationCount} location${locationCount === 1 ? '' : 's'} checked</text>
    </g>
    <text x="26" y="226" class="body" font-size="12" fill="${PALETTE.note}">Public Spin/Veo GBFS snapshot + your own</text>
    <text x="26" y="244" class="body" font-size="12" fill="${PALETTE.note}">ride history — not a citywide average.</text>
  </g>

  <line x1="78" y1="536" x2="1122" y2="536" stroke="${PALETTE.rule}"/>
  <text x="80" y="570" class="mono" font-size="11" letter-spacing="1" fill="${PALETTE.note}">GENERATED ${esc(date).toUpperCase()} · ESTIMATE ONLY, NOT A GUARANTEE</text>
  <text x="1120" y="570" text-anchor="end" class="mono" font-size="11" fill="${PALETTE.brick}">COMPARE YOUR OWN COLUMBUS RIDES</text>
</svg>`;
}
