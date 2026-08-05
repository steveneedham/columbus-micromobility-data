import { COPY } from '../constants/messages.js';

export function generateSkillMarkdown(results, formData) {
  const locationLines = formData.locations
    .map((loc) => `- **${loc.name}**: ${loc.address || `${loc.lat}, ${loc.lon}`}`)
    .join('\n');

  const densityLines = (results.locationData || [])
    .map(
      (loc) => `
### ${loc.name}
- **Spin**: ${loc.spinCount} vehicles nearby
- **Veo**: ${loc.veoCount} vehicles nearby`
    )
    .join('\n');

  return `# Curb Your Spending Result

## Your Data
${locationLines}
- Recent rides: ${formData.receipts.length} receipts
- Monthly estimate: ${formData.frequency} rides/month

## Vehicle Density (public GBFS feed)
${densityLines || '_GBFS data unavailable at time of run._'}

## Cost Projection (${formData.frequency} rides/month)
- **Spin 99¢ Club**: $${results.spin.monthlyTotal.toFixed(2)}
- **Veo Premium**: $${results.veo.monthlyTotal.toFixed(2)}

## Recommendation
🏆 **${results.recommendation.winner.toUpperCase()} wins by $${results.recommendation.savings.toFixed(2)}/month**

**Confidence**: ${results.recommendation.confidenceScore}%
**Reasoning**: ${results.recommendation.reasoning}

> ⚠️ ${COPY.disclaimer}

---

## How to Re-Run This Analysis
1. Update your addresses if you move or change regular destinations.
2. Add any new receipts (operator, duration, cost, date).
3. Adjust your monthly ride frequency estimate.
4. Run this skill in Claude (or paste it into ChatGPT/Gemini) to get an updated recommendation.

Each run pulls the public GBFS feed, so recommendations stay current as fleets change.

---

*Generated: ${new Date().toLocaleDateString()} | Curb Your Spending — Columbus Micromobility Data*
`;
}
