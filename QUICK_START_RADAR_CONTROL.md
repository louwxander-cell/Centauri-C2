# Quick Start: Interactive Radar Control

## What Changed?

The radar status indicator is now **interactive** with three-state status:

### Status Colors

- 🔴 **Gray** = Offline (disabled in config)
- 🟠 **Orange** = Standby (available, click to connect)
- 🟢 **Green** = Online (connected and streaming)

## How to Use

### 1. Start Application

When you launch the C2 application, the ECHOGUARD indicator will show **ORANGE** (standby):

```
[INIT] EchoGuard radar available at 192.168.1.25:29982
[INIT]   Status: STANDBY (click orange indicator to connect)
```

### 2. Connect Radar

**Method 1: Click the indicator**
1. Click the orange ECHOGUARD indicator in the header
2. Select "Connect" from the dropdown menu
3. Wait for indicator to turn green

**What happens:**
- Connects to radar command port
- Initializes radar hardware
- Configures FOV (±60° azimuth, ±40° elevation)
- Starts radar streaming on port 29982
- Indicator turns **GREEN** with pulse animation

### 3. Disconnect Radar

1. Click the green ECHOGUARD indicator
2. Select "Disconnect" from the dropdown menu
3. Indicator returns to **ORANGE** (standby)

## Visual Indicators

### Standby (Orange)
- Slow pulse animation (1.5 second cycle)
- Cursor changes to pointer on hover
- Click to open connection menu

### Online (Green)
- Fast pulse animation (1.0 second cycle)
- Cursor changes to pointer on hover
- Click to open control menu

## Console Messages

**Successful Connection:**
```
[UI] Radar connect requested
[BRIDGE] Radar connect requested
[BRIDGE] Connected to radar command port
[BRIDGE] Radar initialized
[BRIDGE] ✓ Radar started and streaming
[UI] Radar connected successfully
```

**Successful Disconnection:**
```
[UI] Radar disconnect requested
[BRIDGE] Radar disconnect requested
[BRIDGE] ✓ Radar disconnected
[UI] Radar disconnected successfully
```

## Troubleshooting

### Indicator stays gray
- Check `config/settings.json` - ensure `network.radar.enabled` is `true`
- Verify radar IP address is correct (default: 192.168.1.25)

### Connection fails
- Verify radar is powered on
- Check network connection to 192.168.1.25
- Ensure no firewall blocking port 23 (command) or 29982 (data)
- Run `py check_radar_connection.py` to test connectivity

### Indicator doesn't respond to clicks
- Only works when orange (standby) or green (online)
- Gray (offline) indicators are not interactive
- Check console for error messages

## Comparison with RadarUI

| Feature | RadarUI | Centauri C2 |
|---------|---------|-------------|
| **Connection** | Manual button | Click status indicator |
| **Status** | Text label | Color-coded dot |
| **FOV Display** | Separate window | Integrated tactical display |
| **Control** | Multiple buttons | Dropdown menu |
| **Feedback** | Dialog boxes | Console + visual status |

## Benefits

1. **Operator Control** - Connect only when needed
2. **Visual Feedback** - Clear status at a glance
3. **Integrated UI** - No separate radar control window
4. **Quick Access** - Single click to connect/disconnect
5. **Status Monitoring** - Real-time connection status

## Next Steps

Once connected (green), the radar will:
- Stream track data at 10 Hz
- Display tracks on tactical display
- Show radar FOV wedge (future feature)
- Enable engagement capabilities

## Configuration

Edit `config/settings.json` to change radar settings:

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

## Future Features

- [ ] Configure FOV from UI
- [ ] Show radar FOV wedge on display
- [ ] Display connection quality/signal strength
- [ ] Auto-reconnect on connection loss
- [ ] Save last used configuration
