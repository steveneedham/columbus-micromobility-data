import L from 'leaflet';

// Adapted from ../../../assets/columbus-ride-hub-marker.svg and the main
// dashboard's .ride-hub-marker-wrap/.ride-hub-count pattern (index.html) —
// same pin + bike-medallion shape and count-badge treatment, recolored per
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

export function createLocationIcon(colorKey = 'teal', count = 0) {
  const hex = PIN_COLORS[colorKey] ?? PIN_COLORS.teal;
  const badge =
    count > 0
      ? `<span style="position:absolute;top:0;right:-2px;display:grid;place-items:center;min-width:19px;height:19px;padding:0 4px;border:2px solid #FBFAF6;border-radius:10px;background:#A94728;color:#FBFAF6;font:700 9px 'IBM Plex Mono',monospace;line-height:1;box-shadow:0 1px 2px rgba(32,42,47,.35);">${count}</span>`
      : '';

  const html = `<span style="position:relative;display:block;width:30px;height:45px;filter:drop-shadow(0 1px 2px rgba(32,42,47,.45));">${pinSvg(
    hex
  )}${badge}</span>`;

  return L.divIcon({
    className: 'location-pin-icon',
    html,
    iconSize: [30, 45],
    iconAnchor: [15, 45],
    popupAnchor: [0, -40],
  });
}
