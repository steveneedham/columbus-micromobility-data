# 🛴 Scooter Challenge: Public Project Specification

**Open-source research tool for personalizing micromobility operator costs**

---

## OVERVIEW

Scooter Challenge is an interactive web tool that helps residents in shared-scooter cities find the cheapest operator based on their actual riding patterns and neighborhood fleet density.

**Vision:** Residents upload recent ride receipts + their home address + frequent destinations, get a personalized cost breakdown and recommendation, then download a reusable AI skill to re-run analysis with fresh data.

**Status:** MVP specification + proof-of-concept implementation (Aug 1–7, 2026)

---

## CASE STUDY: Sample User Analysis

To validate the tool's logic, we built a case study using sample riding data from a Columbus resident (we'll call them "Sample User").

### Their Situation
- Location: Mid-density residential neighborhood
- Monthly rides: ~25
- Average ride duration: 13–15 minutes
- Riding pattern: Mix of commute and leisure

### Fleet Data (Two GBFS snapshots)
```
Operator           Citywide        Available   Local (0.25 mi)   Local Available
═════════════════════════════════════════════════════════════════════════════
Spin              1,289–1,290      1,244–1,247   2–3 vehicles       100%
Veo               2,234–2,237      2,160–2,173   4 vehicles         100%
Ratio             1.73x Veo                       1.3–2.0x Veo
```

### Cost Comparison
```
Scenario              Spin 99¢ Club    Veo VeoPlus    Winner      Savings
═════════════════════════════════════════════════════════════════════════════
20 rides/month         $52.59           $125.99      SPIN        $73.40
25 rides/month         $63.69           $157.49      SPIN        $93.80
30 rides/month         $78.39           $185.99      SPIN        $107.60

Per-ride math (13.5 min avg):
  Spin:  $2.39 flat = $0.177/minute
  Veo:   (13.5 × $0.475) + ($5.99÷rides) = $6.69/ride
```

### Recommendation
**Stay on Spin 99 Cent Club** — wins by $50–110/month. Veo's 1.73x fleet advantage doesn't offset the per-minute cost premium. Breaks even only if Veo saves 8+ minutes per ride through better availability.

---

## PRODUCT SPECIFICATION

### 🎯 Problem Statement
Most riders don't know which operator is actually cheaper for *their* riding patterns. Marketing shows per-minute rates or monthly passes, but real costs depend on frequency, ride duration, and neighborhood density. We solve this by combining:
- User's actual ride history (via receipt upload)
- Live vehicle distribution (GBFS public feeds)
- Personalized cost projection

### 📋 User Workflow

```
1. INPUT
   ↓
2. RECEIPT PARSE (manual entry for MVP)
   ↓
3. LIVE GBFS FETCH (vehicle density per location)
   ↓
4. COST CALCULATION (monthly projection)
   ↓
5. RECOMMENDATION (confidence-scored)
   ↓
6. SKILL EXPORT (Markdown → Claude/ChatGPT/Gemini)
```

### 📝 Input Form

**Section 1: Locations (required home, optional 2–3 more)**
- Home (required): address or lat/lon
- Work, grocery store, hangout place, partner's place (optional)

**Section 2: Ride History (required)**
- Operator (Spin / Veo)
- Duration (minutes)
- Cost (USD)
- Date
- *Add/remove up to 10 entries*

**Section 3: Frequency (optional)**
- "About ___ rides per month" (slider 5–50)
- Defaults to average of uploaded receipts

### 🔧 Processing Pipeline

#### 1. Receipt Parser
- Manual entry (MVP) → extract: operator, duration, cost, date
- Calculate: per-minute rate, per-ride average
- Flag outliers (rides < 2 min or > 60 min)

#### 2. Live GBFS Lookup
- Fetch Spin + Veo vehicle positions (public endpoints)
- Filter within 0.25 mi radius of each location
- Count available vehicles
- Calculate distance to nearest (each operator)

#### 3. Cost Projection
```
Spin cost = $0.99/mo + ($2.39/ride × rides/mo)
Veo cost  = $5.99/mo + ($0.475/min × avg_duration × rides/mo)
```

#### 4. Hunt Time Estimation
```
hunt_time_minutes = (distance_to_vehicle_miles × 20) + 1
Example: 0.25 mi = ~6 min to walk + mount
```

#### 5. Recommendation Logic
```
IF (Veo_cost < Spin_cost + $20_buffer)
  AND (Veo_hunt_time < Spin_hunt_time + 3_min)
  THEN recommend Veo
ELSE
  recommend Spin

Confidence = 0–100%
  80+: Clear winner, consistent data
  50–79: Close call, tradeoffs
  <50: Nearly tied, preference-based
```

### 📊 Results Card Display

**Winner Badge**
- "Operator A saves you $X/month"
- Confidence score: 0–100%

**Cost Comparison Table**
| Operator | Per Ride | Monthly Total |
|----------|----------|---------------|
| Spin | $X | $Y |
| Veo | $X | $Y |

**Location Breakdown**
- For each location: vehicle count per operator
- Hunt time estimate (if available)

**Reasoning**
- Clear explanation of which factors drove the recommendation
- Notes on data quality/confidence

### 📦 Downloadable Skill Package

**Output 1: Markdown skill** (Claude native)
- `.md` file with:
  - User's addresses + receipt data (snapshot)
  - GBFS snapshot (vehicle counts, timestamp)
  - Cost breakdown + recommendation
  - Instructions for re-running with fresh data

**Output 2: JSON results**
- Machine-readable snapshot for archival/comparison

**Output 3: Zip package** (future)
- Folder with skill + sample receipts + README

### 🌐 Website Integration

**Location:** Research Library section of micromobility dashboard  
**Card:** "🛴 Scooter Challenge — Find your best operator"  
**CTA:** "Start the Challenge"

**Page sections:**
1. **Intro + example:** Case study breakdown (sample user)
2. **Input form:** Addresses + receipt uploader + frequency slider
3. **Results:** Dynamic cost table + recommendation + confidence
4. **Download:** Skill export + instruction links (Claude/ChatGPT/Gemini)
5. **FAQ:** How is hunt time calculated? Why per-minute rates? Multi-city support?

---

## 🚀 MVP SCOPE (1-week sprint)

### Build (Aug 1–6)
- ✅ Input form (manual receipt entry, no OCR)
- ✅ Live GBFS fetch + vehicle count
- ✅ Cost calculator (flat-rate vs. per-minute)
- ✅ Recommendation engine + confidence scoring
- ✅ Results card display
- ✅ Skill export (Markdown)
- ✅ Mobile responsive
- ✅ Error handling

### Defer (Post-MVP)
- ❌ OCR receipt parsing
- ❌ Hunt time estimation (show vehicle count instead)
- ❌ ChatGPT/Gemini skill versions
- ❌ Geocoding API
- ❌ Multi-city support
- ❌ Historical trend tracking

---

## 🛠 TECH STACK

| Layer | Tech |
|-------|------|
| Frontend | React + Tailwind CSS |
| Data | Public GBFS endpoints (HTTP fetch) |
| Calculation | JavaScript (client-side) |
| Export | Markdown generator |
| Hosting | GitHub Pages / static HTML |

**No backend required for MVP** — all processing client-side, public data only.

---

## 📚 DESIGN SYSTEM

This project uses a **dark-ops visual identity** (designed for portfolio + consulting deliverables):

**Colors:**
- **Ink** (`#14171C`): Primary dark background
- **Panel** (`#1B1F27`): Secondary surfaces
- **Amber** (`#E8A33D`): "Ops" accent (operations/cost emphasis)
- **Teal** (`#4FD1C5`): "Sys" accent (systems/technical details)
- **Text** (`#EDEAE2`): Primary text on dark
- **Muted** (`#8B93A1`): Secondary text

**Typography:**
- **Fraunces** (serif): Headlines
- **Inter** (sans): Body copy
- **JetBrains Mono**: Labels, eyebrows, metadata

**Component patterns:**
- Sticky blur-nav with mono links
- Two-track accent discipline (amber vs. teal)
- Small corner radius (minimal rounding)
- Eyebrow + headline + body pattern

---

## 📅 TIMELINE

| Phase | Focus | Deadline |
|-------|-------|----------|
| Spec | Logic validation, wireframes | Day 1 |
| Core Logic | Geo utils, calculator, parser | Day 1–2 |
| GBFS | Live vehicle fetch + parsing | Day 2–3 |
| Components | Form, results, exporter | Day 3–4 |
| Export | Markdown skill generation | Day 4–5 |
| Polish & QA | Mobile, error handling, styling | Day 5–6 |
| Launch | Publish to research library | Day 7 |

---

## 🎯 SUCCESS METRICS

- Form accepts addresses, receipts, frequency without errors
- GBFS fetch returns accurate vehicle counts
- Cost calculations match manual math
- Recommendation matches observed truth (user feedback)
- 50+ residents try the tool in first month
- 60%+ download skill for re-running analysis

---

## 📖 GBFS DATA SOURCES

**Public endpoints (no auth required):**
- Spin Columbus: `https://feeds.spin.app/gbfs/v3/systems/columbus_us/vehicles`
- Veo Columbus: `https://gbfs.veo.dev/columbus/station_information.json`

**Refresh:** Hourly or manual snapshots for MVP

---

## APPENDIX: COST MODEL DETAILS

### Spin 99 Cent Club
- Monthly fee: $0.99
- Per-ride flat: $2.39
- Speed cap: 18–22 mph
- Vehicle type: Scooters + bikes

### Veo VeoPlus Premium
- Monthly fee: $5.99
- Per-minute rate: $0.45–$0.50
- Speed cap: 17 mph
- Vehicle type: Scooters + bikes

### Confidence Scoring (0–100)
```
Factors:
  - Number of receipts (1 = 30 pts, 2–3 = 60 pts, 4+ = 100 pts)
  - Cost consistency (σ of per-ride costs: low variance = +20 pts)
  - Number of locations (1 = 0 pts, 2 = 10 pts, 3 = 15 pts, 4 = 20 pts)
  - GBFS data freshness (< 1 hr = 100%, > 24 hr = 50%)

Example:
  - 3 receipts consistent costs (80 pts)
  - 3 locations (15 pts)
  - Fresh GBFS (100% = no penalty)
  - Total: 95% confidence
```

---

## FUTURE EXPANSIONS

- **Multi-city:** Austin, Denver, San Francisco (other Spin/Veo markets)
- **OCR parsing:** Auto-extract from ride screenshots
- **Hunt time:** Integrate walking time + operator response
- **Trends:** Track cost deltas over time as rates change
- **API:** Let external apps query recommendations

---

**This is an open-source research project designed to help shared-scooter riders make informed operator choices based on their personal usage patterns.**

*Last updated: August 1, 2026*
