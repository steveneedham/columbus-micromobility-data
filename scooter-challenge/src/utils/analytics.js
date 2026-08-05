import { LANDMARKS } from '../constants/landmarks.js';
import { haversineDistance } from './geo.js';

// How "anonymized" works here: raw addresses and exact lat/lon never leave
// the browser for analytics. A location is generalized to its nearest known
// Columbus landmark/neighborhood (within NEARBY_RADIUS_MI) before being
// logged, or dropped to a generic bucket if nothing is close enough that
// "nearest landmark" would still be a meaningful generalization.
const NEARBY_RADIUS_MI = 3;

function nearestNeighborhood(lat, lon) {
  if (typeof lat !== 'number' || typeof lon !== 'number') return null;
  let nearestName = null;
  let nearestDistance = Infinity;
  for (const landmark of LANDMARKS) {
    const distance = haversineDistance(lat, lon, landmark.lat, landmark.lon);
    if (distance < nearestDistance) {
      nearestName = landmark.name;
      nearestDistance = distance;
    }
  }
  return nearestDistance <= NEARBY_RADIUS_MI ? nearestName : 'Columbus area (other)';
}

export function trackAnalyzeCosts({ formData, recommendation }) {
  const locations = formData.locations || [];
  const neighborhoods = [...new Set(
    locations
      .map((loc) => nearestNeighborhood(loc.lat, loc.lon))
      .filter(Boolean)
  )];

  const payload = {
    rides_per_month: formData.frequency,
    num_locations: locations.filter((loc) => loc.address || (loc.lat != null && loc.lon != null)).length,
    num_receipts: (formData.receipts || []).length,
    neighborhoods,
    winner: recommendation.winner,
    savings_usd: Math.round(recommendation.savings * 100) / 100,
    confidence_score: recommendation.confidenceScore,
  };

  if (typeof window === 'undefined') return;
  if (window.posthog && typeof window.posthog.capture === 'function') {
    window.posthog.capture('analyze_costs', payload);
  }
  if (typeof window.gtag === 'function') {
    window.gtag('event', 'analyze_costs', payload);
  }
}
