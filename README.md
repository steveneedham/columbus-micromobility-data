# Columbus Micromobility Data

Live tracking of Spin and Veo fleet positions and city 311 complaints in Columbus, OH. Automated data pipeline feeds the [public GBFS dashboard](https://steveneedham.github.io/columbus-micromobility-data) and powers compliance, operational, and civic analysis.

---

## What This Does

This repo runs two continuously-updated data feeds:

1. **GBFS Fleet Data** — Vehicle positions, battery levels, availability status for Spin and Veo. Pulled 2× daily (8am/8pm UTC) from operator APIs.
2. **311 Complaint Data** — Shared scooter and bike parking/safety complaints from Columbus' public service request system. Pulled hourly from city GIS REST API.

Both feeds are committed as timestamped snapshots. A shared rebuild workflow ingests the latest data and regenerates the public dashboard and GeoJSON layers that power map-based analysis.

The whole pipeline runs on GitHub Actions — no servers, no manual pulls, no stale data.

---

## Automation Pipeline

### Schedules

| Trigger | What | Output | Frequency |
|---------|------|--------|-----------|
| **Every hour** | Fetch 311 complaints | `snapshots/311_requests_*.json` | Hourly |
| **8am UTC** | Run GBFS notebook | `snapshots/columbus_scooters_*.csv` | Daily |
| **8pm UTC** | Run GBFS notebook | `snapshots/columbus_scooters_*.csv` | Daily |
| **On both** | Rebuild dashboard | Push to GitHub Pages | Cascading |

### Workflow Files

- `.github/workflows/pull-311-data.yml` — Hourly 311 API fetch + commit
- `.github/workflows/pull-gbfs-data.yml` — 2× daily GBFS notebook execution
- `.github/workflows/rebuild-site.yml` — Shared rebuild handler (triggered by above)

Each workflow:
- Checks out the repo
- Pulls fresh data from the respective API
- Commits snapshots to `snapshots/` with ISO 8601 timestamps
- Triggers the rebuild workflow via `workflow_call:`

The rebuild workflow:
- Loads the latest 311 JSON snapshot
- Loads the latest GBFS CSV snapshot
- Regenerates HTML map and GeoJSON feature layers
- Commits all outputs
- Pushes to GitHub Pages at `steveneedham.github.io/columbus-micromobility-data`

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
├── .github/workflows/
│   ├── pull-311-data.yml              (hourly 311 fetch)
│   ├── pull-gbfs-data.yml             (2× daily GBFS)
│   └── rebuild-site.yml               (shared rebuild handler)
├── scripts/
│   ├── pull_311.py                    (fetch + parse 311 API)
│   └── rebuild_site.py                (load snapshots → HTML/GeoJSON)
├── snapshots/                         (auto-generated, not committed)
│   ├── 311_requests_*.json
│   └── columbus_scooters_*.csv
├── data/                              (curated reference data)
│   ├── zones.geojson                  (service area boundaries)
│   └── policy.md                      (regulatory caps, status)
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
3. Update the rebuild workflow to ingest the new feed
4. Update this README with schema and schedule

### Local Testing

Pull the latest data locally without running the workflows:

```bash
# Fetch 311 data
python scripts/pull_311.py

# Fetch GBFS data (requires Papermill + notebook)
papermill Veo_Spin_CBS_GBFS_Extract.ipynb -

# Rebuild the site
python scripts/rebuild_site.py
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

---

## License

Public domain. Use this data freely for analysis, research, and civic purposes.
