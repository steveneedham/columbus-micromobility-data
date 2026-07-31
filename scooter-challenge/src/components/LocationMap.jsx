import { Fragment, useEffect } from 'react';
import { MapContainer, TileLayer, Circle, Marker, Tooltip, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { DEFAULT_RADIUS } from '../constants/operators.js';
import { createLocationIcon } from '../utils/locationIcon.js';

const RADIUS_METERS = DEFAULT_RADIUS * 1609.34;

function densityColor(total) {
  if (total === 0) return '#C8C2B5'; // rule — no data yet
  if (total <= 2) return '#9CC6C9'; // river-wash — light
  if (total <= 5) return '#236A73'; // river — moderate
  return '#A94728'; // brick — dense
}

function FitToLocations({ points }) {
  const map = useMap();
  useEffect(() => {
    if (points.length === 1) {
      map.setView(points[0], 14);
    } else if (points.length > 1) {
      map.fitBounds(L.latLngBounds(points), { padding: [24, 24] });
    }
  }, [map, points]);
  return null;
}

export function LocationMap({ locations }) {
  const withCoords = locations.filter((loc) => loc.lat != null && loc.lon != null);
  const points = withCoords.map((loc) => [loc.lat, loc.lon]);

  if (points.length === 0) return null;

  return (
    <div className="h-64 overflow-hidden rounded-sheet border border-rule">
      <MapContainer center={points[0]} zoom={14} scrollWheelZoom={false} className="h-full w-full">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitToLocations points={points} />
        {withCoords.map((loc, i) => {
          const total = loc.spinCount + loc.veoCount;
          const color = densityColor(total);
          const pinColor = i % 2 === 0 ? 'teal' : 'orange';
          return (
            <Fragment key={loc.name}>
              <Circle
                center={[loc.lat, loc.lon]}
                radius={RADIUS_METERS}
                pathOptions={{ color, fillColor: color, fillOpacity: 0.2, weight: 2 }}
              />
              <Marker position={[loc.lat, loc.lon]} icon={createLocationIcon(pinColor, total)}>
                <Tooltip direction="top" offset={[0, -40]}>
                  {loc.name}: Spin {loc.spinCount} · Veo {loc.veoCount}
                </Tooltip>
              </Marker>
            </Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}
