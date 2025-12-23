# Simulated Track Dynamics - Increased Maneuverability

## Overview
Updated simulated tracks to exhibit more aggressive and frequent direction changes, making them more realistic and challenging for threat tracking and prioritization testing.

## Changes Made

### 1. ✅ UAV Tracks - More Aggressive Maneuvering

**Evasive Patterns**: UAVs now perform more dynamic maneuvers

#### Base Turn Rate
- **Before**: `-5° to +5°` per update
- **After**: `-10° to +10°` per update
- **Change**: **2x more dynamic** base turning

#### Sharp Turns (Course Corrections)
- **Frequency Before**: 15% chance per second
- **Frequency After**: 30% chance per second (**2x more frequent**)
- **Turn Angle Before**: `-20° to +20°`
- **Turn Angle After**: `-35° to +35°` (**75% sharper**)

#### Speed Variations
- **Frequency Before**: 10% chance per second
- **Frequency After**: 20% chance per second (**2x more frequent**)
- **Speed Change Before**: `±3 m/s`
- **Speed Change After**: `±5 m/s` (**67% larger**)

**Result**: UAVs now exhibit evasive maneuvering patterns similar to hostile drones attempting to avoid detection/tracking.

---

### 2. ✅ BIRD Tracks - More Erratic Behavior

**Natural Avian Patterns**: Birds now show more realistic erratic flight

#### Base Turn Rate
- **Before**: `-15° to +15°` per update
- **After**: `-20° to +20°` per update
- **Change**: **33% more dynamic**

#### Sharp Turns
- **Frequency Before**: 25% chance per second
- **Frequency After**: 35% chance per second (**40% more frequent**)
- **Turn Angle Before**: `-35° to +35°`
- **Turn Angle After**: `-45° to +45°` (**29% sharper**)

#### Speed Variations
- **Frequency Before**: 15% chance per second
- **Frequency After**: 25% chance per second (**67% more frequent**)
- **Speed Change Before**: `±5 m/s`
- **Speed Change After**: `±7 m/s` (**40% larger**)

**Result**: Birds now exhibit highly erratic, unpredictable flight patterns typical of avian targets.

---

### 3. ✅ UNKNOWN Tracks - More Unpredictable

**Erratic Behavior**: Unknown tracks are now more chaotic

#### Base Turn Rate
- **Before**: `-8° to +8°` per update
- **After**: `-12° to +12°` per update
- **Change**: **50% more dynamic**

**Result**: Unknown tracks are harder to predict and track.

---

## Comparison Table

| Track Type | Parameter | Before | After | Increase |
|------------|-----------|--------|-------|----------|
| **UAV** | Base Turn | ±5°/update | ±10°/update | **+100%** |
| | Sharp Turn Freq | 15%/sec | 30%/sec | **+100%** |
| | Sharp Turn Angle | ±20° | ±35° | **+75%** |
| | Speed Change Freq | 10%/sec | 20%/sec | **+100%** |
| | Speed Change | ±3 m/s | ±5 m/s | **+67%** |
| **BIRD** | Base Turn | ±15°/update | ±20°/update | **+33%** |
| | Sharp Turn Freq | 25%/sec | 35%/sec | **+40%** |
| | Sharp Turn Angle | ±35° | ±45° | **+29%** |
| | Speed Change Freq | 15%/sec | 25%/sec | **+67%** |
| | Speed Change | ±5 m/s | ±7 m/s | **+40%** |
| **UNKNOWN** | Base Turn | ±8°/update | ±12°/update | **+50%** |

---

## Visual Impact

### Before (Gentle Curves):
```
Track Path:
    ╱─────╲
   ╱       ╲
  │         │
   ╲       ╱
    ╲─────╱
```
**Predictable, smooth arcs**

### After (Aggressive Maneuvers):
```
Track Path:
    ╱╲  ╱─╲
   ╱  ╲╱   ╲╱╲
  │    ╲    ╱ │
   ╲   ╱╲  ╱  ╱
    ╲─╱  ╲╱──╱
```
**Unpredictable, sharp turns, evasive patterns**

---

## Testing Impact

### Threat Prioritization
- ✅ **More challenging** to track
- ✅ **Tests tau calculation** with rapid direction changes
- ✅ **Validates range rate** computation accuracy
- ✅ **Stresses tracking algorithms**

### Operator Training
- ✅ **Realistic evasive behavior** - trains operators for hostile drones
- ✅ **Difficult targeting** - requires lead prediction
- ✅ **Priority switching** - tracks change threat level dynamically
- ✅ **Visual tracking** - harder to follow on display

### System Performance
- ✅ **Kalman filter stress test** - rapid state changes
- ✅ **Prediction accuracy** - tests extrapolation
- ✅ **UI responsiveness** - frequent updates
- ✅ **Algorithm robustness** - handles erratic behavior

---

## Use Cases

### 1. C-UAS Training
**Scenario**: Hostile drone performing evasive maneuvers
- UAVs now exhibit realistic evasive patterns
- Operators must track and engage maneuvering targets
- Tests system's ability to maintain lock on agile threats

### 2. Algorithm Validation
**Scenario**: Stress testing threat prioritization
- Rapid direction changes test tau calculation
- Speed variations test range rate computation
- Validates that highest priority updates correctly

### 3. Sensor Fusion Testing
**Scenario**: Multiple sensors tracking same target
- Erratic behavior tests fusion algorithms
- Validates track association with rapid state changes
- Tests covariance updates with high dynamics

---

## Technical Details

### Turn Rate Calculation
```python
# Base continuous turn
turn_rate = random.uniform(-10, 10) * dt  # UAV

# Occasional sharp turn
if random.random() < 0.30 * dt * 30:  # 30% per second
    turn_rate += random.uniform(-35, 35) * dt  # Sharp maneuver
```

### Velocity Vector Rotation
```python
# Apply turn by rotating velocity vector
turn_rad = math.radians(turn_rate)
cos_turn = math.cos(turn_rad)
sin_turn = math.sin(turn_rad)
vx_new = vx * cos_turn - vy * sin_turn
vy_new = vx * sin_turn + vy * cos_turn
```

### Speed Variation
```python
# Random speed changes
if random.random() < 0.20 * dt * 30:  # 20% per second
    speed_change = random.uniform(-5, 5)  # ±5 m/s
    new_speed = max(5.0, current_speed + speed_change)
```

---

## Expected Behavior

### Scenario 5 (Stress Test)
With 25 tracks, you should now see:

1. **UAV Tracks**:
   - Zigzag patterns
   - Sudden direction changes
   - Speed variations
   - Evasive maneuvers

2. **Bird Tracks**:
   - Highly erratic paths
   - Circular/spiral patterns
   - Rapid turns
   - Unpredictable behavior

3. **Unknown Tracks**:
   - Moderate erratic behavior
   - Less predictable than before

### Visual Indicators:
- ✅ Track tails show curved/zigzag patterns
- ✅ Tracks don't move in straight lines
- ✅ Heading changes frequently
- ✅ Speed varies noticeably

---

## Files Modified

**`engine/mock_engine_updated.py`** (lines 423-478):
- Increased UAV base turn rate: 5° → 10°
- Increased UAV sharp turn frequency: 15% → 30%
- Increased UAV sharp turn angle: 20° → 35°
- Increased UAV speed change frequency: 10% → 20%
- Increased UAV speed change magnitude: 3 → 5 m/s
- Increased BIRD base turn rate: 15° → 20°
- Increased BIRD sharp turn frequency: 25% → 35%
- Increased BIRD sharp turn angle: 35° → 45°
- Increased BIRD speed change frequency: 15% → 25%
- Increased BIRD speed change magnitude: 5 → 7 m/s
- Increased UNKNOWN base turn rate: 8° → 12°

---

## Future Enhancements

Potential additions:
1. **Altitude changes** - 3D evasive maneuvers
2. **Formation flying** - Multiple UAVs coordinated
3. **Approach patterns** - Direct vs. circling
4. **Acceleration profiles** - Realistic motor dynamics
5. **Wind effects** - Environmental factors
