# Setup & Deployment Guide

## For Your Own Fork

### Step 1: Enable GitHub Actions

1. Go to your forked repo **Settings** → **Actions**
2. Ensure "Actions permissions" is set to **Allow all actions and reusable workflows**
3. Verify **Workflow permissions** is set to **Read and write permissions**

### Step 2: Enable GitHub Pages

1. Go to **Settings** → **Pages**
2. Set **Source** to: Deploy from a branch
3. Select **Branch**: `main` and folder `/docs`
4. Click Save
5. Wait ~2 minutes for the site to go live at `https://<your-username>.github.io/columbus-micromobility-data`

### Step 3: First Manual Run (Optional)

To test before waiting for the schedule:

```bash
# Fetch 311 data
python scripts/pull_311.py

# Fetch GBFS data (if you have the notebook)
papermill Veo_Spin_CBS_GBFS_Extract.ipynb -

# Rebuild the site
python scripts/rebuild_site.py

# Commit
git add snapshots/ docs/
git commit -m "Initial data pull and site build"
git push
```

Or use the GitHub UI:
1. Go to **Actions** tab
2. Select **Pull 311 Data** workflow
3. Click **Run workflow** → **Run workflow**

Repeat for **Pull GBFS Data** and **Rebuild Site** workflows.

## Automation Schedule

Once deployed, the workflows run on this schedule:

| Workflow | Schedule | Frequency |
|----------|----------|-----------|
| Pull 311 Data | `0 * * * *` | Every hour at :00 |
| Pull GBFS Data | `0 8 * * *` | Daily at 8am UTC |
| Pull GBFS Data | `0 20 * * *` | Daily at 8pm UTC |
| Rebuild Site | On demand (triggered by above) | Cascading |

**Times in UTC.** Convert to your timezone:
- 8am UTC = 3am EST / 2am CST / 12am PST
- 8pm UTC = 3pm EST / 2pm CST / 12pm PST

## Customization

### Change the 311 Filter

Edit `scripts/pull_311.py` line 20, the `PARAMS` dict. The `where` clause controls what gets fetched. Current: `REQUEST_TYPE = 'Shared Electric Bike & Scooters'`

Examples:
```python
# All service requests (no filter)
"where": "1=1",

# Only open complaints
"where": "REQUEST_TYPE = 'Shared Electric Bike & Scooters' AND STATUS = 'Open'",

# Specific date range
"where": "REPORTED_DATE >= 1704067200000 AND REPORTED_DATE <= 1706745599000",  # Unix ms
```

### Change the GBFS Schedule

Edit `.github/workflows/pull-gbfs-data.yml` line 6-7:
```yaml
schedule:
  - cron: '0 8 * * *'   # 8am UTC — change the first 0 to a different hour
  - cron: '0 20 * * *'  # 8pm UTC — change 20 to a different hour
```

Cron syntax: `minute hour day_of_month month day_of_week`
- `0 * * * *` = every hour
- `0 0 * * *` = daily at midnight UTC
- `0 9,21 * * *` = twice daily at 9am and 9pm UTC

### Extend the Dashboard

`scripts/rebuild_site.py` generates a basic HTML scaffold. To enhance it:

1. Edit the `generate_dashboard_html()` function to add charts, filters, or custom styling
2. Edit the `save_geojson()` output to add properties you want to visualize
3. Update the Leaflet initialization in the HTML to consume those properties

The GeoJSON files are already saved to `/docs/`:
- `gbfs_vehicles.geojson` — Spin and Veo vehicles
- `311_complaints.geojson` — 311 complaints by status

### Store Historical Data

The current setup overwrites `/snapshots/` on each pull. To keep a 30-day rolling archive:

```python
# In pull_311.py and rebuild_site.py, keep timestamped files:
# snapshots/311_requests_20260802T091411Z.json
# snapshots/columbus_scooters_20260802T085430Z.csv

# Add a cleanup step to the workflows to delete files older than 30 days:
- name: Clean up old snapshots
  run: |
    find snapshots/ -type f -mtime +30 -delete
```

## Troubleshooting

### Workflow Fails at "Fetch 311 data"

Check the Actions tab for error logs. Common issues:
- **Request timeout**: Columbus GIS API is slow or offline. It sometimes takes 10–30s to respond.
- **API changed**: The endpoint or parameter format changed. Verify at `https://gis.columbus.gov/coc311map/`
- **No snapshots directory**: Run `mkdir -p snapshots` locally and commit `.gitkeep`

### Workflow Fails at "Run GBFS extraction notebook"

- **Papermill error**: The notebook `Veo_Spin_CBS_GBFS_Extract.ipynb` is missing or broken. Check it exists at repo root.
- **Missing dependencies**: The workflow installs pandas, requests, and papermill. If you need more, add to the `pip install` line.
- **Notebook kernel**: Ensure the notebook uses Python 3.11 (or the version in the workflow).

### Site Doesn't Update

1. Check the **Actions** tab for failed runs
2. Verify GitHub Pages is enabled in **Settings** → **Pages**
3. Check that `/docs/` directory exists and has `index.html`
4. GitHub Pages can take 1–2 minutes to redeploy after a push

### 311 Data Always Empty

Verify the Columbus GIS API is responding:
```bash
curl "https://maps2.columbus.gov/arcgis/rest/services/Applications/ServiceRequests/MapServer/0/query?where=REQUEST_TYPE%20%3D%20%27Shared%20Electric%20Bike%20%26%20Scooters%27&f=json&resultRecordCount=1"
```

If it returns an error, the API may have changed or gone offline.

## Production Checklist

- [ ] GitHub Actions enabled
- [ ] GitHub Pages enabled and deployed to `/docs`
- [ ] First manual run successful (all three workflows)
- [ ] 311 and GBFS data appearing in `/snapshots/`
- [ ] Dashboard live at `https://<username>.github.io/columbus-micromobility-data`
- [ ] Workflows scheduled and running on cron
- [ ] Error notifications set up (optional: enable email alerts in Actions)

## Questions?

Check the repo README for data schema and civic context. For technical issues, review workflow logs in the **Actions** tab.
