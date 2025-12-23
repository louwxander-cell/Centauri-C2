# Threat Prioritization - Classification Filter

## Overview
Updated threat prioritization algorithm to **only consider aerial threats**: UAV classes and aircraft. All ground-based and non-threat classifications are now filtered out.

## Allowed Classifications

### ✅ Considered for Threat Prioritization:
1. **UAV** - General UAV classification
2. **UAV_MULTI_ROTOR** - Quadcopters, hexacopters (DJI, etc.)
3. **UAV_FIXED_WING** - Fixed-wing drones
4. **PLANE** - Crewed/manned aircraft

### ❌ Ignored (Filtered Out):
1. **WALKER** - Pedestrians (ground-based, non-threat)
2. **BIRD** - Avian targets (non-threat)
3. **VEHICLE** - Ground vehicles (non-threat)
4. **CLUTTER** - Environmental noise (non-threat)
5. **UNDECLARED** - Unknown/low confidence (non-threat)

## Implementation

### Code Changes

**File**: `orchestration/bridge.py`

**1. Updated `_should_ignore_track()` method:**
```python
def _should_ignore_track(self, track_type: str, confidence: float, range_m: float, classification: str = None) -> bool:
    """
    Filter out tracks that should not be prioritized.
    Only consider: UAV, UAV_MULTI_ROTOR, UAV_FIXED_WING, PLANE
    All other classifications are ignored.
    """
    # Use classification if available (multiclass classifier)
    if classification:
        allowed_classes = ['UAV', 'UAV_MULTI_ROTOR', 'UAV_FIXED_WING', 'PLANE']
        if classification not in allowed_classes:
            return True  # Ignore: WALKER, BIRD, VEHICLE, CLUTTER, UNDECLARED, etc.
    else:
        # Fallback to old type field
        if track_type == 'BIRD':
            return True
        if track_type == 'CLUTTER':
            return True
        if track_type == 'WALKER':
            return True
        if track_type == 'VEHICLE':
            return True
    
    # Ignore low confidence detections
    if confidence < 0.3:
        return True
    
    # Ignore very distant unknowns with low confidence
    if range_m > 2500 and track_type == 'UNKNOWN' and confidence < 0.6:
        return True
    
    return False
```

**2. Updated `_calculate_threat_priority_score()` to extract and pass classification:**
```python
classification = track_data.get('classification', None)  # Multiclass classifier result

# TIER 2: FILTER NON-THREATS (Only UAV classes and PLANE)
if self._should_ignore_track(track_type, confidence, range_m, classification):
    return 0.0
```

## Logic Flow

```
Track Received
    ↓
Extract classification field
    ↓
Is classification in allowed list?
    ├─ YES → Continue to threat scoring
    └─ NO  → Return 0.0 (ignore track)
```

### Allowed List Check:
```python
allowed_classes = ['UAV', 'UAV_MULTI_ROTOR', 'UAV_FIXED_WING', 'PLANE']
```

## Impact

### Before:
- ❌ All tracks considered for prioritization
- ❌ Birds, walkers, vehicles could become "highest priority"
- ❌ Operator distracted by non-threats
- ❌ System resources wasted on irrelevant tracks

### After:
- ✅ Only aerial threats considered
- ✅ Ground-based targets ignored
- ✅ Birds and clutter filtered out
- ✅ Operator focuses on actual threats
- ✅ System resources optimized

## Use Cases

### C-UAS Mission (Counter-UAS)
**Goal**: Detect and track hostile drones

**Filtered Out**:
- ✅ Birds (not a threat)
- ✅ Walkers (ground personnel)
- ✅ Vehicles (ground transport)
- ✅ Clutter (environmental noise)

**Prioritized**:
- 🎯 UAV Multi-Rotor (primary threat)
- 🎯 UAV Fixed-Wing (primary threat)
- 🎯 UAV (general classification)

### Airspace Monitoring
**Goal**: Track all aerial vehicles

**Filtered Out**:
- ✅ Ground-based targets
- ✅ Environmental clutter

**Prioritized**:
- 🎯 All UAV types
- 🎯 Crewed aircraft (planes)

## Testing

### Scenario 5 (Stress Test)
With varied classifications, the system will now:

1. **Prioritize**:
   - UAV Multi-Rotor tracks
   - UAV Fixed-Wing tracks
   - Plane tracks

2. **Ignore**:
   - Walker tracks (even if close)
   - Bird tracks (even if fast)
   - Vehicle tracks (even if large RCS)
   - Clutter tracks
   - Undeclared tracks

### Expected Behavior:
```
25 tracks loaded:
- 8 UAV Multi-Rotor  → ✅ Considered
- 4 UAV Fixed-Wing   → ✅ Considered
- 3 Plane            → ✅ Considered
- 3 Bird             → ❌ Ignored
- 2 Walker           → ❌ Ignored
- 2 Clutter          → ❌ Ignored
- 1 Vehicle          → ❌ Ignored
- 2 Undeclared       → ❌ Ignored

Result: Only 15 tracks (UAV + Plane) compete for "highest priority"
```

## Backward Compatibility

The filter includes fallback logic for tracks without classification:
- Uses old `type` field if `classification` is not available
- Maintains existing behavior for legacy data
- Gracefully handles mixed data sources

## Configuration

This is a **hard-coded filter** in the threat prioritization algorithm. It cannot be changed via UI configuration.

**Rationale**: Threat prioritization is a safety-critical function that should not be user-configurable to prevent accidental misconfiguration.

## Future Enhancements

Potential additions:
1. **Configurable filter list** (admin-only)
2. **Mission-specific profiles** (C-UAS, Border Security, etc.)
3. **Dynamic weighting** based on classification confidence
4. **Threat class hierarchy** (UAV > Plane > Unknown)

## Files Modified

**`orchestration/bridge.py`**:
- Line 1052: Extract classification from track data
- Line 1072: Pass classification to filter
- Lines 1287-1317: Updated `_should_ignore_track()` method with classification-based filtering
