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

export const GBFS_ENDPOINTS = {
  spin: {
    url: 'https://feeds.spin.app/gbfs/v3/systems/columbus_us/vehicles',
    format: 'json',
  },
  veo: {
    url: 'https://gbfs.veo.dev/columbus/station_information.json',
    format: 'json',
  },
};

export const DEFAULT_RADIUS = 0.25; // miles
export const HUNT_SPEED_MPH = 3;
export const UNLOCK_TIME_MIN = 1;
