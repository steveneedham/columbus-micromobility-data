// Minimal line-art bike/scooter pictograms, styled after the circular
// vehicle-type badges on shared-mobility signage (two wheels + frame for
// bike, deck + stem + wheels for scooter) — flat icons, no photo assets.

export function BikeIcon({ className = '', size = 16 }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none" aria-hidden="true">
      <circle cx="6" cy="17" r="3.2" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="18" cy="17" r="3.2" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M6 17l4.5-9h4M10.5 8l3.5 9M14 8l3.5 4M6 17h8"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="14" cy="6.3" r="1.4" fill="currentColor" />
    </svg>
  );
}

export function ScooterIcon({ className = '', size = 16 }) {
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="none" aria-hidden="true">
      <circle cx="5.5" cy="18.5" r="2.3" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="18" cy="18.5" r="2.3" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M5.5 16.2V13a2 2 0 0 1 2-2h9.2L18 16.2M7.5 13h9M16 4h2.6M17.3 4v6.2"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
