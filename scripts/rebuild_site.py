#!/usr/bin/env python3
"""
Rebuild Columbus micromobility data dashboard.
Loads latest 311 and GBFS snapshots, generates HTML and GeoJSON for GitHub Pages.
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timezone
import sys

def load_latest_311():
    """Load latest 311 JSON snapshot."""
    latest_path = Path("snapshots/311_requests_latest.json")
    
    if not latest_path.exists():
        print("No 311 data found", file=sys.stderr)
        return None
    
    try:
        with open(latest_path) as f:
            data = json.load(f)
        print(f"Loaded 311 data: {data.get('record_count', 0)} records", file=sys.stderr)
        return data
    except Exception as e:
        print(f"Failed to load 311 data: {e}", file=sys.stderr)
        return None

def load_latest_gbfs():
    """Load latest GBFS CSV snapshot."""
    snapshots_dir = Path("snapshots")
    
    # Find most recent CSV file
    csv_files = sorted(snapshots_dir.glob("columbus_scooters_*.csv"), reverse=True)
    
    if not csv_files:
        print("No GBFS data found", file=sys.stderr)
        return None
    
    latest_csv = csv_files[0]
    
    try:
        with open(latest_csv) as f:
            reader = csv.DictReader(f)
            vehicles = list(reader)
        print(f"Loaded GBFS data: {len(vehicles)} vehicles from {latest_csv.name}", file=sys.stderr)
        return vehicles
    except Exception as e:
        print(f"Failed to load GBFS data: {e}", file=sys.stderr)
        return None

def generate_gbfs_geojson(vehicles):
    """Generate GeoJSON FeatureCollection from GBFS vehicles."""
    if not vehicles:
        return None
    
    features = []
    for v in vehicles:
        try:
            lat = float(v.get("Latitude", 0))
            lng = float(v.get("Longitude", 0))
            
            if lat == 0 or lng == 0:
                continue
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": {
                    "vehicle_id": v.get("Vehicle_ID"),
                    "company": v.get("Company"),
                    "type": v.get("Type"),
                    "battery_pct": int(v.get("Battery_Pct", 0)),
                    "range_miles": float(v.get("Range_Miles", 0)),
                    "is_available": v.get("Is_Available") == "True",
                    "is_disabled": v.get("Is_Disabled") == "True",
                    "last_reported": v.get("Last_Reported")
                }
            }
            features.append(feature)
        except (ValueError, TypeError):
            continue
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

def generate_311_geojson(data):
    """Generate GeoJSON FeatureCollection from 311 complaints."""
    if not data or not data.get("records"):
        return None
    
    features = []
    for record in data["records"]:
        try:
            lat = float(record.get("LATITUDE", 0))
            lng = float(record.get("LONGITUDE", 0))
            
            if lat == 0 or lng == 0:
                continue
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng, lat]
                },
                "properties": {
                    "case_id": record.get("CASE_ID"),
                    "status": record.get("STATUS"),
                    "reported_date": record.get("REPORTED_DATE"),
                    "status_date": record.get("STATUS_DATE"),
                    "street": record.get("STREET"),
                    "zip": record.get("ZIP"),
                    "community": record.get("COLUMBUSCOMMUNITY"),
                    "council_district": record.get("COUNCILDISTRICT")
                }
            }
            features.append(feature)
        except (ValueError, TypeError):
            continue
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

def save_geojson(name, geojson):
    """Save GeoJSON file."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    filepath = docs_dir / f"{name}.geojson"
    with open(filepath, "w") as f:
        json.dump(geojson, f)
    
    print(f"Saved: {filepath}", file=sys.stderr)

def generate_dashboard_html(gbfs_data, data_311):
    """Generate basic dashboard HTML (scaffold for expansion)."""
    
    # Count vehicles by company
    spin_count = sum(1 for v in gbfs_data if v.get("Company") == "Spin")
    veo_count = sum(1 for v in gbfs_data if v.get("Company") == "Veo")
    
    # Count 311 records by status
    records_311 = data_311.get("records", []) if data_311 else []
    open_count = sum(1 for r in records_311 if r.get("STATUS") == "Open")
    resolved_count = sum(1 for r in records_311 if r.get("STATUS") == "Resolved")
    
    # Use actual 311 fetch time, not script runtime
    if data_311 and "fetched_at" in data_311:
        fetched_iso = data_311["fetched_at"]
        fetched_dt = datetime.fromisoformat(fetched_iso.replace("+00:00", "+00:00"))
        generated_at = fetched_dt.strftime("%Y-%m-%d %H:%M UTC")
    else:
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Columbus Micromobility Data</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #333; }}
        header {{ background: #1a1a1a; color: white; padding: 24px; }}
        h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .subtitle {{ font-size: 14px; color: #aaa; }}
        .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; padding: 24px; }}
        .card {{ background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; }}
        .card h3 {{ font-size: 12px; text-transform: uppercase; color: #666; margin-bottom: 8px; }}
        .card .value {{ font-size: 32px; font-weight: bold; color: #1a1a1a; }}
        .card .unit {{ font-size: 12px; color: #999; margin-top: 4px; }}
        #map {{ width: 100%; height: 500px; margin: 24px; border-radius: 8px; border: 1px solid #e0e0e0; }}
        footer {{ background: #f5f5f5; padding: 16px 24px; font-size: 12px; color: #666; border-top: 1px solid #e0e0e0; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <header>
        <h1>Columbus Micromobility Data</h1>
        <p class="subtitle">Live tracking of Spin and Veo fleet positions + 311 complaints</p>
    </header>
    
    <div class="dashboard">
        <div class="card">
            <h3>Spin vehicles</h3>
            <div class="value">{spin_count}</div>
        </div>
        <div class="card">
            <h3>Veo vehicles</h3>
            <div class="value">{veo_count}</div>
        </div>
        <div class="card">
            <h3>Total fleet</h3>
            <div class="value">{spin_count + veo_count}</div>
        </div>
        <div class="card">
            <h3>311 open complaints</h3>
            <div class="value">{open_count}</div>
        </div>
        <div class="card">
            <h3>311 resolved</h3>
            <div class="value">{resolved_count}</div>
        </div>
        <div class="card">
            <h3>Total 311 records (30d)</h3>
            <div class="value">{len(records_311)}</div>
        </div>
    </div>
    
    <div id="map"></div>
    
    <footer>
        <p>Updated: {generated_at} | <a href="https://github.com/steveneedham/columbus-micromobility-data">Source</a> | <a href="https://gis.columbus.gov/coc311map/">311 Map</a></p>
    </footer>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Basic map setup (enhance with your own visualization logic)
        const map = L.map('map').setView([39.96, -82.99], 12);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        }}).addTo(map);
        
        // Load vehicle GeoJSON
        fetch('docs/gbfs_vehicles.geojson')
            .then(r => r.json())
            .then(data => {{
                L.geoJSON(data, {{
                    pointToLayer: (feature, latlng) => {{
                        const color = feature.properties.company === 'Spin' ? '#FF6B35' : '#00A86B';
                        return L.circleMarker(latlng, {{
                            radius: 5,
                            fillColor: color,
                            color: '#fff',
                            weight: 1,
                            opacity: 0.8,
                            fillOpacity: 0.7
                        }});
                    }}
                }}).addTo(map);
            }})
            .catch(e => console.log('Vehicle layer failed:', e));
        
        // Load 311 complaints
        fetch('docs/311_complaints.geojson')
            .then(r => r.json())
            .then(data => {{
                L.geoJSON(data, {{
                    pointToLayer: (feature, latlng) => {{
                        const color = feature.properties.status === 'Open' ? '#E74C3C' : '#27AE60';
                        return L.circleMarker(latlng, {{
                            radius: 4,
                            fillColor: color,
                            color: '#fff',
                            weight: 1,
                            opacity: 0.6,
                            fillOpacity: 0.5
                        }});
                    }}
                }}).addTo(map);
            }})
            .catch(e => console.log('311 layer failed:', e));
    </script>
</body>
</html>
"""
    return html

def save_html(html, filename="index.html"):
    """Save HTML to docs directory."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    filepath = docs_dir / filename
    with open(filepath, "w") as f:
        f.write(html)
    
    print(f"Saved: {filepath}", file=sys.stderr)

def main():
    print("Rebuilding Columbus micromobility dashboard...", file=sys.stderr)
    
    # Load latest data
    data_311 = load_latest_311()
    gbfs_data = load_latest_gbfs()
    
    if gbfs_data is None:
        print("No data available to rebuild", file=sys.stderr)
        sys.exit(1)
    
    # Generate GeoJSON layers
    print("Generating GeoJSON layers...", file=sys.stderr)
    gbfs_geojson = generate_gbfs_geojson(gbfs_data)
    if gbfs_geojson:
        save_geojson("gbfs_vehicles", gbfs_geojson)
    
    if data_311:
        complaints_geojson = generate_311_geojson(data_311)
        if complaints_geojson:
            save_geojson("311_complaints", complaints_geojson)
    
    # Generate HTML dashboard
    print("Generating dashboard HTML...", file=sys.stderr)
    html = generate_dashboard_html(gbfs_data, data_311)
    save_html(html)
    
    print("✓ Site rebuild complete", file=sys.stderr)

if __name__ == "__main__":
    main()
