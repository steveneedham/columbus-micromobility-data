#!/usr/bin/env python3
"""
Rebuild data-311.json (the live site's 311 layer) from the latest
snapshots/311_requests_latest.json pull, and sync the same payload into
index.html's embedded #data-311 script tag (what the dashboard actually
renders its stats from). Run by .github/workflows/pull-311-data.yml
after each hourly fetch.

Note: the source 311 API has no free-text description field, so
complaint_type cannot be classified automatically (ada_ramp / sidewalk_block
/ etc). Every record is written as "unclassified", which the site's
priority heuristic treats as standard priority.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = ROOT / "snapshots" / "311_requests_latest.json"
OUTPUT_PATH = ROOT / "data-311.json"
INDEX_HTML_PATH = ROOT / "index.html"


def epoch_ms_to_iso(value):
    if value in (None, ""):
        return ""
    return (
        datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


def transform(record):
    return {
        "source_id": record.get("CASE_ID"),
        "city": (record.get("CITY") or "columbus").lower(),
        "operator": "unknown",
        "complaint_type": "unclassified",
        "descriptor": record.get("REQUEST_TYPE"),
        "address": record.get("STREET"),
        "latitude": record.get("LATITUDE"),
        "longitude": record.get("LONGITUDE"),
        "zone_id": record.get("COLUMBUSCOMMUNITY") or record.get("AREACOMMISSION") or "",
        "reported_at": epoch_ms_to_iso(record.get("REPORTED_DATE")),
        "status": (record.get("STATUS") or "").lower().replace(" ", "_"),
        "source_status": record.get("STATUS") or "",
        "source_status_at": epoch_ms_to_iso(record.get("STATUS_DATE")),
        "source_updated_at": epoch_ms_to_iso(record.get("REQUEST_MODIFIED")),
        "source_name": "City of Columbus 311 public map",
        "source_url": "https://gis.columbus.gov/coc311map/",
        "council_district": record.get("COUNCILDISTRICT") or "",
        "zip": record.get("ZIP") or "",
    }


def replace_embedded_script(html, element_id, new_json_text):
    pattern = re.compile(
        rf'(<script type="application/json" id="{element_id}">\n).*?(\n</script>)',
        re.DOTALL,
    )
    new_html, count = pattern.subn(lambda m: m.group(1) + new_json_text + m.group(2), html, count=1)
    if count != 1:
        raise RuntimeError(f"Expected exactly one #{element_id} script block, found {count}")
    return new_html


def sync_index_html(payload):
    """The dashboard renders its 311 stats from the #data-311 script tag
    baked into index.html at load time, not from data-311.json directly
    (that file is only polled client-side for a "refresh available"
    notification). Keep the embedded copy current too."""
    html = INDEX_HTML_PATH.read_text()
    html = replace_embedded_script(html, "data-311", json.dumps(payload, indent=2))
    INDEX_HTML_PATH.write_text(html)


def main():
    if not SNAPSHOT_PATH.exists():
        print(f"No snapshot found at {SNAPSHOT_PATH}", file=sys.stderr)
        sys.exit(1)

    snapshot = json.loads(SNAPSHOT_PATH.read_text())
    raw_records = snapshot.get("records", [])

    seen_ids = set()
    records = []
    duplicate_count = 0
    invalid_count = 0

    for raw in raw_records:
        case_id = raw.get("CASE_ID")
        if not case_id or raw.get("LATITUDE") is None or raw.get("LONGITUDE") is None:
            invalid_count += 1
            continue
        if case_id in seen_ids:
            duplicate_count += 1
            continue
        seen_ids.add(case_id)
        records.append(transform(raw))

    output = {
        "fetched_at": snapshot.get("fetched_at"),
        "source": snapshot.get("source"),
        "record_count": len(records),
        "duplicate_count": duplicate_count,
        "invalid_count": invalid_count,
        "records": records,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")
    sync_index_html(output)
    print(
        f"Wrote {OUTPUT_PATH.name} and synced index.html: {len(records)} records "
        f"({duplicate_count} duplicates, {invalid_count} invalid skipped)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
