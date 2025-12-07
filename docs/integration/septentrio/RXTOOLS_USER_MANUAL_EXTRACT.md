# RxTools User Manual - Key Extracts for TriAD C2

**Version:** 25.0.0  
**Source:** rxtools_v25.0.0_user_manual.pdf (219 pages, 12.3 MB)  
**Location:** `/Integration docs/Septentrio GPS/`  
**Extracted:** December 2, 2025

---

## Overview

This document contains key extracts from the RxTools User Manual specifically relevant to integrating the Holybro H-RTK Mosaic-H with TriAD C2. For complete information, refer to the full PDF manual.

**What is RxTools?**
RxTools is Septentrio's GNSS receiver configuration and monitoring software suite for mosaic-H receivers.

**Key Applications for TriAD C2:**
- **RxControl** - Main GUI for receiver configuration and monitoring
- **RxAssistant** - Simplified configuration interface
- **Expert Console** - Command-line interface for advanced configuration

---

## Quick Reference

### Default Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| **USB Port** | `/dev/ttyACM0` | Linux default |
| **Baud Rate** | 115200 | Default for USB |
| **Web Interface** | `http://192.168.3.1` | Via USB connection |
| **NMEA Update** | Configurable | 1-100 Hz |
| **Protocol** | NMEA 0183 / SBF | Binary or ASCII |

---

## NMEA Configuration

### Enabling NMEA Output

**Via Expert Console (Command Line):**

```bash
# Enable specific NMEA sentences
setNMEAOutput, Stream1, COM1, GGA, sec1
setNMEAOutput, Stream1, COM1, RMC, sec1
setNMEAOutput, Stream1, COM1, HDT, sec1
setNMEAOutput, Stream1, COM1, VTG, sec1

# Or use short form (sno)
sno, Stream1, COM1, GGA, sec1
sno, Stream1, COM1, RMC, sec1
sno, Stream1, COM1, HDT, sec1
sno, Stream1, COM1, VTG, sec1

# Query current settings
getNMEAOutput, Stream1
# Or: gno, Stream1
```

**Command Syntax:**
```
setNMEAOutput, <Stream>, <Port>, <Message>, <Interval>
```

**Parameters:**
- `Stream` - Stream1, Stream2, etc.
- `Port` - COM1, COM2, USB1, etc.
- `Message` - GGA, RMC, HDT, VTG, etc.
- `Interval` - sec1 (1 Hz), sec5 (0.2 Hz), msec100 (10 Hz), etc.

**For TriAD C2 Integration:**
```bash
# Configure for 5 Hz update (recommended)
sno, Stream1, USB1, GGA, msec200
sno, Stream1, USB1, RMC, msec200
sno, Stream1, USB1, HDT, msec200
sno, Stream1, USB1, VTG, msec200
```

### NMEA Sentences Reference

**Required for TriAD C2:**

**$GPGGA - Position Fix Data**
- Latitude, longitude, altitude
- Fix quality indicator
- Number of satellites
- HDOP
- Update: 5-10 Hz recommended

**$GPRMC - Recommended Minimum**
- Position
- Speed over ground
- Track angle
- Date
- Magnetic variation

**$GPHDT - True Heading** ⚠️ **CRITICAL for dual-antenna**
- True heading from dual-antenna baseline
- Only available with mosaic-H in dual-antenna mode
- **This is the primary heading source for TriAD C2**

**$GPVTG - Velocity and Track**
- True track
- Magnetic track
- Ground speed (knots and km/h)
- Backup for heading if HDT not available

**Optional Septentrio Sentences:**

**$PSAT,HPR - Heading, Pitch, Roll**
- More detailed attitude information
- Septentrio proprietary format
- Includes baseline quality metrics

---

## Dual-Antenna / Heading Configuration

### Attitude Tab in RxControl

**Location:** Bottom section of RxControl main window

**Displays:**
- **Mode:** Current GNSS heading/attitude mode
- **Error1:** Status for auxiliary antenna 1
- **Error2:** Status for auxiliary antenna 2  
- **Nr SV:** Average number of satellites in attitude calculations

**Modes:**
- **No heading** - Dual-antenna not configured or no lock
- **Float** - Heading solution with float ambiguities
- **Fixed** - Heading solution with fixed ambiguities (best)

### Configuring Dual-Antenna Heading

**Requirements:**
1. Two antennas connected (ANT1 = primary, ANT2 = secondary)
2. Known baseline length (distance between antennas)
3. Clear sky view for both antennas
4. Receiver firmware supports heading

**Via Web Interface:**
1. Connect to `http://192.168.3.1`
2. Navigate to **Attitude → Heading Setup**
3. Configure:
   - **Mode:** Dual-Antenna / Moving Baseline
   - **Baseline Length:** `1.0` meters (your actual measurement)
   - **Baseline Orientation:** `0` degrees (forward)
   - **Min Elevation:** `10` degrees (recommended)
4. Click **Apply** then **Save to Boot**

**Via Command Line:**
```bash
# Set baseline length (meters)
setHeadingBaseline, 1.0, 0.0

# Enable heading mode
setAttitudeMode, Moving Base

# Save to boot configuration
saveConfiguration, Boot
```

### Heading Accuracy

**Expected Performance:**

| Baseline | Heading Accuracy | Pitch/Roll Accuracy |
|----------|------------------|---------------------|
| 0.5 m | 0.30° | 0.50° |
| **1.0 m** | **0.15°** | **0.25°** |
| 2.0 m | 0.08° | 0.13° |
| 5.0 m | 0.03° | 0.05° |

**For TriAD C2:**
- 1m baseline recommended
- 0.15° accuracy sufficient for threat bearing calculations
- Fixed mode required for best performance

### Troubleshooting Heading

**No heading output (no HDT sentences):**
1. Check both antennas connected
2. Verify baseline configuration
3. Wait 30-60 seconds for initial lock
4. Check satellite count (need 4+ satellites per antenna)
5. Verify clear sky view

**Heading is 180° off:**
- ANT1 and ANT2 are swapped
- **Solution:** Swap antenna cables or set orientation to 180°

**Heading unstable/jumping:**
- Baseline too short (<0.5m)
- Antennas not rigidly mounted
- Multipath from nearby metal surfaces
- **Solution:** Increase baseline, improve mounting

---

## Connection Methods

### USB Connection (Recommended for TriAD C2)

**Advantages:**
- Automatic driver installation
- Creates network interface (192.168.3.1)
- High data rate support
- Power and data on single cable

**Linux Connection:**
```bash
# Device appears as
/dev/ttyACM0

# Check connection
ls -l /dev/ttyACM0

# Should show: crw-rw---- 1 root dialout

# Add user to dialout group if needed
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

**Baud Rate:** 115200 (default, do not change for USB)

### Serial Connection (COM Port)

**If using serial instead of USB:**

**Baud Rates Supported:**
- 4800
- 9600
- 19200
- 38400
- 57600
- **115200** (recommended)
- 230400
- 460800
- 921600

**Configure via command:**
```bash
# Set baud rate for COM1
setCOMSettings, COM1, baud115200

# Save to boot
saveConfiguration, Boot
```

### Network / TCP Connection

**For remote access:**

**Default mosaic-H Network:**
- IP: `192.168.3.1` (USB interface)
- NMEA TCP Port: `28784`
- SBF TCP Port: `28785`

**Connect via TCP:**
```python
import socket

# Connect to NMEA stream
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.3.1', 28784))

# Receive NMEA data
while True:
    data = sock.recv(1024)
    print(data.decode('ascii'))
```

---

## RxControl Expert Console

### Accessing Expert Console

**In RxControl:**
1. Menu: **Tools → Expert Control**
2. Three tabs available:
   - **Receiver Commands** - Send commands, view responses
   - **ASCII Display** - View receiver ASCII output
   - **NMEA** - Monitor NMEA sentences

### Command Line Usage

**Features:**
- Full command set access
- Tab completion (if supported)
- Command history (up/down arrows, last 50 commands)
- Help system built-in

**Example Session:**
```bash
# Get help for a command
help, setNMEAOutput

# Output:
# setNMEAOutput (=sno), Stream, Cd, Messages, Interval
# "Select NMEA message types and update intervals"

# Enable GGA at 1 Hz
sno, Stream1, COM1, GGA, sec1

# Response:
# $R: sno, Stream1, COM1, GGA, sec1
# NMEAOutput, Stream1, COM1, GGA, sec1

# Query current settings
gno, Stream1

# Save configuration
saveConfiguration, Boot
```

**Common Commands:**

| Command | Shortcut | Purpose |
|---------|----------|---------|
| `setNMEAOutput` | `sno` | Configure NMEA output |
| `getNMEAOutput` | `gno` | Query NMEA settings |
| `setHeadingBaseline` | - | Configure antenna baseline |
| `saveConfiguration` | - | Save settings to flash |
| `reboot` | - | Restart receiver |
| `help` | - | Get command help |

---

## RxAssistant (Simplified Configuration)

### Purpose

RxAssistant provides a simplified interface for basic configuration without requiring deep technical knowledge.

**Key Features:**
- Position monitoring
- NTRIP configuration (RTK corrections)
- NMEA output configuration
- Configuration profile management

### Configuring NMEA via RxAssistant

**Steps:**
1. Launch RxAssistant
2. Connect to receiver
3. Navigate to **Communication** tab
4. Select **NMEA Output** section
5. Enable required sentences:
   - ✅ GGA
   - ✅ RMC
   - ✅ HDT
   - ✅ VTG
6. Set update rate: **5 Hz** (or 0.2 seconds)
7. Click **Apply** then **Save to Boot**

**Reference:** User Manual Section 10.2.3, Page 160

---

## Logging NMEA Data

### Via RxControl Logger

**Purpose:** Record NMEA data for analysis or playback

**Steps:**
1. Menu: **Logging → RxControl Logging**
2. **Global tab:**
   - Set log directory
   - Select: **NMEA** (or both SBF and NMEA)
3. **NMEA tab:**
   - Select sentences to log
   - Set update interval
4. Click **Start Logging**

**Log Files:**
- Format: `.nmea` or custom
- Can be replayed for testing
- Useful for driver development

**For TriAD C2 Testing:**
- Log NMEA during test runs
- Verify HDT sentences present
- Check update rates
- Validate data quality

---

## RTK Configuration (Optional)

### For Centimeter-Level Accuracy

**RTK Requirements:**
- NTRIP correction service (or base station)
- Network connection
- Clear sky view

**Via RxAssistant:**
1. Navigate to **Corrections** tab
2. **NTRIP Client** section
3. Enter:
   - **Server:** `your-ntrip-server.com`
   - **Port:** `2101`
   - **Mountpoint:** Select from list
   - **Username/Password:** If required
4. Click **Connect**
5. Verify **RTK FIX** status in Position tab

**Via Command Line:**
```bash
# Configure NTRIP
setNTRIPClient, on, server.com, 2101, mountpoint, user, pass

# Save
saveConfiguration, Boot
```

**RTK Performance:**
- Horizontal: 0.6 cm + 0.5 ppm
- Vertical: 1.0 cm + 1 ppm
- Time to fix: 30-120 seconds

**For TriAD C2:**
- RTK optional (SBAS adequate for most use cases)
- Useful for precise threat localization
- Requires reliable internet connection

---

## Troubleshooting

### No NMEA Output

**Symptoms:** No data on serial port/USB

**Checks:**
1. Verify NMEA enabled: `gno, Stream1`
2. Check correct port selected (USB1, COM1, etc.)
3. Confirm baud rate matches (115200 for USB)
4. Test with RxControl Expert Console → NMEA tab

**Fix:**
```bash
# Re-enable NMEA
sno, Stream1, USB1, GGA, sec1
sno, Stream1, USB1, RMC, sec1
sno, Stream1, USB1, HDT, sec1
sno, Stream1, USB1, VTG, sec1
```

### No Position Fix

**Symptoms:** GGA shows no valid position

**Checks:**
1. Clear sky view (need 4+ satellites)
2. Wait 1-2 minutes for cold start
3. Check antenna connections
4. Verify antenna power (if active antennas)

**Monitor:**
```bash
# Check satellite count
# In RxControl: View → Sky Plot
# Should see 8+ satellites
```

### No Heading (HDT)

**Symptoms:** Position works, no HDT sentences

**Checks:**
1. Both antennas connected
2. Baseline configured
3. Wait 30-60 seconds for heading lock
4. Check Attitude tab in RxControl

**Fix:**
```bash
# Verify baseline
getHeadingBaseline

# Should return: BaselineLength, BaselineOrientation
# If not set:
setHeadingBaseline, 1.0, 0.0
saveConfiguration, Boot
```

### Web Interface Not Accessible

**Symptoms:** Cannot reach `http://192.168.3.1`

**Checks:**
1. USB cable connected
2. USB drivers installed
3. Computer network shows new interface (192.168.3.x)
4. Try different browser

**Linux Network Check:**
```bash
# Check for USB network interface
ip addr show

# Should see interface with 192.168.3.x address
# Example: usb0 or similar

# Test connectivity
ping 192.168.3.1
```

---

## Best Practices for TriAD C2

### Configuration Checklist

**Initial Setup:**
- [ ] Connect USB, verify `/dev/ttyACM0` appears
- [ ] Access web UI at `http://192.168.3.1`
- [ ] Configure NMEA output (GGA, RMC, HDT, VTG)
- [ ] Set update rate to 5-10 Hz
- [ ] Configure dual-antenna baseline (1.0m)
- [ ] Verify heading lock (Fixed mode)
- [ ] Save configuration to boot
- [ ] Test with `test_gps_connection.py`

**Operational:**
- Monitor heading mode (should be Fixed)
- Check satellite count (8+ recommended)
- Verify HDOP < 2.0
- Monitor for error messages
- Log data for analysis if issues occur

**Performance:**
- Use USB connection (not serial)
- Keep antennas clear of obstructions
- Avoid metal surfaces near antennas
- Maintain rigid antenna mounting
- Check for RF interference

---

## Command Reference

### Essential Commands

| Command | Syntax | Example |
|---------|--------|---------|
| **NMEA Output** | `sno, Stream, Port, Msg, Interval` | `sno, Stream1, USB1, GGA, msec200` |
| **Query NMEA** | `gno, Stream` | `gno, Stream1` |
| **Baseline** | `setHeadingBaseline, Length, Orient` | `setHeadingBaseline, 1.0, 0.0` |
| **Save Config** | `saveConfiguration, Boot` | `saveConfiguration, Boot` |
| **Reboot** | `reboot` | `reboot` |
| **Get Status** | `getReceiverStatus` | `getReceiverStatus` |

### NMEA Interval Values

| Value | Rate | Update Frequency |
|-------|------|------------------|
| `sec1` | 1 Hz | Once per second |
| `sec5` | 0.2 Hz | Every 5 seconds |
| `msec200` | 5 Hz | **Recommended for TriAD C2** |
| `msec100` | 10 Hz | High rate |
| `msec50` | 20 Hz | Very high rate |
| `msec10` | 100 Hz | Maximum rate |

---

## References

**Full Documentation:**
- RxTools Manual: rxtools_v25.0.0_user_manual.pdf (219 pages)
- Release Notes: `RXTOOLS_RELEASE_NOTES.md`
- Integration Guide: `INTEGRATION_GUIDE.md`

**TriAD C2 Integration:**
- Quick Start: `QUICKSTART.md`
- Test Script: `/test_gps_connection.py`
- Overview: `OVERVIEW_SPECIFICATIONS.md`

**Septentrio Resources:**
- Website: https://www.septentrio.com
- Support: support@septentrio.com
- Manual Download: www.septentrio.com/support/mosaic/mosaic-h

---

**Status:** ✅ Complete - Key sections extracted  
**Source:** rxtools_v25.0.0_user_manual.pdf (219 pages)  
**Focus:** NMEA configuration, heading setup, commands for TriAD C2  
**Last Updated:** December 2, 2025  
**Extracted By:** Auto-populated from PDF text extraction
