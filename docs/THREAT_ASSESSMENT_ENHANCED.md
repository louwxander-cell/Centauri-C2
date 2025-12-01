# Enhanced Threat Assessment System

## Overview

Advanced multi-factor threat scoring with vector analysis, trajectory prediction, and swarm detection.

**Status:** ✅ Implemented and tested  
**Location:** `/src/threat_assessment/`  
**Demo:** `demo_threat_assessment.py`

---

## Key Features

### 1. **Vector Analysis** 🎯
- **Approach angle calculation** - Determines if threat is head-on, quartering, crossing, or parallel
- **Collision course detection** - Identifies threats on direct intercept path
- **Closing velocity** - True 3D radial velocity toward ownship

### 2. **Trajectory Prediction** 📈
- **10-second prediction** - Where will threat be in 10s?
- **30-second prediction** - Extended prediction for planning
- **Predicted range** - Future distance for engagement timing

### 3. **Elevation Threat Modeling** ⬇️
- **Ground-hugging (<5°)** - Maximum threat (terrain masking)
- **Low altitude (<15°)** - High threat (pop-up attacks)
- **Medium/High altitude** - Lower threat (easier to track)

### 4. **Swarm Detection** 🐝
- **Automatic clustering** - Detects multiple coordinated threats
- **Configurable radius** - Default 200m grouping
- **Minimum swarm size** - Default 3 threats

### 5. **Clear Threat Levels** 🚦
```
🔴 CRITICAL  - <100m, immediate action
🟠 SEVERE    - 100-300m, engage recommended  
🟡 HIGH      - 300-600m, track closely
🔵 MEDIUM    - 600-1000m, monitor
🟢 LOW       - 1000-1500m, awareness
⚪ MINIMAL   - >1500m, distant
```

### 6. **Engagement Recommendations** ⚔️
- **Automatic engage/hold recommendations**
- **Urgency messages** for operators
- **Time-to-impact warnings**

---

## Configuration

All parameters are tunable via `ThreatConfig`:

```python
from src.threat_assessment import ThreatConfig, AdvancedThreatAssessor

# Custom configuration
config = ThreatConfig(
    critical_range=100.0,        # meters
    fast_approach_threshold=30.0, # m/s
    tau_critical=10.0,           # seconds
    swarm_radius=200.0,          # meters
    # ... and more
)

assessor = AdvancedThreatAssessor(config)
```

---

## Usage Example

```python
from src.threat_assessment import AdvancedThreatAssessor

assessor = AdvancedThreatAssessor()

track_data = {
    'id': 1001,
    'range_m': 250.0,
    'azimuth_deg': 0.0,
    'elevation_deg': 5.0,
    'velocity_x_mps': 0.0,
    'velocity_y_mps': -35.0,  # Approaching
    'velocity_z_mps': 0.0,
    'confidence': 0.9
}

assessment = assessor.assess_threat(track_data)

print(f"Threat Level: {assessment.level}")
print(f"Score: {assessment.score:.3f}")
print(f"Time to Impact: {assessment.time_to_impact}s")
print(f"Collision Course: {assessment.collision_course}")
print(f"Engage: {assessment.engage_recommended}")
print(f"Message: {assessment.urgency_message}")
```

---

## Integration with Existing System

The enhanced system **complements** the existing threat scoring in `bridge.py`:

### Option 1: Parallel System (Recommended for now)
- Keep existing `_calculate_threat_priority_score()` for UI sorting
- Use `AdvancedThreatAssessor` for detailed analysis and recommendations
- Best for testing before full integration

### Option 2: Replace Existing
- Swap out current algorithm with enhanced version
- Requires testing to ensure UI compatibility
- Can be done incrementally

### Option 3: Hybrid
- Use existing for quick scoring
- Call enhanced for detailed threat analysis on high-priority tracks
- Best of both worlds

---

## Improvements Over Current System

| Feature | Current | Enhanced |
|---------|---------|----------|
| **Vector Analysis** | Range rate only | ✅ Full 3D approach angle |
| **Collision Detection** | Implicit | ✅ Explicit collision course flag |
| **Trajectory Prediction** | None | ✅ 10s and 30s predictions |
| **Elevation Modeling** | Basic | ✅ Terrain-masking detection |
| **Swarm Detection** | None | ✅ Automatic clustering |
| **Recommendations** | Score only | ✅ Engage/hold + urgency |
| **Configuration** | Hardcoded | ✅ Fully configurable |

---

## Test Results

**Demo Scenarios:**
1. ✅ Close fast-approaching UAV → **CRITICAL** (Score: 0.797)
2. ✅ Collision course medium range → **HIGH** (Score: 0.622)
3. ✅ Hovering close range → **LOW** (Score: 0.289)
4. ✅ Perpendicular crossing → **LOW** (Score: 0.236)
5. ✅ Receding track → **MEDIUM** (Score: 0.470)
6. ✅ Distant slow mover → **LOW** (Score: 0.280)
7. ✅ Swarm detection → 3 threats grouped

---

## Next Steps

### Integration Path:
1. ✅ **Phase 1 Complete** - Standalone module working
2. **Phase 2** - Add to bridge for parallel operation
3. **Phase 3** - UI enhancements to show trajectory predictions
4. **Phase 4** - Full replacement of existing algorithm

### Recommended Immediate Actions:
- Test with real sensor data (when available)
- Tune `ThreatConfig` parameters for your operational environment
- Add trajectory visualization to tactical display
- Integrate swarm alerts into UI

---

## API Reference

### Main Classes

#### `AdvancedThreatAssessor`
Main threat assessment engine.

**Methods:**
- `assess_threat(track_data, ownship_position)` → `ThreatAssessment`
- `detect_swarms(all_tracks)` → `List[List[int]]`

#### `ThreatAssessment`
Complete threat analysis output (dataclass).

**Key Fields:**
- `score`: float (0.0-1.0)
- `level`: ThreatLevel enum
- `time_to_impact`: Optional[float]
- `collision_course`: bool
- `approach_angle`: float
- `predicted_range_10s`: float
- `engage_recommended`: bool
- `urgency_message`: str

#### `ThreatConfig`
Configuration parameters (dataclass).

**Key Fields:**
- `critical_range`: float
- `fast_approach_threshold`: float
- `tau_critical`: float
- `swarm_radius`: float
- Weights for multi-factor scoring

#### `ThreatLevel`
Enum of threat classifications.

**Values:**
- `CRITICAL`, `SEVERE`, `HIGH`, `MEDIUM`, `LOW`, `MINIMAL`

---

## Performance

- **Assessment time:** <1ms per track (Python)
- **Swarm detection:** O(n²) for n tracks
- **Memory:** Minimal (no history stored by default)

---

## Future Enhancements

1. **Machine learning integration** - Train on historical engagement data
2. **Probabilistic prediction** - Confidence bounds on trajectories
3. **Multi-track coordination** - Predict coordinated maneuvers
4. **Terrain integration** - Use elevation maps for true ground-hugging detection
5. **Weather effects** - Wind drift compensation

---

**Questions or issues?** See `/demo_threat_assessment.py` for working examples.
