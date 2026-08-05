// Both operators' Columbus GBFS feeds use the free_bike_status shape:
// { data: { bikes: [...] } }. Neither feed's vehicle_type_id string
// reliably says "bike" or "scooter" on its own (that needs a separate
// vehicle_types.json lookup, like scripts/export_fleet.py does
// server-side) -- this app doesn't use vehicle type for anything but a
// display count, so it's a best-effort guess here, not authoritative.
function parseBikes(json, operator) {
  const bikes = json?.data?.bikes ?? [];
  return bikes
    .filter((v) => typeof v.lat === 'number' && typeof v.lon === 'number')
    .map((v) => ({
      id: v.bike_id ?? v.vehicle_id ?? v.id,
      operator,
      lat: v.lat,
      lon: v.lon,
      available: v.is_disabled === false && v.is_reserved === false,
      battery: typeof v.battery_pct === 'number'
        ? v.battery_pct
        : typeof v.battery_level === 'number'
          ? Math.round(v.battery_level * 100)
          : typeof v.current_fuel_percent === 'number'
            ? Math.round(v.current_fuel_percent * 100)
            : null,
      type: /bike/i.test(v.vehicle_type_id || '') ? 'bike' : 'scooter',
    }));
}

export function parseSpinVehicles(json) {
  return parseBikes(json, 'spin');
}

export function parseVeoVehicles(json) {
  return parseBikes(json, 'veo');
}

export function isDataFresh(timestamp, maxAgeMinutes = 60) {
  if (!timestamp) return false;
  return (Date.now() - timestamp) / 60000 < maxAgeMinutes;
}
