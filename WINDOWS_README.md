# Centauri C2 - Windows Edition

**Counter-UAS Command & Control System**

---

## Quick Start

```powershell
# Run the application
py triad_c2.py
```

The UI will open maximized and ready to use.

---

## System Overview

**Architecture:** Engine → Orchestration Bridge → QML UI

- **Engine:** Mock engine for development/testing
- **Orchestration:** Connects data sources to UI, handles engagement logic
- **UI:** Qt Quick (QML) GPU-accelerated interface
- **Gunner Interface:** UDP broadcast to gunner stations

---

## Display Configuration

**Optimized for:** 1920×1080 Full HD displays
- Window opens maximized automatically
- Accounts for Windows taskbar
- Can be restored/resized as needed

---

## Features

### ✅ Working Features
- **Track Display:** Real-time track visualization on tactical radar display
- **Track Selection:** Click tracks to select, auto-selects highest priority
- **Engagement Control:** Engage/disengage tracks for gunner streaming
- **Gunner Streaming:** UDP broadcast of engaged track to gunner stations (192.168.10.255:5100)
- **System Status:** Real-time system operational status
- **GPS Integration:** Ready (disabled by default in config)
- **Radar Integration:** Ready (disabled by default in config)

### 🔧 Configuration

Edit `config/settings.json`:

```json
{
  "gps": {
    "enabled": false,
    "port": "COM3",
    "baud_rate": 115200
  },
  "network": {
    "radar": {
      "enabled": false,
      "host": "192.168.1.25",
      "port": 29982
    }
  }
}
```

---

## Controls

### Engagement Workflow
1. **Select Track:** Click a track in the Active Tracks list or on the radar display
2. **Engage:** Click the `ENGAGE [track_id]` button
3. **Monitor:** Track streams to gunner stations, status shows "Engagement Active"
4. **Disengage:** Click the `CANCEL [track_id]` button to stop streaming

### Window Controls
- **Maximize/Restore:** Standard Windows controls
- **Close:** Click X or Alt+F4
- **Move:** Drag title bar when restored

---

## Known Issues

### Disengage Button
**Status:** Under investigation
- Backend successfully disengages (confirmed in logs)
- UI state not updating properly
- Workaround: Restart application to reset engagement state

**Console Output Shows:**
```
[BRIDGE] *** DISENGAGE CALLED ***
[GUNNER INTERFACE] [OK] Track XXXX DISENGAGED
```
But UI remains in "Engagement Active" state.

---

## Performance

**Update Rates:**
- Track updates: 30 Hz (33ms)
- Gunner streaming: 10 Hz
- UI rendering: GPU-accelerated

**Windows-Specific:**
- Performance comparable to macOS version
- No jitter issues with current configuration
- Console output optimized for Windows

---

## File Structure

```
Centauri-C2/
├── triad_c2.py              # Main entry point
├── config/
│   └── settings.json        # System configuration
├── orchestration/
│   ├── bridge.py            # Orchestration bridge
│   └── gunner_interface.py  # Gunner streaming service
├── src/
│   ├── core/                # Core systems
│   ├── drivers/             # Hardware drivers (GPS, Radar)
│   └── engines/             # Track processing engines
└── ui/
    ├── Main.qml             # Main UI window
    ├── EngagementPanel.qml  # Engagement controls
    ├── Theme.qml            # UI theme/styling
    └── components/          # Reusable UI components
```

---

## Hardware Integration

### GPS (Septentrio mosaic-X5)
See: `docs/integration/septentrio/QUICKSTART.md`

### Radar (EchoGuard)
See: `RADAR_INTEGRATION_GUIDE_MACOS.md`

### BlueHalo Effector
See: `docs/integration/BLUEHALO_QUICK_SUMMARY.md`

---

## Development

### Requirements
- Python 3.10+
- PySide6
- Windows 10/11

### Running Tests
```powershell
# Test GPS connection
py -m src.drivers.gps_driver

# Test radar connection
py test_radar_simple.py
```

---

## GitHub Repository

**Windows Version:** https://github.com/louwxander-cell/Centauri-C2_Windows

This is a separate repository for Windows-specific development, branched from the macOS version.

---

## Support

For issues or questions, refer to:
- `ARCHITECTURE.md` - System architecture details
- `docs/integration/` - Hardware integration guides
- Console output for debugging (all print statements visible)

---

**Last Updated:** December 20, 2025
