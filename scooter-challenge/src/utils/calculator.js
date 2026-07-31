import { OPERATORS } from '../constants/operators.js';

export function projectCost(operator, config) {
  const defaults = OPERATORS[operator];
  if (!defaults) throw new Error(`Unknown operator: ${operator}`);

  const { avgRideDurationMin, ridesPerMonth } = config;
  const monthlyFee = config.monthlyFee ?? defaults.monthlyFee;

  let perRideAvg;
  let breakdown;

  if (operator === 'spin') {
    const ratePerRide = config.ratePerRide ?? defaults.perRideFlat;
    perRideAvg = ratePerRide;
    breakdown = { base: monthlyFee, perMinute: 0, subscription: monthlyFee, perRide: ratePerRide };
  } else {
    const ratePerMin = config.ratePerMin ?? defaults.perMinRate;
    perRideAvg = ratePerMin * avgRideDurationMin;
    breakdown = { base: 0, perMinute: ratePerMin, subscription: monthlyFee, perRide: perRideAvg };
  }

  const monthlyTotal = monthlyFee + perRideAvg * ridesPerMonth;

  return {
    operator,
    perRideAvg,
    monthlyTotal,
    breakdown,
  };
}

export function compareOperators(spinCost, veoCost, huntTimeDiffMin = 0) {
  const diff = veoCost.monthlyTotal - spinCost.monthlyTotal;
  const winner = diff >= 0 ? 'spin' : 'veo';
  const savings = Math.abs(diff);

  let message;
  if (winner === 'spin') {
    message = `Spin saves you $${savings.toFixed(2)}/month.`;
  } else {
    message = `Veo saves you $${savings.toFixed(2)}/month.`;
  }
  if (huntTimeDiffMin) {
    message += ` Veo hunt time is ${huntTimeDiffMin > 0 ? 'longer' : 'shorter'} by ${Math.abs(huntTimeDiffMin)} min on average.`;
  }

  return { winner, savings, message };
}

export function confidenceScore({ numReceipts = 0, costConsistency = 0.5, numLocations = 1, gbfsDataAgeMin = 0 }) {
  const receiptsScore = numReceipts >= 4 ? 60 : numReceipts >= 2 ? 40 : numReceipts >= 1 ? 20 : 0;
  const consistencyScore = Math.round(Math.max(0, Math.min(1, costConsistency)) * 20);
  const locationsScore = numLocations >= 4 ? 20 : numLocations === 3 ? 15 : numLocations === 2 ? 10 : 0;

  const base = receiptsScore + consistencyScore + locationsScore;

  const freshnessMultiplier = gbfsDataAgeMin < 60 ? 1 : gbfsDataAgeMin < 1440 ? 0.85 : 0.5;

  return Math.round(Math.min(100, base) * freshnessMultiplier);
}

export function recommend(spinCost, veoCost, { huntTimeDiffMin = 0, confidence = {} } = {}) {
  const { winner, savings, message } = compareOperators(spinCost, veoCost, huntTimeDiffMin);
  const score = confidenceScore(confidence);

  return {
    winner,
    savings,
    confidenceScore: score,
    reasoning: message,
    factors: {
      costAdvantage: savings > 15 ? 'clear' : savings > 3 ? 'close' : 'near-tie',
      availabilityWin: huntTimeDiffMin < 0,
      speedFactor: winner === 'spin' ? 'favors_spin' : 'neutral',
    },
  };
}
