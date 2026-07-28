# Columbus Micromobility Data

An independent, public-data-only look at shared-scooter operations in Columbus, Ohio — 311 complaint activity, published vehicle positions, and city policy boundaries. Built and maintained by Steven Needham as a personal project. **Not affiliated with, endorsed by, or built using data from any current or former employer** — everything here comes from public sources: the City of Columbus 311 feed, published GBFS vehicle-position data, and Columbus's published mobility policy boundaries.

## What's here

### `columbus-observer-dashboard.html`
A single self-contained HTML dashboard — no build step, no server required. Open it directly in a browser. It renders a Leaflet map of Columbus with four layers you can toggle independently:

- **311 requests** — shared bike/scooter complaints from the City's public feed, color-coded by a priority heuristic (critical / high / standard) derived from complaint type. Click a marker for source ID, address, zone, status, and a link back to the source record.
- **GBFS vehicle positions** — published Veo and Spin vehicle locations, filterable by operator and availability.
- **Cross-vendor pile-ups** — clusters of four or more vehicles from more than one operator within ~20 metres of each other, flagged as a review signal (not a confirmed violation).
- **Policy boundaries** — published no-parking, mandatory-parking, and no-ride zones.

Summary stat cards and a legend sit above the map. The dashboard is read-only: no accounts, no write-back, no tracking scripts.

### `data-311.json`, `data-gbfs.json`, `data-policy.json`
The data snapshots the dashboard is built from, pulled from the companion prototype repo [`steveneedham/311-Intel`](https://github.com/steveneedham/311-Intel). Each file documents its own source (query URL, fetch timestamp, method) inline.

**These snapshots are partial**, not the full feed — each file has an `_extraction_note` field stating exactly how much was recovered versus what the source reports. To refresh with complete data, pull the full versions directly from `311-Intel`:

| This repo | Full source in `311-Intel` |
|---|---|
| `data-311.json` | `columbus-311-current.json` |
| `data-gbfs.json` | `gbfs-vehicle-positions.json` |
| `data-policy.json` | `mobility-policy-boundaries.json` |

Swap the file contents in and reload the dashboard — no code changes needed, since it reads by the same embedded structure.

## Why this exists

This project sits alongside the market-monitoring "watch mode" work described in the rest of this repo: a lightweight, sustainable way to track the Columbus shared-mobility market using only what's publicly available — no insider access required. The framing is deliberately that of an informed outside observer, not an advocate: claims are hedged to what the data actually supports, and every figure traces back to a named public source.

## Data sources

- **311 complaints** — City of Columbus 311 public map (`gis.columbus.gov/coc311map`), filtered to "Shared Electric Bike & Scooters" requests.
- **Vehicle positions** — published GBFS feeds for Veo and Spin.
- **Policy boundaries** — Columbus's published Populus mobility-policy export (no-parking, mandatory-parking, no-ride zones).

None of this requires or uses any operator- or employer-internal system, login, or dataset.

## Evidence boundaries

- Cross-vendor proximity clusters are a spatial review signal, not a confirmed pile-up, complaint, or violation.
- Policy-boundary proximity does not establish that a boundary caused a complaint or was active at the time of the report.
- 311 status and vehicle availability reflect a single fetch timestamp (see each JSON file's `fetched_at` / `snapshot_id`) — not a live feed.

## Running locally

No install needed:

```
open columbus-observer-dashboard.html
```

or serve the folder with any static file server if your browser blocks local file access to the embedded scripts.

---

© 2026 Steven Needham. Independent project, public data only.
