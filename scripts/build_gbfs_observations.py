#!/usr/bin/env python3
# Append evidence-bounded vendor observations for the newest GBFS snapshot.
import argparse, csv, json, math, statistics
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path("/Users/sjneedhamicloud.com/Library/CloudStorage/GoogleDrive-sjneedham1974@gmail.com/My Drive/columbus_micromobility_snapshots")
AREAS = {
    "Arena District review area": {"lat": 39.9699, "lng": -83.0065, "radius_m": 800},
    "Short North review area": {"lat": 39.9785, "lng": -83.0033, "radius_m": 900},
    "Downtown review area": {"lat": 39.9612, "lng": -82.9988, "radius_m": 1100},
    "Ohio State review area": {"lat": 40.0067, "lng": -83.0305, "radius_m": 1300},
}

def read_csv(path):
    result = []
    with path.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            try:
                result.append({"company": row["Company"], "lat": float(row["Latitude"]), "lng": float(row["Longitude"]), "range": float(row["Range_Miles"] or 0), "available": row["Is_Available"].lower() == "true"})
            except (KeyError, TypeError, ValueError):
                pass
    return result

def distance(item, area):
    x = (item["lng"] - area["lng"]) * 111320 * math.cos(math.radians((item["lat"] + area["lat"]) / 2))
    y = (item["lat"] - area["lat"]) * 111320
    return math.hypot(x, y)

def metrics(items, company):
    vendor = [item for item in items if item.get("company") == company]
    ranges = [float(item.get("range") or 0) for item in vendor]
    return {
        "vehicle_count": len(vendor),
        "median_range_miles": round(statistics.median(ranges), 1) if ranges else None,
        "available_share_pct": round(100 * sum(bool(item.get("available")) for item in vendor) / len(vendor), 1) if vendor else None,
        "review_area_counts": {name: sum(distance(item, area) <= area["radius_m"] for item in vendor) for name, area in AREAS.items()},
    }

def pct(current, previous):
    return None if not previous else round(100 * (current - previous) / previous, 1)

def observations(company, current, previous):
    output = []
    delta = current["vehicle_count"] - previous["vehicle_count"]
    change_pct = pct(current["vehicle_count"], previous["vehicle_count"])
    movement = "up" if delta > 0 else "down" if delta < 0 else "unchanged"
    suffix = "" if not delta or change_pct is None else " (" + format(abs(change_pct), ".1f") + "%)"
    output.append({"category": "fleet_size", "vendor": company, "text": company + " published " + format(current["vehicle_count"], ",") + " vehicles, " + movement + " " + format(abs(delta), ",") + suffix + " from the prior snapshot.", "current": current["vehicle_count"], "previous": previous["vehicle_count"], "change": delta, "change_pct": change_pct})
    current_range = current["median_range_miles"]
    previous_range = previous["median_range_miles"]
    if current_range is not None and previous_range is not None:
        range_delta = round(current_range - previous_range, 1)
        direction = "essentially unchanged" if abs(range_delta) <= 0.25 else "higher" if range_delta > 0 else "lower"
        output.append({"category": "published_range", "vendor": company, "text": company + "’s median published range was " + direction + " at " + format(current_range, ".1f") + " miles (" + format(range_delta, "+.1f") + " miles versus the prior snapshot).", "current": current_range, "previous": previous_range, "change": range_delta, "unit": "miles"})
    availability_delta = round(current["available_share_pct"] - previous["available_share_pct"], 1)
    if abs(availability_delta) >= 1:
        output.append({"category": "availability", "vendor": company, "text": company + "’s published available share moved " + format(availability_delta, "+.1f") + " percentage points to " + format(current["available_share_pct"], ".1f") + "%.", "change_percentage_points": availability_delta})
    shifts = []
    for name, current_count in current["review_area_counts"].items():
        previous_count = previous["review_area_counts"].get(name, 0)
        area_delta = current_count - previous_count
        area_pct = pct(current_count, previous_count)
        if abs(area_delta) >= 15 and (area_pct is None or abs(area_pct) >= 8):
            shifts.append((abs(area_delta), name, current_count, previous_count, area_delta, area_pct))
    for _, name, current_count, previous_count, area_delta, area_pct in sorted(shifts, reverse=True)[:2]:
        movement = "up" if area_delta > 0 else "down"
        output.append({"category": "geographic_concentration", "vendor": company, "area": name, "text": company + " had " + format(current_count, ",") + " vehicles in the " + name + ", " + movement + " " + format(abs(area_delta), ",") + " (" + format(abs(area_pct), ".1f") + "%) from the prior snapshot.", "current": current_count, "previous": previous_count, "change": area_delta, "change_pct": area_pct})
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, default=Path("data-gbfs.json"))
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=Path("data-gbfs-observations.json"))
    args = parser.parse_args()
    current_payload = json.loads(args.current.read_text())
    current_id = current_payload["snapshot_id"]
    current_items = current_payload.get("vehicles", [])
    candidates = sorted(args.archive_root.glob("*/snapshots/columbus_scooters_*.csv"))
    older = [path for path in candidates if path.stem.replace("columbus_scooters_", "") < current_id]
    if not older:
        raise SystemExit("No older archived snapshot is available.")
    previous_path = older[-1]
    previous_id = previous_path.stem.replace("columbus_scooters_", "")
    previous_items = read_csv(previous_path)
    existing = json.loads(args.output.read_text()) if args.output.exists() else {"snapshots": []}
    snapshots = [item for item in existing.get("snapshots", []) if item.get("snapshot_id") != current_id]
    notes, vendor_metrics = [], {}
    for company in sorted({item.get("company") for item in current_items if item.get("company")}):
        current_metrics = metrics(current_items, company)
        previous_metrics = metrics(previous_items, company)
        vendor_metrics[company] = {"current": current_metrics, "previous": previous_metrics}
        notes.extend(observations(company, current_metrics, previous_metrics))
    snapshots.insert(0, {"snapshot_id": current_id, "compared_with": previous_id, "observations": notes, "vendor_metrics": vendor_metrics})
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "method": {"scope": "GBFS vendor behavior only; no 311 records or complaint signals are used.", "comparison": "Newest website GBFS snapshot versus the newest older archived snapshot.", "review_areas": AREAS, "interpretation": "Published point-in-time fleet observations, not proof of deployment intent, demand, service quality, or causation."}, "snapshots": snapshots[:24]}
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"snapshot_id": current_id, "compared_with": previous_id, "observations": len(notes)}, indent=2))

if __name__ == "__main__":
    main()
