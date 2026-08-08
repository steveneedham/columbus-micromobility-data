#!/usr/bin/env python3
"""
Track how long each cross-vendor pile-up has persisted across GBFS
snapshots. Pile-ups are recomputed fresh from a single snapshot every time
the site loads (see detectPileups() in index.html) with no memory of prior
snapshots -- this script is that memory, following the same
snapshot-to-snapshot pattern as build_gbfs_observations.py.

Clustering is a faithful port of the client-side algorithm: vehicles
within CLUSTER_RADIUS_M of a neighbor join the same cluster; a cluster
of MIN_CLUSTER_SIZE+ vehicles spanning more than one company is a
pile-up. A pile-up is considered "the same" one across snapshots if its
centroid is within MATCH_RADIUS_M of a previously tracked pile-up --
looser than CLUSTER_RADIUS_M since the exact vehicles making up a
real-world hotspot change between snapshots and can shift the centroid.

On first run (no data-pileup-history.json yet), backfills from every
archived snapshots/columbus_scooters_*.csv in this repo in chronological
order, so "how long has this been here" doesn't start from zero. Every
run after processes only the current snapshot against the existing
tracked state.
"""
import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = ROOT / "snapshots"
CURRENT_GBFS_PATH = ROOT / "data-gbfs.json"
HISTORY_PATH = ROOT / "data-pileup-history.json"

CLUSTER_RADIUS_M = 20
MATCH_RADIUS_M = 60
MIN_CLUSTER_SIZE = 4


def distance_meters(a, b):
    lat_scale = 111320
    lng_scale = 111320 * math.cos(math.radians((a["lat"] + b["lat"]) / 2))
    return math.hypot((a["lat"] - b["lat"]) * lat_scale, (a["lng"] - b["lng"]) * lng_scale)


def detect_pileups(vehicles):
    cell = 0.00018
    buckets = {}
    for index, vehicle in enumerate(vehicles):
        key = (math.floor(vehicle["lat"] / cell), math.floor(vehicle["lng"] / cell))
        buckets.setdefault(key, []).append(index)

    visited = set()
    clusters = []
    for index, vehicle in enumerate(vehicles):
        if index in visited:
            continue
        queue = [index]
        members = []
        visited.add(index)
        while queue:
            current_index = queue.pop()
            current = vehicles[current_index]
            members.append(current)
            cell_lat = math.floor(current["lat"] / cell)
            cell_lng = math.floor(current["lng"] / cell)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    for neighbor_index in buckets.get((cell_lat + dy, cell_lng + dx), []):
                        if neighbor_index not in visited and distance_meters(current, vehicles[neighbor_index]) <= CLUSTER_RADIUS_M:
                            visited.add(neighbor_index)
                            queue.append(neighbor_index)
        companies = sorted({m["company"] for m in members if m.get("company")})
        if len(members) >= MIN_CLUSTER_SIZE and len(companies) > 1:
            clusters.append({
                "lat": sum(m["lat"] for m in members) / len(members),
                "lng": sum(m["lng"] for m in members) / len(members),
                "vehicle_count": len(members),
                "companies": companies,
            })
    return clusters


def load_vehicles_from_csv(path):
    vehicles = []
    with path.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            try:
                vehicles.append({
                    "company": row["Company"],
                    "lat": float(row["Latitude"]),
                    "lng": float(row["Longitude"]),
                })
            except (KeyError, TypeError, ValueError):
                pass
    return vehicles


def snapshot_timestamp_from_filename(path):
    stem = path.stem.replace("columbus_scooters_", "")
    return datetime.strptime(stem, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()


def apply_snapshot(state, clusters, observed_at_iso):
    matched_ids = set()
    for cluster in clusters:
        best_entry = None
        best_distance = None
        for entry in state["pileups"]:
            if entry["id"] in matched_ids:
                continue
            distance = distance_meters(cluster, entry)
            if distance <= MATCH_RADIUS_M and (best_distance is None or distance < best_distance):
                best_entry, best_distance = entry, distance
        if best_entry:
            best_entry["lat"] = cluster["lat"]
            best_entry["lng"] = cluster["lng"]
            best_entry["vehicle_count"] = cluster["vehicle_count"]
            best_entry["companies"] = cluster["companies"]
            best_entry["last_seen_at"] = observed_at_iso
            best_entry["snapshot_count"] = best_entry.get("snapshot_count", 1) + 1
            best_entry["active"] = True
            matched_ids.add(best_entry["id"])
        else:
            new_id = f"PILEUP-{state['next_id']:04d}"
            state["next_id"] += 1
            state["pileups"].append({
                "id": new_id,
                "lat": cluster["lat"],
                "lng": cluster["lng"],
                "vehicle_count": cluster["vehicle_count"],
                "companies": cluster["companies"],
                "first_detected_at": observed_at_iso,
                "last_seen_at": observed_at_iso,
                "snapshot_count": 1,
                "active": True,
            })
            matched_ids.add(new_id)
    for entry in state["pileups"]:
        if entry["id"] not in matched_ids:
            entry["active"] = False


def main():
    if HISTORY_PATH.exists():
        state = json.loads(HISTORY_PATH.read_text())
    else:
        state = {"next_id": 1, "pileups": []}
        archived = sorted(SNAPSHOTS_DIR.glob("columbus_scooters_*.csv"))
        for path in archived:
            vehicles = load_vehicles_from_csv(path)
            if not vehicles:
                continue
            clusters = detect_pileups(vehicles)
            apply_snapshot(state, clusters, snapshot_timestamp_from_filename(path))
        print(f"Backfilled from {len(archived)} archived snapshot(s)", file=sys.stderr)

    if not CURRENT_GBFS_PATH.exists():
        print(f"No current snapshot found at {CURRENT_GBFS_PATH}", file=sys.stderr)
        sys.exit(1)
    current_payload = json.loads(CURRENT_GBFS_PATH.read_text())
    current_vehicles = [
        {"company": v.get("company"), "lat": v.get("lat"), "lng": v.get("lng")}
        for v in current_payload.get("vehicles", [])
        if isinstance(v.get("lat"), (int, float)) and isinstance(v.get("lng"), (int, float))
    ]
    observed_at = current_payload.get("snapshot_id") or current_payload.get("fetched_at")
    try:
        observed_at_iso = snapshot_timestamp_from_filename(Path(f"columbus_scooters_{observed_at}.csv"))
    except ValueError:
        observed_at_iso = datetime.now(timezone.utc).isoformat()
    apply_snapshot(state, detect_pileups(current_vehicles), observed_at_iso)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": {
            "cluster_radius_m": CLUSTER_RADIUS_M,
            "match_radius_m": MATCH_RADIUS_M,
            "min_cluster_size": MIN_CLUSTER_SIZE,
            "note": "A pile-up is matched across snapshots by centroid proximity, not vehicle identity. Gaps between GBFS pulls (currently up to ~12h apart) mean a pile-up could dissolve and reform without being caught as a gap.",
        },
        "next_id": state["next_id"],
        "pileups": state["pileups"],
    }
    HISTORY_PATH.write_text(json.dumps(output, indent=2) + "\n")
    active_count = sum(1 for p in state["pileups"] if p["active"])
    print(
        f"Wrote {HISTORY_PATH.name}: {active_count} active, {len(state['pileups'])} tracked total",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
