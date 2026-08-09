# Columbus Micromobility Data

[![Pull 311 Data](https://github.com/steveneedham/columbus-micromobility-data/actions/workflows/pull-311-data.yml/badge.svg)](https://github.com/steveneedham/columbus-micromobility-data/actions/workflows/pull-311-data.yml)
[![Pull GBFS Data](https://github.com/steveneedham/columbus-micromobility-data/actions/workflows/pull-gbfs-data.yml/badge.svg)](https://github.com/steveneedham/columbus-micromobility-data/actions/workflows/pull-gbfs-data.yml)
[![Columbus Micromobility Fleet Export](https://github.com/steveneedham/columbus-micromobility-data/actions/workflows/fleet-export.yml/badge.svg)](https://github.com/steveneedham/columbus-micromobility-data/actions/workflows/fleet-export.yml)

Live tracking of Spin and Veo fleet positions and city 311 complaints in Columbus, OH. Automated data pipeline feeds the [public GBFS dashboard](https://steveneedham.github.io/columbus-micromobility-data) and powers compliance, operational, and civic analysis.

---

## What This Does

This repo runs two continuously-updated data feeds:

1. **GBFS Fleet Data** — Vehicle positions, battery levels, availability status for Spin and Veo. Pulled 2× daily (8am/8pm UTC) from operator APIs.
2. **311 Complaint Data** — Shared scooter and bike parking/safety complaints from Columbus' public service request system. Pulled hourly from city GIS REST API.

Both feeds are committed as timestamped snapshots, and each pull refreshes the live dashboard (`index.html`) directly — its embedded map/analysis data is rewritten and committed as part of the same automation run.

The whole pipeline runs on GitHub Actions — no servers, no manual pulls, no stale data.

---

## Automation Pipeline

### Schedules

| Trigger | What | Output | Frequency |
|---------|------|--------|-----------|
| **Every hour** | Fetch 311 complaints, rebuild the site's 311 layer | `snapshots/311_requests_*.json`, `data-311.json`, `index.html` | Hourly |
| **8am UTC** | Run GBFS notebook, then trigger a fleet export | `snapshots/columbus_scooters_*.csv` | Daily |
| **8pm UTC** | Run GBFS notebook, then trigger a fleet export | `snapshots/columbus_scooters_*.csv` | Daily |
| **4am UTC** (fallback) | Fetch live GBFS + rebuild the dashboard | `index.html`, `data-gbfs.json`, `data-gbfs-observations.json`, plots | Daily |

### Workflow Files

- `.github/workflows/pull-311-data.yml` — Hourly 311 API fetch, rebuilds `data-311.json` and syncs it into `index.html`, commits
- `.github/workflows/pull-gbfs-data.yml` — 2× daily GBFS notebook execution, then dispatches `fleet-export.yml`
- `.github/workflows/fleet-export.yml` — Fetches live Veo/Spin GBFS data, rewrites `index.html`'s embedded map/analysis data, commits. Runs on its own daily cron and whenever `pull-gbfs-data.yml` finishes.

Each pull workflow:
- Checks out the repo
- Pulls fresh data from the respective API
- Commits snapshots (and, for 311, the rebuilt `data-311.json` + `index.html`) with ISO 8601 timestamps
- (GBFS only) dispatches `fleet-export.yml` so the live dashboard reflects the new snapshot

---

## Data Schema

### GBFS Snapshots: `columbus_scooters_YYYYMMDDTHHMMSSZ.csv`

Columns:
- `Company` — "Spin" or "Veo"
- `Vehicle_ID` — Operator's internal ID
- `Type` — Vehicle type ("scooter" or "bike")
- `Latitude` — Decimal latitude
- `Longitude` — Decimal longitude
- `Battery_Pct` — Battery percentage (integer, 0–100)
- `Range_Miles` — Estimated range in miles (float)
- `Is_Available` — String: 'True' or 'False'
- `Is_Disabled` — String: 'True' or 'False'
- `Is_Reserved` — String: 'True' or 'False'
- `Last_Reported` — ISO 8601 timestamp of last position update

**File naming:** `columbus_scooters_20260802T085430Z.csv` (UTC timezone always).

**Size:** ~350KB per snapshot (2,000–2,400 vehicles × 11 columns).

### 311 Data: `311_requests_YYYYMMDDTHHMMSSZ.json`

Array of complaint objects. Each object contains:
- `CASE_ID` — Unique case identifier (e.g., "CAS-3089579-L6N6Q9")
- `STATUS` — Current status ("Open", "Resolved", "Duplicate", etc.)
- `REPORTED_DATE` — ISO 8601 timestamp when complaint was filed
- `STATUS_DATE` — Last status update timestamp
- `REQUEST_TYPE` — "Shared Electric Bike & Scooters" (filtered)
- `STREET` — Street address
- `CITY` — City (Columbus, OH)
- `ZIP` — Zip code
- `COLUMBUSCOMMUNITY` — Neighborhood name
- `AREACOMMISSION` — Area commission district
- `COUNCILDISTRICT` — City council district
- `LATITUDE` — Decimal latitude
- `LONGITUDE` — Decimal longitude

**Source:** Columbus GIS REST API (public, read-only)
```
https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query
?REQUEST_TYPE='Shared Electric Bike & Scooters'
```

**Scope:** Last 30 days (rolling window).

**File naming:** `311_requests_20260802T091411Z.json` (UTC timezone always).

---

## Directory Structure

```
columbus-micromobility-data/
├── README.md                          (this file)
├── index.html                         (the live dashboard, deployed as-is)
├── data-311.json                      (standalone 311 layer, synced into index.html)
├── data-gbfs.json                     (standalone GBFS layer, synced into index.html)
├── data-gbfs-observations.json        (snapshot-to-snapshot vendor change log)
├── .github/workflows/
│   ├── pull-311-data.yml              (hourly 311 fetch + site sync)
│   ├── pull-gbfs-data.yml             (2× daily GBFS, triggers fleet-export.yml)
│   └── fleet-export.yml               (live GBFS fetch → rebuilds index.html)
├── scripts/
│   ├── pull_311.py                    (fetch + parse 311 API)
│   ├── build_311_data.py              (snapshot → data-311.json + index.html sync)
│   └── export_fleet.py                (live GBFS fetch → data-gbfs*.json + index.html sync)
├── snapshots/                         (timestamped pull history, committed)
│   ├── 311_requests_*.json
│   └── columbus_scooters_*.csv
└── plots/                             (dashboard assets)
    ├── battery_percentage_distribution.png
    ├── range_distribution.png
    └── vehicle_type_distribution.png
```

---

## Using the Data

### Live Dashboard

**[steveneedham.github.io/columbus-micromobility-data](https://steveneedham.github.io/columbus-micromobility-data)**

Interactive map showing:
- Current Spin and Veo fleet positions (updated 2× daily)
- 311 complaint hotspots (updated hourly)
- Zone concentrations and deployment heatmaps
- Vehicle availability by operator

### CSV Access

Latest GBFS snapshot:
```
https://raw.githubusercontent.com/steveneedham/columbus-micromobility-data/main/snapshots/columbus_scooters_latest.csv
```

All snapshots available in `/snapshots/` directory on `main` branch. Filter by date/operator in your analysis tool (Python pandas, R, Excel, etc.).

### JSON Access

Latest 311 complaints:
```
https://raw.githubusercontent.com/steveneedham/columbus-micromobility-data/main/snapshots/311_requests_latest.json
```

### Analysis Templates

Python notebook examples coming soon. For now, the GBFS CSV is straightforward to load:

```python
import pandas as pd

df = pd.read_csv('columbus_scooters_20260802T085430Z.csv')
print(f"Spin: {len(df[df['Company']=='Spin'])} | Veo: {len(df[df['Company']=='Veo'])}")
print(f"Available: {len(df[df['Is_Available']=='True'])} | Disabled: {len(df[df['Is_Disabled']=='True'])}")
```

---

## Civic Context

**Regulatory Caps (City of Columbus, Populus.ai):**
- Spin: Max 2,000 vehicles
- Veo: Max 2,000 vehicles

**Key Metrics to Watch:**
- Fleet compliance with deployed-vehicle caps
- 311 complaint velocity (new complaints per day)
- Parking/obstruction hotspots by zone
- Battery health distribution (median %, disabled count)
- Operator response patterns (fleet volatility, rebalancing cadence)

This data is public and intended for:
- City planners and transit advocates
- Researchers studying micromobility policy
- Operator compliance analysis
- Community organizing around parking and safety

---

## Contributing

### Add a New Data Source

1. Create a new workflow file in `.github/workflows/`
2. Add a fetch script in `scripts/` that outputs a timestamped JSON or CSV to `snapshots/`
3. If it should show up on the live dashboard, sync it into `index.html`'s embedded data (see `sync_index_html` in `build_311_data.py` or `write_dashboard_data` in `export_fleet.py` for the pattern)
4. Update this README with schema and schedule

### Local Testing

Pull the latest data locally without running the workflows:

```bash
# Fetch 311 data and sync it into data-311.json / index.html
python scripts/pull_311.py
python scripts/build_311_data.py

# Fetch GBFS data (requires Papermill + notebook)
papermill Veo_Spin_CBS_GBFS_Extract.ipynb /dev/null

# Rebuild the live dashboard's GBFS layer (live fetch, no notebook needed)
python scripts/export_fleet.py
```

### Reporting Issues

If a workflow fails or data is stale:
1. Check the Actions tab for error logs
2. Verify the upstream API is reachable
3. Open an issue with the workflow name, timestamp, and error output

---

## Maintenance

### Data Retention

- **Snapshots:** Last 90 days retained in `/snapshots/`. Older files are archived or deleted to keep repo size manageable.
- **GitHub Pages site:** Always reflects the latest snapshot. Historical data available via snapshot archive or direct API calls to operators.

### Secrets & Credentials

No credentials required. Both data sources are public:
- 311 API: Columbus GIS REST (no auth)
- GBFS: Operator public endpoints (no auth required for read-only)

If you fork this repo, workflows will run with your GitHub Actions quota. No additional setup needed.

---

## Authors & Attribution

**Steven Needham** — Micromobility operations analyst, former Spin and Veo operations lead in Columbus. This project combines operational experience with public data to provide transparent, actionable intelligence on the local micromobility market.

**Data sources:**
- Spin GBFS: `https://mds.bird.co/gbfs/v2/public/provider/spin/columbus/`
- Veo GBFS: `https://cluster-prod.veoride.com/api/shares/name/cbs/gbfs/`
- Columbus 311: `https://gis.columbus.gov/coc311map/`
- Municipality boundaries (`data-municipality-boundaries.json`): The Ohio State University boundary is a supplied policy geography export (see `data-osu-boundary.json`); Marble Cliff, Grandview Heights, Upper Arlington, Bexley, and Dublin are from [OpenStreetMap](https://www.openstreetmap.org/copyright) (ODbL) via the Overpass API — see `scripts/build_municipality_boundaries.py` to regenerate.

---

## License

Public domain. Use this data freely for analysis, research, and civic purposes.
