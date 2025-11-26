# TriAD C2 Operator Quick Reference Guide

## Starting the System

### Method 1: Direct Python
```bash
cd /path/to/TriAD_C2
python3 main.py
```

### Method 2: Launch Script
```bash
cd /path/to/TriAD_C2
./run.sh
```

## System Startup Sequence

1. **Initialization** (2-3 seconds)
   - Signal bus initialization
   - Driver thread creation
   - UI window creation

2. **Driver Startup**
   - Radar Driver → ONLINE (green)
   - RF Driver → ONLINE (green)
   - GPS Driver → ONLINE (green)
   - RWS Driver → STANDBY (orange)

3. **Operational**
   - Tracks appear in left panel
   - Radar scope shows moving targets
   - System ready for engagement

## User Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  TriAD Counter-UAS C2 System                                    │
├───────────────┬─────────────────────────┬───────────────────────┤
│               │                         │                       │
│  TRACK LIST   │     RADAR SCOPE         │   SYSTEM STATUS       │
│               │                         │                       │
│  ID | Range   │         ╱│╲             │  Radar: ONLINE        │
│  1  | 500m    │        ╱ │ ╲            │  RF: ONLINE           │
│  2  | 800m    │       ╱  │  ╲           │  GPS: ONLINE          │
│  3  | 1100m   │      ╱   ●   ╲          │  RWS: STANDBY         │
│               │     ╱    │    ╲         │                       │
│               │    ╱     │     ╲        │  Ownship:             │
│               │   ╱      │      ╲       │  Lat: 37.7749°        │
│               │  ╱       │       ╲      │  Lon: -122.4194°      │
│               │ ╱        │        ╲     │  Heading: 045°        │
│               │╱─────────┼─────────╲    │                       │
│               │          │          │   │                       │
├───────────────┴─────────────────────────┴───────────────────────┤
│  Selected: Track 1 | DRONE | Range: 500m | Az: 045°             │
│                                    [🎯 ENGAGE / SLEW]           │
└─────────────────────────────────────────────────────────────────┘
```

## Track List Columns

| Column | Description | Example |
|--------|-------------|---------|
| **ID** | Unique track identifier | 1, 2, 3, 100, 1000 |
| **Range (m)** | Distance to target in meters | 500, 1200 |
| **Azimuth (°)** | Bearing from north (0-360°) | 45.0, 180.5 |
| **Type** | Target classification | DRONE, BIRD, UNKNOWN |
| **Source** | Originating sensor | RADAR, RF, FUSED |
| **Conf** | Classification confidence | 0.80, 0.95 |

## Track Color Coding

| Color | Meaning | Symbol |
|-------|---------|--------|
| 🔴 **Red** | Drone target | Highest threat |
| 🔵 **Blue** | Bird (non-threat) | Low priority |
| 🟠 **Orange** | Unknown target | Investigate |
| 🟣 **Magenta** | Fused track | Multi-sensor confirmed |

## Operating Procedures

### 1. Track Selection

**Action**: Click on any row in the track list

**Result**:
- Row highlights in blue
- Selected track info appears at bottom
- Engage button becomes active (red)
- Track details displayed

### 2. Target Engagement

**Prerequisites**:
- Track must be selected
- RWS must be ONLINE or STANDBY
- Engage button must be enabled

**Procedure**:
1. Select target track in list
2. Verify track information
3. Click **"🎯 ENGAGE / SLEW"** button
4. System sends slew command to RWS
5. Status bar shows confirmation

**Example Output**:
```
SLEW COMMAND: Track 1 | Az: 45.0° | El: 10.0°
```

### 3. Monitoring System Status

**Sensor Status Indicators**:
- 🟢 **ONLINE**: Sensor operational, receiving data
- 🟠 **STANDBY**: System ready but not active
- 🔴 **OFFLINE**: Sensor not responding

**Check Regularly**:
- All sensors should be ONLINE during operations
- Track count should update continuously
- Ownship position should change (if vehicle moving)

### 4. Track Interpretation

**Track ID Ranges**:
- `1-99`: Radar tracks
- `100-199`: RF tracks
- `1000+`: Fused tracks (multi-sensor)

**Confidence Levels**:
- `0.9-1.0`: Very high confidence
- `0.7-0.9`: High confidence
- `0.5-0.7`: Medium confidence
- `< 0.5`: Low confidence

**Source Interpretation**:
- **RADAR**: Good position, may misclassify
- **RF**: Good classification, poor range
- **FUSED**: Best of both sensors

## Common Scenarios

### Scenario 1: Single Drone Detection

```
Track List:
ID | Range | Azimuth | Type  | Source | Conf
1  | 500m  | 45.0°   | DRONE | RADAR  | 0.75
100| 520m  | 46.0°   | DRONE | RF     | 0.92
1000| 510m | 45.5°   | DRONE | FUSED  | 0.95
```

**Interpretation**:
- Radar detected drone at 500m
- RF confirmed drone at similar position
- System fused tracks → Track 1000
- **Action**: Select Track 1000 (highest confidence)

### Scenario 2: Multiple Targets

```
Track List:
ID | Range | Azimuth | Type    | Source | Conf
1  | 500m  | 45.0°   | DRONE   | RADAR  | 0.80
2  | 800m  | 120.0°  | UNKNOWN | RADAR  | 0.60
3  | 1100m | 240.0°  | DRONE   | RADAR  | 0.75
```

**Interpretation**:
- Three distinct targets
- Track 1 and 3 classified as drones
- Track 2 unknown (investigate)
- **Action**: Prioritize Track 1 (closest drone)

### Scenario 3: Bird vs Drone

```
Track List:
ID | Range | Azimuth | Type | Source | Conf
1  | 300m  | 90.0°   | BIRD | RADAR  | 0.85
2  | 600m  | 180.0°  | DRONE| FUSED  | 0.92
```

**Interpretation**:
- Track 1 is likely a bird (high confidence)
- Track 2 is confirmed drone (fused, high confidence)
- **Action**: Engage Track 2, ignore Track 1

## Troubleshooting

### Problem: No Tracks Appearing

**Check**:
1. Radar status → Should be ONLINE
2. RF status → Should be ONLINE
3. Console output → Look for errors

**Solution**:
- Restart application
- Check network connections (production)
- Verify sensor power (production)

### Problem: Tracks Disappearing

**Cause**: Track timeout (5 seconds without update)

**Normal Behavior**:
- Tracks automatically removed when stale
- Prevents display of old data

**If Excessive**:
- Check sensor update rates
- Verify network stability (production)

### Problem: Engage Button Disabled

**Causes**:
1. No track selected → Select a track
2. RWS offline → Check RWS status
3. System error → Check console

**Solution**:
- Click on a track in the list
- Verify RWS is STANDBY or ONLINE

### Problem: Inaccurate Track Positions

**Mock Mode**: Expected behavior (simulated data)

**Production Mode**:
1. Check sensor calibration
2. Verify ownship position accuracy
3. Review fusion parameters

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Ctrl+C** | Emergency shutdown |
| **Esc** | Deselect track |
| **↑/↓** | Navigate track list |
| **Enter** | Engage selected track |

## Emergency Procedures

### Emergency Stop

**Action**: Press **Ctrl+C** in terminal

**Result**:
- All drivers stop immediately
- Threads terminate gracefully
- Application exits

**Use When**:
- System malfunction
- Unauthorized operation
- Safety concern

### System Restart

```bash
# Stop application (Ctrl+C)
# Wait 3 seconds
# Restart
python3 main.py
```

## Performance Indicators

### Normal Operation

- **Track Updates**: 10 per second (radar)
- **UI Refresh**: Smooth, no lag
- **CPU Usage**: < 20%
- **Memory**: < 200 MB

### Degraded Performance

- **Symptoms**: Laggy UI, delayed updates
- **Causes**: Too many tracks, system overload
- **Action**: Restart application, check system resources

## Data Interpretation

### Range Accuracy

| Sensor | Typical Accuracy |
|--------|------------------|
| Radar | ±10m |
| RF | ±200m |
| Fused | ±5m |

### Azimuth Accuracy

| Sensor | Typical Accuracy |
|--------|------------------|
| Radar | ±1° |
| RF | ±5° |
| Fused | ±0.5° |

### Update Rates

| Sensor | Rate | Latency |
|--------|------|---------|
| Radar | 10 Hz | 100ms |
| RF | 2 Hz | 500ms |
| GPS | 1 Hz | 1000ms |

## Best Practices

### 1. Pre-Mission Checks
- ✅ All sensors ONLINE
- ✅ GPS lock acquired
- ✅ RWS responding
- ✅ Clear radar scope

### 2. During Operations
- 👁️ Monitor sensor status continuously
- 🎯 Prioritize fused tracks over single-sensor
- 📊 Check confidence levels before engagement
- 🔄 Refresh track selection regularly

### 3. Post-Mission
- 📝 Review engagement log
- 🔍 Analyze track data
- 🛠️ Report any anomalies
- 💾 Save mission data (future feature)

## Support Contacts

**Technical Issues**: TriAD Development Team  
**Operational Questions**: System Administrator  
**Emergency**: Follow standard protocols

---

## Quick Command Reference

```bash
# Start system
python3 main.py

# Run tests
pytest tests/ -v

# Check dependencies
pip3 list | grep -E 'PyQt6|pydantic|pyqtgraph'

# View logs (future)
tail -f logs/triad_c2.log
```

## Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 🟢 ONLINE | Operational | Continue |
| 🟠 STANDBY | Ready | Normal |
| 🔴 OFFLINE | Not responding | Investigate |
| ⚠️ ERROR | Malfunction | Restart |

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Classification**: UNCLASSIFIED // FOR TRAINING USE ONLY
