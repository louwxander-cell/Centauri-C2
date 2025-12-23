# Radar Configuration Guide

## Overview

The radar configuration system allows operators to adjust EchoGuard radar settings through an intuitive UI dialog. Settings are organized by category and some are restricted based on radar connection status.

## Accessing Configuration

1. **Click** the ECHOGUARD status indicator (orange or green)
2. **Select** "Configure..." from the dropdown menu
3. **Configuration dialog** opens with current settings

## Configuration Categories

### 1. Basic Settings (Offline Only)

These settings can only be changed when radar is **disconnected** (standby/offline):

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| **Label** | Radar identifier | R1 | Text |
| **IPv4 Address** | Radar IP address | 192.168.1.25 | Valid IP |
| **Product Mode** | Radar model | EchoGuard | EchoGuard/EchoFlight/EchoDrone |
| **Mission Set** | Mission profile | cUAS | cUAS/Surveillance/Tracking |

### 2. Platform Position (Offline Only)

Radar physical location - **read-only when online**:

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| **Latitude (°)** | GPS latitude | -25.848810 | -90 to 90 |
| **Longitude (°)** | GPS longitude | 28.997978 | -180 to 180 |
| **Altitude (m)** | Height above sea level | 1.4 | -500 to 10000 |
| **Heading (°)** | Platform heading | 30.0 | 0 to 360 |

### 3. Platform Orientation (Offline Only)

Radar mounting angles - **read-only when online**:

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| **Pitch (°)** | Forward/backward tilt | 19.8 | -90 to 90 |
| **Roll (°)** | Left/right tilt | -0.3 | -180 to 180 |

### 4. Range Settings (Editable Anytime)

Detection range limits - **can edit while online**:

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| **Range Min (m)** | Minimum detection range | 21 | 10 to 1000 |
| **Range Max (m)** | Maximum detection range | 500 | 100 to 5000 |

### 5. Search Field of View (Editable Anytime)

Search scan area - **can edit while online**:

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| **Search Az Min (°)** | Left azimuth limit | -60 | -180 to 0 |
| **Search Az Max (°)** | Right azimuth limit | 60 | 0 to 180 |
| **Search El Min (°)** | Lower elevation limit | -40 | -90 to 0 |
| **Search El Max (°)** | Upper elevation limit | 40 | 0 to 90 |

### 6. Track Field of View (Editable Anytime)

Track confirmation area - **can edit while online**:

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| **Track Az Min (°)** | Left azimuth limit | -60 | -180 to 0 |
| **Track Az Max (°)** | Right azimuth limit | 60 | 0 to 180 |
| **Track El Min (°)** | Lower elevation limit | -40 | -90 to 0 |
| **Track El Max (°)** | Upper elevation limit | 40 | 0 to 90 |

### 7. Frequency (Offline Only)

RF channel selection - **read-only when online**:

| Setting | Description | Default | Options |
|---------|-------------|---------|---------|
| **Freq Channel** | Operating frequency | 0 | 0, 1, 2, 3, 4 |

## Configuration Workflow

### Scenario 1: Configure Before Connection

**Best Practice** - Configure all settings before connecting:

1. Ensure radar is **ORANGE** (standby)
2. Click ECHOGUARD → "Configure..."
3. Adjust **all settings** as needed
4. Click **OK** to save
5. Click ECHOGUARD → "Connect"
6. Radar connects with new configuration

### Scenario 2: Adjust While Online

**Dynamic Adjustment** - Change FOV and range while streaming:

1. Radar is **GREEN** (online and streaming)
2. Click ECHOGUARD → "Configure..."
3. Notice: Basic settings are **grayed out**
4. Adjust **Search/Track FOV** or **Range** settings
5. Click **OK** to apply
6. Changes take effect immediately
7. Radar continues streaming with new FOV

### Scenario 3: Change Basic Settings

**Requires Disconnect** - To change IP, position, or frequency:

1. Radar is **GREEN** (online)
2. Click ECHOGUARD → "Disconnect"
3. Radar becomes **ORANGE** (standby)
4. Click ECHOGUARD → "Configure..."
5. All settings now **editable**
6. Make changes and click **OK**
7. Click ECHOGUARD → "Connect"
8. Radar reconnects with new settings

## Status Indicators in Dialog

### Blue Info Box (Radar Offline)
```
ℹ Radar Offline
All settings can be changed when radar is offline.
```
- All fields are **editable**
- Changes saved to configuration
- Applied on next connection

### Yellow Warning Box (Radar Online)
```
⚠ Radar Online
Some settings cannot be changed while radar is streaming.
```
- Basic settings are **grayed out**
- FOV and range settings remain **editable**
- Changes applied immediately

## Field of View Visualization

### Azimuth (Horizontal)
```
        0° (Forward)
         |
   -60° ← → +60°
    Left   Right
```

### Elevation (Vertical)
```
    +40° (Up)
      |
      0° (Horizon)
      |
    -40° (Down)
```

### Typical FOV Configurations

**Wide Area Surveillance:**
- Az: -90° to +90° (180° coverage)
- El: -20° to +60° (80° coverage)

**Focused Tracking:**
- Az: -30° to +30° (60° coverage)
- El: -10° to +40° (50° coverage)

**Perimeter Defense:**
- Az: -180° to +180° (360° coverage)
- El: -10° to +30° (40° coverage)

## Console Output

### Opening Configuration Dialog
```
[UI] Radar configure requested
[UI] Loading current configuration...
```

### Applying Configuration (Offline)
```
[UI] Applying radar configuration...
[BRIDGE] Radar configuration requested
[BRIDGE] Applying configuration: {'search_az_min': -60, 'search_az_max': 60, ...}
[BRIDGE] ✓ Radar configuration applied
[UI] ✓ Radar configuration applied successfully
```

### Applying Configuration (Online)
```
[UI] Applying radar configuration...
[BRIDGE] Radar configuration requested
[BRIDGE] Applying configuration: {'search_az_min': -90, 'search_az_max': 90, ...}
[BRIDGE] ✓ Radar configuration applied
[UI] ✓ Radar configuration applied successfully
```

## Technical Details

### Configuration Storage

Configuration is stored in:
- **UI State**: `RadarConfigDialog.config` (QML)
- **Bridge**: `bridge.get_radar_config()` (Python)
- **Radar**: Persistent in radar firmware

### Configuration Commands

The system sends these commands to the radar:

```python
# Operation Mode
MODE:SWT:OPERATIONMODE 1  # 0=Pedestrian, 1=UAS, 2=Plane

# Search FOV
MODE:SWT:SEARCH:AZFOVMIN -60
MODE:SWT:SEARCH:AZFOVMAX 60
MODE:SWT:SEARCH:ELFOVMIN -40
MODE:SWT:SEARCH:ELFOVMAX 40

# Track FOV
MODE:SWT:TRACK:AZFOVMIN -60
MODE:SWT:TRACK:AZFOVMAX 60
MODE:SWT:TRACK:ELFOVMIN -40
MODE:SWT:TRACK:ELFOVMAX 40
```

### Validation

All fields have input validation:
- **Latitude**: -90 to 90 degrees
- **Longitude**: -180 to 180 degrees
- **Altitude**: -500 to 10000 meters
- **Heading**: 0 to 360 degrees
- **Pitch/Roll**: -180 to 180 degrees
- **Azimuth**: -180 to 180 degrees
- **Elevation**: -90 to 90 degrees
- **Range**: Positive integers

## Best Practices

### 1. Configure Before First Connection
- Set all basic parameters while offline
- Verify IP address and position
- Set appropriate FOV for mission

### 2. Use Appropriate FOV
- **Wider FOV** = More coverage, lower update rate
- **Narrower FOV** = Faster updates, focused area
- Match FOV to threat approach vectors

### 3. Adjust Range Limits
- **Min Range**: Avoid ground clutter
- **Max Range**: Balance detection vs false alarms
- Consider terrain and obstacles

### 4. Test Configuration
- Apply settings
- Verify radar starts successfully
- Check track quality and update rate
- Adjust as needed

## Troubleshooting

### Configuration Not Applied
- Check console for error messages
- Verify radar is connected
- Ensure values are within valid ranges
- Try disconnecting and reconnecting

### Settings Grayed Out
- This is normal when radar is online
- Disconnect radar to edit basic settings
- FOV and range always editable

### Invalid Values
- Red border indicates invalid input
- Check value is within allowed range
- Ensure correct format (numbers only)

## Files Modified

1. `ui/components/RadarConfigDialog.qml` - Configuration dialog UI
2. `orchestration/bridge.py` - Added `configure_radar()` and `get_radar_config()` methods
3. `ui/Main.qml` - Added "Configure..." menu item and dialog integration
4. `src/drivers/radar_controller.py` - Existing `configure_radar()` method used

## Future Enhancements

- [ ] Save/load configuration presets
- [ ] Import/export configuration files
- [ ] Real-time FOV visualization on tactical display
- [ ] Configuration history/undo
- [ ] Validate FOV against terrain/obstacles
- [ ] Auto-optimize FOV based on threat patterns
