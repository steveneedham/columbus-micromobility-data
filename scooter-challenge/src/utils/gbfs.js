export function parseSpinVehicles(json) {
  const vehicles = json?.data?.vehicles ?? [];
  return vehicles
    .filter((v) => typeof v.lat === 'number' && typeof v.lon === 'number')
    .map((v) => ({
      id: v.vehicle_id ?? v.id,
      operator: 'spin',
      lat: v.lat,
      lon: v.lon,
      available: v.is_disabled === false && v.is_reserved === false,
      battery: typeof v.current_fuel_percent === 'number' ? Math.round(v.current_fuel_percent * 100) : null,
      type: v.vehicle_type_id?.includes('bike') ? 'bike' : 'scooter',
    }));
}

export function parseVeoVehicles(json) {
  const vehicles = json?.data?.vehicles ?? json?.data?.stations ?? [];
  return vehicles
    .filter((v) => typeof v.lat === 'number' && typeof v.lon === 'number')
    .map((v) => ({
      id: v.vehicle_id ?? v.station_id ?? v.id,
      operator: 'veo',
      lat: v.lat,
      lon: v.lon,
      available: v.is_disabled === false && v.is_reserved === false,
      battery: typeof v.current_fuel_percent === 'number' ? Math.round(v.current_fuel_percent * 100) : null,
      type: v.vehicle_type_id?.includes('bike') ? 'bike' : 'scooter',
    }));
}

export function isDataFresh(timestamp, maxAgeMinutes = 60) {
  if (!timestamp) return false;
  return (Date.now() - timestamp) / 60000 < maxAgeMinutes;
}
