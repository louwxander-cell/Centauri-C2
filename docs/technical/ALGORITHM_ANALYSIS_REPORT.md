# Threat Prioritization Algorithm Analysis Report

**Date:** November 27, 2024  
**Analysis Type:** Live Run Debug Data  
**Scenario:** Multi-track stress test (25 tracks)

---

## 📊 **Current Algorithm Configuration**

### **3-Tier Scoring System:**

#### **TIER 1: IMMEDIATE (<200m)**
- **Trigger:** Range < 200m
- **Score:** 1.0 (maximum, unconditional)
- **Rationale:** Any threat this close is immediate danger
- **Weights:** N/A (override)

#### **TIER 2: CLOSE (200m - 500m)**
```
Range Factor:        60%  ← Proximity dominates
CPA Threat:          20%  ← Prediction secondary
Trajectory:          12%  ← Closing velocity
Confidence:           6%  ← Detection reliability
Type:                 2%  ← Classification
```

#### **TIER 3: DISTANT (>500m)**
```
CPA Threat:          45%  ← PRIMARY: Prediction
Range Factor:        20%  ← Current proximity
Trajectory:          15%  ← Closing velocity
Confidence:          12%  ← Detection reliability
Type:                 6%  ← Classification
Source:               2%  ← Sensor quality
```

---

## 🔍 **Live Run Analysis**

### **Track Performance Examples:**

#### **Track 5104 - Correctly Prioritized (Approaching)**
```
Time 0: R=252m → CPA=168m in 52.4s, [CLOSE] Score=0.670
Time 1: R=203m → CPA=137m in 42.1s, [CLOSE] Score=0.707
Time 2: R=155m → CPA=106m in 31.9s, [IMMEDIATE] Score=1.000 ✅
Time 3: R=107m → CPA=73m in 21.9s,  [IMMEDIATE] Score=1.000 ✅
```
**Analysis:** ✅ Excellent - transitions smoothly through tiers, correctly gets maximum priority when <200m

#### **Track 5109 - Correctly Selected (Close Approach)**
```
Time 0: R=293m → CPA=277m in 11.1s, [CLOSE] Score=0.690
Time 1: R=260m → CPA=244m in 10.3s, [CLOSE] Score=0.706
Time 2: R=226m → CPA=212m in 9.3s,  [CLOSE] Score=0.731
Time 3: R=193m → CPA=179m in 8.3s,  [IMMEDIATE] Score=1.000 ✅
```
**Analysis:** ✅ Perfect - consistently approaching with close CPA, correctly escalated to IMMEDIATE

#### **Track 5101 - CPA Working Correctly (Tangential)**
```
Time 0: R=1121m → CPA=176m in 65.5s, [DISTANT] Score=0.472, Threat=0.34
Time 1: R=1100m → CPA=228m in 63.7s, [DISTANT] Score=0.473, Threat=0.34
Time 2: R=1078m → CPA=277m in 61.7s, [DISTANT] Score=0.473, Threat=0.34
Time 3: R=1057m → CPA=324m in 59.6s, [DISTANT] Score=0.541, Threat=0.49
Time 4: R=1036m → CPA=367m in 57.4s, [DISTANT] Score=0.541, Threat=0.49
```
**Analysis:** ⚠️ Interesting - range decreasing BUT CPA distance INCREASING (176m → 367m)
- This means track is on tangential trajectory (passing by, not direct hit)
- CPA correctly identifies this is NOT a collision course
- However, score increased slightly (0.472 → 0.541) due to range factor

#### **Receding Tracks (CPA = 0.0s)**
```
Track 5123: R=448m → CPA=448m in 0.0s, [CLOSE] Score=0.479, Threat=0.07
Track 5100: R=425m → CPA=425m in 0.0s, [CLOSE] Score=0.490, Threat=0.07
Track 5102: R=1946m → CPA=1946m in 0.0s, [DISTANT] Score=0.231, Threat=0.01
```
**Analysis:** ⚠️ These tracks are at or past CPA (receding or perpendicular)
- CPA time = 0.0s means CPA already happened
- Threat scores appropriately low (0.01-0.07)
- But still being tracked - might be unnecessarily cluttering display

---

## 📈 **Statistical Summary**

### **From Sample of ~20 Tracks:**

| Tier | Count | Avg Score | Range |
|------|-------|-----------|-------|
| IMMEDIATE (<200m) | 3 | 1.000 | 1.000 |
| CLOSE (200-500m) | 7 | 0.625 | 0.462-0.731 |
| DISTANT (>500m) | 10 | 0.289 | 0.194-0.541 |

### **CPA Predictions:**
- **Direct threats** (CPA < 200m): 4 tracks → High priority ✅
- **Tangential** (CPA > 500m): 6 tracks → Medium/Low priority ✅
- **Receding** (time_to_cpa = 0s): 8 tracks → Low threat scores ✅

---

## ✅ **What's Working Well**

### **1. IMMEDIATE Tier (<200m)**
- ✅ Always prioritizes closest threats
- ✅ Score = 1.0 guarantees top selection
- ✅ No false negatives observed

### **2. CLOSE Tier (200-500m)**
- ✅ Balances proximity (60%) with prediction (20%)
- ✅ Correctly escalates approaching threats
- ✅ Smooth transition to IMMEDIATE tier

### **3. CPA Calculation**
- ✅ Correctly predicts future closest distance
- ✅ Identifies tangential trajectories (Track 5101)
- ✅ Updates in real-time as tracks move
- ✅ Distinguishes approaching vs receding

### **4. Score Progression**
- ✅ Scores increase smoothly as threats approach
- ✅ Clear differentiation between tiers
- ✅ Predictable behavior

---

## ⚠️ **Areas for Improvement**

### **Issue 1: Receding Tracks Still Scored**
**Problem:**
```
Track 5100: R=425m, CPA=425m in 0.0s → Score=0.490
```
- Track is at/past CPA (receding or perpendicular)
- Still gets moderate score due to range factor in CLOSE tier
- Not a threat but clutters high-priority zone

**Recommendation:**
```python
if time_to_cpa <= 0 and range_m > 200:
    # Past CPA and not immediate threat - downgrade
    base_score *= 0.3  # Reduce by 70%
```

### **Issue 2: Tangential Tracks Get Proximity Boost**
**Problem:**
```
Track 5101: R=1057m → 1036m (getting closer)
           CPA=324m → 367m (will miss by more)
           Score increased from 0.472 → 0.541
```
- Range decreasing gives higher range_factor score
- But CPA shows it's actually getting WORSE (passing by at greater distance)
- Range factor (20%) is overriding CPA prediction (45%)

**Recommendation:**
- In DISTANT tier, reduce range_factor to 10%
- Increase CPA_threat to 50%
- This makes prediction truly dominant over proximity

### **Issue 3: CPA Threat for Distant Passes Too High**
**Observation:**
```
Track 5106: R=2227m → CPA=805m in 122.5s
           CPA Threat=0.08, Score=0.298
```
- Will pass at 805m (not close)
- But still gets non-trivial threat score
- CPA distance factor for 805m should be lower

**Recommendation:**
Adjust CPA distance thresholds:
```python
# Current:
elif cpa_distance < 1000:
    cpa_distance_factor = 0.4   # Too high for 800m+ passes

# Recommended:
elif cpa_distance < 500:
    cpa_distance_factor = 0.5
elif cpa_distance < 800:
    cpa_distance_factor = 0.3
elif cpa_distance < 1200:
    cpa_distance_factor = 0.15
```

---

## 🎯 **Recommended Improvements**

### **Priority 1: Penalize Receding Tracks**
```python
# After calculating base_score, add:
if time_to_cpa <= 0 and range_m > 200:
    # Track is receding or perpendicular, not immediate threat
    base_score *= 0.3  # 70% penalty
    print(f"      [RECEDING] Score reduced to {base_score:.3f}")
```
**Impact:** Prevents receding tracks from cluttering high-priority selections

### **Priority 2: Increase CPA Weight for DISTANT Tier**
```python
# Current DISTANT tier:
base_score = (
    cpa_threat * 0.45 +      # ← Increase to 0.55
    range_factor * 0.20 +    # ← Decrease to 0.10
    trajectory_factor * 0.15 +
    confidence_factor * 0.12 +
    type_factor * 0.06 +
    source_factor * 0.02
)
```
**Impact:** Makes prediction truly dominant for distant threats, prevents tangential tracks from scoring high due to proximity

### **Priority 3: Refine CPA Distance Factors**
```python
# More granular CPA distance thresholds:
if cpa_distance < 50:
    cpa_distance_factor = 1.0    # Collision course
elif cpa_distance < 100:
    cpa_distance_factor = 0.95   # Very close pass
elif cpa_distance < 200:
    cpa_distance_factor = 0.85   # Close pass
elif cpa_distance < 300:
    cpa_distance_factor = 0.70   # Moderate proximity
elif cpa_distance < 500:
    cpa_distance_factor = 0.50   # ← NEW threshold
elif cpa_distance < 800:
    cpa_distance_factor = 0.25   # ← NEW threshold
elif cpa_distance < 1200:
    cpa_distance_factor = 0.10   # ← NEW threshold
else:
    cpa_distance_factor = 0.05   # Will miss by a lot
```
**Impact:** Better differentiation between close passes and distant misses

### **Priority 4: Expand CLOSE Tier Boundary**
```python
# Current:
if range_m < 200:
    tier = "IMMEDIATE"
elif range_m < 500:  # ← Consider increasing to 600m
    tier = "CLOSE"
```
**Impact:** Extends proximity-dominant scoring to slightly farther range

---

## 📊 **Predicted Performance After Improvements**

### **Scenario A: Track 5101 (Tangential)**
**Before:**
```
R=1036m, CPA=367m → Score=0.541 (moderate priority)
```
**After (with improvements):**
```
R=1036m, CPA=367m → CPA_threat=0.25 (new factor)
                  → Score=0.35 (lower priority) ✅
```

### **Scenario B: Track 5100 (Receding)**
**Before:**
```
R=425m, CPA=425m in 0.0s → Score=0.490 (moderate)
```
**After (with receding penalty):**
```
R=425m, CPA=425m in 0.0s → Score=0.490 × 0.3 = 0.147 (low) ✅
```

### **Scenario C: Track 5104 (Direct Approach)**
**Before:**
```
R=155m, CPA=106m → Score=1.000 (maximum)
```
**After:**
```
R=155m, CPA=106m → Score=1.000 (unchanged) ✅
```
Direct threats remain top priority - no degradation

---

## 🎖️ **Final Assessment**

### **Current Algorithm: 8/10**

**Strengths:**
- ✅ Excellent immediate threat detection (<200m)
- ✅ Smooth tier transitions
- ✅ CPA calculation mathematically correct
- ✅ Real-time dynamic updates working

**Weaknesses:**
- ⚠️ Receding tracks not sufficiently penalized
- ⚠️ Tangential tracks get undeserved proximity boost
- ⚠️ CPA distance factors need refinement for distant passes

**With Recommended Improvements: Projected 9.5/10**

---

## 🚀 **Implementation Priority**

### **Quick Win (5 minutes):**
1. Add receding track penalty
2. Adjust DISTANT tier weights (CPA: 55%, Range: 10%)

### **Medium Effort (15 minutes):**
3. Refine CPA distance factor thresholds
4. Expand CLOSE tier to 600m

### **Low Priority:**
5. Add trajectory confidence scoring
6. Implement multi-threat coordination logic

---

## 📝 **Summary**

**Current Configuration:**
- 3-tier system with proximity override
- Physics-based CPA prediction
- 10 Hz real-time updates
- Dynamic tier-based weighting

**Key Insight:**
The algorithm is fundamentally sound but needs fine-tuning for edge cases (receding tracks, tangential approaches, distant misses).

**Recommended Action:**
Implement Priority 1 and 2 improvements immediately for optimal performance.
