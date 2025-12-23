# Track Classification - Bug Fixes

## Issues Fixed

### 1. ✅ Classification Not Showing in UI
**Problem**: Scenario 5 showed only UAV, BIRD, and UNKNOWN - not the varied classifications (UAV_MULTI_ROTOR, UAV_FIXED_WING, WALKER, PLANE, VEHICLE, CLUTTER, UNDECLARED)

**Root Cause**: The `Track` class in `bridge.py` didn't expose the `classification` property to QML

**Fix**: Added `classification` property to Track class
```python
@Property(str, notify=dataChanged)
def classification(self):
    return self._data.get('classification', 'UNDECLARED')
```

**File**: `orchestration/bridge.py` line 45-47

---

### 2. ✅ Legend Overlapping "TACTICAL DISPLAY" Text
**Problem**: Track Class Legend was positioned at top-left (20px margin) which overlapped the "TACTICAL DISPLAY" header text

**Fix**: Moved legend down from 20px to 80px top margin
```qml
anchors.topMargin: 80  // Moved down to avoid "TACTICAL DISPLAY" text
```

**File**: `ui/Main.qml` line 1892

---

### 3. ✅ Legend Expanded by Default
**Problem**: Legend was expanded by default, taking up screen space

**Fix**: Changed default collapsed state to `true`
```qml
property bool collapsed: true  // Default to collapsed
```

**File**: `ui/components/TrackClassLegend.qml` line 17

---

### 4. ✅ Added Debug Output
**Enhancement**: Added classification breakdown to console when Scenario 5 loads

**Output Example**:
```
[ENGINE] Scenario 5: 25 tracks for stress testing
[ENGINE]   Velocities: 5-50 m/s (minimum enforced), mix of RADAR/RF/FUSED
[ENGINE]   Smooth motion with realistic maneuvering
[ENGINE]   Tracks stay in bounds (200-3000m) via boundary redirection
[ENGINE]   Classifications: {'UAV_MULTI_ROTOR': 8, 'UAV_FIXED_WING': 4, 'BIRD': 3, 'WALKER': 2, 'PLANE': 3, 'VEHICLE': 1, 'CLUTTER': 2, 'UNDECLARED': 2}
```

**File**: `engine/mock_engine_updated.py` lines 1038-1043

---

## Testing

1. **Run Application**
2. **Load Scenario 5**: Click TEST → Scenario 5
3. **Check Console**: Should see classification breakdown
4. **Check Display**: Tracks should have varied colors
5. **Check Legend**: Should be collapsed by default, positioned below header
6. **Expand Legend**: Click arrow to see all 9 classes
7. **Filter Classes**: Open Radar Config → Toggle classes on/off

## Expected Results

- ✅ Tracks show varied colors (red, orange, blue, yellow, cyan, purple, gray, white)
- ✅ Legend is collapsed by default
- ✅ Legend doesn't overlap "TACTICAL DISPLAY" text
- ✅ Console shows classification breakdown
- ✅ Filtering works (hiding/showing specific classes)

## Files Modified

1. `orchestration/bridge.py` - Added classification property
2. `ui/Main.qml` - Moved legend position
3. `ui/components/TrackClassLegend.qml` - Default collapsed
4. `engine/mock_engine_updated.py` - Added debug output
