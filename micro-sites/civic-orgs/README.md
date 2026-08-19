# Civic Organization Microsites

Real-time micromobility and 311 complaint tracking for Columbus civic organizations.

## Adding a New Civic Organization Microsite

### 1. Create Directory Structure

```bash
mkdir micro-sites/civic-orgs/{organization-slug}
```

Example: `micro-sites/civic-orgs/downtown-business-association/`

### 2. Copy and Customize Template

```bash
cp TEMPLATE.html {organization-slug}/index.html
```

Replace placeholders in `index.html`:
- `{{CIVIC_NAME}}` - Full organization name (e.g., "Short North Civic Association")
- `{{CIVIC_SLUG}}` - URL-safe slug (e.g., "short-north-civic-association")
- `{{WEBSITE_URL}}` - Organization website URL
- `{{COVERAGE_DESCRIPTION}}` - Area description (e.g., "5th Ave (North) to Goodale St (South)...")

### 3. Add Boundary GeoJSON

**CRITICAL: Do not skip this step.** The boundary file is essential for correct data filtering.

Place `boundary.geojson` in the organization directory:

```
micro-sites/civic-orgs/{organization-slug}/boundary.geojson
```

**Format requirements:**
- Must be a valid GeoJSON FeatureCollection
- First feature's geometry will be used for filtering
- Supports Polygon or MultiPolygon types
- Coordinates in [longitude, latitude] format

**Example structure:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": { "NAME": "Organization Name" },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-83.123, 39.987],
          [-83.124, 39.986],
          ...
        ]]
      }
    }
  ]
}
```

### 4. Add Hero Image

Place hero image in assets directory:

```
assets/hero/{organization-slug}.jpg
```

Image requirements:
- JPG format recommended
- Aspect ratio: landscape (4:3 or 16:9)
- Size: 800px width minimum
- File naming: `{organization-slug}.jpg`

The image will be automatically filtered with:
- `grayscale(75%)` - removes brand colors
- `contrast(110%)` - maintains definition
- `brightness(115%)` - adjusts intensity
- `blur(1.5px)` - obscures details
- `opacity(0.85)` - subtle appearance

### 5. Verify Data Loading

The template automatically:
- Loads `boundary.geojson` from the organization directory
- Filters vehicle data using `turf.booleanPointInPolygon()`
- Filters 311 complaints by geofence and 30-day window
- Auto-refreshes data every 60 seconds
- Displays top 10 complaint categories

## How It Works

### Data Filtering

1. **Boundary Loading**: Reads `boundary.geojson` and extracts first feature's geometry
2. **Vehicle Filtering**: Checks each GBFS vehicle against boundary polygon
3. **Complaint Filtering**: Checks each 311 record against boundary AND 30-day window
4. **Display**: Renders active counts and complaint categories

### JavaScript Execution Flow

```
loadCivicData() → Fetch boundary.geojson + data-gbfs.json + data-311.json
  ↓
Parse boundary geometry (first feature)
  ↓
Loop vehicles: turf.booleanPointInPolygon(vehicle_point, boundary)
  ↓
Loop complaints: date >= thirtyDaysAgo && turf.booleanPointInPolygon(complaint_point, boundary)
  ↓
Render metrics and complaint categories
  ↓
Set 60-second auto-refresh interval
```

## Troubleshooting

### No Data Showing?

1. **Check boundary.geojson exists** in organization directory
2. **Verify GeoJSON format** - must have `features[0].geometry`
3. **Check browser console** for fetch errors (Right-click → Inspect → Console)
4. **Verify coordinates** are in [longitude, latitude] format (not [lat, lng])

### Wrong Area Being Tracked?

1. **Verify boundary.geojson** covers correct geographic area
2. **Check coordinate order** - must be [lng, lat], not [lat, lng]
3. **Use GeoJSON viewer** (geojson.io) to visualize boundary

### Metrics Not Updating?

1. **Check data files exist** at `/columbus-micromobility-data/data-gbfs.json` and `/data-311.json`
2. **Verify fetch paths** in JavaScript (relative vs absolute)
3. **Check auto-refresh** - should update every 60 seconds

## Files Checklist

When creating a new civic org microsite:

- [ ] `micro-sites/civic-orgs/{slug}/index.html` (from TEMPLATE.html)
- [ ] `micro-sites/civic-orgs/{slug}/boundary.geojson` (required for filtering)
- [ ] `assets/hero/{slug}.jpg` (optional but recommended)
- [ ] All placeholders replaced in index.html
- [ ] Tested: metrics display, data filtering works, auto-refresh functions
