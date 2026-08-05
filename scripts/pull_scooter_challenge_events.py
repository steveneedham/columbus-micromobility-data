#!/usr/bin/env python3
"""
Pull anonymized "analyze_costs" events from PostHog and build the ticker
feed for the Scooter Challenge app
(scooter-challenge/src/constants/submissions.json).

Only the anonymized properties already sent to PostHog client-side are
used here -- no addresses, no exact coordinates, no receipt amounts. See
scooter-challenge/src/utils/analytics.js for what actually gets captured.

Requires POSTHOG_PROJECT_ID and POSTHOG_PERSONAL_API_KEY environment
variables (GitHub repo secrets in CI). Exits quietly (no error) if either
is unset, so this is safe to leave enabled before those secrets exist.
Run by .github/workflows/pull-scooter-challenge-events.yml.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "scooter-challenge" / "src" / "constants" / "submissions.json"
POSTHOG_HOST = "https://us.i.posthog.com"
MAX_ENTRIES = 40
MAX_EVENTS_FETCHED = 500


def fetch_events(project_id, api_key):
    events = []
    url = f"{POSTHOG_HOST}/api/projects/{project_id}/events/"
    params = {"event": "analyze_costs", "limit": 100}
    headers = {"Authorization": f"Bearer {api_key}"}
    while url and len(events) < MAX_EVENTS_FETCHED:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        payload = response.json()
        events.extend(payload.get("results", []))
        url = payload.get("next")
        params = None  # "next" is already a full URL with querystring
    return events


def build_message(properties):
    neighborhoods = properties.get("neighborhoods") or []
    location = neighborhoods[0] if neighborhoods else "Columbus"
    winner_raw = properties.get("winner")
    savings = properties.get("savings_usd")
    if not winner_raw or savings is None:
        return None
    winner = str(winner_raw).capitalize()
    try:
        savings = float(savings)
    except (TypeError, ValueError):
        return None
    return f"{location} rider: {winner} saves ${savings:.2f}/month"


def main():
    project_id = os.environ.get("POSTHOG_PROJECT_ID")
    api_key = os.environ.get("POSTHOG_PERSONAL_API_KEY")
    if not project_id or not api_key:
        print("POSTHOG_PROJECT_ID / POSTHOG_PERSONAL_API_KEY not set; skipping.", file=sys.stderr)
        sys.exit(0)

    events = fetch_events(project_id, api_key)
    events.sort(key=lambda event: event.get("timestamp", ""), reverse=True)

    messages = []
    seen = set()
    for event in events:
        message = build_message(event.get("properties", {}))
        if not message or message in seen:
            continue
        seen.add(message)
        messages.append(message)
        if len(messages) >= MAX_ENTRIES:
            break

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "PostHog analyze_costs events, anonymized (see scooter-challenge/src/utils/analytics.js)",
        "count": len(messages),
        "messages": messages,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {len(messages)} ticker messages to {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
