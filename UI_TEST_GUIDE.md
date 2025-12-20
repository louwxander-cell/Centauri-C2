# C2 System UI Test Guide

## Starting the System

### Option 1: Direct Launch
```bash
py main.py
```

### Option 2: Batch File
```bash
start_c2.bat
```

---

## Expected Startup Sequence

### Console Output

You should see the following in the console:

```
[Main] Initializing application...

╔═══════════════════════════════════════════════════════════════════════╗
║                    TriAD C2 Banner                                    ║
╚═══════════════════════════════════════════════════════════════════════╝

[Main] Initializing Qt application...
[Main] Initializing signal bus...
[Main] Loading configuration...
[Main] Initializing radar controller at 192.168.1.25...
[radar_controller] INFO: Connecting to radar at 192.168.1.25:23
[radar_controller] INFO: Connected to radar command port
[radar_controller] INFO: Initializing radar...
[radar_controller] INFO: Radar initialization complete
[radar_controller] INFO: Configuring radar...
[radar_controller] INFO: Radar configuration complete
[radar_controller] INFO: Starting radar in Search-While-Track mode...
[radar_controller] INFO: Radar started successfully - now streaming data
[Main] Radar started - streaming data on port 29982
[Main] Connecting to radar data stream at 192.168.1.25:29982...
[Main] Starting drivers...
[Main] All drivers started
[Main] Main window displayed

[Main] System operational - Ready for mission
```

### UI Window

A window should open showing:

**Main Display:**
- Polar radar display (circular)
- Range rings
- FOV wedge indicator
- Grid lines

**Left Panel:**
- Track list (empty if no targets)
- Threat priority indicators
- Track details

**Top Bar:**
- System status
- Radar status
- Connection indicators

---

## What to Look For

### ✅ Success Indicators

1. **Console Messages**
   - "Radar started successfully"
   - "All drivers started"
   - "System operational"
   - No error messages

2. **UI Window Opens**
   - Window appears and is responsive
   - Radar display visible
   - Controls functional

3. **Radar Status**
   - Green indicator (if implemented)
   - "Connected" or "Active" status
   - No error messages

### ⚠️ Expected Behavior (No Targets)

**Track Display:**
- Empty track list (normal - no targets in FOV)
- No dots/icons on radar display
- "No tracks" or "0 tracks" indicator

**This is NORMAL** - The radar is working but there are no flying objects to detect.

### ❌ Potential Issues

**If radar connection fails:**
- Check radar is powered on
- Verify network connection: `ping 192.168.1.25`
- Ensure no other applications are using radar (close RadarUI)

**If UI doesn't open:**
- Check console for Qt errors
- Verify PyQt6 is installed: `pip list | findstr PyQt6`
- Check display settings

**If system crashes:**
- Look for error messages in console
- Check Python version: `py --version` (need 3.11+)
- Verify all dependencies installed

---

## Testing Checklist

### Basic Functionality

- [ ] System starts without errors
- [ ] Radar connects and initializes
- [ ] UI window opens
- [ ] Radar display renders
- [ ] No crash or freeze

### Radar Integration

- [ ] Console shows "Radar started successfully"
- [ ] Console shows "streaming data on port 29982"
- [ ] No "Failed to connect" errors
- [ ] Radar status indicator shows connected

### UI Responsiveness

- [ ] Window can be moved/resized
- [ ] Controls are clickable
- [ ] Display updates smoothly
- [ ] No lag or freezing

### Expected Behavior

- [ ] Track list is empty (no targets)
- [ ] Radar display shows range rings
- [ ] FOV wedge visible
- [ ] No error dialogs

---

## Simulating Tracks (Optional)

If you want to see tracks without actual targets, you can:

### Option 1: Use Simulation Mode

Temporarily switch to simulation driver in `main.py`:

```python
# Comment out production driver
# self.radar_driver = RadarDriverProduction(radar_host, radar_port)

# Use simulation driver instead
from src.drivers.radar import RadarDriver
self.radar_driver = RadarDriver()
```

This will generate simulated tracks for testing the UI.

### Option 2: Field Test

Take the system outdoors:
1. Deploy radar with clear sky view
2. Launch test drone or wait for aircraft/birds
3. Watch tracks appear in real-time
4. Test track selection and engagement

---

## Keyboard Shortcuts

(If implemented in your UI)

- **ESC** - Deselect track
- **Space** - Auto-select highest threat
- **+/-** - Zoom in/out
- **Arrow Keys** - Pan display (if implemented)

---

## Shutting Down

### Graceful Shutdown

**Method 1:** Close window (X button)
- System will automatically stop radar
- Clean disconnect from all sensors
- Safe shutdown

**Method 2:** Ctrl+C in console
- Triggers shutdown sequence
- Stops radar
- Exits cleanly

### Expected Shutdown Output

```
[Main] Interrupt received, shutting down...
[Main] Initiating shutdown sequence...
[Main] Stopping radar...
[radar_controller] INFO: Stopping radar...
[radar_controller] INFO: Radar stopped
[radar_controller] INFO: Disconnected from radar
[Main] Stopping RadarDriverProduction...
[Main] All drivers stopped
[Main] Shutdown complete
```

---

## Troubleshooting

### Issue: "Failed to connect to radar"

**Check:**
1. Radar is powered on (LED lights visible)
2. Network cable connected
3. Can ping radar: `ping 192.168.1.25`
4. RadarUI is closed
5. Firewall not blocking ports

**Solution:**
- Power cycle radar (wait 90 seconds)
- Check network adapter IP: `ipconfig`
- Verify PC IP is 192.168.1.10

### Issue: "Invalid Command" errors

**This should be fixed**, but if it occurs:
- Check `radar_controller.py` uses `\r\n` not `\n`
- Verify radar firmware is SW 18.1.5
- Power cycle radar

### Issue: UI window doesn't open

**Check:**
1. PyQt6 installed: `pip install PyQt6`
2. No Qt errors in console
3. Display is connected
4. Windows display settings

**Solution:**
- Reinstall PyQt6: `pip install --upgrade PyQt6`
- Check for error messages in console

### Issue: System freezes or crashes

**Check:**
1. Console for error messages
2. Python version (need 3.11+)
3. Memory usage (Task Manager)

**Solution:**
- Restart system
- Check logs for errors
- Report issue with console output

---

## Performance Monitoring

### What to Monitor

**Console Output:**
- Track update messages (if verbose logging enabled)
- Error messages
- Warning messages
- Performance metrics

**Task Manager:**
- CPU usage (should be <20% idle)
- Memory usage (should be <500MB)
- Network activity (when targets present)

**UI Responsiveness:**
- Smooth animation (60 FPS target)
- No lag when interacting
- Quick track updates

---

## Success Criteria

### ✅ Integration Test Passed If:

1. System starts without errors
2. Radar connects and initializes
3. UI window opens and renders
4. No crashes or freezes
5. System shuts down cleanly

### ✅ Operational Test Passed If:

(Requires targets in FOV)

1. Tracks appear on display
2. Track list updates in real-time
3. Track selection works
4. Threat prioritization functions
5. Engagement controls respond

---

## Next Steps After UI Test

### If Test Passes:

1. **Document UI behavior**
2. **Test with simulation mode** (if needed)
3. **Plan field test** with real targets
4. **Prepare deployment checklist**

### If Issues Found:

1. **Note error messages**
2. **Check console output**
3. **Verify configuration**
4. **Report issues for debugging**

---

## Quick Reference

**Start System:**
```bash
py main.py
```

**Check Radar:**
```bash
ping 192.168.1.25
telnet 192.168.1.25 23
```

**Stop System:**
- Close window or Ctrl+C

**View Logs:**
- Check console output
- Look for ERROR or WARNING messages

---

**Ready to test!** 🚀

Run `py main.py` and watch the magic happen!
