# 🛴 Scooter Challenge — Claude Code Project

**Interactive operator recommendation tool for Columbus micromobility users**

Build personalized Spin vs. Veo cost analysis based on live GBFS data and user riding patterns.

---

## 📋 Quick Start

### What This Project Does
1. User uploads ride receipts (or enters manually) + home address + 3 other locations
2. System fetches live Spin/Veo vehicle density from each neighborhood
3. Calculates cost projections (Spin flat-rate vs. Veo per-minute)
4. Recommends the cheaper operator + confidence score
5. Outputs downloadable Claude skill for re-running analysis

### MVP Scope (Aug 1–7)
- ✅ Input form (addresses + manual receipt entry)
- ✅ Live GBFS fetch + vehicle count per location
- ✅ Cost calculator (no OCR yet)
- ✅ Recommendation card + confidence
- ✅ Skill template export (Markdown)

### Tech Stack
- **Frontend:** React + Tailwind (existing dashboard pattern)
- **Data:** Client-side GBFS fetch, public endpoints
- **Calculation:** JavaScript (no backend needed for MVP)
- **Export:** JSON → Markdown skill generation

---

## 📁 Project Structure

```
scooter-challenge/
├── README.md                          (this file)
├── DEVELOPMENT_PLAN.md                (detailed build sequence)
│
├── public/
│   └── index.html
│
├── src/
│   ├── App.jsx                        (main component)
│   ├── index.css                      (Tailwind config)
│   │
│   ├── components/
│   │   ├── InputForm.jsx              (address + receipt inputs)
│   │   ├── ResultsCard.jsx            (cost breakdown + recommendation)
│   │   ├── SkillExporter.jsx          (Markdown + JSON export)
│   │   └── LocationInput.jsx          (multi-address field)
│   │
│   ├── hooks/
│   │   ├── useGBFS.js                 (fetch vehicle density)
│   │   ├── useReceiptParser.js        (regex-based parsing)
│   │   └── useCostCalculator.js       (Spin vs. Veo projections)
│   │
│   ├── utils/
│   │   ├── gbfs.js                    (GBFS endpoints + parsing)
│   │   ├── geo.js                     (haversine, nearby vehicles)
│   │   ├── calculator.js              (cost math, confidence scoring)
│   │   ├── receiptParser.js           (regex patterns for OCR fallback)
│   │   └── skillTemplate.js           (Markdown generator)
│   │
│   └── constants/
│       ├── operators.js               (Spin/Veo rate defaults)
│       ├── gbfsEndpoints.js           (public GBFS feed URLs)
│       └── messages.js                (copy, FAQs, tooltips)
│
├── skills/
│   └── scooter-challenge-skill.md     (exportable Claude skill)
│
├── docs/
│   ├── USER_GUIDE.md                  (end-user docs)
│   ├── GBFS_NOTES.md                  (data source reference)
│   └── COST_MODEL.md                  (formulas & assumptions)
│
└── tests/
    ├── calculator.test.js             (cost math tests)
    ├── parser.test.js                 (receipt parsing tests)
    └── geo.test.js                    (distance/density tests)
```

---

## 🎯 MVP Features (Sprint 1)

### 1. Input Form (`InputForm.jsx`)
**User provides:**
- Home address (required) — text input or lat/lon
- Up to 3 additional locations (optional)
  - Work, grocery, hangout, SO's house
- Ride history: manual entry OR receipt screenshot upload
  - Operator (Spin/Veo)
  - Duration (minutes)
  - Date
  - Total cost
- Monthly ride frequency (slider, 5–50 rides)

**Validation:**
- At least one ride history entry
- Valid addresses or coordinates
- Plausible costs ($2–15/ride)

### 2. Live GBFS Lookup (`useGBFS.js`)
**Per location:**
- Fetch Spin + Veo vehicle positions (public endpoints)
- Filter within 0.5 mi radius
- Count available vehicles
- Calculate distance to nearest (each operator)

**Data sources:**
- Spin GBFS: `https://feeds.spin.app/gbfs/v3/systems/columbus_us/vehicles`
- Veo GBFS: `https://gbfs.veo.dev/columbus/station_information.json`

### 3. Cost Calculator (`useCostCalculator.js`)
**Inputs:** User receipts + frequency + ride duration estimate

**Outputs:**
```javascript
{
  spin: {
    perRideFlat: 2.39,
    monthlyTotal: 60.74,
    avgRideCost: 2.39
  },
  veo: {
    perMinuteRate: 0.475,
    monthlySubscription: 5.99,
    avgRideCost: 6.69,
    monthlyTotal: 173.24
  },
  recommendation: {
    winner: "spin",
    savings: 112.50,
    confidenceScore: 95,
    reasoning: "Cost advantage is clear; Veo's density doesn't compensate"
  }
}
```

### 4. Results Card (`ResultsCard.jsx`)
**Display:**
- Cost comparison table (monthly projection)
- Vehicle count per location (Spin vs. Veo)
- Confidence score (0–100%) with color coding
- Recommendation badge ("Winner: Spin saves you $X/month")
- Hunt time estimate (if available)

### 5. Skill Exporter (`SkillExporter.jsx`)
**Outputs:**
- `.md` file (Claude native skill)
- `.json` file (results snapshot)
- Zip package option (later)

**Skill includes:**
- User's addresses + receipt data
- Current GBFS snapshot
- Cost breakdown
- Recommendation with reasoning
- Instructions for re-running

---

## 🔑 Key Utilities

### `geo.js` — Distance Calculations
```javascript
haversineDistance(lat1, lon1, lat2, lon2) → miles
nearbyVehicles(userLat, userLon, vehicles, radiusMiles) → filtered array
huntTimeEstimate(distanceMiles) → minutes  // 3 mph walk + 1 min unlock
```

### `calculator.js` — Cost Math
```javascript
projectCost(operator, avgDurationMin, ridesPerMonth, rateConfig) → monthlyTotal
confidenceScore(data) → 0–100 (based on consistency across locations)
recommendation(spinCost, veoCost, huntTimeDiff) → { winner, reasoning }
```

### `receiptParser.js` — Fallback Parsing
```javascript
// MVP: Manual entry only
// Future: Regex patterns for OCR
parseReceiptText(text) → { operator, duration, cost, date }
```

### `skillTemplate.js` — Markdown Export
```javascript
generateSkillMarkdown(userData, gbfsSnapshot, results) → markdown string
```

---

## 📊 Operator Rate Constants

**Spin 99 Cent Club:**
- Monthly fee: $0.99
- Per-ride flat: $2.39
- Speed: 18–22 mph

**Veo VeoPlus Premium:**
- Monthly fee: $5.99
- Per-minute rate: $0.45–$0.50
- Speed: 17 mph cap

*(Store in `constants/operators.js` for easy updates)*

---

## 🚀 Development Sequence

### Day 1: Setup + Core Logic
1. ✅ Project scaffold (React template)
2. ✅ Geo utilities (haversine, nearby vehicles)
3. ✅ Cost calculator (projection logic)
4. ✅ Confidence scoring

### Day 2: GBFS Integration
1. ✅ Fetch Spin + Veo endpoints
2. ✅ Parse vehicle JSON
3. ✅ Filter by radius, count availability
4. ✅ Error handling for unavailable feeds

### Day 3: UI Components
1. ✅ InputForm (addresses + manual receipt entry)
2. ✅ LocationInput (repeatable field)
3. ✅ ResultsCard (cost table + recommendation)
4. ✅ Basic styling (Tailwind)

### Day 4: Export & Polish
1. ✅ SkillExporter (Markdown generation)
2. ✅ JSON results snapshot
3. ✅ Mobile responsive
4. ✅ Error messages + help text

### Day 5: Testing + Launch
1. ✅ Cost calculator edge cases
2. ✅ GBFS fetch failure handling
3. ✅ Address validation (geocoding?)
4. ✅ Deploy to research library

---

## 🔗 Integration Points

### Website Integration
- Embed in: `steveneedham.github.io/columbus-micromobility-data/research/scooter-challenge`
- Link from: Research Library card
- Example user: Steven's case (Spin $60/mo vs Veo $173/mo)

### Skill Export Target
- Claude native skill (primary)
- ChatGPT Project (secondary, later)
- Gemini Gem (secondary, later)

### Future Expansions
- OCR receipt parsing
- Hunt time estimation (distance + wait time)
- Other cities (Spin/Veo markets)
- Historical trend analysis (track cost deltas over time)

---

## 📝 Testing Checklist

### Unit Tests
- [ ] Haversine distance (known coords → known distances)
- [ ] Cost calculation (Spin $2.39 × 25 rides = $60.74)
- [ ] Confidence scoring (consistent data = high score)
- [ ] GBFS parsing (vehicle count from JSON)

### Integration Tests
- [ ] Form submission → calculator → results card
- [ ] GBFS fetch failure → graceful error message
- [ ] Skill export → valid Markdown syntax
- [ ] Multiple locations → per-location cost breakdown

### Manual Testing
- [ ] Try 20 rides/month → Spin wins
- [ ] Try 5 rides/month → review tradeoff
- [ ] Enter addresses without GBFS data → show defaults
- [ ] Export skill → paste into Claude → works

---

## 🛠 Tech Decisions

| Choice | Why |
|--------|-----|
| React | Existing dashboard pattern; component reuse |
| Tailwind | Consistent with steven-needham/design-system |
| Client-side only | No backend needed; public data only |
| GBFS public feeds | Free, no auth required |
| Markdown export | Universal; works in Claude/ChatGPT/Gemini |

---

## 📚 Docs to Write

- `USER_GUIDE.md` — How to use the tool
- `GBFS_NOTES.md` — Data source details, refresh rates, limitations
- `COST_MODEL.md` — Formulas, assumptions, confidence scoring logic
- `DEVELOPMENT_PLAN.md` — This build sequence (detailed version)

---

## 🎓 Next Session

**Goal:** Have a working MVP by EOD Aug 7

**Bring:**
- Fresh GBFS pulls from Columbus (for integration testing)
- More receipt examples (if available, for parser validation)
- Feedback on form UX from Transit Columbus Slack

---

**Maintained by:** Steven Needham  
**Status:** MVP in development (Sprint 1: Aug 1–7)  
**Last updated:** July 31, 2026
