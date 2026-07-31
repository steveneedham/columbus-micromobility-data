import L from 'leaflet';

// Adapted from ../../../assets/columbus-ride-hub-marker.svg (the main
// dashboard's Ride Hub pin) — same pin + bike-medallion shape, recolored per
// location and with the "RIDE HUB" lettering dropped since these mark a
// rider's own stops, not a CoGo dock.
const PIN_COLORS = {
  teal: '#236A73', // river
  orange: '#A94728', // brick
};

function pinSvg(hex) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 96" width="30" height="45">
    <path d="M32 2C15.4 2 4 14.2 4 31v44c0 11.7 9.5 19 21.2 19h13.6C50.5 94 60 86.7 60 75V31C60 14.2 48.6 2 32 2Z" fill="${hex}"/>
    <path d="M32 5.5C17.8 5.5 7.5 16.1 7.5 31v43.5c0 9.7 7.8 16 17.7 16h13.6c9.9 0 17.7-6.3 17.7-16V31C56.5 16.1 46.2 5.5 32 5.5Z" fill="#FBFAF6"/>
    <circle cx="32" cy="45" r="16" fill="#FBFAF6" stroke="${hex}" stroke-width="2.5"/>
    <g fill="none" stroke="${hex}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="23" cy="50" r="5.5"/>
      <circle cx="42" cy="50" r="5.5"/>
      <path d="m23 50 7-13 5 13H23Zm7-13h7m-4-5h5m-3 18 5-13h-4"/>
    </g>
  </svg>`;
}

export function createLocationIcon(colorKey = 'teal') {
  const hex = PIN_COLORS[colorKey] ?? PIN_COLORS.teal;
  return L.divIcon({
    className: 'location-pin-icon',
    html: pinSvg(hex),
    iconSize: [30, 45],
    iconAnchor: [15, 45],
    popupAnchor: [0, -40],
  });
}
