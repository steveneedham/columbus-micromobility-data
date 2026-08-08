const EARTH_RADIUS_MI = 3958.8;

export function haversineDistance(lat1, lon1, lat2, lon2) {
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return EARTH_RADIUS_MI * c;
}

export function nearbyVehicles(userLat, userLon, vehicles, radiusMiles = 0.25) {
  const result = { spin: [], veo: [] };
  for (const vehicle of vehicles) {
    const distance = haversineDistance(userLat, userLon, vehicle.lat, vehicle.lon);
    if (distance <= radiusMiles) {
      const withDistance = { ...vehicle, distanceMiles: distance };
      if (vehicle.operator === 'spin') result.spin.push(withDistance);
      else if (vehicle.operator === 'veo') result.veo.push(withDistance);
    }
  }
  result.spin.sort((a, b) => a.distanceMiles - b.distanceMiles);
  result.veo.sort((a, b) => a.distanceMiles - b.distanceMiles);
  return result;
}

export function huntTimeEstimate(distanceMiles, huntSpeedMph = 3, unlockTimeMin = 1) {
  const walkMinutes = distanceMiles * (60 / huntSpeedMph);
  return Math.round(walkMinutes + unlockTimeMin);
}

export function validateCoordinates(lat, lon) {
  if (typeof lat !== 'number' || typeof lon !== 'number' || Number.isNaN(lat) || Number.isNaN(lon)) {
    return { valid: false, message: 'Latitude and longitude must be numbers.' };
  }
  if (lat < -90 || lat > 90) return { valid: false, message: 'Latitude must be between -90 and 90.' };
  if (lon < -180 || lon > 180) return { valid: false, message: 'Longitude must be between -180 and 180.' };
  return { valid: true, message: '' };
}
