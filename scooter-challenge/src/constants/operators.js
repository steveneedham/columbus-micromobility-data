// Rate figures (monthlyFee/perRideFlat/perMinRate) live in rates.json, the
// single source of truth for every visitor -- there is no per-user or
// per-session override anywhere in this app, so everyone always sees the
// same published numbers. Update rates by editing that file (see
// scooter-challenge/admin/index.html for a form that generates its
// content), not by changing anything here.
import RATES from './rates.json';

export const RATES_UPDATED_AT = RATES.updated_at;

export const OPERATORS = {
  spin: {
    name: 'Spin',
    ...RATES.spin,
    speedMph: { min: 18, max: 22 },
    accent: '#A94728',
  },
  veo: {
    name: 'Veo',
    ...RATES.veo,
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
