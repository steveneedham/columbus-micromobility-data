export const OPERATORS = {
  spin: {
    name: 'Spin',
    monthlyFee: 0.99,
    perRideFlat: 2.39,
    perMinRate: null,
    speedMph: { min: 18, max: 22 },
    accent: '#A94728',
  },
  veo: {
    name: 'Veo',
    monthlyFee: 5.99,
    perRideFlat: null,
    perMinRate: 0.475,
    speedMph: { min: 17, max: 17 },
    accent: '#236A73',
  },
};

// Same endpoints scripts/export_fleet.py fetches server-side for the main
// dashboard (confirmed working there). Both are free_bike_status feeds --
// Columbus is a free-floating deployment for both operators, not
// station-based, so a station_information.json endpoint (what this used to
// point Veo at) would never return anything here.
export const GBFS_ENDPOINTS = {
  spin: {
    url: 'https://mds.bird.co/gbfs/v2/public/provider/spin/columbus/free_bike_status.json',
    format: 'json',
  },
  veo: {
    url: 'https://cluster-prod.veoride.com/api/shares/name/cbs/gbfs/free_bike_status',
    format: 'json',
  },
};

export const DEFAULT_RADIUS = 0.25; // miles
export const HUNT_SPEED_MPH = 3;
export const UNLOCK_TIME_MIN = 1;
