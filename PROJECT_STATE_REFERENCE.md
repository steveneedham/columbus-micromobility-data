# Columbus Micromobility Data — Project State Reference

**Last Updated:** August 2, 2026 | **Repo:** steveneedham/columbus-micromobility-data

## Current Status

✅ **COMPLETE:** All automation workflows, scripts, and documentation created.

**Files created on disk:** `/mnt/project/`
- 3 GitHub Actions workflows (.yml)
- 2 Python scripts (pull_311.py, rebuild_site.py)
- 3 documentation files (README.md, SETUP.md, AUTOMATION_MANIFEST.md)
- .gitignore + snapshots/.gitkeep

**NOT YET DONE:**
- Commit/push to GitHub repo
- Enable GitHub Actions on repo
- Enable GitHub Pages on repo
- Test first manual run

---

## Files & Their Exact Paths

### Workflows (must be in `.github/workflows/`)
```
/mnt/project/.github/workflows/pull-311-data.yml
  - Runs: Every hour (0 * * * *)
  - Env: GitHub Actions, Python 3.11
  - Does: Fetch 311 API → save JSON → trigger rebuild
  - Size: 1.4 KB

/mnt/project/.github/workflows/pull-gbfs-data.yml
  - Runs: 2x daily (8am & 8pm UTC)
  - Env: GitHub Actions, Python 3.11, Papermill
  - Does: Execute notebook → save CSV → trigger rebuild
  - Size: 1.6 KB

/mnt/project/.github/workflows/rebuild-site.yml
  - Runs: On demand (workflow_call from above)
  - Env: GitHub Actions, Python 3.11
  - Does: Load snapshots → generate HTML/GeoJSON → push to GitHub Pages
  - Size: 1.1 KB
```

### Scripts (must be in `scripts/`)
```
/mnt/project/scripts/pull_311.py
  - Env: Python 3.11
  - Deps: requests (installed by workflow)
  - API: https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query
  - Auth: None (public read-only)
  - Output: snapshots/311_requests_YYYYMMDDTHHMMSSZ.json + latest.json
  - Size: 3.8 KB

/mnt/project/scripts/rebuild_site.py
  - Env: Python 3.11
  - Deps: Standard library only (json, csv, pathlib, datetime)
  - Input: snapshots/311_requests_latest.json, snapshots/columbus_scooters_*.csv
  - Output: docs/index.html, docs/gbfs_vehicles.geojson, docs/311_complaints.geojson
  - Size: 12 KB
```

### Documentation
```
/mnt/project/README.md (8.7 KB)
  - What: Full project documentation
  - For: Public + maintainers
  - Contains: Pipeline overview, data schemas, civic context, contributing guidelines

/mnt/project/SETUP.md (5.4 KB)
  - What: Deployment instructions
  - For: People deploying their own fork
  - Contains: GitHub Actions setup, Pages config, troubleshooting, customization

/mnt/project/AUTOMATION_MANIFEST.md (7.1 KB)
  - What: Technical inventory
  - For: Developers maintaining the pipeline
  - Contains: Workflow breakdown, data flow diagram, enhancement roadmap

/mnt/project/.gitignore
  - Excludes: snapshots/, __pycache__, *.pyc, venv/, .env, .DS_Store, .vscode/, .idea/
  - Keeps: .gitkeep files to preserve directory structure

/mnt/project/snapshots/.gitkeep
  - Empty marker file
  - Ensures snapshots/ directory exists in repo even though contents are ignored
```

---

## Data Flow

### 311 Data Pipeline
1. **Source:** https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query
2. **Fetch:** `pull_311.py` (runs hourly via `pull-311-data.yml`)
3. **Store:** `snapshots/311_requests_YYYYMMDDTHHMMSSZ.json` (timestamped, committed to repo)
4. **Latest:** `snapshots/311_requests_latest.json` (updated file for dashboard consumption)
5. **Consume:** `rebuild_site.py`
6. **Output:** `docs/311_complaints.geojson` + dashboard HTML
7. **Deploy:** GitHub Pages (https://steveneedham.github.io/columbus-micromobility-data)

### GBFS Data Pipeline
1. **Source:** Veo (https://cluster-prod.veoride.com/api/shares/name/cbs/gbfs/...)
              Spin (https://mds.bird.co/gbfs/v2/public/provider/spin/columbus/...)
2. **Fetch:** `Veo_Spin_CBS_GBFS_Extract.ipynb` (notebook, run via Papermill in `pull-gbfs-data.yml`)
3. **Store:** `snapshots/columbus_scooters_YYYYMMDDTHHMMSSZ.csv` (timestamped, committed to repo)
4. **Consume:** `rebuild_site.py`
5. **Output:** `docs/gbfs_vehicles.geojson` + dashboard HTML
6. **Deploy:** GitHub Pages (automatic)

---

## Schedule

| Task | Frequency | Cron | UTC Times |
|------|-----------|------|-----------|
| Pull 311 Data | Every hour | `0 * * * *` | 00:00, 01:00, ..., 23:00 |
| Pull GBFS Data | 2x daily | `0 8 * * *` | 08:00 (8am) |
| Pull GBFS Data | 2x daily | `0 20 * * *` | 20:00 (8pm) |
| Rebuild Site | On demand | workflow_call | ~1-2 min after 311 or GBFS pull |

---

## GitHub Setup (Required Before Deployment)

### Step 1: Enable GitHub Actions
1. Go to repo → **Settings** → **Actions**
2. Select "Allow all actions and reusable workflows"
3. Verify "Workflow permissions" = "Read and write permissions"

### Step 2: Enable GitHub Pages
1. Go to repo → **Settings** → **Pages**
2. Set Source: **Deploy from a branch**
3. Select Branch: **main**, folder: **/docs**
4. Click Save
5. Wait 2 minutes for site to go live

### Step 3: First Test (Optional)
Run manually from Actions tab:
- Pull 311 Data (menu → Run workflow)
- Pull GBFS Data (menu → Run workflow)
- Rebuild Site (menu → Run workflow)

---

## Environment Variables & Secrets

**None required.** All APIs are public (no auth).

External dependencies:
- Columbus GIS API (public, read-only)
- Veo GBFS (public, read-only)
- Spin GBFS (public, read-only)
- GitHub Actions (standard Ubuntu container)
- GitHub Pages (static hosting)

---

## Failure Modes & Recovery

### If 311 fetch fails:
- Workflow logs error to GitHub Actions
- NO snapshot committed
- Rebuild NOT triggered
- Site shows stale 311 data
- **Recovery:** Manual run from Actions tab or wait for next hourly trigger

### If GBFS fetch fails:
- Papermill logs error
- NO snapshot committed
- Rebuild NOT triggered
- Site shows stale GBFS data
- **Recovery:** Manual run or wait for next scheduled time

### If rebuild fails:
- Error in GitHub Actions log
- Site NOT updated
- Previous version remains live
- **Recovery:** Check logs, fix error in rebuild_site.py, commit fix, re-run

---

## Quick Reference: File Contents

### pull-311-data.yml
- Trigger: `schedule: - cron: '0 * * * *'` (every hour)
- Runs: `python scripts/pull_311.py`
- Commits: `snapshots/311_requests_*.json`
- Triggers: `rebuild-site.yml` via workflow_call

### pull-gbfs-data.yml
- Trigger: `schedule: - cron: '0 8 * * *'` AND `- cron: '0 20 * * *'` (8am & 8pm UTC)
- Runs: `papermill Veo_Spin_CBS_GBFS_Extract.ipynb /dev/null`
- Commits: `snapshots/columbus_scooters_*.csv` + `plots/`
- Triggers: `rebuild-site.yml` via workflow_call

### rebuild-site.yml
- Trigger: `workflow_dispatch` (called by above)
- Runs: `python scripts/rebuild_site.py`
- Generates: `docs/index.html`, `docs/gbfs_vehicles.geojson`, `docs/311_complaints.geojson`
- Deploys: GitHub Pages (automatic via `actions/deploy-pages@v2`)

### pull_311.py
```
API_URL = "https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query"
PARAMS = {"where": "REQUEST_TYPE = 'Shared Electric Bike & Scooters'", ...}
Output: snapshots/311_requests_YYYYMMDDTHHMMSSZ.json
```

### rebuild_site.py
```
load_latest_311() → snapshots/311_requests_latest.json
load_latest_gbfs() → snapshots/columbus_scooters_*.csv
generate_gbfs_geojson() → docs/gbfs_vehicles.geojson
generate_311_geojson() → docs/311_complaints.geojson
generate_dashboard_html() → docs/index.html
```

---

## Repository Structure (After Deployment)

```
columbus-micromobility-data/
├── .github/
│   └── workflows/
│       ├── pull-311-data.yml        ✓ CREATED
│       ├── pull-gbfs-data.yml       ✓ CREATED
│       └── rebuild-site.yml         ✓ CREATED
├── scripts/
│   ├── pull_311.py                  ✓ CREATED
│   └── rebuild_site.py              ✓ CREATED
├── snapshots/
│   ├── .gitkeep                     ✓ CREATED
│   ├── 311_requests_*.json          (auto-generated hourly)
│   └── columbus_scooters_*.csv      (auto-generated 2x daily)
├── docs/                            (auto-generated)
│   ├── index.html
│   ├── gbfs_vehicles.geojson
│   └── 311_complaints.geojson
├── plots/                           (auto-generated from notebook)
│   ├── battery_percentage_distribution.png
│   ├── range_distribution.png
│   └── vehicle_type_distribution.png
├── README.md                        ✓ CREATED
├── SETUP.md                         ✓ CREATED
├── AUTOMATION_MANIFEST.md           ✓ CREATED
└── .gitignore                       ✓ CREATED
```

---

## Next Steps Checklist

- [ ] Copy all files from `/mnt/project/` to your GitHub repo
- [ ] Push to `main` branch
- [ ] Enable GitHub Actions in repo Settings
- [ ] Enable GitHub Pages in repo Settings (deploy from `/docs`)
- [ ] Manually test: Pull 311 Data workflow
- [ ] Manually test: Pull GBFS Data workflow
- [ ] Manually test: Rebuild Site workflow
- [ ] Verify site live at https://steveneedham.github.io/columbus-micromobility-data
- [ ] Confirm workflows run on schedule (wait 1 hour for 311, 8am/8pm for GBFS)

---

## How to Reference This in Future Chats

**Paste this entire document** into any new Claude chat, then say:

> "This is the state of my Columbus micromobility data project. I need to [whatever task]. Here's what exists..."

That way, the new Claude instance will have the full context and won't redo work or make inconsistent changes.

---

**All files are also available at:** `/mnt/user-data/outputs/`

