import { useCallback } from 'react';
import { projectCost, recommend } from '../utils/calculator.js';

function averageDurationMin(receipts) {
  if (!receipts.length) return 13.5;
  return receipts.reduce((sum, r) => sum + r.durationMin, 0) / receipts.length;
}

function costConsistency(receipts) {
  if (receipts.length < 2) return 0.5;
  const costs = receipts.map((r) => r.costUSD);
  const mean = costs.reduce((a, b) => a + b, 0) / costs.length;
  const variance = costs.reduce((sum, c) => sum + (c - mean) ** 2, 0) / costs.length;
  const stdev = Math.sqrt(variance);
  const relativeStdev = mean > 0 ? stdev / mean : 1;
  return Math.max(0, 1 - relativeStdev);
}

export function useCostCalculator() {
  const calculateCosts = useCallback((operator, formData) => {
    return projectCost(operator, {
      avgRideDurationMin: averageDurationMin(formData.receipts),
      ridesPerMonth: formData.frequency,
    });
  }, []);

  const getRecommendation = useCallback((spinCost, veoCost, formData, gbfsDataAgeMin = 0) => {
    return recommend(spinCost, veoCost, {
      confidence: {
        numReceipts: formData.receipts.length,
        costConsistency: costConsistency(formData.receipts),
        numLocations: formData.locations.length,
        gbfsDataAgeMin,
      },
    });
  }, []);

  return { calculateCosts, getRecommendation };
}
