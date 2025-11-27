# Threat Prioritization Algorithm

## Overview

**Implementation:** Hybrid Tiered + Physics-Based Weighted Scoring  
**Location:** `/orchestration/bridge.py` → `_calculate_threat_priority_score()`  
**Output:** Continuous score 0.0 - 1.0 (higher = more dangerous)

---

## Algorithm Architecture

### **TIER 1: Immediate Threat Detection**
Flags tracks requiring urgent operator attention (does NOT auto-engage).

**Criteria:**
- UAV within 200m with confidence > 0.8
- UNKNOWN within 150m with confidence > 0.9

**Effect:** 1.5× priority multiplier

---

### **TIER 2: Filtering (Non-Threats)**
Automatically excludes tracks that should not be prioritized.

**Filtered Out:**
- ✗ BIRD tracks (always ignored)
- ✗ CLUTTER tracks
- ✗ Low confidence < 0.3
- ✗ Distant (>2500m) UNKNOWN tracks with confidence < 0.6

**Result:** Returns score 0.0 (not prioritized)

---

### **TIER 3: Physics-Based Weighted Scoring**

#### **Factors & Weights:**

| Factor | Weight | Description |
|--------|--------|-------------|
| **Time to Closest Approach (TCA)** | 35% | PRIMARY: When will it arrive? Physics-based calculation |
| **Trajectory** | 25% | How fast is it closing? (approaching vs receding) |
| **Confidence** | 15% | Can we trust this detection? |
| **Range** | 15% | Distance (affects kinetic energy on target) |
| **Type** | 8% | UAV=1.0, UNKNOWN=0.6, BIRD=0.1 |
| **Source Quality** | 2% | FUSED=1.0, RADAR=0.75, RF=0.6 |

**Priority Focus:** "Which threat will reach us first?"

**Algorithm Strategy:** Option B - Balanced Time Priority
- Prioritizes time-to-impact over simple distance
- Fast distant threats outrank slow close threats
- Maintains confidence threshold to prevent false engagements
- Range still matters for kinetic energy assessment

**Note:** Elevation is NOT a threat factor. Drones can drop munitions from any altitude, so high-altitude threats are just as dangerous as low-altitude.

#### **Physics Calculations:**

**1. 3D Velocity Magnitude:**
```
v_3d = √(vx² + vy² + vz²)
```

**2. Closing Velocity:**
```
closing_velocity = -velocity_x  (negative x = approaching)
```

**3. Time to Closest Approach (TCA):**
```
if closing_velocity > 1.0 m/s:
    TCA = range / closing_velocity
```

**TCA Thresholds:**
- < 20 seconds → Factor: 1.0 (CRITICAL)
- < 40 seconds → Factor: 0.9
- < 60 seconds → Factor: 0.7
- < 120 seconds → Factor: 0.4
- \> 120 seconds → Factor: 0.2

**4. Elevation:**
- **Not used as a threat factor**
- All elevations considered equally dangerous
- Rationale: Drones can drop munitions from any altitude

**5. Track Stability Bonus:**
- Age > 10 seconds → +0.2 bonus
- Age > 5 seconds → +0.1 bonus
- Age < 5 seconds → No bonus

---

### **TIER 4: Context Multipliers**

Applied to base score:

| Condition | Multiplier |
|-----------|------------|
| Immediate threat flag | ×1.5 |
| FUSED track with aircraft model | ×1.2 |
| RF intelligence (pilot location) | ×1.15 |
| High velocity (>40 m/s) | ×1.1 |

**Example:**
```
Base score = 0.6
Has RF pilot location + High velocity
Final score = 0.6 × 1.15 × 1.1 = 0.759
```

---

## Algorithm Flow

```
┌─────────────────────────────────┐
│  Track Data Input               │
│  (range, velocity, type, etc.)  │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  TIER 1: Immediate Threat?      │
│  Flag for urgent attention      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  TIER 2: Should Ignore?         │
│  (BIRD, low conf, clutter)      │
└────────────┬────────────────────┘
             │ No
             ▼
┌─────────────────────────────────┐
│  TIER 3: Calculate Base Score   │
│  - Range factor (exponential)   │
│  - Trajectory (closing velocity)│
│  - Time to closest approach     │
│  - Confidence & stability       │
│  - Type & source quality        │
│  - Elevation threat             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  TIER 4: Apply Multipliers      │
│  - Immediate threat ×1.5        │
│  - RF intelligence ×1.15-1.2    │
│  - High velocity ×1.1           │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Final Priority Score (0.0-1.0) │
│  Higher = More Dangerous        │
└─────────────────────────────────┘
```

---

## Example Scenarios

### **Scenario 1: Close Fast UAV**
```
Range: 300m
Type: UAV
Closing velocity: 25 m/s (approaching)
Confidence: 0.95
Elevation: 25° (not a threat factor)
Source: FUSED with aircraft model

Calculation:
- TCA: 300/25 = 12s → Factor: 1.0 (CRITICAL time window)
- Trajectory factor: 25/30 = 0.833 (fast approach)
- Confidence: 0.95 (very reliable)
- Range factor: e^(-300/1000) = 0.741 (close)
- Type: 1.0 (UAV)
- Source: 1.0 (FUSED)

Base: 1.0×0.35 + 0.833×0.25 + 0.95×0.15 + 0.741×0.15 + 1.0×0.08 + 1.0×0.02
Base ≈ 0.851

Multipliers: ×1.2 (FUSED with model)
Final: 0.851 × 1.2 = 1.021 → clamped to 1.0

Priority: CRITICAL (maximum threat)
```

### **Scenario 2: Distant Slow UNKNOWN**
```
Range: 2000m
Type: UNKNOWN
Closing velocity: 5 m/s
Confidence: 0.6
Elevation: 35° (not a threat factor)

Calculation:
- TCA: 2000/5 = 400s → Factor: 0.2 (not urgent)
- Trajectory: 5/30 = 0.167 (slow approach)
- Confidence: 0.6 (moderate)
- Range factor: e^(-2000/1000) = 0.135 (distant)
- Type: 0.6 (UNKNOWN)
- Source: 0.75 (assume RADAR)

Base: 0.2×0.35 + 0.167×0.25 + 0.6×0.15 + 0.135×0.15 + 0.6×0.08 + 0.75×0.02
Base ≈ 0.244

No multipliers
Final: 0.244

Priority: LOW (<0.4)
```

### **Scenario 3: BIRD (Filtered)**
```
Type: BIRD

TIER 2 Filter: Ignored
Final Score: 0.0
Priority: NONE (not displayed)
```

### **Scenario 4: Fast Distant vs Slow Close (Time Priority Test)**
**Demonstrates the advantage of time-based prioritization**

**Track A - Fast Distant:**
```
Range: 1500m
Closing velocity: 40 m/s (very fast approach)
TCA: 37.5 seconds
Confidence: 0.9
Type: UAV

Calculation:
- TCA: 37.5s → Factor: 0.9 (urgent)
- Trajectory: 40/30 = 1.0 (capped at max)
- Confidence: 0.9
- Range: e^(-1500/1000) = 0.223
- Type: 1.0
- Source: 0.75 (RADAR)

Base: 0.9×0.35 + 1.0×0.25 + 0.9×0.15 + 0.223×0.15 + 1.0×0.08 + 0.75×0.02
Base ≈ 0.734

Priority: HIGH (will arrive soon despite distance)
```

**Track B - Slow Close:**
```
Range: 400m
Closing velocity: 10 m/s (slow approach)
TCA: 40 seconds
Confidence: 0.85
Type: UAV

Calculation:
- TCA: 40s → Factor: 0.9
- Trajectory: 10/30 = 0.333
- Confidence: 0.85
- Range: e^(-400/1000) = 0.670
- Type: 1.0
- Source: 0.75 (RADAR)

Base: 0.9×0.35 + 0.333×0.25 + 0.85×0.15 + 0.670×0.15 + 1.0×0.08 + 0.75×0.02
Base ≈ 0.604

Priority: HIGH but LOWER than Track A
```

**Result:** Track A (fast distant) correctly prioritized because it will **reach you first** despite being farther away. This is the tactical advantage of time-based prioritization.

---

## Operator Workflow

### **Automatic Selection:**
- System continuously calculates priority for all tracks
- Highest priority track auto-selected
- Selection updates every second
- Birds and low-confidence tracks automatically filtered

### **Manual Selection:**
- Operator can click any track to override
- Manual selection lasts 10 seconds
- Timer resets with each new selection
- Auto-reverts to highest priority after timeout

### **Engagement:**
- **NO AUTO-ENGAGE** - Operator approval always required
- Engage button shows selected track ID
- Even immediate threats require operator action
- Safety validation performed before engaging

---

## Tuning Parameters

Easily adjustable in `/orchestration/bridge.py`:

### **Weights (Line ~513):**
```python
# Option B: Balanced Time Priority - "Which threat will reach us first?"
base_score = (
    tca_factor * 0.35 +            # PRIMARY: Time urgency (when will it arrive?)
    trajectory_factor * 0.25 +     # Closing velocity (how fast approaching?)
    confidence_factor * 0.15 +     # Detection reliability (can we trust this?)
    range_factor * 0.15 +          # Distance (kinetic energy on target)
    type_factor * 0.08 +           # Target classification (UAV vs Unknown)
    source_factor * 0.02           # Sensor quality (minor bonus)
)
# Note: Prioritizes fast distant threats over slow close threats
```

### **TCA Thresholds (Line ~462):**
```python
if tca_seconds < 20:      # Adjust critical threshold
    tca_factor = 1.0
elif tca_seconds < 40:    # Adjust high threshold
    tca_factor = 0.9
```

### **Multipliers (Line ~535):**
```python
if is_immediate:
    multiplier *= 1.5     # Adjust immediate threat urgency

if source == 'FUSED' and track_data.get('aircraft_model'):
    multiplier *= 1.2     # Adjust RF intelligence bonus
```

---

## Key Advantages

1. **Time-to-Impact Focused:** Prioritizes threats that will reach you first
2. **Physics-Based:** Uses actual kinematics (velocity, range, TCA)
3. **Tactical Superiority:** Fast distant threats correctly outrank slow close threats
4. **No Mass Required:** Works without knowing drone weight
5. **Operator Approval:** No auto-engage - human in the loop
6. **Auto-Filtering:** Birds and clutter removed automatically
7. **Elevated Confidence:** 15% weight prevents false positives
8. **Explainable:** Clear factors and weights for audit
9. **Tunable:** Easy to adjust without code changes
10. **Real-Time:** Fast computation (<1ms per track)
11. **Context-Aware:** Leverages RF intelligence when available

---

## Testing

**Test Scenario 3** (5 tracks):
- 3 UAVs at different ranges and velocities
- 1 BIRD (automatically filtered → score 0.0)
- 1 UNKNOWN

**Expected Behavior:**
- BIRD never selected
- Closest approaching UAV prioritized
- Selection adapts as tracks move
- TCA becomes dominant as tracks approach

---

## Future Enhancements (Optional)

- ☐ Protected zone concept (geo-fence)
- ☐ Swarm detection (track clustering)
- ☐ Threat trajectory prediction
- ☐ Machine learning threat patterns
- ☐ Historical engagement outcomes
- ☐ Weather/wind compensation

---

**Version:** 1.0  
**Date:** November 26, 2024  
**Author:** C2 System Development Team
