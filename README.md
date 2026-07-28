# Columbus Fleet Ops — Automated Operations Pipeline
### Six months of AI-assisted micromobility operations (Jan–Jun 2026)

This repo documents an automated operations system I built and ran for the Bird/Spin shared-scooter fleet in Columbus, Ohio. Twice a day, an AI agent pulled live data from the fleet data warehouse (Presto via Metabase), analyzed coverage and workload, rebuilt a suite of six cross-linked HTML dashboards, deployed them to a static host, and sent targeted iMessage updates to each stakeholder — the ops lead, the team lead, and two external operator partners.

The system is no longer running as a daily live pipeline. What's here is a retrospective: the architecture, the code and query patterns that held up, real (sanitized) output examples, and the operational lessons.

---

## Architecture

```
Presto / Metabase  ──►  Analysis layer (AI agent, twice daily)
  scans, tasks,           coverage classification, schedule inference,
  bounties, vehicles      anomaly detection, partner gap evaluation
                                   │
          ┌────────────────────────┼──────────────────────────┐
          ▼                        ▼                          ▼
  6 static HTML dashboards   JSON snapshot            iMessage per audience
  (Surge deploy)             (state across runs)      (4 recipients, tone rules)
          │                        │
          ▼                        ▼
  Notion hub + partner       Feedback loop: notes widget →
  reports                    JSON export → read at next run's pre-flight
```

**Outputs per run:** main ops dashboard · GPS scan map · two partner-facing reports · schedule comparison view · worker registry · OOB rebalance worklists (xlsx) + self-contained SVG map.

---

## What it did

### 1. Coverage-gap detection (schedule vs. presence)
Three signals cross-referenced every run: the official Homebase schedule (ground truth, parsed from a PDF export), a schedule *inferred* from 14 days of scan patterns, and live scan activity today. Each run classified the day 🟢 COVERED / 🟡 AT RISK / 🔴 GAP DETECTED and alerted only on the last two. A five-type discrepancy taxonomy (new/returning worker, unscheduled worker, day mismatch, time mismatch, scheduled-but-inactive) caught schedule drift automatically.

### 2. Partner accountability without adversarial alerts
External operators set their own schedules — a scan gap on a low-demand day is planned downtime, not a no-show. Alert triggers were gated on demand context: no alert unless bounty volume made the gap a missed opportunity. Messages used collaborative tone rules, deduped via a persisted `alert_sent_today` flag, and were suppressed entirely on off-schedule runs. See [examples/imessage-alerts.md](examples/imessage-alerts.md).

### 3. Commitment tracking
The core KPI: percentage of battery swaps (target 100%) and rebalances (target ≥50%) completed by external operators, computed daily from task completions and rendered as color-thresholded progress bars. See [sql/task-completions-external-share.sql](sql/task-completions-external-share.sql).

### 4. Out-of-bounds rebalance pipeline
Twice daily: pull every vehicle with a **same-day** GPS fix, run an exclusion cascade (active bounty → in-bounds polygon → launched nest polygons), and emit xlsx worklists with per-vehicle deep links plus a fully self-contained inline-SVG map — no CDN dependencies, so it renders in any context including chat previews. See [sql/fresh-gps-oob-export.sql](sql/fresh-gps-oob-export.sql).

### 5. Human-in-the-loop feedback across autonomous runs
Each dashboard carried a notes widget (localStorage, zero backend). Notes exported to JSON, were read at the next run's pre-flight step, and re-rendered as "prior run notes" — a feedback loop between a human and an autonomous agent with no infrastructure at all. See [snippets/feedback-widget.html](snippets/feedback-widget.html).

---

## What we learned

**Scans are attendance, not performance.** Scan counts systematically underrepresent workers who skip scanning before resolving tasks — one field worker showed 13 scans against 31 confirmed task completions in the same window. Every presence signal was cross-referenced against the task table before any conclusion.

**Demand context must gate alerts.** Early versions flagged every partner scan gap. That erodes trust fast when the partner simply wasn't scheduled. Gating alerts on "was there meaningful work available?" turned the alert channel from noise into signal.

**Distrust convenient documents.** Two externally-produced audit spreadsheets were proven unreliable — one showed zero activity on a day with confirmed field work; another introduced phantom workers. Policy: the warehouse is canonical, conflicts resolve toward it, and missing date ranges are flagged as pipeline gaps rather than assumed to be zero activity.

**Identity resolution needs a human channel.** Day-of-week pattern inference misbucketed multiple workers; database email evidence and human confirmation were the only reliable sources. The worker registry carried explicit confidence states (Confirmed / Unconfirmed) and a "Needs ID" banner for high-activity unknowns.

**GPS freshness is correctness.** A rebalance worklist built on stale coordinates sends field workers to places vehicles no longer are. The vehicle query joins the dimension table for the same-day GPS fix rather than trusting the current-state snapshot.

**Static HTML + chat messages beat BI logins.** Field operators reliably opened a short link from a text message. Nobody logged into a BI tool. Distribution was: static site, Bitly permalinks, per-audience texts with per-recipient tone rules.

**Admin accounts distort field metrics.** The ops lead's own account was excluded from every field-action query by standing policy.

---

## Repo contents

| Path | Contents |
|---|---|
| `sql/` | Annotated production queries (Presto dialect) |
| `snippets/` | Feedback widget, reusable patterns |
| `examples/` | Sanitized message examples, partner report excerpts, run snapshot JSON schema |
| `sanitized-dashboards/` | Sanitized full-page copies of all 8 live dashboard/report pages (names, emails, UUIDs, and internal admin links replaced with placeholders) |
| `screenshots/` | Dashboard and map captures |

All personal identifiers (names, phone numbers, emails, account UUIDs, internal admin URLs) have been removed or replaced with placeholders. Fleet-level data shown is representative.
