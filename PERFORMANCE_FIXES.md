# Performance Optimization Summary

**Date:** December 8, 2025  
**Issue:** UI jitter that gets worse over time

---

## Root Causes Identified

### 1. Excessive Console Output
- Bridge was printing debug info every 1.5 seconds
- Gunner interface printing periodically
- Console I/O causes main thread blocking

### 2. Track Tail Memory Growth
- Track tails were set to 15 seconds
- At 30 Hz updates, that's 450 points per track
- With 25 tracks in test scenario = 11,250 points being processed
- No hard limit, could grow indefinitely

### 3. High Update Frequency
- Original: 30 Hz (33ms interval)
- Too fast for complex UI with many tracks
- CPU/GPU couldn't keep up over time

---

## Fixes Applied

### 1. Disabled Debug Console Output
```python
# Commented out periodic debug printing in bridge.py
# Was printing every 50 iterations (~1.5 sec at 30Hz)
```

### 2. Reduced Track Tail Duration
```python
self.track_tail_duration = 5.0  # Reduced from 15 seconds
```

### 3. Hard Limit on Tail Points
```python
# Limit max tail length to prevent memory issues
if len(self.track_tails[track_id]) > 200:
    self.track_tails[track_id] = self.track_tails[track_id][-150:]
```

### 4. Reduced Update Frequency
```python
self.update_timer.start(50)  # 20 Hz (50ms) - was 33ms (30 Hz)
```

---

## Track Tail Fading Issue

**Status:** NOT IMPLEMENTED in QML

The track tails (position history trails) are calculated in the Python backend but:
- ❌ **Not rendered in the current QML UI**
- ❌ **No fading visualization exists**

### To Implement Track Tails:

Would need to add to QML radar display:
```qml
// For each track
Repeater {
    model: track.tail  // Array of position history
    delegate: Rectangle {
        // Position at historical location
        x: calculateX(modelData.az, modelData.range)
        y: calculateY(modelData.el, modelData.range)
        
        // Fade based on age
        opacity: 1.0 - (currentTime - modelData.time) / tailDuration
        
        width: 2
        height: 2
        radius: 1
        color: Theme.accentCyan
    }
}
```

This requires modification of `ui/Main.qml` radar canvas section.

---

## Engage/Disengage Button Status

### Added Debug Output
```python
@Slot(int, str, result='QVariant')
def engage_track(self, track_id: int, operator_id: str):
    print(f"[BRIDGE] engage_track called: track_id={track_id}, operator={operator_id}")
    ...

@Slot(result='QVariant')
def disengage_track(self):
    print(f"[BRIDGE] disengage_track called, current engaged={self.engaged_track_id_value}")
    ...
```

**To Debug:**
- Click ENGAGE button
- Check console for `[BRIDGE] engage_track called`
- If message appears → Python function is called, check QML state update
- If no message → QML not calling Python, check QML MouseArea/button bindings

---

## Current Performance

### Before Fixes:
- **Update Rate:** 30 Hz
- **Console Output:** Every 1.5 sec
- **Track Tails:** 15 sec × 30 Hz = 450 points/track
- **Result:** Smooth initially, jitter increases over time

### After Fixes:
- **Update Rate:** 20 Hz (33% reduction in processing)
- **Console Output:** Disabled
- **Track Tails:** 5 sec × 20 Hz = 100 points/track max (hard capped at 150)
- **Result:** Should be consistently smooth

---

## Additional Optimizations (If Needed)

### 1. Further Reduce Update Rate
```python
self.update_timer.start(100)  # 10 Hz if 20 Hz still has jitter
```

### 2. Reduce Track Count in Test Scenarios
```python
# In engine, use scenario_3 (5 tracks) instead of scenario_5 (25 tracks)
```

### 3. Disable Gunner Interface
```python
bridge = OrchestrationBridge(engine, enable_gunner_interface=False)
```

### 4. Profile QML Rendering
Add to QML:
```qml
Window {
    // Enable QML profiling
    Component.onCompleted: {
        console.log("FPS:", Qt.application.active ? "Active" : "Inactive")
    }
}
```

---

## Testing Checklist

- [ ] Run for 2+ minutes - does jitter still worsen?
- [ ] CPU usage in Task Manager - should be <30%
- [ ] Memory usage - should stabilize, not grow
- [ ] Engage button - prints `[BRIDGE] engage_track called`
- [ ] Disengage button - prints `[BRIDGE] disengage_track called`

---

## Known Issues

1. **Track tails don't fade** - Not implemented in QML (by design)
2. **Disengage button may not work** - Needs QML debugging
3. **Jitter may still occur** - Monitor for 2+ minutes to confirm

---

## Next Steps

1. **Test current fixes** - Run for 2+ minutes
2. **Debug engage buttons** - Check console output when clicking
3. **Implement track tail rendering** - If desired (requires QML work)
4. **Enable radar integration** - Once UI is stable (set `radar.enabled=true` in config)
