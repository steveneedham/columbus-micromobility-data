# Scooter Challenge: Operator Analysis & Project Spec

**Project Lead:** Steven Needham  
**Date:** July 31, 2026  
**Status:** Research phase spec + personal recommendation

---

## PART 1: STEVEN'S PERSONAL ANALYSIS

### Your Situation (Mid-density residential neighborhood, Columbus)

#### Fleet Data (Two GBFS snapshots, ~11 min apart)

| Metric | Spin | Veo | Veo Advantage |
|--------|------|-----|---|
| **Citywide vehicles** | 1,289–1,290 | 2,234–2,237 | **1.73x** |
| **Citywide available** | 1,244–1,247 (96.5–96.7%) | 2,160–2,173 (96.7–97.1%) | Slight edge |
| **Near your home (0.25 mi radius)** | 2–3 vehicles | 4 vehicles | **1.3–2.0x** |
| **Local availability** | 100% | 100% | Tie |

**Key finding:** Veo's 1.73x fleet advantage citywide **shrinks to 1.3–2.0x** in your immediate neighborhood. Both operators maintain near-perfect availability at your location.

---

#### Cost Comparison (Your Real Riding Pattern)

**Assumptions:**
- 12–15 minute average ride duration (based on your Spin receipt analysis)
- 20–30 rides/month
- Recent Spin cost: $2.39/ride flat
- Recent Veo cost: $0.45–$0.50/min + $5.99/mo Premium subscription

| Scenario | Spin 99¢ Club | Veo VeoPlus | Winner | Savings |
|----------|---------------|------------|--------|---------|
| 20 rides/month | **$52.59** | $125.99 | Spin | **$73.40** |
| 25 rides/month | **$63.69** | $157.49** | Spin | **$93.80** |
| 30 rides/month | **$78.39** | $185.99** | Spin | **$107.60** |

**Per-ride breakdown (13.5 min avg):**
- **Spin:** $2.39 (flat) = $0.177/min
- **Veo:** (13.5 min × $0.475/min) + ($5.99÷30 rides) = **$6.69/ride**

**Verdict: Spin wins decisively — stay on 99 Cent Club.**

---

#### The Veo Density Caveat

**What Veo would need to break even:**
- **Availability win scenario:** Veo saves you 8+ minutes per ride vs. hunting for Spin
  - 8 min saved × 30 rides = 240 min saved/month
  - At $0.475/min, that's ~$114 in cost avoidance
  - Still only breaks even ($186 Veo cost - $114 savings = $72 net vs. $78 Spin)

**What the data shows:**
- Your neighborhood is **medium-density** for both operators (not downtown core, not periphery)
- Both have 100% local availability right now
- Veo's 1.3–2.0x local edge is real but **not enough to overcome 2.8x per-minute cost premium**

**Speed factor:** Spin (18–22 mph) vs Veo (17 mph cap) means your rides stay shorter on Spin, compounding the cost advantage.

---

#### RECOMMENDATION

### **Stay on Spin 99 Cent Club**

**Rationale:**
1. Spin costs **$50–110 less per month** on your current volume
2. Veo's density advantage (1.73x citywide, 1.3–2.0x locally) **does not translate to enough time savings** to offset per-minute rates
3. Spin's speed advantage (18–22 mph) helps you
4. Your neighborhood has balanced coverage; you're not in a coverage desert

**Contingency:** Keep Veo as a backup app for edge cases (Spin coverage gap, maintenance window). Download VeoPlus for emergencies, but don't make it primary.

---

---

## PART 2: SCOOTER CHALLENGE — PROJECT SPECIFICATION

### 🎯 Vision

An interactive, fun tool that **personalizes operator recommendations** based on real GBFS data, user receipts, and riding patterns. Residents can:
- Upload recent scooter receipts (to extract costs + ride durations)
- Input their home + frequent destinations
- Get live vehicle density data from their neighborhoods
- Receive a personalized cost breakdown + operator recommendation
- **Download an AI skill** to re-run analysis locally with fresh data

**Target audience:** Columbus residents (and eventually other Veo/Spin markets)  
**Tone:** Gamified, data-driven, not dry  
**Location:** Research Library section of [steveneedham.github.io/columbus-micromobility-data](https://steveneedham.github.io/columbus-micromobility-data)

---

### 📋 Core Workflow

```
User Input
  ↓
Receipt Parse + Cost Extraction
  ↓
Live GBFS Density Lookup (Spin + Veo at each location)
  ↓
Availability + Hunt Time Estimation
  ↓
Per-ride Cost Projection
  ↓
Recommendation Engine (cost vs. convenience tradeoff)
  ↓
Downloadable AI Skill Package (Claude/ChatGPT/Gemini)
```

---

### 📄 Input Form

**Location 1: Home (required)**
- Address or lat/lon
- Name: "Home"

**Locations 2–4 (optional but recommended)**
- Work address
- Grocery store
- Social hangout / regular destination
- Significant other's place

*Tip: The more locations, the more accurate the recommendation*

**Ride History (required)**
- Upload 2–3 recent receipt screenshots (JPG/PNG)
  - *OR* manually paste: operator, duration, date, cost
- *Auto-extracts: ride duration, per-ride cost, operator, vehicle type*

**Monthly Frequency (optional)**
- "About ___ rides per month" (slider 5–50)
- *Default: calculate from uploaded receipts*

---

### ⚙️ Processing Engine

#### 1. Receipt Parser
- OCR or regex-based extraction from screenshot
- Fields: Operator, Duration (min), Date, Total Cost
- Calculate: Per-minute rate, per-ride rate
- Flag outliers (unusually short/long rides)

#### 2. Live GBFS Lookup
- Pull current vehicle positions (Spin + Veo) within 0.5 mi of each location
- Calculate:
  - Total available vehicles per operator
  - Distance to nearest vehicle (each operator)
  - Availability % (working / total nearby)
  
**Data source:** Public GBFS feeds (update freq: hourly or manual)

#### 3. Hunt Time Estimation
- Base model: Average walking speed to vehicle (3 mph) + unlock + mounting (1 min)
- Formula: `hunt_time_min = (distance_to_vehicle_mi × 20) + 1`
- Example: 0.25 mi away = ~6 min hunt
- Discount if operator has 2+ vehicles nearby (pick closer one)

#### 4. Cost Projection
**Per-ride cost calculation:**

```
Spin:  flat_rate_per_ride (from receipt)
Veo:   (avg_ride_duration × per_min_rate) + (monthly_sub ÷ rides_per_month)
```

**Monthly projection:**
- Use user's frequency (rides/mo) or extract from receipt history
- Cost = sum(per-ride costs) × frequency

#### 5. Recommendation Logic

**Decision tree:**
```
IF (Veo_monthly_cost < Spin_monthly_cost + $20_buffer)
  AND (Veo_hunt_time < Spin_hunt_time + 3_min)
  THEN recommend Veo
ELSE
  recommend Spin
```

**Confidence score:** 0–100%
- High (80+): Clear winner, consistent across all locations
- Medium (50–79): Close call, tradeoffs matter
- Low (<50): Nearly tied; choose by preference

**Output:** "Based on your data, [Operator A] saves you approximately **$X/month** and has **Y min less hunt time** on average."

---

### 📦 Output: Downloadable Skill Package

**For Claude users:**
- `.zip` file containing:
  - `scooter-challenge-skill.md` (skill definition + instructions)
  - `receipts/` folder (sample receipts for testing)
  - `output.json` template (results snapshot)
- Install via: Settings → Customize → Skills → Upload

**For ChatGPT/Gemini users:**
- `.md` file (importable as Project context or Gem knowledge)
- Standalone instructions for re-running analysis

**Skill includes:**
- Receipt parser (regex + manual fallback)
- GBFS live-pull logic (fetch + filter)
- Cost calculator
- Recommendation engine
- Re-runnable at any time with fresh data

**Example invocation:**
```
@scooter-challenge-skill
addresses: Home, Work, Grocery store...
receipts: [paste/upload recent rides]
target_rides_per_month: 25
```

---

### 🎨 Website Integration

#### Research Library Page

**Card:**
```
🛴 SCOOTER CHALLENGE
Find Your Best Operator

See where Spin and Veo make sense in YOUR neighborhood.
Upload receipts + addresses → get a personalized breakdown.
```

**CTA:** "Start the Challenge"

#### Page Structure

**Section 1: Intro + Example**
- "Steven pays $52/month on Spin, but would pay $126 on Veo in his neighborhood"
- Show his breakdown (chart or table)

**Section 2: Input Form**
- Address inputs
- Receipt uploader (drag-and-drop)
- Frequency slider
- "Analyze" button

**Section 3: Results (dynamic)**
- Cost comparison table (Spin vs Veo)
- Hunt time breakdown by location
- Recommendation card ("Winner: [Operator]")
- Confidence score + reasoning

**Section 4: Download Skill**
- "Use this in your AI tool" button
- Links to Claude, ChatGPT, Gemini instructions
- Sample skills for testing

**Section 5: FAQ**
- "How is hunt time calculated?"
- "Why is per-minute rate so high on Veo?"
- "Can I use this in other cities?" (future)

---

### 📊 Data Considerations

**Public GBFS Data:**
- Refresh frequency: Hourly (or nightly)
- Caching strategy: Keep last 24–48 hr of snapshots
- Availability: Public endpoints (no auth needed)

**User Data (inputs only):**
- No login required
- Receipts: Local processing only (no upload to server)
- Results: Option to save as JSON export
- Privacy: No tracking of which operator users choose

---

### 🚀 MVP Scope (Week 1–2)

**Minimum viable feature set:**
1. ✅ Input form (address + manual receipt entry)
2. ✅ Live GBFS fetch + nearby vehicle count
3. ✅ Basic cost calculator (flat-rate vs. per-minute)
4. ✅ Recommendation card ("Winner: X saves $Y/month")
5. ✅ Downloadable skill template (Markdown)

**Can defer:**
- OCR receipt parsing (manual entry only for MVP)
- Hunt time estimation (MVP shows vehicle count, not time)
- ChatGPT/Gemini skill versions (Claude native only for MVP)
- Historical trend analysis

---

### 🎯 Success Metrics

- **Adoption:** 50+ residents try tool in first month
- **Accuracy:** Recommendations match user's actual experience (survey)
- **Engagement:** 60%+ of users download skill + re-run analysis
- **Content:** Featured in Transit Columbus Slack, local Reddit threads

---

### 📅 Timeline

| Phase | Tasks | Deadline |
|-------|-------|----------|
| **Spec & Validation** | Finalize form, test GBFS pulls | July 31 |
| **MVP Frontend** | Form UI, results display | Aug 7 |
| **Backend** | Cost calc, GBFS integration | Aug 14 |
| **Skill Package** | Claude native skill template | Aug 21 |
| **Launch** | Publish to research library | Aug 28 |

---

## PART 3: IMPLEMENTATION NOTES

### Technology Stack
- **Frontend:** HTML/React (existing dashboard tech)
- **GBFS pulls:** Direct HTTP fetch (no auth, public endpoints)
- **Calculations:** JavaScript (client-side, no server)
- **Skill:** Markdown + embedded formulas (re-usable in Claude/ChatGPT)

### Sample Skill Output

```markdown
# Scooter Challenge Result

## Your Data
- Home: Mid-density residential neighborhood, Columbus
- Recent rides: 3 Spin receipts, avg 13.5 min, $2.39/ride
- Monthly estimate: 25 rides

## Live Vehicle Density (now)
- **Spin:** 3 vehicles within 0.25 mi (100% available)
- **Veo:** 4 vehicles within 0.25 mi (100% available)

## Cost Projection (25 rides/month)
- **Spin 99¢ Club:** $0.99 + (25 × $2.39) = **$60.74**
- **Veo Premium:** $5.99 + (25 × $6.69) = **$173.24**

## Recommendation
🏆 **Spin wins by $112.50/month**

Confidence: 95% (cost advantage is clear; density doesn't compensate)

**Contingency:** Use Veo if Spin is unavailable; don't switch primary.
```

---

## APPENDIX: Steven's Current Setup

**Live dashboards:**
- [columbus-micromobility-data](https://steveneedham.github.io/columbus-micromobility-data/) — GBFS + 311 map
- Twice-daily FleetHal snapshots (Spin + Veo positions)
- Custom Claude skill for 311 case lookup

**Data flow:**
- Public GBFS feeds → local CSV snapshot
- 311 portal scrape (daily)
- Dashboard refresh (nightly)
- Research library export (manual, as-needed)

**Skill packages:**
- columbus-311-case-lookup (deployed)
- scooter-challenge (ready to spec)
- Future: BFS 311 Risk Predictor integration

---

**Next session:** Build MVP form + test GBFS integration against fresh pulls.
