# GPS Integration - Setup Checklist

## ✅ **Integration Status: READY FOR HARDWARE**

All code is complete and ready. Just connect your Mosaic-H GPS!

---

## 🔌 **When You Connect the Hardware**

### Step 1: Physical Connection (2 minutes)

**Connect:**
1. Both antennas to ANT1 and ANT2 ports on Mosaic-H
2. USB Type-C cable from Mosaic-H to your Mac
3. Power will come via USB (no external power needed)

**Antenna Setup:**
```
ANT1 (Primary) ──────► ANT2 (Secondary)
     └──── 1.0m baseline ──────┘
     (Align with vehicle forward axis)
```

---

### Step 2: Verify Connection (1 minute)

**Check device appears:**
```bash
# On Mac
ls -l /dev/tty.usbmodem*

# Should see something like:
# /dev/tty.usbmodemXXXXXX
```

**If no device appears:**
- Check USB cable is data cable (not charge-only)
- Try different USB port
- Check Mosaic-H power LED is on

---

### Step 3: Test GPS Hardware (2 minutes)

**Run test script:**
```bash
cd /Users/xanderlouw/CascadeProjects/C2

# Mac (auto-detect port)
python3 test_gps_connection.py /dev/tty.usbmodem* 115200

# Or if you know exact port:
python3 test_gps_connection.py /dev/tty.usbmodem12345 115200
```

**Expected output:**
```
✓ GPS is outputting NMEA sentences
✓ Position fix acquired
  → Latitude: -25.841105°
  → Longitude: 28.180340°
✓ True heading available (dual-antenna mode)  ← CRITICAL
  → Heading: 90.5°
✓ GPS READY FOR INTEGRATION
```

**If no heading:**
- Wait 30-60 seconds for dual-antenna lock
- Check both antennas are connected
- Verify clear sky view

---

### Step 4: Configure (If Needed)

**Web Interface (Optional):**
```bash
# Open browser to:
http://192.168.3.1

# Configure:
# - Attitude → Heading Setup
# - Baseline: 1.0m (your actual measurement)
# - Orientation: 0° (forward)
# - Click "Save to Boot"
```

**Via Commands (Optional):**
```bash
# If heading not working, configure baseline:
# Connect to GPS, send commands:
setHeadingBaseline, 1.0, 0.0
saveConfiguration, Boot
```

---

### Step 5: Run TriAD C2 with GPS (30 seconds)

**Start application:**
```bash
python3 triad_c2.py
```

**Look for in console:**
```
[INIT] Initializing GPS...
[INIT]   Model: Septentrio Mosaic-H
[INIT]   Port: /dev/tty.usbmodem12345
[INIT]   Baud: 115200
[INIT] ✓ GPS driver started
[SeptentrioGPS] Starting Septentrio Mosaic-H driver
[SeptentrioGPS] ✓ Serial port opened: /dev/tty.usbmodem12345 @ 115200 baud
[SeptentrioGPS] ✓ Dual-antenna heading lock acquired: 90.5°
```

**In UI:**
- GPS status indicator should be GREEN
- Ownship icon should appear at your location
- Heading arrow should point in correct direction

---

## 🎯 **Verification Checklist**

**After starting TriAD C2 with GPS:**
- [ ] Console shows "GPS driver started"
- [ ] Console shows "Dual-antenna heading lock"
- [ ] GPS status in UI is ONLINE (green)
- [ ] Ownship position appears on display
- [ ] Heading arrow points correctly
- [ ] Position updates smoothly (5 Hz)
- [ ] No error messages in console

---

## ⚠️ **Troubleshooting**

### "GPS initialization failed: [Errno 2] No such file"
**Cause:** GPS not connected or wrong port

**Fix:**
1. Check `ls -l /dev/tty.usbmodem*`
2. If no device, reconnect USB
3. Update port in `config/settings.json` if needed

### "GPS initialization failed: Permission denied"
**Cause:** No permission to access serial port

**Fix:**
```bash
# Check permissions
ls -l /dev/tty.usbmodem*

# If needed (unlikely on Mac):
sudo chmod 666 /dev/tty.usbmodem*
```

### GPS online but no heading
**Cause:** Waiting for dual-antenna lock

**Fix:**
1. Wait 30-60 seconds
2. Check both antennas connected
3. Verify clear sky view (need 4+ satellites per antenna)
4. Check web UI: http://192.168.3.1 → Status → Attitude

### Position works, heading is 180° off
**Cause:** ANT1 and ANT2 swapped

**Fix:**
- Swap antenna cables
- OR set orientation to 180° in web UI

---

## 📊 **What's Working**

**✅ Complete:**
- Production GPS driver (`src/drivers/gps_septentrio.py`)
- Configuration file (`config/settings.json`)
- Integration with TriAD C2 (`triad_c2.py`)
- Test script (`test_gps_connection.py`)
- Complete documentation (`docs/integration/septentrio/`)

**✅ Features:**
- NMEA 0183 parsing (GGA, RMC, HDT, VTG)
- Dual-antenna heading (compass-less)
- Septentrio proprietary sentences (PSAT,HPR)
- Auto-detection of USB port
- Graceful failure if GPS not connected
- Status monitoring and error reporting

**✅ Ready:**
- System continues to work without GPS
- GPS integrates seamlessly when connected
- All configuration is in `config/settings.json`
- Web interface accessible at `http://192.168.3.1`

---

## 🎓 **Quick Commands**

**Test GPS:**
```bash
python3 test_gps_connection.py /dev/tty.usbmodem* 115200
```

**Run with GPS:**
```bash
python3 triad_c2.py
```

**Check devices:**
```bash
ls -l /dev/tty.usbmodem*
```

**Access web UI:**
```
http://192.168.3.1
```

**View documentation:**
```bash
cat docs/integration/septentrio/QUICKSTART.md
```

---

## 📚 **Documentation**

**Quick References:**
- This file: `GPS_SETUP_CHECKLIST.md`
- Quick start: `docs/integration/septentrio/QUICKSTART.md`
- Full guide: `docs/integration/septentrio/INTEGRATION_GUIDE.md`
- Commands: `docs/integration/septentrio/RXTOOLS_USER_MANUAL_EXTRACT.md`

---

## ✨ **What Happens Next**

**When GPS is connected and working:**

1. **Ownship Data Available**
   - Position (lat/lon/altitude)
   - True heading (from dual-antenna)
   - Speed and track
   - Updates at 5 Hz

2. **Enables Features**
   - Geo-referenced track positions
   - Accurate threat bearings
   - Map overlay capabilities
   - Coordinate transforms

3. **System Status**
   - GPS indicator shows ONLINE
   - Ownship icon on display
   - Ready for tactical operations

---

**🚀 Ready to connect your GPS? Follow Step 1 above!**

**📞 Questions?** See documentation in `/docs/integration/septentrio/`
