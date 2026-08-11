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


MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# How far back the "recent" list reaches.
RECENT_DAYS = 120


def format_season(months):
    """Render the months a category occurs in, e.g. 'Oct-Apr' or 'Feb-Oct'.

    Runs are merged around the year boundary so a winter sport reads as one
    season rather than two fragments at either end of the calendar.
    """
    if not months:
        return ""
    if len(months) == 12:
        return "Year-round"
    present = set(months)
    runs = []
    for month in sorted(present):
        if runs and month == runs[-1][1] + 1:
            runs[-1][1] = month
        else:
            runs.append([month, month])
    # A season crossing New Year shows up as a run ending in December and
    # another starting in January; join them.
    if len(runs) > 1 and runs[0][0] == 1 and runs[-1][1] == 12:
        runs[0][0] = runs[-1][0]
        runs.pop()
    return ", ".join(
        MONTH_NAMES[a - 1] if a == b else f"{MONTH_NAMES[a - 1]}-{MONTH_NAMES[b - 1]}"
        for a, b in runs
    )


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
        every = past + upcoming

        # Profile the kinds of event that recur here, rather than only listing
        # individual dates. This is what makes the section describe a pattern of
        # demand instead of a schedule.
        grouped = {}
        for entry in every:
            grouped.setdefault(entry["category"], []).append(entry)

        span_days = (dt.date.fromisoformat(every[-1]["date"])
                     - dt.date.fromisoformat(every[0]["date"])).days or 1
        span_years = span_days / 365.25

        drivers = []
        for category, entries in grouped.items():
            crowds = sorted(e["attendance"] for e in entries if e["attendance"])
            months = sorted({int(e["date"][5:7]) for e in entries})
            # Each row is one recorded date. A MiLB row stands for a multi-game
            # homestand, so these are dates on the calendar rather than a claim
            # about how many days of activity each one produces.
            dates = len({e["date"] for e in entries})
            drivers.append({
                "category": category,
                "count": len(entries),
                "event_dates": dates,
                "dates_per_year": round(dates / span_years, 1) if span_years else None,
                "share_pct": round(100 * len(entries) / len(every)),
                "median_attendance": crowds[len(crowds) // 2] if crowds else None,
                "total_attendance": sum(crowds) if crowds else None,
                "attendance_known": len(crowds),
                "season": format_season(months),
                "venues": sorted({e["venue"] for e in entries})[:3],
                "first": entries[0]["date"],
                "last": entries[-1]["date"],
            })
        drivers.sort(key=lambda d: -d["count"])

        recent_cutoff = (today - dt.timedelta(days=RECENT_DAYS)).date().isoformat()
        neighborhoods[slug] = {
            "drivers": drivers,
            "recent": [e for e in past if e["date"] >= recent_cutoff][-6:][::-1],
            "upcoming": upcoming,
            "recorded_total": len(every),
            "recorded_past": len(past),
            "recorded_from": every[0]["date"] if every else None,
            "recorded_to": every[-1]["date"] if every else None,
            "top_categories": [[d["category"], d["count"]] for d in drivers[:4]],
            "areas": sorted({e["area"] for e in every}),
            "venues": sorted({e["venue"] for e in every}),
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
