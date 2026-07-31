const REPO_ISSUES_URL = 'https://github.com/steveneedham/columbus-micromobility-data/issues/new';

// Only computed numbers go into the prefilled report — never location names
// or addresses, since those are free-text fields a user could have typed
// personal details into and this opens a *public* GitHub issue.
export function buildReportIssueUrl(results) {
  const { spin, veo, recommendation } = results;

  const body = `**What looks wrong?**
(describe the incorrect rate, calculation, or data here)

---
_Auto-filled context — no addresses included:_
- Spin: $${spin.breakdown.subscription.toFixed(2)}/mo pass + $${spin.breakdown.perRide.toFixed(2)}/ride → $${spin.monthlyTotal.toFixed(2)}/mo
- Veo: $${veo.breakdown.subscription.toFixed(2)}/mo pass + $${veo.breakdown.perMinute.toFixed(2)}/min → $${veo.monthlyTotal.toFixed(2)}/mo
- Recommendation: ${recommendation.winner} wins by $${recommendation.savings.toFixed(2)}/month (${recommendation.confidenceScore}% confidence)
- Reported from: Curb Your Spending, ${new Date().toLocaleDateString()}`;

  const params = new URLSearchParams({
    title: 'Incorrect rate or calculation in Curb Your Spending',
    body,
    labels: 'bug',
  });

  return `${REPO_ISSUES_URL}?${params.toString()}`;
}
