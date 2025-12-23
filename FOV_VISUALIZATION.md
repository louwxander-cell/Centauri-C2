# Radar FOV Visualization on Tactical Display

## Overview

The tactical display now shows the **actual configured radar field of view** (FOV) based on the radar configuration settings. The FOV wedge updates automatically when configuration changes are applied.

## Features

### ✅ **Dynamic FOV Wedge**
- Displays radar search azimuth FOV on tactical display
- Updates in real-time when configuration changes
- Matches actual radar configuration (not hardcoded)
- Subtle cyan wedge with glow effect

### ✅ **FOV Info Box**
- Shows current azimuth range (e.g., "-60° to 60°")
- Displays total FOV angle (e.g., "120°")
- Appears when radar is enabled (standby or online)
- Located bottom-left of tactical display

### ✅ **Automatic Updates**
- FOV refreshes when radar connects
- Updates immediately when configuration is applied
- Reflects live radar settings

## Visual Elements

### FOV Wedge

The wedge on the tactical display shows:

```
         0° (North)
           |
    -60° ← | → +60°
      \    |    /
       \   |   /
        \  |  /
         \ | /
          \|/
           ●  (Ownship)
```

**Properties:**
- **Fill**: Very light transparent cyan (3% opacity)
- **Border**: Ultra-thin cyan line (0.5px, 25% opacity)
- **Glow**: Subtle drop shadow effect
- **Dynamic**: Adjusts based on `search_az_min` and `search_az_max`

### FOV Info Box

Located bottom-left corner:

```
┌─────────────────────┐
│ RADAR FOV           │
├─────────────────────┤
│ Az:   -60° to 60°   │
│ Total: 120°         │
└─────────────────────┘
```

**Properties:**
- **Visibility**: Only when radar is standby or online
- **Background**: Semi-transparent dark (90% opacity)
- **Text**: Cyan monospace for values
- **Size**: 180x85 pixels

## How It Works

### Configuration Flow

```
User Changes FOV in Config Dialog
         ↓
Configuration Applied to Radar
         ↓
UI Updates FOV Canvas Properties
         ↓
Canvas Repaints with New FOV
         ↓
Info Box Updates Automatically
```

### Technical Implementation

#### 1. FOV Canvas Properties

```qml
Canvas {
    id: fovCanvas
    
    property var radarConfig: ({
        search_az_min: -60,
        search_az_max: 60
    })
    
    property real azMin: radarConfig.search_az_min || -60
    property real azMax: radarConfig.search_az_max || 60
    property real fovAngleTotal: azMax - azMin
    property real fovCenter: (azMin + azMax) / 2
}
```

#### 2. Configuration Update Handler

```qml
onConfigurationChanged: (newConfig) => {
    var success = bridge.configure_radar(newConfig)
    if (success) {
        // Update FOV display
        fovCanvas.radarConfig = newConfig
        fovCanvas.requestPaint()
    }
}
```

#### 3. Radar Status Connection

```qml
Connections {
    target: systemStatus
    function onRadarStatusChanged() {
        if (systemStatus.radarStatus === "online") {
            fovCanvas.radarConfig = bridge.get_radar_config()
            fovCanvas.requestPaint()
        }
    }
}
```

## Usage Examples

### Example 1: Default FOV (120°)

**Configuration:**
- Search Az Min: -60°
- Search Az Max: 60°
- Total FOV: 120°

**Display:**
- Wedge spans 120° centered on vehicle heading
- Info box shows: "Az: -60° to 60°, Total: 120°"

### Example 2: Wide FOV (180°)

**Configuration:**
- Search Az Min: -90°
- Search Az Max: 90°
- Total FOV: 180°

**Display:**
- Wedge spans 180° (half circle)
- Info box shows: "Az: -90° to 90°, Total: 180°"

### Example 3: Narrow FOV (60°)

**Configuration:**
- Search Az Min: -30°
- Search Az Max: 30°
- Total FOV: 60°

**Display:**
- Wedge spans 60° (narrow cone)
- Info box shows: "Az: -30° to 30°, Total: 60°"

### Example 4: Asymmetric FOV (90°)

**Configuration:**
- Search Az Min: -20°
- Search Az Max: 70°
- Total FOV: 90°

**Display:**
- Wedge spans 90° offset to the right
- Center at +25° from vehicle heading
- Info box shows: "Az: -20° to 70°, Total: 90°"

## Testing Workflow

### Test 1: Verify Initial FOV

1. Start application
2. Radar shows ORANGE (standby)
3. Check tactical display shows 120° FOV wedge
4. Verify info box shows: "Az: -60° to 60°, Total: 120°"

### Test 2: Change FOV While Offline

1. Radar is ORANGE (standby)
2. Click ECHOGUARD → "Configure..."
3. Change Search Az Max: 60° → 90°
4. Click OK
5. Verify wedge expands to 150° total
6. Verify info box shows: "Az: -60° to 90°, Total: 150°"

### Test 3: Change FOV While Online

1. Connect radar (GREEN)
2. Click ECHOGUARD → "Configure..."
3. Change Search Az Min: -60° → -45°
4. Change Search Az Max: 60° → 45°
5. Click OK
6. Verify wedge narrows to 90° total
7. Verify info box shows: "Az: -45° to 45°, Total: 90°"
8. Verify radar continues streaming

### Test 4: Verify FOV After Reconnect

1. Disconnect radar
2. Reconnect radar
3. Verify FOV wedge matches last configured settings
4. Open config dialog to confirm values match display

## Console Output

### FOV Update on Configuration Change

```
[UI] Applying radar configuration...
[BRIDGE] Radar configuration requested
[BRIDGE] Applying configuration: {'search_az_min': -90, 'search_az_max': 90, ...}
[BRIDGE] [OK] Radar configuration applied
[UI] ✓ Radar configuration applied successfully
[UI] FOV display updated
```

### FOV Update on Radar Connect

```
[UI] Radar connect requested
[BRIDGE] Radar connect requested
[BRIDGE] Connected to radar command port
[BRIDGE] Radar initialized
[BRIDGE] [OK] Radar started and streaming
[UI] Connect result: true
[SystemStatus] radarStatusChanged: online
[FOV] Configuration loaded: {search_az_min: -60, search_az_max: 60}
```

## Benefits

### 1. **Situational Awareness**
- Operators see exactly where radar is looking
- No guessing about coverage area
- Immediate visual feedback on FOV changes

### 2. **Mission Planning**
- Visualize coverage before connecting
- Adjust FOV to match threat vectors
- Optimize for specific scenarios

### 3. **Configuration Validation**
- Verify FOV settings are correct
- Spot configuration errors immediately
- Confirm changes were applied

### 4. **Training**
- New operators understand FOV concept
- Visual learning of radar coverage
- Experimentation with different FOVs

## Technical Details

### FOV Calculation

```javascript
// Extract config values
azMin = radarConfig.search_az_min  // e.g., -60
azMax = radarConfig.search_az_max  // e.g., 60

// Calculate total FOV and center
fovAngleTotal = azMax - azMin      // e.g., 120
fovCenter = (azMin + azMax) / 2    // e.g., 0

// Convert to radians for drawing
radarPointingRad = (vehicleHeading + fovCenter - 90) * PI / 180
fovAngle = fovAngleTotal * PI / 180

// Draw arc
ctx.arc(centerX, centerY, radius,
        radarPointingRad - fovAngle/2,
        radarPointingRad + fovAngle/2)
```

### Coordinate System

```
Canvas Coordinates:
- 0° = East (right)
- 90° = South (down)
- 180° = West (left)
- 270° = North (up)

Radar Coordinates:
- 0° = North (forward)
- 90° = East (right)
- 180° = South (back)
- 270° = West (left)

Conversion: canvasAngle = radarAngle - 90
```

## Files Modified

1. **`ui/Main.qml`**
   - Updated `fovCanvas` to use radar configuration (lines 1115-1195)
   - Added FOV info box (lines 1533-1601)
   - Added FOV update on configuration change (lines 2138-2143)
   - Added radar status connection for FOV refresh (lines 1130-1139)

## Limitations

### Current Implementation

- **Azimuth Only**: Shows horizontal FOV, not elevation
- **Search FOV**: Uses search FOV, not track FOV
- **2D Display**: Elevation angle not visualized
- **Static Range**: FOV wedge extends to display edge

### Not Implemented

- Elevation FOV visualization (would require 3D view)
- Range-limited FOV (min/max range boundaries)
- Track FOV overlay (separate from search FOV)
- FOV animation during scan

## Future Enhancements

- [ ] Add elevation FOV indicator (side view)
- [ ] Show range min/max boundaries on FOV
- [ ] Display both search and track FOV
- [ ] Add FOV animation/sweep effect
- [ ] Color-code FOV by radar mode
- [ ] Show detection probability heatmap
- [ ] Add FOV sector labels (left/center/right)
- [ ] Display blind spots and coverage gaps

## Comparison: Before vs After

### Before
- Fixed 120° FOV wedge
- Hardcoded in QML
- No connection to radar config
- No info display

### After
- **Dynamic FOV** based on actual config
- **Live updates** when config changes
- **Info box** shows current settings
- **Automatic refresh** on radar connect

## Summary

The FOV visualization system provides:

✅ **Real-time visual feedback** of radar coverage  
✅ **Automatic updates** when configuration changes  
✅ **Clear info display** with azimuth range and total angle  
✅ **Professional appearance** with subtle styling  
✅ **Integrated workflow** with configuration system  

Operators can now **see exactly where the radar is looking** and verify FOV settings at a glance.
