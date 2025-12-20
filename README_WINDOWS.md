# TriAD C2 - Windows Edition

**Platform:** Windows 10/11  
**Status:** Functional with Known Performance Issues  
**Version:** Windows Development Branch  
**Last Updated:** December 20, 2025

---

## ⚠️ IMPORTANT: Windows-Specific Build

This is the **Windows-optimized fork** of Centauri-C2. It includes Windows-specific performance optimizations and workarounds for platform differences.

**For macOS/Linux:** Use the main repository at [Centauri-C2](https://github.com/louwxander-cell/Centauri-C2)

---

## 🎯 Key Differences from macOS Version

### Performance Optimizations
- **Update Rate:** 15 Hz (vs 30 Hz on macOS) to reduce jitter
- **Console Output:** Disabled periodic debug printing on Windows
- **Platform Detection:** Automatic Windows-specific behavior

### Known Issues
- ⚠️ **UI Jitter:** QML rendering performance degrades over time on Windows
- ⚠️ **Slower Than macOS:** Qt/QML rendering is less optimized on Windows
- ⚠️ **Not Production Ready:** Recommended to use macOS version for deployment

### Windows-Specific Code
```python
# In orchestration/bridge.py
update_interval = 67 if sys.platform == 'win32' else 33  # 15 Hz on Windows

# Debug output disabled on Windows
if sys.platform != 'win32':  # Only print on macOS/Linux
    print(f"[DEBUG] ...")
```

---

## 📋 Requirements

### Hardware
- **CPU:** Intel i5 or better (i7 recommended)
- **RAM:** 8GB minimum, 16GB recommended
- **GPU:** Dedicated graphics card recommended for QML rendering
- **Network:** Gigabit Ethernet adapter for radar connection

### Software
- **OS:** Windows 10 version 1903+ or Windows 11
- **Python:** 3.11 or 3.12 (3.13 not tested)
- **PySide6:** 6.5+ (Qt 6.5 or later)

### Network Requirements
- **Radar IP:** 192.168.1.25
- **PC IP:** 192.168.1.10 (or any in same subnet)
- **Ethernet:** Direct connection to radar (no WiFi)

---

## 🚀 Installation

### 1. Install Python
```powershell
# Download Python 3.11 or 3.12 from python.org
# During installation, check "Add Python to PATH"

# Verify installation
python --version
# Should show: Python 3.11.x or 3.12.x
```

### 2. Install Dependencies
```powershell
# Navigate to project directory
cd "C:\Users\YourName\Documents\Centauri C2\Centauri-C2"

# Install required packages
pip install PySide6
pip install pyserial

# Verify PySide6
python -c "from PySide6 import QtCore; print(QtCore.qVersion())"
# Should show: 6.5.x or later
```

### 3. Configure Network
```powershell
# Windows Network Settings:
# Control Panel → Network and Sharing Center → Change adapter settings
# Right-click Ethernet adapter → Properties → IPv4
# 
# Set to:
# IP Address: 192.168.1.10
# Subnet Mask: 255.255.255.0
# Default Gateway: (leave blank)

# Test connection
ping 192.168.1.25
# Should get replies if radar is on
```

### 4. Configure Radar
Edit `config/settings.json`:
```json
{
  "network": {
    "radar": {
      "enabled": true,
      "host": "192.168.1.25",
      "port": 29982
    }
  },
  "gps": {
    "enabled": false
  }
}
```

---

## 🎮 Running the System

### Standard Launch
```powershell
# From project root
python main.py
```

### With Verbose Output (for debugging)
```powershell
python main.py --verbose
```

### Using the Batch File
```powershell
# Double-click: start_c2.bat
# Or from command line:
.\start_c2.bat
```

---

## 📊 Expected Performance

### Normal Operation
- **Update Rate:** 15 Hz (67ms interval)
- **CPU Usage:** 20-40% on i7
- **Memory:** ~500MB
- **UI Responsiveness:** Some jitter, increases over time

### Performance Tips
1. **Close unnecessary apps** before running
2. **Use dedicated GPU** if available (NVIDIA/AMD)
3. **Disable Windows animations** (System → Performance Options)
4. **Run as Administrator** (may improve I/O performance)
5. **Close Windows Terminal** background tasks

---

## 🔧 Windows-Specific Files

### New Files (not in macOS version)
- `start_c2.bat` - Windows batch launcher
- `README_WINDOWS.md` - This file
- `PERFORMANCE_FIXES.md` - Windows optimization attempts

### Modified Files (Windows-specific changes)
- `orchestration/bridge.py` - Reduced update rate, disabled debug output
- `orchestration/gunner_interface.py` - Disabled Windows logging
- `triad_c2.py` - Windows platform detection
- `src/core/bus.py` - SignalBus singleton fix

### Configuration
- `config/settings.json` - Windows-tested radar config

---

## 🐛 Known Issues & Workarounds

### Issue 1: UI Jitter Increases Over Time
**Status:** KNOWN BUG - Windows-Specific

**Symptoms:**
- UI smooth at startup
- Jitter gradually increases
- After 2-3 minutes, noticeable lag

**Cause:** Qt/QML rendering performance on Windows

**Workaround:**
- Restart application periodically
- Reduce track count in scenarios
- Use macOS version for production

### Issue 2: Console Output Causes Lag
**Status:** MITIGATED

**Solution Applied:**
- Debug output disabled on Windows
- Only critical messages print
- Use `--verbose` flag if needed

### Issue 3: Disengage Button Not Working
**Status:** UNDER INVESTIGATION

**Symptoms:**
- Engage button works
- Cancel/Disengage button doesn't respond

**Debug:**
Check console for:
```
[BRIDGE] *** DISENGAGE CALLED ***
```
If message appears → QML state issue  
If no message → QML not calling Python

**Temporary Fix:** Restart application to reset engagement state

---

## 📡 Radar Integration

### EchoGuard Radar Setup
See `RADAR_INTEGRATION_GUIDE_MACOS.md` for detailed radar setup (same hardware for Windows).

**Quick Setup:**
1. Power on radar
2. Connect Ethernet cable
3. Set PC IP to 192.168.1.10
4. Test: `ping 192.168.1.25`
5. Set `radar.enabled: true` in config
6. Run `python main.py`

### Verification
Console should show:
```
[INIT] Initializing EchoGuard radar at 192.168.1.25...
[INIT] Connected to radar command port
[INIT] Radar initialized
[INIT] Radar started - streaming on port 29982
```

---

## 🧪 Testing

### Test Scenarios
Use keyboard in UI:
- **2** - Single track test
- **3** - Priority test (5 tracks)
- **4** - Sensor fusion test
- **5** - Stress test (25 tracks) - NOT RECOMMENDED on Windows
- **D** - Disable scenarios

**Recommendation:** Use scenario 3 (5 tracks) on Windows for better performance

### Test Scripts
```powershell
# Test radar connection
python -c "from src.drivers.radar_controller import RadarController; r = RadarController('192.168.1.25'); print('✓' if r.connect() else '✗')"

# Test signal bus (should not crash)
python test_signalbus.py
```

---

## 🔍 Troubleshooting

### Application Won't Start
1. Check Python version: `python --version`
2. Check PySide6 installed: `pip list | findstr PySide6`
3. Check for errors: `python main.py 2> error.txt`

### Radar Won't Connect
1. Check network: `ping 192.168.1.25`
2. Check port: `telnet 192.168.1.25 23` (enable telnet client in Windows Features)
3. Close RadarUI if running
4. Power cycle radar

### UI Performance Issues
1. Reduce scenario to 5 tracks (press **3**)
2. Close other applications
3. Check GPU usage in Task Manager
4. Consider switching to macOS

### Python Import Errors
```powershell
# Reinstall dependencies
pip uninstall PySide6
pip install PySide6

# Clear Python cache
python -m pip cache purge
```

---

## 📚 Documentation

### Windows-Specific Docs
- `README_WINDOWS.md` - This file
- `PERFORMANCE_FIXES.md` - Optimization attempts
- `SESSION_SUMMARY.md` - Development session notes

### General Documentation (applies to both platforms)
- `RADAR_INTEGRATION_GUIDE_MACOS.md` - Radar setup (hardware same for Windows)
- `RADAR_INTEGRATION.md` - Integration architecture
- `UI_MIGRATION.md` - UI cleanup notes

---

## 🚨 Important Notes

### NOT Recommended for Production
This Windows version has known performance issues. For production deployment:
- ✅ **Use macOS version** (smooth, 30 Hz, no jitter)
- ⚠️ **Windows version** for development/testing only

### Why Windows Performance Issues?
1. **Qt/QML Rendering:** Metal (macOS) vs DirectX (Windows)
2. **Console I/O:** Windows console is significantly slower
3. **Thread Scheduling:** Different OS-level behavior
4. **Graphics Composition:** Windows DWM adds overhead

### When to Use This Version
- ✅ Windows development environment
- ✅ Testing radar integration on Windows
- ✅ Demonstrating functionality (with caveats)
- ❌ Operational/production deployment
- ❌ Extended runtime (>5 minutes)

---

## 🔗 Related Repositories

- **Main Repository (macOS):** [Centauri-C2](https://github.com/louwxander-cell/Centauri-C2)
- **Windows Fork:** [Centauri-C2_Windows](https://github.com/louwxander-cell/Centauri-C2_Windows) (this repo)

---

## 📝 Development Notes

### Branching Strategy
- `main` - Windows-optimized code
- Keep in sync with macOS repo for non-platform-specific features
- Platform-specific changes only in this repo

### Contributing
When adding features:
1. Test on Windows first
2. Consider performance impact
3. Add Windows-specific workarounds if needed
4. Document any platform differences

### Syncing with macOS Version
```powershell
# Add macOS repo as upstream
git remote add upstream https://github.com/louwxander-cell/Centauri-C2.git

# Fetch changes
git fetch upstream

# Merge non-platform-specific features
git merge upstream/main
# Resolve conflicts, keeping Windows-specific optimizations
```

---

## ⚖️ License

Same as main Centauri-C2 repository.

---

## 📧 Contact

For Windows-specific issues, create an issue in this repository.  
For general C2 system questions, refer to main repository.

---

**Last Updated:** December 20, 2025  
**Maintainer:** louwxander-cell  
**Platform:** Windows 10/11 (Development Branch)
