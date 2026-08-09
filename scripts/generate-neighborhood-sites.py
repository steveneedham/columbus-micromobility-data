#!/usr/bin/env python3
"""
Generate neighborhood-specific micro-sites from 311 and GBFS data.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import math

def load_json_file(filepath: str) -> Dict:
    """Load JSON data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def point_in_bbox(point: Tuple[float, float], bbox: List[List[float]]) -> bool:
    """Check if a point is within a bounding box.

    Args:
        point: (lon, lat) tuple
        bbox: [[min_lat, min_lon], [max_lat, max_lon]]

    Returns:
        True if point is within bbox
    """
    lat, lon = point[1], point[0]
    min_lat, min_lon = bbox[0][1], bbox[0][0]
    max_lat, max_lon = bbox[1][1], bbox[1][0]

    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

def point_in_polygon(point: Tuple[float, float], polygon: List[List[Tuple[float, float]]]) -> bool:
    """Check if point is inside polygon using ray casting algorithm."""
    x, y = point[0], point[1]
    inside = False

    p1x, p1y = polygon[0][0], polygon[0][1]
    for i in range(1, len(polygon)):
        p2x, p2y = polygon[i][0], polygon[i][1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

def filter_311_data_for_neighborhood(records: List[Dict], neighborhood: Dict,
                                     municipality_boundaries: Dict) -> List[Dict]:
    """Filter 311 records that fall within a neighborhood."""
    filtered = []

    # First, try matching by zone_id if available
    zone_ids = neighborhood.get('zone_ids', [])
    if zone_ids:
        for record in records:
            if record.get('zone_id') in zone_ids:
                filtered.append(record)
        # If we found records by zone, return early
        if filtered:
            return filtered

    # Fall back to polygon boundary (for municipalities)
    boundary_geojson = None
    if neighborhood.get('boundary_source') == 'municipality-boundaries':
        for municipality in municipality_boundaries.get('municipalities', []):
            if municipality.get('id') == neighborhood.get('id'):
                features = municipality.get('feature_collection', {}).get('features', [])
                if features:
                    boundary_geojson = features[0].get('geometry')
                break

    if boundary_geojson:
        for record in records:
            point = (record.get('longitude'), record.get('latitude'))
            if boundary_geojson.get('type') == 'MultiPolygon':
                for polygon in boundary_geojson.get('coordinates', []):
                    if point_in_polygon(point, polygon[0]):
                        filtered.append(record)
                        break
            elif boundary_geojson.get('type') == 'Polygon':
                if point_in_polygon(point, boundary_geojson.get('coordinates', [[]])[0]):
                    filtered.append(record)
        return filtered

    # Fall back to bbox for neighborhood zones
    if neighborhood.get('bounds'):
        for record in records:
            point = (record.get('longitude'), record.get('latitude'))
            if point_in_bbox(point, neighborhood['bounds']):
                filtered.append(record)

    return filtered

def filter_gbfs_data_for_neighborhood(records: List[Dict], neighborhood: Dict) -> List[Dict]:
    """Filter GBFS records that fall within a neighborhood."""
    filtered = []

    if not neighborhood.get('bounds'):
        return filtered

    for record in records:
        # GBFS uses 'lat'/'lng' instead of 'latitude'/'longitude'
        point = (record.get('lng'), record.get('lat'))
        if point_in_bbox(point, neighborhood['bounds']):
            filtered.append(record)

    return filtered

def generate_neighborhood_html(neighborhood: Dict, c311_data: List[Dict],
                              gbfs_data: List[Dict]) -> str:
    """Generate HTML for a neighborhood micro-site."""

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{neighborhood['name']} — Columbus Micromobility Data</title>
    <meta name="description" content="Neighborhood data view: {neighborhood['description']}">
    <link rel="canonical" href="https://steveneedham.github.io/columbus-micromobility-data/{neighborhood['slug']}/">
    <meta property="og:title" content="{neighborhood['name']} — Columbus Micromobility">
    <meta property="og:description" content="{neighborhood['description']}">
    <meta property="og:url" content="https://steveneedham.github.io/columbus-micromobility-data/{neighborhood['slug']}/">
    <link rel="icon" type="image/svg+xml" href="../assets/field-ledger-mark.svg">
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
            --color-status-success: #4caf50;
            --color-status-warning: #ff9800;
            --color-status-error: #f44336;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --color-surface: #1a1714;
                --color-text: #f3f0e8;
                --color-text-secondary: #a89f95;
                --color-border: #3a3530;
                --color-accent-amber: #faa71a;
                --color-accent-teal: #00bfa5;
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
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .metric-card {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: 8px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .metric-label {{
            font-size: 0.875rem;
            color: var(--color-text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .metric-value {{
            font-size: 2rem;
            font-weight: 600;
            color: var(--color-accent-amber);
        }}

        #map {{
            height: 400px;
            border-radius: 8px;
            border: 1px solid var(--color-border);
            margin: 2rem 0;
        }}

        .data-section {{
            margin: 3rem 0;
        }}

        .data-section h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            font-family: 'Newsreader', serif;
        }}

        .no-data {{
            color: var(--color-text-secondary);
            padding: 2rem;
            background: var(--color-surface);
            border: 1px dashed var(--color-border);
            border-radius: 8px;
            text-align: center;
        }}

        footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--color-border);
            font-size: 0.875rem;
            color: var(--color-text-secondary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="../">← Back to all neighborhoods</a>
            <h1>{neighborhood['name']}</h1>
            <p class="description">{neighborhood['description']}</p>
        </header>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">311 Requests</div>
                <div class="metric-value">{len(c311_data)}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">GBFS Records</div>
                <div class="metric-value">{len(gbfs_data)}</div>
            </div>
        </div>

        <div id="map"></div>

        <div class="data-section">
            <h2>311 Service Requests</h2>
            {generate_311_section(c311_data)}
        </div>

        <div class="data-section">
            <h2>Micromobility Data</h2>
            {generate_gbfs_section(gbfs_data)}
        </div>

        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
            <p>Data sources: Columbus 311, GBFS operators, OpenStreetMap</p>
        </footer>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        const neighborhood = {json.dumps(neighborhood)};
        const c311Data = {json.dumps(c311_data[:10])};
        const gbfsData = {json.dumps(gbfs_data[:10])};

        // Initialize map
        const map = L.map('map').setView(neighborhood.center, neighborhood.zoom);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }}).addTo(map);

        // Add neighborhood bounds rectangle if available
        if (neighborhood.bounds) {{
            const bounds = L.latLngBounds(
                [neighborhood.bounds[0][1], neighborhood.bounds[0][0]],
                [neighborhood.bounds[1][1], neighborhood.bounds[1][0]]
            );
            L.rectangle(bounds, {{
                color: '#faa71a',
                weight: 2,
                fill: false,
                opacity: 0.7
            }}).addTo(map);
        }}

        // Add 311 markers
        c311Data.forEach(record => {{
            const color = record.status === 'received' ? '#ff9800' : '#4caf50';
            L.circleMarker([record.latitude, record.longitude], {{
                radius: 5,
                fillColor: color,
                color: color,
                weight: 1,
                opacity: 0.7,
                fillOpacity: 0.6
            }}).addTo(map).bindPopup(
                '<strong>' + record.descriptor + '</strong><br/>' +
                record.address + '<br/>' +
                'Status: ' + record.status
            );
        }});

        // Add GBFS markers
        gbfsData.forEach(record => {{
            L.circleMarker([record.lat, record.lng], {{
                radius: 4,
                fillColor: '#00bfa5',
                color: '#00bfa5',
                weight: 1,
                opacity: 0.7,
                fillOpacity: 0.5
            }}).addTo(map).bindPopup(
                '<strong>' + (record.company || 'Unknown') + ' ' + (record.type || 'vehicle') + '</strong><br/>' +
                'Battery: ' + (record.battery || 'N/A') + '%<br/>' +
                'Range: ' + (record.range ? record.range.toFixed(1) : 'N/A') + ' km'
            );
        }});
    </script>
</body>
</html>'''

    return html

def generate_311_section(data: List[Dict]) -> str:
    """Generate 311 data section HTML."""
    if not data:
        return '<div class="no-data">No 311 requests found in this neighborhood.</div>'

    # Count by status
    by_status = {}
    for record in data:
        status = record.get('status', 'unknown')
        by_status[status] = by_status.get(status, 0) + 1

    status_html = ''.join([
        f'<div style="margin-bottom: 0.5rem;"><strong>{status}:</strong> {count}</div>'
        for status, count in sorted(by_status.items())
    ])

    return f'''
    <div style="margin-bottom: 2rem;">
        <h3 style="font-size: 1rem; margin-bottom: 1rem;">Summary</h3>
        {status_html}
    </div>
    <p style="color: var(--color-text-secondary); font-size: 0.875rem;">
        Total: {len(data)} requests
    </p>
    '''

def generate_gbfs_section(data: List[Dict]) -> str:
    """Generate GBFS data section HTML."""
    if not data:
        return '<div class="no-data">No micromobility data available for this neighborhood.</div>'

    by_company = {}
    by_type = {}
    for record in data:
        company = record.get('company', 'unknown')
        vtype = record.get('type', 'unknown')
        by_company[company] = by_company.get(company, 0) + 1
        by_type[vtype] = by_type.get(vtype, 0) + 1

    company_html = ''.join([
        f'<div style="margin-bottom: 0.5rem;"><strong>{company}:</strong> {count}</div>'
        for company, count in sorted(by_company.items())
    ])

    type_html = ''.join([
        f'<div style="margin-bottom: 0.5rem;"><strong>{vtype}:</strong> {count}</div>'
        for vtype, count in sorted(by_type.items())
    ])

    return f'''
    <div style="margin-bottom: 2rem;">
        <h3 style="font-size: 1rem; margin-bottom: 1rem;">By Operator</h3>
        {company_html}
    </div>
    <div style="margin-bottom: 2rem;">
        <h3 style="font-size: 1rem; margin-bottom: 1rem;">By Type</h3>
        {type_html}
    </div>
    <p style="color: var(--color-text-secondary); font-size: 0.875rem;">
        Total: {len(data)} vehicles
    </p>
    '''

def main():
    """Main build process."""
    # Load all data
    neighborhoods = load_json_file('neighborhoods-data.json')['neighborhoods']
    c311_data = load_json_file('data-311.json')['records']
    gbfs_json = load_json_file('data-gbfs.json')
    gbfs_data = gbfs_json.get('vehicles', [])
    municipality_boundaries = load_json_file('data-municipality-boundaries.json')

    # Create output directories
    base_dir = Path('.')
    micro_sites_dir = base_dir / 'micro-sites'
    micro_sites_dir.mkdir(exist_ok=True)

    # Generate HTML for each neighborhood
    for neighborhood in neighborhoods:
        print(f"Generating site for {neighborhood['name']}...")

        # Filter data for this neighborhood
        filtered_311 = filter_311_data_for_neighborhood(c311_data, neighborhood, municipality_boundaries)
        filtered_gbfs = filter_gbfs_data_for_neighborhood(gbfs_data, neighborhood)

        # Generate HTML
        html = generate_neighborhood_html(neighborhood, filtered_311, filtered_gbfs)

        # Create neighborhood directory
        neighborhood_dir = micro_sites_dir / neighborhood['slug']
        neighborhood_dir.mkdir(exist_ok=True)

        # Write index.html
        output_file = neighborhood_dir / 'index.html'
        with open(output_file, 'w') as f:
            f.write(html)

        print(f"  ✓ Created {output_file}")
        print(f"    - 311 records: {len(filtered_311)}")
        print(f"    - GBFS records: {len(filtered_gbfs)}")

    print("\nDone! Generated micro-sites for all neighborhoods.")

if __name__ == '__main__':
    main()
