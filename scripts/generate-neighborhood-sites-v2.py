#!/usr/bin/env python3
"""
Generate neighborhood-specific micro-sites - simplified version.
"""

import json
from pathlib import Path
from datetime import datetime

def load_json_file(filepath: str) -> dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_neighborhood_html(neighborhood: dict, c311_count: int, gbfs_count: int) -> str:
    """Generate simplified HTML for a neighborhood micro-site."""

    slug = neighborhood['slug']
    name = neighborhood['name']
    description = neighborhood['description']

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} — Columbus Micromobility Data</title>
    <meta name="description" content="Neighborhood data: {description}">
    <link rel="canonical" href="https://steveneedham.github.io/columbus-micromobility-data/micro-sites/{slug}/">
    <link rel="icon" type="image/svg+xml" href="../../assets/field-ledger-mark.svg">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,500&display=swap');

        :root {{
            --color-surface: #f3f0e8;
            --color-text: #1a1714;
            --color-text-secondary: #5a5550;
            --color-border: #ccc8bf;
            --color-accent-amber: #faa71a;
            --color-accent-teal: #00bfa5;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --color-surface: #1a1714;
                --color-text: #f3f0e8;
                --color-text-secondary: #a89f95;
                --color-border: #3a3530;
            }}
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: var(--color-surface);
            color: var(--color-text);
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            margin-bottom: 2rem;
            border-bottom: 1px solid var(--color-border);
            padding-bottom: 2rem;
        }}

        header a {{
            color: var(--color-accent-amber);
            text-decoration: none;
            font-size: 0.875rem;
            display: inline-block;
            margin-bottom: 1rem;
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 600;
            margin: 1rem 0;
            font-family: 'Newsreader', serif;
        }}

        .description {{
            color: var(--color-text-secondary);
            font-size: 1.125rem;
        }}

        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .metric-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1.5rem;
        }}

        .metric-label {{
            font-size: 0.875rem;
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: 600;
            color: var(--color-accent-amber);
            font-family: 'IBM Plex Mono', monospace;
        }}

        #map {{
            height: 500px;
            border-radius: 8px;
            border: 1px solid var(--color-border);
            margin: 2rem 0;
        }}

        .info-section {{
            margin: 2rem 0;
            padding: 1.5rem;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
        }}

        .info-section h2 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            font-family: 'Newsreader', serif;
        }}

        .info-section p {{
            color: var(--color-text-secondary);
            margin-bottom: 0.5rem;
        }}

        footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--color-border);
            font-size: 0.875rem;
            color: var(--color-text-secondary);
        }}

        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            h1 {{ font-size: 1.75rem; }}
            #map {{ height: 300px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="../">← All neighborhoods</a>
            <h1>{name}</h1>
            <p class="description">{description}</p>
        </header>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">311 Requests</div>
                <div class="metric-value">{c311_count}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Vehicles</div>
                <div class="metric-value">{gbfs_count}</div>
            </div>
        </div>

        <div id="map"></div>

        <div class="info-section">
            <h2>About This Data</h2>
            <p><strong>311 Service Requests:</strong> City service requests related to shared electric bikes and scooters, including parking violations, safety concerns, and accessibility issues.</p>
            <p><strong>Vehicle Data:</strong> Real-time or recent snapshots of available scooters and bikes from operators like Veo and Spin, showing location, battery status, and availability.</p>
        </div>

        <footer>
            <p>Data sources: Columbus 311 Service Requests, GBFS operators (Veo, Spin), OpenStreetMap</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
        </footer>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Neighborhood configuration
        const neighborhood = {json.dumps(neighborhood)};

        // Initialize map
        const map = L.map('map').setView(neighborhood.center, neighborhood.zoom);

        // Add tile layer
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }}).addTo(map);

        // Add neighborhood bounds if available
        if (neighborhood.bounds) {{
            const bounds = L.latLngBounds(
                [neighborhood.bounds[0][1], neighborhood.bounds[0][0]],
                [neighborhood.bounds[1][1], neighborhood.bounds[1][0]]
            );
            L.rectangle(bounds, {{
                color: '#faa71a',
                weight: 2,
                fill: false,
                opacity: 0.8,
                dashArray: '5, 5'
            }}).addTo(map);
        }}

        // Fallback message if map doesn't load
        if (!window.L) {{
            document.getElementById('map').innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--color-text-secondary);">Map failed to load. <a href="https://www.openstreetmap.org" target="_blank">View on OpenStreetMap</a></div>';
        }}
    </script>
</body>
</html>'''

    return html

def main():
    """Main build process."""
    # Load data
    neighborhoods = load_json_file('neighborhoods-data.json')['neighborhoods']
    c311_data = load_json_file('data-311.json')['records']
    gbfs_data = load_json_file('data-gbfs.json').get('vehicles', [])
    municipality_boundaries = load_json_file('data-municipality-boundaries.json')

    # Create output directory
    micro_sites_dir = Path('micro-sites')
    micro_sites_dir.mkdir(exist_ok=True)

    # Generate sites for each neighborhood
    for neighborhood in neighborhoods:
        print(f"Generating {neighborhood['name']}...")

        # Filter data by zone_id
        zone_ids = neighborhood.get('zone_ids', [])
        c311_filtered = [r for r in c311_data if r.get('zone_id') in zone_ids] if zone_ids else []

        # Filter GBFS by bounds
        gbfs_filtered = []
        if neighborhood.get('bounds'):
            bounds = neighborhood['bounds']
            min_lat, min_lon = bounds[0][1], bounds[0][0]
            max_lat, max_lon = bounds[1][1], bounds[1][0]
            for record in gbfs_data:
                lat, lon = record.get('lat'), record.get('lng')
                if lat and lon and min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    gbfs_filtered.append(record)

        # Generate HTML
        html = generate_neighborhood_html(neighborhood, len(c311_filtered), len(gbfs_filtered))

        # Write to file
        neighborhood_dir = micro_sites_dir / neighborhood['slug']
        neighborhood_dir.mkdir(exist_ok=True)

        output_file = neighborhood_dir / 'index.html'
        with open(output_file, 'w') as f:
            f.write(html)

        print(f"  ✓ {neighborhood['name']}: {len(c311_filtered)} 311 requests, {len(gbfs_filtered)} vehicles")

    print("\nAll neighborhood sites generated!")

if __name__ == '__main__':
    main()
