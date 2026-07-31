# Scooter Challenge — Detailed Development Plan

**Target:** Working MVP by Aug 7, 2026  
**For:** Claude Code execution  
**Owner:** Steven Needham

---

## SPRINT 1: MVP Build (Aug 1–7)

### Phase 1: Core Utilities & Logic (Aug 1–2)

#### Task 1.1: Geo Utilities (`src/utils/geo.js`)

**Functions to implement:**
```javascript
// Haversine distance calculation
export function haversineDistance(lat1, lon1, lat2, lon2) {
  // Returns distance in miles
  // Test with: two Columbus points ~1.8 miles apart
  // Expected: ~1.8 miles
}

// Find nearby vehicles
export function nearbyVehicles(userLat, userLon, vehicles, radiusMiles = 0.25) {
  // Filter vehicles array
  // Returns: { spin: [...], veo: [...] } with distances
}

// Hunt time estimation
export function huntTimeEstimate(distanceMiles) {
  // Formula: (distance_miles × 20 min/mi) + 1 min unlock/mount
  // Example: 0.25 mi = ~6 min
  // Returns: minutes
}

// Geocode address (MVP: store as lat/lon manually, defer geocoding API)
export function validateCoordinates(lat, lon) {
  // Simple validation: lat ±90, lon ±180
  // Returns: { valid: bool, message: string }
}
```

**Tests:**
- Haversine: Known distance pairs (e.g., 1 degree = ~69 miles)
- Nearby vehicles: Mock vehicle array with known coords
- Hunt time: 0.25 mi → 6 min, 0.5 mi → 11 min

---

#### Task 1.2: Cost Calculator (`src/utils/calculator.js`)

**Functions to implement:**
```javascript
// Project monthly cost for one operator
export function projectCost(operator, config) {
  // operator: "spin" | "veo"
  // config: {
  //   avgRideDurationMin: number,
  //   ridesPerMonth: number,
  //   ratePerRide?: number,  // Spin
  //   ratePerMin?: number,   // Veo
  //   monthlyFee?: number    // Veo
  // }
  // Returns: {
  //   perRideAvg: number,
  //   monthlyTotal: number,
  //   breakdown: { base, perMinute, subscription }
  // }
}

// Compare operators
export function compareOperators(spinCost, veoCost, huntTimeDiff = 0) {
  // spinCost, veoCost: output from projectCost()
  // huntTimeDiff: Veo hunt time minus Spin hunt time (minutes)
  // Returns: {
  //   winner: "spin" | "veo",
  //   savings: number ($/month),
  //   message: string
  // }
}

// Confidence scoring
export function confidenceScore(data) {
  // data: {
  //   numReceipts: number,
  //   costConsistency: number (0–1, stdev of ride costs),
  //   numLocations: number (1–4),
  //   gbfsDataAge: minutes
  // }
  // Returns: 0–100 score with reasoning
  // High (80+): Many receipts, consistent costs, current GBFS
  // Medium (50–79): Decent data, some variability
  // Low (<50): Single receipt or outdated GBFS
}

// Recommendation logic
export function recommend(spinCost, veoCost, huntTimeData) {
  // Returns: {
  //   winner: "spin" | "veo",
  //   savings: number,
  //   confidenceScore: number,
  //   reasoning: string,
  //   factors: {
  //     costAdvantage: "clear" | "close" | "opposite",
  //     availabilityWin: boolean,
  //     speedFactor: "favors_spin" | "neutral" | "favors_veo"
  //   }
  // }
}
```

**Tests:**
- Spin $2.39 × 25 rides → $60.74
- Veo ($0.475 × 13.5 min) × 25 + $5.99 → ~$173
- Confidence: Single receipt = 45, three receipts = 75, many + current GBFS = 90

---

#### Task 1.3: Receipt Parser (`src/utils/receiptParser.js`)

**Functions to implement:**
```javascript
// MVP: Manual entry only (no OCR)
export function parseManualEntry(entry) {
  // entry: {
  //   operator: "spin" | "veo",
  //   durationMin: number,
  //   costUSD: number,
  //   date: ISO string
  // }
  // Returns: { operator, durationMin, costUSD, date, perMinRate }
  // Validate: cost > 0, duration > 0, duration < 60 (flag outliers)
}

// Validate receipt data
export function validateReceipt(receipt) {
  // Check for:
  // - Missing fields
  // - Unreasonable values (< $1, > $30 for typical ride)
  // - Duration outliers (< 2 min, > 60 min)
  // Returns: { valid: bool, errors: [] }
}

// Regex patterns for future OCR parsing (document for context)
export const RECEIPT_PATTERNS = {
  operator: /^(Spin|Veo)/i,
  duration: /(\d+)\s*min(?:ute)?s?/i,
  cost: /\$(\d+\.?\d{0,2})/,
  date: /(\d{1,2})\/(\d{1,2})\/(\d{2,4})/
};
```

**Tests:**
- Manual entry: { operator: "spin", durationMin: 13, costUSD: 2.39 } → valid
- Outlier: { operator: "spin", durationMin: 120, costUSD: 50 } → flag
- Missing field: { operator: "veo", durationMin: 10 } → invalid (no cost)

---

#### Task 1.4: Constants (`src/constants/operators.js`)

```javascript
export const OPERATORS = {
  spin: {
    name: "Spin",
    monthlyFee: 0.99,
    perRideFlat: 2.39,
    perMinRate: null,
    speedMph: { min: 18, max: 22 },
    defaultColor: "#d9230f"
  },
  veo: {
    name: "Veo",
    monthlyFee: 5.99,
    perRideFlat: null,
    perMinRate: 0.475,  // Mid-range estimate
    speedMph: { min: 17, max: 17 },
    defaultColor: "#00a8a8"
  }
};

export const GBFS_ENDPOINTS = {
  spin: {
    url: "https://feeds.spin.app/gbfs/v3/systems/columbus_us/vehicles",
    format: "json"
  },
  veo: {
    url: "https://gbfs.veo.dev/columbus/station_information.json",
    format: "json"
  }
};

export const DEFAULT_RADIUS = 0.25; // miles
export const HUNT_SPEED_MPH = 3;
export const UNLOCK_TIME_MIN = 1;
```

---

### Phase 2: GBFS Integration (Aug 2–3)

#### Task 2.1: GBFS Fetcher (`src/hooks/useGBFS.js`)

**Hook to implement:**
```javascript
export function useGBFS() {
  const [data, setData] = useState({
    spin: { vehicles: [], loading: false, error: null, age: null },
    veo: { vehicles: [], loading: false, error: null, age: null }
  });

  // Fetch both operators' vehicle data
  const fetchVehicles = useCallback(async () => {
    // For each operator:
    // 1. Fetch from endpoint
    // 2. Parse JSON
    // 3. Extract lat/lon/availability
    // 4. Store with timestamp
    // 5. Handle errors gracefully
  }, []);

  // Get nearby count for location
  const getNearbyCount = useCallback((lat, lon, radius = 0.25) => {
    // Returns: { spin: count, veo: count }
  }, [data]);

  return { data, fetchVehicles, getNearbyCount };
}
```

**Data transformation:**
- Input: Raw GBFS JSON (varies by operator)
- Output: Normalized vehicle array
  ```javascript
  {
    id: string,
    operator: "spin" | "veo",
    lat: number,
    lon: number,
    available: boolean,
    battery: number (0–100, if available),
    type: "scooter" | "bike" (if available)
  }
  ```

**Error handling:**
- Network timeout → show "Unable to fetch live data; using defaults"
- Invalid JSON → log error, continue
- Missing fields → filter out, count as unavailable

**Tests:**
- Fetch returns normalized vehicle array
- Nearby count: 3 Spin vehicles within 0.25 mi
- Error: Network failure → graceful degradation

---

#### Task 2.2: GBFS Utilities (`src/utils/gbfs.js`)

```javascript
// Parse operator-specific GBFS formats
export function parseSpinVehicles(json) {
  // Spin format: { data: { vehicles: [...] } }
  return json.data.vehicles.map(v => ({
    id: v.id,
    operator: "spin",
    lat: v.lat,
    lon: v.lon,
    available: v.is_available,
    battery: null,
    type: v.type || "scooter"
  }));
}

export function parseVeoVehicles(json) {
  // Veo format: varies by endpoint
  // Transform to normalized array
}

// Validate GBFS data freshness
export function isDataFresh(timestamp, maxAgeMinutes = 60) {
  return (Date.now() - timestamp) / 60000 < maxAgeMinutes;
}
```

---

### Phase 3: React Components (Aug 3–4)

#### Task 3.1: Input Form (`src/components/InputForm.jsx`)

**Component structure:**
```jsx
export function InputForm({ onSubmit }) {
  const [locations, setLocations] = useState([
    { name: "Home", address: "", lat: null, lon: null }
  ]);
  const [receipts, setReceipts] = useState([
    { operator: "spin", durationMin: 13, costUSD: 2.39, date: new Date() }
  ]);
  const [frequency, setFrequency] = useState(25);

  const handleSubmit = () => {
    // Validate all fields
    // Call onSubmit(formData)
  };

  return (
    <form>
      <h2>Scooter Challenge</h2>
      <p>Find your best operator in Columbus</p>

      {/* Location inputs */}
      <div>
        <h3>Where do you ride?</h3>
        <LocationInput key={location.name} ... />
      </div>

      {/* Receipt inputs */}
      <div>
        <h3>Your recent rides</h3>
        <ReceiptInput key={receipt.date} ... />
      </div>

      {/* Frequency slider */}
      <div>
        <label>About {frequency} rides per month</label>
        <input type="range" min="5" max="50" ... />
      </div>

      <button type="submit">Analyze My Costs</button>
    </form>
  );
}
```

**Features:**
- Add/remove location fields (min 1, max 4)
- Add/remove receipt entries (min 1, max 10)
- Manual entry only (drag-and-drop UI for future OCR)
- Validate on submit

---

#### Task 3.2: Results Card (`src/components/ResultsCard.jsx`)

**Component structure:**
```jsx
export function ResultsCard({ results }) {
  // results: {
  //   spin: { monthlyTotal, breakdown },
  //   veo: { monthlyTotal, breakdown },
  //   recommendation: { winner, savings, confidenceScore, reasoning }
  //   locationData: [{ name, spinCount, veoCount, huntTime }]
  // }

  return (
    <div className="results-card">
      <h2>Your recommendation</h2>

      {/* Winner badge */}
      <div className="winner-badge">
        🏆 {results.recommendation.winner} saves you ${results.recommendation.savings}/month
      </div>

      {/* Confidence score */}
      <div className="confidence">
        Confidence: {results.recommendation.confidenceScore}%
        <div className="confidence-bar">...</div>
      </div>

      {/* Cost comparison table */}
      <table>
        <tr>
          <th>Operator</th>
          <th>Per Ride</th>
          <th>Monthly</th>
        </tr>
        <tr>
          <td>Spin 99¢ Club</td>
          <td>${results.spin.perRideAvg}</td>
          <td>${results.spin.monthlyTotal}</td>
        </tr>
        <tr>
          <td>Veo Premium</td>
          <td>${results.veo.perRideAvg}</td>
          <td>${results.veo.monthlyTotal}</td>
        </tr>
      </table>

      {/* Location breakdown */}
      <div className="locations">
        <h3>Vehicle density by location</h3>
        {results.locationData.map(loc => (
          <div key={loc.name}>
            <strong>{loc.name}</strong>
            <p>Spin: {loc.spinCount} | Veo: {loc.veoCount}</p>
          </div>
        ))}
      </div>

      {/* Reasoning */}
      <div className="reasoning">
        <p>{results.recommendation.reasoning}</p>
      </div>

      {/* Export button */}
      <button onClick={handleExportSkill}>Download Skill for Claude/ChatGPT</button>
    </div>
  );
}
```

---

#### Task 3.3: Location Input (`src/components/LocationInput.jsx`)

```jsx
export function LocationInput({ location, onChange, onRemove, index }) {
  const [showCoordinates, setShowCoordinates] = useState(false);

  return (
    <div className="location-input">
      <div className="input-group">
        <label>Location {index}: {location.name}</label>
        <input
          type="text"
          placeholder="Address or intersection"
          value={location.address}
          onChange={(e) => onChange({ ...location, address: e.target.value })}
        />
      </div>

      {showCoordinates && (
        <div className="coords">
          <input
            type="number"
            placeholder="Latitude"
            step="0.0001"
            value={location.lat}
            onChange={(e) => onChange({ ...location, lat: parseFloat(e.target.value) })}
          />
          <input
            type="number"
            placeholder="Longitude"
            step="0.0001"
            value={location.lon}
            onChange={(e) => onChange({ ...location, lon: parseFloat(e.target.value) })}
          />
        </div>
      )}

      <button type="button" onClick={() => setShowCoordinates(!showCoordinates)}>
        {showCoordinates ? "Use Address" : "Enter Coordinates"}
      </button>

      {index > 0 && (
        <button type="button" onClick={onRemove}>Remove</button>
      )}
    </div>
  );
}
```

---

#### Task 3.4: Skill Exporter (`src/components/SkillExporter.jsx`)

```jsx
export function SkillExporter({ results, formData }) {
  const handleExport = (format) => {
    if (format === "markdown") {
      const markdown = generateSkillMarkdown(results, formData);
      downloadFile(markdown, "scooter-challenge-skill.md", "text/markdown");
    } else if (format === "json") {
      const json = JSON.stringify(results, null, 2);
      downloadFile(json, "scooter-challenge-results.json", "application/json");
    }
  };

  return (
    <div className="skill-exporter">
      <h3>Download Your Analysis</h3>
      <p>Run this in Claude, ChatGPT, or Gemini to re-analyze with fresh data.</p>

      <button onClick={() => handleExport("markdown")}>
        📥 Claude Skill (.md)
      </button>
      <button onClick={() => handleExport("json")}>
        📥 Results Snapshot (.json)
      </button>

      <div className="instructions">
        <h4>How to use:</h4>
        <p>Claude: Settings → Customize → Skills → Upload ZIP</p>
        <p>ChatGPT: Create Project → Upload this file as context</p>
        <p>Gemini: Create Gem → Upload to Knowledge</p>
      </div>
    </div>
  );
}
```

---

### Phase 4: Skill Template & Export (Aug 4–5)

#### Task 4.1: Skill Template Generator (`src/utils/skillTemplate.js`)

```javascript
export function generateSkillMarkdown(results, formData) {
  return `
# Scooter Challenge Result

## Your Data
${formData.locations.map(loc => `- **${loc.name}**: ${loc.address || \`\${loc.lat}, \${loc.lon}\`}`).join('\n')}
- Recent rides: ${formData.receipts.length} receipts
- Monthly estimate: ${formData.frequency} rides
- Average ride: ${formData.avgDurationMin} minutes

## Live Vehicle Density
${results.locationData.map(loc => `
### ${loc.name}
- **Spin**: ${loc.spinCount} vehicles (${loc.spinAvailability}% available)
- **Veo**: ${loc.veoCount} vehicles (${loc.veoAvailability}% available)
- Hunt time: Spin ~${loc.spinHuntMin}min | Veo ~${loc.veoHuntMin}min
`).join('\n')}

## Cost Projection (${formData.frequency} rides/month)
- **Spin 99¢ Club**: $${results.spin.monthlyTotal.toFixed(2)}
  - Monthly fee: $0.99
  - Per-ride: $${results.spin.perRideAvg.toFixed(2)}
  - Total: $${results.spin.monthlyTotal.toFixed(2)}

- **Veo Premium**: $${results.veo.monthlyTotal.toFixed(2)}
  - Monthly fee: $5.99
  - Per-minute: $0.475
  - Per-ride (est.): $${results.veo.perRideAvg.toFixed(2)}
  - Total: $${results.veo.monthlyTotal.toFixed(2)}

## Recommendation
🏆 **${results.recommendation.winner.toUpperCase()} wins by $${results.recommendation.savings.toFixed(2)}/month**

**Confidence**: ${results.recommendation.confidenceScore}%
**Reasoning**: ${results.recommendation.reasoning}

---

## How to Re-Run This Analysis

1. **Update your addresses** if you move or change regular destinations
2. **Upload recent receipts** (or paste operator/duration/cost)
3. **Set your monthly ride frequency** (slider or estimate)
4. **Run in your AI tool** to get updated costs and recommendation

Each run pulls live vehicle data, so recommendations stay current as fleets change.

---

*Generated: ${new Date().toLocaleDateString()} | Steven Needham's Columbus Micromobility Observer*
  `;
}
```

---

### Phase 5: Assembly & Testing (Aug 5–6)

#### Task 5.1: Main App Component (`src/App.jsx`)

```jsx
import { useState } from 'react';
import { InputForm } from './components/InputForm';
import { ResultsCard } from './components/ResultsCard';
import { useGBFS } from './hooks/useGBFS';
import { useCostCalculator } from './hooks/useCostCalculator';

export default function App() {
  const [formData, setFormData] = useState(null);
  const [results, setResults] = useState(null);
  const { data: gbfsData, fetchVehicles, getNearbyCount } = useGBFS();
  const { calculateCosts, getRecommendation } = useCostCalculator();

  const handleFormSubmit = async (data) => {
    setFormData(data);

    // Fetch live GBFS data
    await fetchVehicles();

    // Calculate costs
    const spinCost = calculateCosts("spin", data);
    const veoCost = calculateCosts("veo", data);

    // Get location-specific density
    const locationData = data.locations.map(loc => {
      const nearby = getNearbyCount(loc.lat, loc.lon);
      return { ...loc, ...nearby };
    });

    // Get recommendation
    const recommendation = getRecommendation(spinCost, veoCost);

    setResults({ spin: spinCost, veo: veoCost, recommendation, locationData });
  };

  return (
    <div className="app">
      <header>
        <h1>🛴 Scooter Challenge</h1>
        <p>Which operator is cheaper for you in Columbus?</p>
      </header>

      <main>
        {!results ? (
          <InputForm onSubmit={handleFormSubmit} />
        ) : (
          <>
            <ResultsCard results={results} />
            <button onClick={() => setResults(null)}>← Start Over</button>
          </>
        )}
      </main>

      <footer>
        <p>Public GBFS data | No signup required | Your data stays local</p>
      </footer>
    </div>
  );
}
```

---

#### Task 5.2: Test Cases

**`tests/calculator.test.js`:**
```javascript
import { projectCost, compareOperators, confidenceScore } from '../utils/calculator';

describe('Cost Calculator', () => {
  it('projects Spin cost correctly', () => {
    const result = projectCost("spin", {
      avgRideDurationMin: 13.5,
      ridesPerMonth: 25
    });
    expect(result.monthlyTotal).toBeCloseTo(60.74, 0.01);
  });

  it('projects Veo cost correctly', () => {
    const result = projectCost("veo", {
      avgRideDurationMin: 13.5,
      ridesPerMonth: 25
    });
    expect(result.monthlyTotal).toBeCloseTo(173.24, 0.01);
  });

  it('recommends Spin for Steven's case', () => {
    const spinCost = projectCost("spin", {...});
    const veoCost = projectCost("veo", {...});
    const rec = compareOperators(spinCost, veoCost);
    expect(rec.winner).toBe("spin");
  });
});
```

**`tests/geo.test.js`:**
```javascript
import { haversineDistance, huntTimeEstimate } from '../utils/geo';

describe('Geo Utilities', () => {
  it('calculates distance between two Columbus points', () => {
    const dist = haversineDistance(39.9612, -82.9988, 39.9357, -82.9758);
    expect(dist).toBeCloseTo(1.8, 0.1);
  });

  it('estimates hunt time correctly', () => {
    expect(huntTimeEstimate(0.25)).toBe(6); // 0.25 mi = 5 min + 1 min
    expect(huntTimeEstimate(0.5)).toBe(11);
  });
});
```

---

### Phase 6: Deployment (Aug 6–7)

#### Task 6.1: Website Integration

1. Add to research library page HTML
2. Add card link to main navigation
3. Test in production environment
4. Verify GBFS endpoints work from CDN

#### Task 6.2: Documentation

1. Write `USER_GUIDE.md` (for end users)
2. Write `GBFS_NOTES.md` (data source reference)
3. Write `COST_MODEL.md` (formulas + assumptions)

#### Task 6.3: QA & Launch

- [ ] Form validation works
- [ ] GBFS fetch handles errors
- [ ] Cost math matches manual calculations
- [ ] Results display on mobile
- [ ] Skill export generates valid Markdown
- [ ] Page loads under 2 seconds
- [ ] Accessibility (keyboard nav, alt text, etc.)

---

## SUCCESS CRITERIA (MVP)

✅ Form accepts: home address + 3 locations + ride history + frequency  
✅ Live GBFS fetch returns vehicle counts per operator  
✅ Cost calculator outputs: monthly projections + confidence score  
✅ Results card displays: cost table + recommendation + reasoning  
✅ Skill exporter generates: downloadable Markdown + JSON  
✅ Mobile responsive: tested on iOS + Android  
✅ Handles errors gracefully: shows user-friendly messages  
✅ Performance: <2s page load, <1s calculation

---

## DEFERRED (Post-MVP)

❌ OCR receipt parsing (manual entry only for now)  
❌ Hunt time estimation per location  
❌ ChatGPT/Gemini skill versions (Claude native only)  
❌ Historical trend tracking  
❌ Geocoding API integration (manual lat/lon entry)  
❌ Multi-city support  

---

**Ready to start building.** Let me know when you're ready for Phase 1!
