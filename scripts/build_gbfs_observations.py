#!/usr/bin/env python3
# Append evidence-bounded vendor observations for the newest GBFS snapshot.
# --backfill (or --backfill-only) also reconstructs entries for older
# consecutive pairs of archived snapshots not yet covered -- see
# build_backfill_entries() -- so growing the archive with older files
# extends this log the same way it already extends pile-up history.
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
    """Only Company/Latitude/Longitude are required. Range_Miles and
    Is_Available are read as None (not 0 / False) when missing or blank --
    some older archived exports only ever captured position, not range or
    availability, and defaulting those to 0/False would fabricate a
    reading rather than reflect that it's simply unknown. metrics() below
    excludes None values from its aggregates instead of counting them."""
    result = []
    with path.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            try:
                item = {"company": row["Company"], "lat": float(row["Latitude"]), "lng": float(row["Longitude"])}
            except (KeyError, TypeError, ValueError):
                continue
            range_raw = row.get("Range_Miles")
            try:
                item["range"] = float(range_raw) if range_raw not in (None, "") else None
            except (TypeError, ValueError):
                item["range"] = None
            avail_raw = row.get("Is_Available")
            item["available"] = avail_raw.lower() == "true" if avail_raw not in (None, "") else None
            result.append(item)
    return result

def distance(item, area):
    x = (item["lng"] - area["lng"]) * 111320 * math.cos(math.radians((item["lat"] + area["lat"]) / 2))
    y = (item["lat"] - area["lat"]) * 111320
    return math.hypot(x, y)

def metrics(items, company):
    vendor = [item for item in items if item.get("company") == company]
    ranges = [item["range"] for item in vendor if item.get("range") is not None]
    known_availability = [item["available"] for item in vendor if item.get("available") is not None]
    return {
        "vehicle_count": len(vendor),
        "median_range_miles": round(statistics.median(ranges), 1) if ranges else None,
        "available_share_pct": round(100 * sum(known_availability) / len(known_availability), 1) if known_availability else None,
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
    availability_delta = (
        round(current["available_share_pct"] - previous["available_share_pct"], 1)
        if current["available_share_pct"] is not None and previous["available_share_pct"] is not None
        else None
    )
    if availability_delta is not None and abs(availability_delta) >= 1:
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

def compare_pair(prev_path, curr_path):
    """Build one snapshot-log entry comparing two archived CSVs, or None if
    either side has no rows with a usable Company/Latitude/Longitude at
    all (a genuinely unparseable file). Reduced-schema exports missing
    only Range_Miles/Is_Available still produce fleet_size and
    geographic_concentration observations -- metrics() excludes the
    unknown range/availability values from its aggregates rather than
    fabricating a "range is 0 miles" or "0% available" reading, so
    observations() naturally omits the categories that would need them."""
    curr_items = read_csv(curr_path)
    prev_items = read_csv(prev_path)
    if not curr_items or not prev_items:
        return None
    curr_id = curr_path.stem.replace("columbus_scooters_", "")
    prev_id = prev_path.stem.replace("columbus_scooters_", "")
    notes, vendor_metrics = [], {}
    for company in sorted({item.get("company") for item in curr_items if item.get("company")}):
        current_metrics = metrics(curr_items, company)
        previous_metrics = metrics(prev_items, company)
        vendor_metrics[company] = {"current": current_metrics, "previous": previous_metrics}
        notes.extend(observations(company, current_metrics, previous_metrics))
    return {
        "snapshot_id": curr_id,
        "compared_with": prev_id,
        "observations": notes,
        "vendor_metrics": vendor_metrics,
        "backfilled": True,
    }


def build_backfill_entries(snapshots_dir, already_present):
    """Reconstruct an observation entry for every consecutive pair of
    archived snapshots not already covered, in chronological order.
    Pairs spanning a schema gap (see compare_pair) are skipped, not
    faked, so coverage is whatever the real archive actually supports --
    including pairs separated by several days where the archive itself
    has a gap, which is disclosed via "backfilled": true rather than
    presented the same as a routine same-day comparison."""
    archived = sorted(snapshots_dir.glob("columbus_scooters_*.csv"))
    entries = []
    for prev_path, curr_path in zip(archived, archived[1:]):
        curr_id = curr_path.stem.replace("columbus_scooters_", "")
        if curr_id in already_present:
            continue
        entry = compare_pair(prev_path, curr_path)
        if entry is None:
            continue
        entries.append(entry)
        already_present.add(curr_id)
    return entries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, default=Path("data-gbfs.json"))
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output", type=Path, default=Path("data-gbfs-observations.json"))
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Also reconstruct observations for every consecutive pair of archived "
             "snapshots/columbus_scooters_*.csv not already covered, in addition to "
             "the usual current-vs-newest-older-archive comparison.",
    )
    parser.add_argument(
        "--backfill-only",
        action="store_true",
        help="Run only the backfill pass; skip requiring a current data-gbfs.json snapshot.",
    )
    args = parser.parse_args()
    if args.backfill_only:
        existing = json.loads(args.output.read_text()) if args.output.exists() else {"snapshots": []}
        already_present = {item.get("snapshot_id") for item in existing.get("snapshots", [])}
        backfilled = build_backfill_entries(Path("snapshots"), already_present)
        snapshots = existing.get("snapshots", []) + backfilled
        snapshots.sort(key=lambda item: item["snapshot_id"], reverse=True)
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "method": {
                "scope": "GBFS vendor behavior only; no 311 records or complaint signals are used.",
                "comparison": "Newest website GBFS snapshot versus the newest older archived snapshot; backfilled entries compare each archived snapshot against the one immediately before it in the repo's archive, which may be several days apart where the archive itself has a gap.",
                "review_areas": AREAS,
                "interpretation": "Published point-in-time fleet observations, not proof of deployment intent, demand, service quality, or causation.",
            },
            "snapshots": snapshots,
        }
        args.output.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"Backfilled {len(backfilled)} new entr{'y' if len(backfilled) == 1 else 'ies'}; {len(snapshots)} tracked total")
        return
    current_payload = json.loads(args.current.read_text())
    current_id = current_payload["snapshot_id"]
    current_items = current_payload.get("vehicles", [])
    # Nested per-date archive (e.g. the local Google Drive export root); falls
    # back to a flat snapshots/ directory (e.g. this repo's own committed archive).
    candidates = sorted(args.archive_root.glob("*/snapshots/columbus_scooters_*.csv"))
    if not candidates:
        candidates = sorted(args.archive_root.glob("snapshots/columbus_scooters_*.csv"))
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
    comparison_note = "Newest website GBFS snapshot versus the newest older archived snapshot."
    backfilled_count = 0
    if args.backfill:
        already_present = {item.get("snapshot_id") for item in snapshots}
        backfilled = build_backfill_entries(Path("snapshots"), already_present)
        backfilled_count = len(backfilled)
        snapshots.extend(backfilled)
        snapshots.sort(key=lambda item: item["snapshot_id"], reverse=True)
        comparison_note += " Backfilled entries compare each archived snapshot against the one immediately before it in the repo's archive, which may be several days apart where the archive itself has a gap."
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "method": {"scope": "GBFS vendor behavior only; no 311 records or complaint signals are used.", "comparison": comparison_note, "review_areas": AREAS, "interpretation": "Published point-in-time fleet observations, not proof of deployment intent, demand, service quality, or causation."}, "snapshots": snapshots}
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"snapshot_id": current_id, "compared_with": previous_id, "observations": len(notes), "backfilled": backfilled_count}, indent=2))

if __name__ == "__main__":
    main()
