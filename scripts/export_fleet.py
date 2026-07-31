#!/usr/bin/env python3
# Fetch current Veo/Spin GBFS vehicle positions and archive a daily snapshot,
# rollup summary, and fleet-count plot. Run by .github/workflows/fleet-export.yml.
import json
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


def available(vehicle):
    return vehicle.get("is_disabled") == 0 and vehicle.get("is_reserved") == 0


def fetch_fleet():
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
    for bike in veo_bikes:
        records.append({
            "Company": "Veo",
            "Vehicle_ID": bike.get("bike_id", "Unknown"),
            "Type": veo_types.get(bike.get("vehicle_type_id"), "") or "",
            "Latitude": bike.get("lat"),
            "Longitude": bike.get("lon"),
            "Battery_Pct": bike.get("battery_level") or bike.get("battery_pct"),
            "Range_Miles": meters_to_miles(bike.get("current_range_meters")),
            "Is_Available": available(bike),
        })
    for bike in spin_bikes:
        records.append({
            "Company": "Spin",
            "Vehicle_ID": bike.get("bike_id") or bike.get("vehicle_id") or "Unknown",
            "Type": SPIN_TYPES.get(bike.get("vehicle_type_id"), "e-bike"),
            "Latitude": bike.get("lat"),
            "Longitude": bike.get("lon"),
            "Battery_Pct": battery_percent(bike),
            "Range_Miles": meters_to_miles(bike.get("current_range_meters") or bike.get("range_meters")),
            "Is_Available": available(bike),
        })
    return pd.DataFrame.from_records(records)


def write_snapshot(df, timestamp):
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    path = SNAPSHOTS_DIR / f"columbus_scooters_{timestamp}.csv"
    df.to_csv(path, index=False)
    return path


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


def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    df = fetch_fleet()
    snapshot_path = write_snapshot(df, timestamp)
    summary_path = write_daily_summary(df, timestamp)
    plot_path = write_plot(df, timestamp)
    print(json.dumps({
        "timestamp": timestamp,
        "snapshot": str(snapshot_path),
        "daily_summary": str(summary_path),
        "plot": str(plot_path),
        "total_vehicles": int(len(df)),
    }))


if __name__ == "__main__":
    main()
