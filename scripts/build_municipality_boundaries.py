#!/usr/bin/env python3
"""
Build data-municipality-boundaries.json: the Ohio State University boundary
(already in data-osu-boundary.json) plus administrative boundaries for
Marble Cliff, Grandview Heights, Upper Arlington, Bexley, and Dublin,
sourced from OpenStreetMap.

The OSM boundaries are not fetched live -- this repo has no automated
pipeline for them (they change rarely, unlike GBFS/311). Re-run this
script by hand against a fresh Overpass export when a boundary needs
updating:

  1. Run OVERPASS_QUERY (printed by --print-query) at https://overpass-turbo.eu/
  2. Export > GeoJSON, save the file somewhere
  3. python3 scripts/build_municipality_boundaries.py path/to/export.geojson
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OSU_BOUNDARY_PATH = ROOT / "data-osu-boundary.json"
OUTPUT_PATH = ROOT / "data-municipality-boundaries.json"

# admin_level=8 is the Ohio Census TIGER "place" level (city/village), which
# is what distinguishes these from Columbus itself or Franklin County.
OVERPASS_QUERY = """[out:json][timeout:25];
area["name"="Ohio"]["admin_level"="4"]->.searchArea;
(
  relation["admin_level"="8"]["name"="Grandview Heights"](area.searchArea);
  relation["admin_level"="8"]["name"="Marble Cliff"](area.searchArea);
  relation["admin_level"="8"]["name"="Upper Arlington"](area.searchArea);
  relation["admin_level"="8"]["name"="Bexley"](area.searchArea);
  relation["admin_level"="8"]["name"="Dublin"](area.searchArea);
);
out geom;"""

NAME_TO_ID = {
    "Marble Cliff": "marble-cliff",
    "Grandview Heights": "grandview-heights",
    "Upper Arlington": "upper-arlington",
    "Bexley": "bexley",
    "Dublin": "dublin",
}


def build(osm_export_path):
    osu = json.loads(OSU_BOUNDARY_PATH.read_text())
    osm = json.loads(Path(osm_export_path).read_text())

    municipalities = [{
        "id": "osu",
        "name": "The Ohio State University",
        "type": "university",
        "feature_collection": osu["feature_collection"],
        "source": "Supplied GeoJSON policy geography export "
                   "(osu-spin-osu_expanded_campus_boundary_export.geojson) -- "
                   "the same boundary used by the Ohio State compliance insight tab.",
    }]

    found = set()
    for feature in osm.get("features", []):
        name = feature.get("properties", {}).get("name")
        municipality_id = NAME_TO_ID.get(name)
        if not municipality_id:
            continue
        found.add(name)
        municipalities.append({
            "id": municipality_id,
            "name": name,
            "type": feature["properties"].get("place", "municipality"),
            "feature_collection": {"type": "FeatureCollection", "features": [feature]},
            "source": "OpenStreetMap administrative boundary (admin_level=8), via Overpass API.",
        })

    missing = set(NAME_TO_ID) - found
    if missing:
        print(f"Warning: export did not include {sorted(missing)}", file=sys.stderr)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "osm_attribution": "Boundary data for Grandview Heights, Marble Cliff, Upper Arlington, "
                                "Bexley, and Dublin is from OpenStreetMap, made available under the "
                                "Open Database License (ODbL): https://www.openstreetmap.org/copyright",
            "osm_query": OVERPASS_QUERY,
            "how_to_refresh": "Run the query above at https://overpass-turbo.eu/ (Export > GeoJSON), "
                               "then re-run this script against the downloaded file. The Ohio State "
                               "University boundary is sourced separately (see data-osu-boundary.json) "
                               "and is not part of this query.",
        },
        "municipalities": municipalities,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {len(municipalities)} municipalities to {OUTPUT_PATH}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("osm_export", nargs="?", help="Path to an Overpass GeoJSON export")
    parser.add_argument("--print-query", action="store_true", help="Print the Overpass query and exit")
    args = parser.parse_args()

    if args.print_query:
        print(OVERPASS_QUERY)
        return

    if not args.osm_export:
        parser.error("osm_export is required unless --print-query is passed")

    build(args.osm_export)


if __name__ == "__main__":
    main()
