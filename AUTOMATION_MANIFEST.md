# Automation Manifest

Complete inventory of workflows and scripts that power the columbus-micromobility-data pipeline.

---

## GitHub Actions Workflows

### `.github/workflows/pull-311-data.yml`
**Purpose:** Fetch Columbus 311 complaints hourly

**Trigger:** `0 * * * *` (every hour at :00)

**Process:**
1. Checkout repo
2. Set up Python 3.11
3. Run `scripts/pull_311.py` to fetch from Columbus GIS API
4. Commit snapshot to `snapshots/311_requests_YYYYMMDDTHHMMSSZ.json`
5. Trigger `rebuild-site.yml` workflow

**Output:**
- `snapshots/311_requests_*.json` (timestamped snapshots)
- `snapshots/311_requests_latest.json` (symlink to latest)

---

### `.github/workflows/pull-gbfs-data.yml`
**Purpose:** Execute GBFS extraction notebook 2× daily

**Trigger:**
- `0 8 * * *` (daily at 8am UTC)
- `0 20 * * *` (daily at 8pm UTC)

**Process:**
1. Checkout repo
2. Set up Python 3.11
3. Run `Veo_Spin_CBS_GBFS_Extract.ipynb` via Papermill
4. Commit snapshots to `snapshots/columbus_scooters_*.csv`
5. Trigger `rebuild-site.yml` workflow

**Output:**
- `snapshots/columbus_scooters_*.csv` (timestamped vehicle positions)
- `plots/*.png` (summary visualizations from notebook)

---

### `.github/workflows/rebuild-site.yml`
**Purpose:** Aggregate 311 + GBFS data and regenerate the public dashboard

**Trigger:** Workflow dispatch (called by both pull workflows)

**Process:**
1. Checkout repo
2. Set up Python 3.11
3. Run `scripts/rebuild_site.py` to:
   - Load latest 311 JSON snapshot
   - Load latest GBFS CSV snapshot
   - Generate GeoJSON feature layers
   - Generate dashboard HTML
4. Commit outputs to `docs/`
5. Deploy to GitHub Pages

**Output:**
- `docs/index.html` (main dashboard page)
- `docs/gbfs_vehicles.geojson` (Spin/Veo fleet layer)
- `docs/311_complaints.geojson` (complaints layer)

---

## Python Scripts

### `scripts/pull_311.py`
**Purpose:** Fetch 311 data from Columbus GIS REST API

**Environment:** Called by `.github/workflows/pull-311-data.yml`

**Dependencies:** `requests`

**Function:**
- Queries Columbus GIS endpoint with filter: `REQUEST_TYPE = 'Shared Electric Bike & Scooters'`
- Parses JSON response
- Saves timestamped snapshot: `snapshots/311_requests_20260802T091411Z.json`
- Updates `snapshots/311_requests_latest.json` for easy access

**Error handling:** Logs failures to stderr, returns non-zero exit code on failure

**Notes:**
- API endpoint: `https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query`
- Scope: Last 30 days (rolling window set by API)
- No authentication required

---

### `scripts/rebuild_site.py`
**Purpose:** Aggregate data snapshots and regenerate the public dashboard

**Environment:** Called by `.github/workflows/rebuild-site.yml`

**Dependencies:** Standard library (`json`, `csv`, `pathlib`, `datetime`)

**Functions:**

#### `load_latest_311()`
- Loads `snapshots/311_requests_latest.json`
- Returns parsed data dict

#### `load_latest_gbfs()`
- Finds most recent `columbus_scooters_*.csv` in snapshots/
- Loads as list of vehicle dicts

#### `generate_gbfs_geojson(vehicles)`
- Converts vehicle list to GeoJSON FeatureCollection
- Includes: vehicle_id, company, type, battery_pct, range_miles, is_available, is_disabled, last_reported
- Filters out invalid lat/lon

#### `generate_311_geojson(data)`
- Converts complaint records to GeoJSON FeatureCollection
- Includes: case_id, status, reported_date, status_date, street, zip, community, council_district
- Filters out invalid lat/lon

#### `generate_dashboard_html(gbfs_data, data_311)`
- Creates HTML with Leaflet map and stat cards
- Loads GeoJSON layers for vehicles and complaints
- Color coding: Spin (coral #FF6B35), Veo (green #00A86B), Open (red), Resolved (green)

#### `save_geojson(name, geojson)` / `save_html(html, filename)`
- Writes files to `docs/` directory

---

## Supporting Files

### `README.md`
**Comprehensive documentation** covering:
- Pipeline overview
- Data schemas (GBFS CSV columns, 311 JSON fields)
- Automation schedules
- Directory structure
- Data access (live dashboard, CSV/JSON downloads)
- Civic context (regulatory caps, key metrics)
- Contributing & maintenance

### `SETUP.md`
**Deployment guide** covering:
- GitHub Actions setup
- GitHub Pages configuration
- First manual run instructions
- Customization (change schedules, filters, add features)
- Troubleshooting common issues
- Production checklist

### `.gitignore`
- Excludes `snapshots/` (auto-generated)
- Excludes Python cache, venv, IDE files, OS files
- Keeps `.gitkeep` to preserve directory structure

### `snapshots/.gitkeep`
- Placeholder to ensure snapshots/ exists in the repo
- Actual snapshots are ignored by git

---

## Data Flow Diagram

```
311 API (hourly)  ─→  pull_311.py  ─→  311_requests_*.json  ┐
                                                              │
GBFS endpoints    ─→  notebook          columbus_scooters_  ├──→  rebuild_site.py  ─→  docs/  ─→  GitHub Pages
(2x daily)           (papermill)        *.csv               │
                                                              │
                                        + plots/ ────────────┘
```

---

## Troubleshooting Quick Reference

| Issue | Check |
|-------|-------|
| Workflows not running | GitHub Actions enabled? `.github/workflows/*.yml` present? |
| 311 data empty | Columbus GIS API online? Filter correct? |
| GBFS data missing | Notebook exists at repo root? Dependencies installed? |
| Dashboard not live | GitHub Pages enabled? `/docs/` directory exists? |
| Site not updating | Rebuild workflow triggered? No errors in Actions log? |

---

## Next Steps for Enhancement

1. **Add real-time updates:** Reduce GBFS schedule to every 30 minutes
2. **Historical analysis:** Keep full 90-day snapshot archive instead of latest-only
3. **Advanced visualizations:** Add heatmaps, density clustering, time-series charts to HTML
4. **Alerts & webhooks:** Trigger Slack notification when 311 count spikes or fleet cap exceeded
5. **Data validation:** Add schema checks and anomaly detection before committing
6. **Multi-operator:** Expand to include Lime, Bird, Jump if they enter market
7. **API wrapper:** Create `/api/latest.json` endpoint for third-party consumption

---

## File Manifest

```
.github/workflows/
├── pull-311-data.yml        (hourly 311 fetch)
├── pull-gbfs-data.yml       (2x daily GBFS)
└── rebuild-site.yml         (shared rebuild)

scripts/
├── pull_311.py              (Columbus GIS API client)
└── rebuild_site.py          (dashboard generator)

snapshots/
└── .gitkeep                 (preserved directory, auto-generated data ignored)

docs/
├── index.html               (auto-generated dashboard)
├── gbfs_vehicles.geojson    (auto-generated vehicle layer)
└── 311_complaints.geojson   (auto-generated complaint layer)

Root:
├── README.md                (data schema, civil context, usage guide)
├── SETUP.md                 (deployment instructions)
├── AUTOMATION_MANIFEST.md   (this file)
└── .gitignore               (exclude auto-generated files)
```
