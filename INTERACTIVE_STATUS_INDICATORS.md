# Interactive Status Indicators - Implementation Guide

## Overview

The status indicators now support three states and interactive control for radar connection management.

## Three-State Status System

### Status States

1. **🔴 Offline (Gray #64748B)**
   - Sensor is disabled in configuration
   - Not available for use
   - No interaction possible

2. **🟠 Standby (Orange #F59E0B)**
   - Sensor is enabled in configuration
   - Available but not connected
   - **Interactive**: Click to open connection menu
   - Slow pulse animation (1.5s cycle)

3. **🟢 Online (Green #10B981)**
   - Sensor connected and operational
   - Actively streaming data
   - **Interactive**: Click to open control menu
   - Fast pulse animation (1.0s cycle)

## Interactive Radar Control

### User Workflow

1. **Application Start**
   - Radar shows **ORANGE** (standby) if enabled in config
   - Message: "Status: STANDBY (click orange indicator to connect)"

2. **Connect Radar**
   - Click orange ECHOGUARD indicator
   - Select "Connect" from dropdown menu
   - System performs:
     - Connect to radar command port (192.168.1.25:23)
     - Initialize radar
     - Configure FOV settings (±60° az, ±40° el)
     - Start radar streaming
   - Indicator turns **GREEN** when successful

3. **Disconnect Radar**
   - Click green ECHOGUARD indicator
   - Select "Disconnect" from dropdown menu
   - System stops radar and disconnects
   - Indicator returns to **ORANGE** (standby)

### Dropdown Menu Options

**When Standby (Orange):**
- ✅ Connect - Initiate radar connection
- ❌ Configure... (disabled - future feature)

**When Online (Green):**
- ✅ Disconnect - Stop radar and disconnect
- ❌ Configure... (disabled - future feature)

## Technical Implementation

### Backend (Python)

**SystemStatus Class** (`orchestration/bridge.py`)
```python
class SystemStatus(QObject):
    # Properties: gpsStatus, radarStatus, rfStatus, gunnerStatus
    # Values: "offline", "standby", "online"
```

**Bridge Methods**
- `connect_radar()` - Connect and start radar
- `disconnect_radar()` - Stop and disconnect radar
- `_update_system_status()` - Monitor sensor states (1 Hz)

**Status Logic**
```python
if not enabled:
    status = "offline"
elif driver and driver.is_online():
    status = "online"
elif enabled:
    status = "standby"
```

### Frontend (QML)

**StatusIndicator Component** (`ui/components/StatusIndicator.qml`)
- Displays status dot with appropriate color
- Shows sensor name
- Handles mouse interaction
- Provides dropdown menu
- Emits signals: `connectRequested`, `disconnectRequested`

**Main.qml Integration**
```qml
StatusIndicator {
    sensorName: "ECHOGUARD"
    status: systemStatus ? systemStatus.radarStatus : "offline"
    interactive: true
    
    onConnectRequested: {
        bridge.connect_radar()
    }
    
    onDisconnectRequested: {
        bridge.disconnect_radar()
    }
}
```

## Configuration

**Enable Radar** (`config/settings.json`)
```json
{
  "network": {
    "radar": {
      "enabled": true,
      "host": "192.168.1.25",
      "port": 29982
    }
  }
}
```

## Sensor Status Summary

| Sensor | Interactive | Auto-Connect | Notes |
|--------|-------------|--------------|-------|
| **GPS** | No | Yes | Connects automatically if enabled |
| **SKYVIEW** | No | No | Not yet implemented |
| **ECHOGUARD** | **Yes** | **No** | Operator-controlled via UI |
| **GUNNER** | No | Yes | Service starts automatically |

## Console Output

**Application Start:**
```
[INIT] EchoGuard radar available at 192.168.1.25:29982
[INIT]   Status: STANDBY (click orange indicator to connect)
```

**Connect Radar:**
```
[BRIDGE] Radar connect requested
[BRIDGE] Connected to radar command port
[BRIDGE] Radar initialized
[BRIDGE] ✓ Radar started and streaming
```

**Disconnect Radar:**
```
[BRIDGE] Radar disconnect requested
[BRIDGE] ✓ Radar disconnected
```

## Future Enhancements

1. **Configure Menu**
   - Adjust FOV (azimuth/elevation limits)
   - Change operation mode
   - Set detection thresholds

2. **GPS Interactive Control**
   - Connect/disconnect serial port
   - Change baud rate
   - Reset GPS module

3. **RF Sensor Control**
   - Connect to SkyView API
   - Configure detection parameters

4. **Status Tooltips**
   - Hover to see connection details
   - Show last update time
   - Display error messages

## Testing

1. **Start Application**
   - Verify ECHOGUARD shows **ORANGE**
   - Verify cursor changes to pointer on hover

2. **Connect Radar**
   - Click orange indicator
   - Select "Connect" from menu
   - Verify indicator turns **GREEN**
   - Verify pulse animation

3. **Disconnect Radar**
   - Click green indicator
   - Select "Disconnect" from menu
   - Verify indicator returns to **ORANGE**

4. **Check Console**
   - Verify connection messages
   - Check for errors

## Files Modified

1. `orchestration/bridge.py` - Three-state status + connect/disconnect methods
2. `src/drivers/radar_controller.py` - Added is_online() method
3. `triad_c2.py` - Removed auto-connect, pass enabled flags
4. `ui/components/StatusIndicator.qml` - New interactive component
5. `ui/Main.qml` - Use StatusIndicator component
6. `config/settings.json` - Radar enabled configuration

## Color Reference

- **Offline**: `#64748B` (Slate 500)
- **Standby**: `#F59E0B` (Amber 500)
- **Online**: `#10B981` (Emerald 500)
