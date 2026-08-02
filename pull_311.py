#!/usr/bin/env python3
"""
Fetch Columbus 311 service requests for shared scooters/bikes.
Outputs timestamped JSON snapshot to snapshots/ directory.
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import sys

# Columbus GIS REST API endpoint
API_URL = "https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query"

# Filter for shared electric bikes & scooters only
PARAMS = {
    "where": "REQUEST_TYPE = 'Shared Electric Bike & Scooters'",
    "outFields": (
        "CASE_ID,STATUS,REPORTED_DATE,STATUS_DATE,REQUEST_TYPE,"
        "STREET,CITY,ZIP,COLUMBUSCOMMUNITY,AREACOMMISSION,COUNCILDISTRICT,"
        "LATITUDE,LONGITUDE,REQUEST_MODIFIED"
    ),
    "returnGeometry": True,
    "outSR": 4326,  # WGS84
    "orderByFields": "REPORTED_DATE DESC",
    "resultRecordCount": 2000,  # Max results to fetch
    "f": "json",
}

HEADERS = {
    "User-Agent": "columbus-micromobility-data/1.0 (+https://github.com/steveneedham/columbus-micromobility-data)"
}

def fetch_311_data():
    """Fetch latest 311 requests from Columbus GIS API."""
    print("Fetching 311 data from Columbus GIS API...", file=sys.stderr)
    
    try:
        response = requests.get(API_URL, params=PARAMS, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            print(f"API error: {data['error']}", file=sys.stderr)
            return None
        
        features = data.get("features", [])
        print(f"Retrieved {len(features)} records", file=sys.stderr)
        
        # Extract attributes from features
        records = []
        for feature in features:
            attr = feature.get("attributes", {})
            records.append(attr)
        
        return {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "source": {
                "name": "City of Columbus 311 Service Requests",
                "map_url": "https://gis.columbus.gov/coc311map/",
                "query_url": API_URL,
                "request_type": "Shared Electric Bike & Scooters",
                "mode": "read-only"
            },
            "record_count": len(records),
            "records": records
        }
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return None

def save_snapshot(data):
    """Save data to timestamped JSON file."""
    snapshots_dir = Path("snapshots")
    snapshots_dir.mkdir(exist_ok=True)
    
    # ISO 8601 timestamp in UTC
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = f"311_requests_{timestamp}.json"
    filepath = snapshots_dir / filename
    
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    # Also update latest.json symlink (for easy dashboard consumption)
    latest_path = snapshots_dir / "311_requests_latest.json"
    try:
        latest_path.unlink()  # Remove old symlink/file
    except FileNotFoundError:
        pass
    latest_path.write_text(json.dumps(data, indent=2))
    
    print(f"Saved: {filepath}", file=sys.stderr)
    print(f"Updated: {latest_path}", file=sys.stderr)
    return filepath

def main():
    data = fetch_311_data()
    
    if data is None:
        print("Failed to fetch 311 data", file=sys.stderr)
        sys.exit(1)
    
    save_snapshot(data)
    print(f"✓ 311 data pull complete ({data['record_count']} records)", file=sys.stderr)

if __name__ == "__main__":
    main()
