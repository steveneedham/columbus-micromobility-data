import { useCallback, useState } from 'react';
import { GBFS_ENDPOINTS, DEFAULT_RADIUS } from '../constants/operators.js';
import { parseSpinVehicles, parseVeoVehicles } from '../utils/gbfs.js';
import { nearbyVehicles } from '../utils/geo.js';

const EMPTY_STATE = {
  spin: { vehicles: [], loading: false, error: null, age: null },
  veo: { vehicles: [], loading: false, error: null, age: null },
};

export function useGBFS() {
  const [data, setData] = useState(EMPTY_STATE);

  const fetchOne = useCallback(async (operator, parser) => {
    try {
      const res = await fetch(GBFS_ENDPOINTS[operator].url);
      if (!res.ok) throw new Error(`${operator} GBFS request failed: ${res.status}`);
      const json = await res.json();
      return { vehicles: parser(json), loading: false, error: null, age: Date.now() };
    } catch (err) {
      return { vehicles: [], loading: false, error: err.message, age: null };
    }
  }, []);

  const fetchVehicles = useCallback(async () => {
    setData((prev) => ({
      spin: { ...prev.spin, loading: true },
      veo: { ...prev.veo, loading: true },
    }));

    const [spin, veo] = await Promise.all([
      fetchOne('spin', parseSpinVehicles),
      fetchOne('veo', parseVeoVehicles),
    ]);

    setData({ spin, veo });
    return { spin, veo };
  }, [fetchOne]);

  const getNearbyCount = useCallback(
    (lat, lon, radius = DEFAULT_RADIUS) => {
      if (typeof lat !== 'number' || typeof lon !== 'number') {
        return { spinCount: 0, veoCount: 0, spinNearest: null, veoNearest: null, scooterCount: 0, bikeCount: 0 };
      }
      const allVehicles = [...data.spin.vehicles, ...data.veo.vehicles];
      const nearby = nearbyVehicles(lat, lon, allVehicles, radius);
      const combined = [...nearby.spin, ...nearby.veo];
      return {
        spinCount: nearby.spin.length,
        veoCount: nearby.veo.length,
        spinNearest: nearby.spin[0]?.distanceMiles ?? null,
        veoNearest: nearby.veo[0]?.distanceMiles ?? null,
        scooterCount: combined.filter((v) => v.type === 'scooter').length,
        bikeCount: combined.filter((v) => v.type === 'bike').length,
      };
    },
    [data]
  );

  return { data, fetchVehicles, getNearbyCount };
}
