# Festival Event Microsite Setup

Real-time micromobility monitoring for Columbus festivals and multi-day events.

## Adding a Festival Event to Registry

Festival events require **geofence center coordinates + radius** for geographic filtering. Unlike civic org microsites that use boundary.geojson files, festival events use Turf.js distance calculations.

### 1. Add Festival to data-events-registry.json

```json
{
  "id": "festival-slug",
  "name": "Festival Name",
  "date": "2026-06-15",
  "category": "Festival",
  "venue": "Event Location/Park",
  "area": "Downtown or specific neighborhood",
  "hero_image": "festival-slug.jpg",
  "geofence": {
    "center": [longitude, latitude],
    "radius_meters": 1500
  },
  "operators": ["Veo", "Spin"],
  "monitoring_start": "2026-06-08",
  "monitoring_end": "2026-06-22",
  "expected_attendance": 50000
}
```

### 2. Geofence Coordinates

Festival geofences use **center point + radius** (distance-based filtering):

- **center**: `[longitude, latitude]` (decimal degrees, standard geographic format)
- **radius_meters**: Search radius in meters (typical: 1000-2000m for city festivals)

**Finding Center Coordinates:**
1. Use Google Maps or OpenStreetMap
2. Find festival venue/main area
3. Right-click → coordinates (format: decimal, not DMS)
4. Example: Downtown (39.9612, -82.9988)

**Typical Festival Radii:**
- Small neighborhood festival: 500-800m
- Mid-size park festival: 1000-1500m
- Large city-wide festival: 1500-3000m

### 3. Event Dates

- **date**: Day event occurs (for display)
- **monitoring_start**: 1 week before or earlier (advance traffic)
- **monitoring_end**: 1 week after (cleanup period)
- **Example**: Festival on June 15
  - monitoring_start: June 8
  - monitoring_end: June 22

### 4. Add Hero Image

Place image in assets directory:

```
assets/hero/{festival-slug}.jpg
```

Image requirements:
- JPG format preferred
- Landscape aspect ratio (4:3 or 16:9)
- 800px width minimum
- Same CSS filters applied (grayscale, contrast, brightness, blur, opacity)

### 5. Regenerate Microsites

After adding to registry, regenerate all event microsites:

```bash
node generate-event-microsites.js
```

This creates:
- `micro-sites/events/{festival-slug}/index.html`

## Festival vs. Sports Events

### Key Differences

**Sports Events** (Current)
- Single game on specific date
- Fixed venue (stadium)
- Defined geofence around venue
- Attendance from team data

**Festival Events** (Pattern)
- Multi-day event
- May span entire neighborhood/area
- Larger geofence radius (covers festival area + parking/transit)
- Higher expected attendance
- Complaint window = entire event duration (not just 24 hours)

### Registry Example: Comfest

```json
{
  "id": "comfest",
  "name": "Comfest (Community Festival)",
  "date": "2026-06-27",
  "category": "Festival",
  "venue": "Goodale Park",
  "area": "Short North / Goodale Area",
  "hero_image": "comfest.jpg",
  "geofence": {
    "center": [39.9850, -83.0100],
    "radius_meters": 1800
  },
  "operators": ["Veo", "Spin"],
  "monitoring_start": "2026-06-20",
  "monitoring_end": "2026-07-04",
  "expected_attendance": 500000
}
```

## How Festival Data Filtering Works

1. **Load geofence center + radius** from EVENT_DATA
2. **For each vehicle**: Calculate distance to geofence center using Turf.js
3. **For each 311 complaint**: 
   - Check date is within event window (start to end date)
   - Check distance to geofence center <= radius_meters
4. **Display metrics** for vehicles and complaints matching both filters

## Complaint Window in Festivals

**Sports Events**: Last 24 hours only
**Festival Events**: Entire monitoring window (start_date to end_date)

This captures:
- Advance setup (traffic congestion)
- Event day (peak vehicle deployment)
- Cleanup period (final adjustments)

## Common Festival Locations & Geofences

### Downtown Festivals
- Center: [39.9612, -82.9988] (Civic Center area)
- Radius: 1500-2000m
- Covers: Streets, parking, Transit Center

### Goodale Park Area (Short North)
- Center: [39.9850, -83.0100]
- Radius: 1800m
- Covers: Goodale Park + surrounding streets/parking

### Scioto Riverfront (Bicentennial Park)
- Center: [39.9571, -83.1088]
- Radius: 1200-1500m
- Covers: Park + riverfront + downtown access

### Easton Area (Northeast)
- Center: [40.0360, -82.9010]
- Radius: 1500m
- Covers: Shopping area + parking

## Files Checklist

When adding a festival microsite:

- [ ] Entry added to `data-events-registry.json`
  - [ ] Valid geofence with center + radius_meters
  - [ ] monitoring_start and monitoring_end dates set
  - [ ] Expected attendance estimated
- [ ] Regenerated microsites: `node generate-event-microsites.js`
- [ ] `micro-sites/events/{festival-slug}/index.html` created
- [ ] Hero image added to `assets/hero/{festival-slug}.jpg` (optional but recommended)
- [ ] Tested: metrics display, geofence filtering works, data updates every 60 seconds

## Troubleshooting

### No Data Showing?

1. **Check geofence center**: Verify longitude/latitude are in correct order [lng, lat]
2. **Check radius**: Ensure radius_meters is reasonable (500-3000)
3. **Check event window**: Verify event hasn't ended yet
4. **Check data files**: Ensure data-gbfs.json and data-311.json are current

### Wrong Area Being Tracked?

1. **Verify center coordinates** match actual event location
2. **Increase radius** if festival area is larger than expected
3. **Use mapping tool** to visualize geofence (find center + draw circle with radius)

### Metrics Don't Match Expected?

1. **Festival may be too early**: Data may not exist for future dates
2. **Operators not deployed yet**: Veo/Spin may not have vehicles in that area
3. **No complaints yet**: 311 data lags behind real-time
4. **Check date range**: Event window must include current date
