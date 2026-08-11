#!/usr/bin/env python3
"""Build data-events.json: events cross-referenced to the neighborhood micro-sites.

Source is the events workbook, which records a venue Area per event. Areas are
mapped to micro-site slugs by name, not by coordinate: the claim on the page is
that an event tends to *impact* a neighborhood, which is what a venue area
supports. A venue sitting just outside a boundary polygon still drives trips
through it.

Areas with no corresponding micro-site (the Ohio Expo Center, out-of-town
venues) are dropped rather than forced into the nearest neighborhood.

Re-run after updating the workbook:
    python3 scripts/build_events_data.py
"""
import datetime as dt
import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
WORKBOOK = ROOT / "Claude Forecast 0 Columbus_Micromobility_Events_Historical_2024-2026.xlsx"
OUTPUT = ROOT / "data-events.json"

# Venue area, as recorded in the workbook -> micro-site slug.
AREA_TO_SLUG = {
    "Arena District": "downtown",
    "Nationwide Arena": "downtown",
    "Downtown Columbus": "downtown",
    "Greater Columbus Convention Center": "downtown",
    "Greater Columbus Convention Center + downtown": "downtown",
    "University District": "the-ohio-state-university",
    "Ohio Stadium": "the-ohio-state-university",
    "Schottenstein Center": "the-ohio-state-university",
    "Newport Music Hall": "the-ohio-state-university",
    "Short North Arts District": "short-north",
    "Goodale Park / Short North": "short-north",
}

# Recorded in the workbook but deliberately unmapped, with the reason.
UNMAPPED = {
    "Ohio Expo Center": "no micro-site covers the fairgrounds",
    "Cleveland (not Columbus)": "outside Columbus",
}


def cell(row, idx, name):
    value = row[idx[name]]
    return value if value is not None else ""


def main():
    if not WORKBOOK.exists():
        sys.exit(f"workbook not found: {WORKBOOK}")

    workbook = openpyxl.load_workbook(WORKBOOK, data_only=True)
    rows = list(workbook["Events"].iter_rows(values_only=True))
    idx = {header: i for i, header in enumerate(rows[0])}

    today = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
    by_slug = {}
    unmapped_areas = {}
    skipped_no_date = 0

    for row in rows[1:]:
        area = cell(row, idx, "Area")
        slug = AREA_TO_SLUG.get(area)
        if slug is None:
            unmapped_areas[area] = unmapped_areas.get(area, 0) + 1
            continue

        date = row[idx["Date"]]
        if not isinstance(date, dt.datetime):
            skipped_no_date += 1
            continue

        attendance = row[idx["Est. Attendance"]]
        try:
            attendance = int(attendance) if attendance not in (None, "") else None
        except (TypeError, ValueError):
            attendance = None

        entry = {
            "date": date.date().isoformat(),
            "event": str(cell(row, idx, "Event")),
            "category": str(cell(row, idx, "Category")),
            "venue": str(cell(row, idx, "Venue")),
            "area": str(area),
            "attendance": attendance,
            "status": str(cell(row, idx, "Status")),
            "source": str(cell(row, idx, "Source")),
        }
        bucket = by_slug.setdefault(slug, {"upcoming": [], "past": []})
        bucket["upcoming" if date >= today else "past"].append(entry)

    neighborhoods = {}
    for slug, bucket in by_slug.items():
        upcoming = sorted(bucket["upcoming"], key=lambda e: e["date"])
        past = sorted(bucket["past"], key=lambda e: e["date"])
        categories = {}
        for entry in past + upcoming:
            categories[entry["category"]] = categories.get(entry["category"], 0) + 1
        neighborhoods[slug] = {
            "upcoming": upcoming,
            "recorded_total": len(past) + len(upcoming),
            "recorded_past": len(past),
            "top_categories": [list(pair) for pair in sorted(categories.items(), key=lambda kv: -kv[1])[:4]],
            "areas": sorted({e["area"] for e in past + upcoming}),
        }

    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source_workbook": WORKBOOK.name,
        "method": (
            "Events are cross-referenced to neighborhoods by the venue area recorded "
            "in the source workbook, not by coordinate. A listing means the event "
            "tends to drive trips through the neighborhood, not that the venue sits "
            "inside the boundary polygon."
        ),
        "caveat": (
            "The workbook is an AI-compiled event list carrying its own status "
            "column and a Data Gaps sheet. Scheduled, Projected and Unconfirmed "
            "entries are not equally certain and are labelled as such."
        ),
        "unmapped_areas": {a: UNMAPPED.get(a, "no micro-site") for a in sorted(unmapped_areas)},
        "neighborhoods": neighborhoods,
    }

    # This runs hourly alongside the 311 pull. Writing unconditionally would
    # change generated_at every hour and push a timestamp-only commit even when
    # nothing about the events actually moved, so only write on a real change.
    def comparable(doc):
        # Serialize before comparing: a tuple in the payload and the list it
        # becomes after a JSON round-trip are not equal as Python objects.
        return json.dumps(
            {k: v for k, v in doc.items() if k != "generated_at"},
            sort_keys=True,
        )

    changed = True
    if OUTPUT.exists():
        try:
            changed = comparable(json.loads(OUTPUT.read_text())) != comparable(payload)
        except (json.JSONDecodeError, OSError, AttributeError):
            changed = True

    if not changed:
        print(f"{OUTPUT.name} unchanged, leaving it alone")
        return

    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"wrote {OUTPUT.name}")
    for slug, info in sorted(neighborhoods.items()):
        print(f"  {slug:28} {info['recorded_total']:4} recorded, {len(info['upcoming']):3} upcoming")
    for area, count in sorted(unmapped_areas.items()):
        print(f"  unmapped: {area} ({count}) — {UNMAPPED.get(area, 'no micro-site')}")
    if skipped_no_date:
        print(f"  skipped {skipped_no_date} rows with no usable date")


if __name__ == "__main__":
    main()
