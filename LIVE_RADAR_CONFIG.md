# Live Radar Configuration System

## Overview

The radar configuration system now **queries actual radar settings** and allows **real-time modification** of parameters. The dialog displays live values when the radar is connected and allows changes based on radar state.

## Key Features

### ✅ **Live Configuration Query**
- When radar is **ONLINE** (connected), the dialog queries actual settings from the radar
- When radar is **OFFLINE**, displays default/last-known configuration
- Visual indicator shows whether configuration is live or default

### ✅ **Real-Time Updates**
- Configuration values are read from radar on dialog open
- "Refresh" button reloads current settings from radar
- Changes are applied immediately to the radar

### ✅ **State-Aware Editing**
- **Offline/Standby**: All parameters editable
- **Online/Streaming**: Only FOV and range editable
- Grayed-out fields indicate read-only parameters

## How It Works

### Opening Configuration Dialog

1. **Click** ECHOGUARD indicator
2. **Select** "Configure..."
3. **System queries radar** (if connected)
4. **Dialog displays** current settings

**Console Output:**
```
[UI] Radar configure requested
[BRIDGE] Querying radar configuration...
[BRIDGE] Radar is online, querying actual configuration...
[RadarController] Querying radar configuration...
[RadarController] Sent: MODE:SWT:SEARCH:AZFOVMIN?
[RadarController] Received: -60
[RadarController] Sent: MODE:SWT:SEARCH:AZFOVMAX?
[RadarController] Received: 60
... (continues for all parameters)
[RadarController] Retrieved radar configuration: {'search_az_min': -60, ...}
[BRIDGE] ✓ Retrieved live configuration from radar
[RadarConfigDialog] Configuration updated: {...}
```

### Configuration Status Indicator

**Header shows configuration source:**

```
┌─────────────────────────────────┐
│     GLOBAL - Radar 1            │
│   ● LIVE CONFIGURATION          │  ← Green = Live from radar
└─────────────────────────────────┘
```

or

```
┌─────────────────────────────────┐
│     GLOBAL - Radar 1            │
│   ○ Default Configuration       │  ← Gray = Default values
└─────────────────────────────────┘
```

### Modifying Settings

#### Scenario 1: Adjust FOV While Streaming (Online)

1. Radar is **GREEN** (streaming)
2. Click "Configure..."
3. Dialog shows **● LIVE CONFIGURATION**
4. FOV and Range fields are **editable**
5. Basic settings are **grayed out**
6. Modify Search Az Max from 60° to 90°
7. Click **OK**
8. Change applied immediately to radar

**Console Output:**
```
[UI] Applying radar configuration...
[BRIDGE] Radar configuration requested
[BRIDGE] Applying configuration: {'search_az_min': -60, 'search_az_max': 90, ...}
[RadarController] Configuring radar...
[RadarController] Setting search FOV: Az[-60,90], El[-40,40]
[RadarController] Sent: MODE:SWT:SEARCH:AZFOVMAX 90
[BRIDGE] ✓ Radar configuration applied
[UI] ✓ Radar configuration applied successfully
```

#### Scenario 2: Change IP Address (Offline)

1. Radar is **ORANGE** (standby)
2. Click "Configure..."
3. Dialog shows **○ Default Configuration**
4. All fields are **editable**
5. Change IP from 192.168.1.25 to 192.168.1.30
6. Click **OK**
7. Configuration saved
8. Click "Connect" to connect at new IP

### Refresh Button

**Purpose:** Reload current settings from radar

**When to use:**
- Verify changes were applied
- Check if another operator changed settings
- Reload after radar restart

**How to use:**
1. Click **Refresh** button (bottom left)
2. System queries radar
3. All fields update with current values

**Console Output:**
```
[RadarConfig] Refresh requested
[UI] Refreshing radar configuration...
[BRIDGE] Querying radar configuration...
[BRIDGE] Radar is online, querying actual configuration...
[RadarController] Retrieved radar configuration: {...}
[BRIDGE] ✓ Retrieved live configuration from radar
[UI] ✓ Configuration refreshed
```

## Queried Parameters

### From Radar (When Online)

The system queries these parameters directly from the radar:

| Parameter | Command | Example Response |
|-----------|---------|------------------|
| Operation Mode | `MODE:SWT:OPERATIONMODE?` | `1` (UAS) |
| Search Az Min | `MODE:SWT:SEARCH:AZFOVMIN?` | `-60` |
| Search Az Max | `MODE:SWT:SEARCH:AZFOVMAX?` | `60` |
| Search El Min | `MODE:SWT:SEARCH:ELFOVMIN?` | `-40` |
| Search El Max | `MODE:SWT:SEARCH:ELFOVMAX?` | `40` |
| Track Az Min | `MODE:SWT:TRACK:AZFOVMIN?` | `-60` |
| Track Az Max | `MODE:SWT:TRACK:AZFOVMAX?` | `60` |
| Track El Min | `MODE:SWT:TRACK:ELFOVMIN?` | `-40` |
| Track El Max | `MODE:SWT:TRACK:ELFOVMAX?` | `40` |

### Static Parameters (Not Queried)

These are stored locally and not queried from radar:

- Label
- IPv4 Address
- Product Mode
- Mission Set
- Latitude/Longitude/Altitude
- Heading/Pitch/Roll
- Range Min/Max
- Frequency Channel

## Configuration Flow

### Complete Workflow

```
User Clicks "Configure..."
         ↓
    UI calls bridge.get_radar_config()
         ↓
    Bridge checks if radar is online
         ↓
    ┌─────────────┬─────────────┐
    │   ONLINE    │   OFFLINE   │
    └─────────────┴─────────────┘
         ↓              ↓
    Query radar    Use defaults
         ↓              ↓
    Parse responses    ↓
         ↓              ↓
    Merge with defaults
         ↓
    Return config to UI
         ↓
    Dialog displays values
         ↓
    User modifies settings
         ↓
    User clicks OK
         ↓
    UI calls bridge.configure_radar(newConfig)
         ↓
    Bridge sends commands to radar
         ↓
    Radar applies changes
         ↓
    Success/failure returned to UI
```

## Technical Implementation

### RadarController.get_configuration()

```python
def get_configuration(self) -> Dict[str, Any]:
    """Query radar for current configuration settings"""
    if not self.connected:
        return {}
    
    config = {}
    
    # Query each parameter
    response = self.send_command("MODE:SWT:SEARCH:AZFOVMIN?", wait=0.5)
    if response:
        config['search_az_min'] = int(float(response.strip()))
    
    # ... (repeat for all parameters)
    
    return config
```

### OrchestrationBridge.get_radar_config()

```python
@Slot(result='QVariantMap')
def get_radar_config(self):
    """Get current radar configuration"""
    # Start with defaults
    config = {
        'label': 'R1',
        'ipv4_address': self.radar_driver.host,
        # ... all default values
    }
    
    # If radar online, query actual values
    if self.radar_driver.is_online():
        radar_config = self.radar_driver.get_configuration()
        config.update(radar_config)  # Merge live values
    
    return config
```

### RadarConfigDialog.qml

```qml
// Update fields when config changes
onConfigChanged: {
    updateFields()
}

function updateFields() {
    searchAzMinSpin.value = config.search_az_min || -60
    searchAzMaxSpin.value = config.search_az_max || 60
    // ... update all fields
}

// Refresh button handler
onReset: {
    refreshRequested()
}
```

## Benefits

### 1. **Accuracy**
- Always shows actual radar state
- No guessing what settings are active
- Immediate feedback on changes

### 2. **Flexibility**
- Adjust FOV without disconnecting
- Quick parameter tuning
- Real-time optimization

### 3. **Safety**
- Verify settings before mission
- Confirm changes were applied
- Detect unexpected configuration

### 4. **Usability**
- Single interface for all settings
- No need for separate RadarUI application
- Integrated workflow

## Comparison with RadarUI

| Feature | RadarUI | TriAD C2 |
|---------|---------|----------|
| **Query Settings** | ✅ Yes | ✅ Yes |
| **Modify Settings** | ✅ Yes | ✅ Yes |
| **Live Updates** | ✅ Yes | ✅ Yes |
| **State-Aware** | ❌ No | ✅ Yes |
| **Integrated** | ❌ Separate app | ✅ Built-in |
| **Mission Context** | ❌ No | ✅ Yes |

## Testing Checklist

- [x] Open dialog when radar offline → Shows default config
- [x] Open dialog when radar online → Shows live config
- [x] Modify FOV while online → Changes applied
- [x] Click Refresh → Values reload from radar
- [x] Verify grayed-out fields when online
- [x] Verify all fields editable when offline
- [x] Check console shows query commands
- [x] Confirm live indicator shows correct state

## Troubleshooting

### Configuration Not Loading

**Symptom:** Dialog shows default values even when radar is online

**Check:**
1. Verify radar is actually connected (green indicator)
2. Check console for query errors
3. Ensure radar responds to query commands
4. Try clicking Refresh button

**Console Check:**
```
[BRIDGE] Radar is online, querying actual configuration...
[RadarController] Querying radar configuration...
```

### Changes Not Applied

**Symptom:** Modified settings don't take effect

**Check:**
1. Verify radar is connected
2. Check if field is editable (not grayed out)
3. Look for error messages in console
4. Try disconnecting and reconnecting

**Console Check:**
```
[BRIDGE] ✓ Radar configuration applied
```

### Query Timeout

**Symptom:** Dialog takes long time to open

**Cause:** Radar not responding to query commands

**Solution:**
1. Check radar network connection
2. Verify radar is in correct state
3. Increase query timeout in code

## Future Enhancements

- [ ] Cache configuration to reduce query time
- [ ] Show which parameters changed
- [ ] Highlight modified fields
- [ ] Add "Apply" button for live preview
- [ ] Configuration diff viewer
- [ ] Auto-refresh on timer
- [ ] Export/import configuration files
- [ ] Configuration validation warnings

## Files Modified

1. `src/drivers/radar_controller.py`
   - Added `get_configuration()` method

2. `orchestration/bridge.py`
   - Updated `get_radar_config()` to query live values

3. `ui/components/RadarConfigDialog.qml`
   - Added live/default indicator
   - Added Refresh button
   - Added automatic field updating

4. `ui/Main.qml`
   - Added refresh handler

## Summary

The live radar configuration system provides **full integration** with the EchoGuard radar, allowing operators to:

✅ **View actual radar settings** in real-time  
✅ **Modify parameters** based on mission needs  
✅ **Verify changes** were applied correctly  
✅ **Work efficiently** without switching applications  

This eliminates the need for the separate RadarUI application for most configuration tasks.
