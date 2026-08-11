#!/usr/bin/env python3
# Fetch current Veo/Spin GBFS vehicle positions, archive a daily snapshot,
# rollup summary, and fleet-count plot, then refresh the dashboard's own
# data-gbfs.json / data-gbfs-observations.json / data-pileup-history.json
# and their embedded copies in index.html so the live site stays current.
# Run by .github/workflows/fleet-export.yml (daily 4:00 UTC, or on demand).
import csv
import json
import math
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOTS_DIR = ROOT / "snapshots"
DAILY_SUMMARY_DIR = ROOT / "daily_summary"
PLOTS_DIR = ROOT / "plots"
DATA_GBFS_PATH = ROOT / "data-gbfs.json"
DATA_OBSERVATIONS_PATH = ROOT / "data-gbfs-observations.json"
DATA_PILEUP_HISTORY_PATH = ROOT / "data-pileup-history.json"
INDEX_HTML_PATH = ROOT / "index.html"
BUILD_OBSERVATIONS_SCRIPT = ROOT / "scripts" / "build_gbfs_observations.py"
BUILD_PILEUP_HISTORY_SCRIPT = ROOT / "scripts" / "build_pileup_history.py"

VEO_STATUS = "https://cluster-prod.veoride.com/api/shares/name/cbs/gbfs/free_bike_status"
VEO_TYPES = "https://cluster-prod.veoride.com/api/shares/name/cbs/gbfs/vehicle_types"
SPIN_STATUS = "https://mds.bird.co/gbfs/v2/public/provider/spin/columbus/free_bike_status.json"
USER_AGENT = "Mozilla/5.0 (compatible; Columbus-mobility-observer/1.0)"

SPIN_TYPES = {
    "2ea3c8b2-ed07-4c53-b87e-638c08471309": "scooter",
    "bae2102b-56ba-42ba-9097-720e5990b4b2": "e-bike",
}


def fetch_json(url):
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    return response.json()


def meters_to_miles(value):
    try:
        return round(float(value) / 1609.34, 2)
    except (TypeError, ValueError):
        return None


def battery_percent(vehicle):
    for key in ("battery_pct", "battery_level", "current_fuel_percent"):
        value = vehicle.get(key)
        if value in (None, ""):
            continue
        try:
            numeric = float(value)
            if 0 < numeric <= 1:
                numeric *= 100
            return int(round(max(0, min(100, numeric))))
        except (TypeError, ValueError):
            continue
    return None


def fetch_fleet():
    """Fetch live Veo/Spin vehicles with full field fidelity, deduplicated by (company, id)."""
    veo_types_payload = fetch_json(VEO_TYPES)
    veo_payload = fetch_json(VEO_STATUS)
    spin_payload = fetch_json(SPIN_STATUS)

    veo_types = {
        item.get("vehicle_type_id"): item.get("form_factor")
        for item in veo_types_payload.get("data", {}).get("vehicle_types", [])
    }
    veo_bikes = veo_payload.get("data", {}).get("bikes", [])
    spin_bikes = spin_payload.get("data", {}).get("bikes", [])
    if not veo_bikes or not spin_bikes:
        raise RuntimeError(f"Refusing partial snapshot: Veo={len(veo_bikes)}, Spin={len(spin_bikes)}")

    records = []
    seen = set()

    def upsert(company, vehicle_id, vtype, lat, lng, battery, rng, disabled, reserved):
        if not vehicle_id or lat is None or lng is None:
            return
        key = (company, vehicle_id)
        if key in seen:
            return
        seen.add(key)
        records.append({
            "Company": company,
            "Vehicle_ID": str(vehicle_id),
            "Type": vtype or "",
            "Latitude": lat,
            "Longitude": lng,
            "Battery_Pct": battery,
            "Range_Miles": rng,
            "Is_Available": bool(disabled == 0 and reserved == 0),
            "Is_Disabled": bool(disabled),
            "Is_Reserved": bool(reserved),
        })

    for bike in veo_bikes:
        upsert(
            "Veo",
            bike.get("bike_id"),
            veo_types.get(bike.get("vehicle_type_id"), "") or "",
            bike.get("lat"),
            bike.get("lon"),
            bike.get("battery_level") or bike.get("battery_pct"),
            meters_to_miles(bike.get("current_range_meters")),
            bike.get("is_disabled"),
            bike.get("is_reserved"),
        )

    for bike in spin_bikes:
        upsert(
            "Spin",
            bike.get("bike_id") or bike.get("vehicle_id"),
            SPIN_TYPES.get(bike.get("vehicle_type_id"), "e-bike"),
            bike.get("lat"),
            bike.get("lon"),
            battery_percent(bike),
            meters_to_miles(bike.get("current_range_meters") or bike.get("range_meters")),
            bike.get("is_disabled"),
            bike.get("is_reserved"),
        )

    return pd.DataFrame.from_records(records)


def write_snapshot(df, timestamp):
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    path = SNAPSHOTS_DIR / f"columbus_scooters_{timestamp}.csv"
    df.to_csv(path, index=False)
    return path


def distance_meters(a, b):
    lat_scale = 111320
    lng_scale = 111320 * math.cos(math.radians((a[0] + b[0]) / 2))
    return math.hypot((a[0] - b[0]) * lat_scale, (a[1] - b[1]) * lng_scale)


def load_previous_veo_positions(current_timestamp):
    """Most recent archived snapshot strictly older than the one just
    written, keyed by Veo's own vehicle_id. Veo's IDs are stable across
    pulls (99.9% overlap between consecutive snapshots observed in this
    repo's archive); Spin's rotate every pull (0% overlap), so this is
    deliberately Veo-only (#22)."""
    candidates = sorted(SNAPSHOTS_DIR.glob("columbus_scooters_*.csv"))
    older = [p for p in candidates if p.stem.replace("columbus_scooters_", "") < current_timestamp]
    if not older:
        return None, {}
    previous_path = older[-1]
    previous_id = previous_path.stem.replace("columbus_scooters_", "")
    positions = {}
    with previous_path.open(newline="", encoding="utf-8-sig") as source:
        for row in csv.DictReader(source):
            if row.get("Company") != "Veo":
                continue
            try:
                positions[row["Vehicle_ID"]] = {
                    "lat": float(row["Latitude"]),
                    "lng": float(row["Longitude"]),
                    "range": float(row["Range_Miles"]) if row.get("Range_Miles") not in (None, "") else None,
                }
            except (KeyError, TypeError, ValueError):
                pass
    return previous_id, positions


def write_daily_summary(df, timestamp):
    DAILY_SUMMARY_DIR.mkdir(exist_ok=True)
    date_str = timestamp[:8]
    summary_path = DAILY_SUMMARY_DIR / f"{date_str}.json"
    existing = json.loads(summary_path.read_text()) if summary_path.exists() else {"date": date_str, "runs": []}
    by_company = (
        df.groupby("Company")
        .agg(
            vehicle_count=("Vehicle_ID", "count"),
            available_count=("Is_Available", "sum"),
            median_range_miles=("Range_Miles", "median"),
        )
        .reset_index()
    )
    existing["runs"].append({
        "snapshot_id": timestamp,
        "companies": by_company.to_dict(orient="records"),
        "total_vehicles": int(len(df)),
    })
    summary_path.write_text(json.dumps(existing, indent=2, default=float) + "\n")
    return summary_path


def write_plot(df, timestamp):
    PLOTS_DIR.mkdir(exist_ok=True)
    counts = df.groupby("Company")["Vehicle_ID"].count()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=counts.index, y=counts.values, ax=ax)
    ax.set_title(f"Columbus fleet counts — {timestamp}")
    ax.set_ylabel("Vehicle count")
    ax.set_xlabel("")
    fig.tight_layout()
    date_str = timestamp[:8]
    path = PLOTS_DIR / f"{date_str}_fleet_counts.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def snapshot_id_to_iso(timestamp):
    """Convert a compact snapshot id (20260810T203225Z) to ISO-8601."""
    try:
        return datetime.strptime(timestamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


def build_dashboard_payload(df, timestamp, previous_snapshot_id=None, previous_veo_positions=None):
    previous_veo_positions = previous_veo_positions or {}
    vehicles = []
    for row in df.itertuples(index=False):
        battery = row.Battery_Pct
        rng = row.Range_Miles
        vehicle = {
            "id": row.Vehicle_ID,
            "company": row.Company,
            "type": row.Type,
            "lat": row.Latitude,
            "lng": row.Longitude,
            "battery": int(battery) if pd.notna(battery) else 0,
            "range": float(rng) if pd.notna(rng) else 0,
            "available": bool(row.Is_Available),
            "disabled": bool(row.Is_Disabled),
            "reserved": bool(row.Is_Reserved),
        }
        previous = previous_veo_positions.get(row.Vehicle_ID) if row.Company == "Veo" else None
        if previous:
            vehicle["prev_snapshot_id"] = previous_snapshot_id
            vehicle["prev_lat"] = previous["lat"]
            vehicle["prev_lng"] = previous["lng"]
            vehicle["moved_m"] = round(distance_meters((row.Latitude, row.Longitude), (previous["lat"], previous["lng"])), 1)
            if previous["range"] is not None and pd.notna(rng):
                vehicle["range_delta"] = round(float(rng) - previous["range"], 2)
        vehicles.append(vehicle)
    return {
        "snapshot_id": timestamp,
        "fetched_at": snapshot_id_to_iso(timestamp),
        "source_file": f"columbus_scooters_{timestamp}.csv",
        "position_count": len(vehicles),
        "invalid_row_count": 0,
        "vehicles": vehicles,
    }


def replace_embedded_script(html, element_id, new_json_text):
    pattern = re.compile(
        rf'(<script type="application/json" id="{element_id}">\n).*?(\n</script>)',
        re.DOTALL,
    )
    new_html, count = pattern.subn(lambda m: m.group(1) + new_json_text + m.group(2), html, count=1)
    if count != 1:
        raise RuntimeError(f"Expected exactly one #{element_id} script block, found {count}")
    return new_html


def write_dashboard_data(payload):
    DATA_GBFS_PATH.write_text(json.dumps(payload, separators=(",", ":")))
    html = INDEX_HTML_PATH.read_text()
    html = replace_embedded_script(html, "data-gbfs", json.dumps(payload, indent=2))
    INDEX_HTML_PATH.write_text(html)


def refresh_observations():
    """Rebuild data-gbfs-observations.json against the newest older archived
    snapshot in this repo's own snapshots/ directory, then sync it into
    index.html. A no-op (with a note) on the very first run, when there's no
    prior snapshot to compare against yet."""
    result = subprocess.run(
        [sys.executable, str(BUILD_OBSERVATIONS_SCRIPT), "--archive-root", str(ROOT), "--backfill"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Observation log not updated: {result.stderr.strip() or result.stdout.strip()}")
        return False
    html = INDEX_HTML_PATH.read_text()
    html = replace_embedded_script(html, "data-gbfs-observations", DATA_OBSERVATIONS_PATH.read_text().rstrip("\n"))
    INDEX_HTML_PATH.write_text(html)
    return True


def refresh_pileup_history():
    """Rebuild data-pileup-history.json (tracks how long each cross-vendor
    pile-up has persisted across snapshots) and sync it into index.html.
    Backfills from every archived snapshot on its very first run."""
    result = subprocess.run(
        [sys.executable, str(BUILD_PILEUP_HISTORY_SCRIPT)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Pile-up history not updated: {result.stderr.strip() or result.stdout.strip()}")
        return False
    html = INDEX_HTML_PATH.read_text()
    html = replace_embedded_script(html, "data-pileup-history", DATA_PILEUP_HISTORY_PATH.read_text().rstrip("\n"))
    INDEX_HTML_PATH.write_text(html)
    return True


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    df = fetch_fleet()

    snapshot_path = write_snapshot(df, timestamp)
    summary_path = write_daily_summary(df, timestamp)
    plot_path = write_plot(df, timestamp)

    previous_snapshot_id, previous_veo_positions = load_previous_veo_positions(timestamp)
    payload = build_dashboard_payload(df, timestamp, previous_snapshot_id, previous_veo_positions)
    write_dashboard_data(payload)
    observations_updated = refresh_observations()
    pileup_history_updated = refresh_pileup_history()

    counts = Counter(df["Company"])
    veo_with_movement = sum(1 for v in payload["vehicles"] if v.get("moved_m") is not None)
    print(json.dumps({
        "timestamp": timestamp,
        "snapshot": str(snapshot_path),
        "daily_summary": str(summary_path),
        "plot": str(plot_path),
        "total_vehicles": int(len(df)),
        "by_company": dict(counts),
        "observations_updated": observations_updated,
        "pileup_history_updated": pileup_history_updated,
        "veo_vehicles_matched_to_previous_snapshot": veo_with_movement,
    }, indent=2))


if __name__ == "__main__":
    main()
