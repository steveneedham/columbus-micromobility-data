#!/usr/bin/env python3
"""
Generate neighborhood-specific micro-sites - minimal version without external dependencies.
"""

import json
from pathlib import Path
from datetime import datetime

def load_json_file(filepath: str) -> dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_neighborhood_html(neighborhood: dict, c311_count: int, gbfs_count: int) -> str:
    """Generate minimal HTML for a neighborhood micro-site."""

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

        .location-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }}

        .location-detail {{
            padding: 1rem;
            background: rgba(250, 167, 26, 0.1);
            border-left: 3px solid var(--color-accent-amber);
            border-radius: 4px;
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
                <div class="metric-label">Active Vehicles</div>
                <div class="metric-value">{gbfs_count}</div>
            </div>
        </div>

        <div class="info-section">
            <h2>Neighborhood Data Summary</h2>
            <p>This neighborhood has <strong>{c311_count} 311 service requests</strong> related to shared electric bikes and scooters, and <strong>{gbfs_count} active vehicles</strong> currently tracked in the system.</p>
            <div class="location-info">
                <div class="location-detail">
                    <strong>311 Service Requests</strong><br>
                    City complaints and service requests related to micromobility (parking, safety, accessibility)
                </div>
                <div class="location-detail">
                    <strong>Active Vehicles</strong><br>
                    Real-time or recent scooters and bikes from operators like Veo and Spin
                </div>
            </div>
        </div>

        <div class="info-section">
            <h2>Data Sources</h2>
            <p><strong>311 Data:</strong> Columbus 311 Service Request public map</p>
            <p><strong>Vehicle Data:</strong> GBFS feeds from Veo and Spin (public bike/scooter sharing feeds)</p>
            <p><strong>Geography:</strong> OpenStreetMap municipality and neighborhood boundaries</p>
        </div>

        <footer>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
            <p><a href="../">Browse all neighborhoods →</a></p>
        </footer>
    </div>
</body>
</html>'''

    return html

def main():
    """Main build process."""
    # Load data
    neighborhoods = load_json_file('neighborhoods-data.json')['neighborhoods']
    c311_data = load_json_file('data-311.json')['records']
    gbfs_data = load_json_file('data-gbfs.json').get('vehicles', [])

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
