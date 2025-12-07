# Dual-Antenna GPS Integration Guide

## Overview

This guide walks through integrating a dual-antenna GPS/GNSS system with the TriAD C2 platform. Dual-antenna GPS provides both **position** and **true heading** without requiring vehicle motion, making it ideal for stationary or slow-moving C-UAS platforms.

**Status:** Ready to implement  
**Hardware Required:** Dual-antenna GPS/GNSS receiver with NMEA output  
**Connection:** Serial (RS-232/USB) or Network (TCP/UDP)

---

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Understanding Dual-Antenna GPS](#understanding-dual-antenna-gps)
3. [Pre-Integration Checklist](#pre-integration-checklist)
4. [Step-by-Step Integration](#step-by-step-integration)
5. [Testing & Validation](#testing--validation)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Configuration](#advanced-configuration)

---

## Hardware Requirements

### Minimum Requirements

**GPS/GNSS Receiver:**
- **Dual-antenna system** (primary + secondary antenna)
- **NMEA 0183 output** (standard GPS sentence format)
- **True heading output** (HDT or custom sentence)
- **Update rate:** ≥1 Hz (5-10 Hz recommended)

**Connection Options:**
- **Serial:** RS-232, RS-422, or USB-to-Serial
- **Network:** TCP or UDP over Ethernet

**Antenna Specifications:**
- **Baseline:** 0.5m - 2.0m separation (longer = better accuracy)
- **Mounting:** Rigid, level platform with clear sky view
- **Cable:** Low-loss, proper grounding

### Recommended Systems

**Common Dual-Antenna GPS Units:**
1. **Trimble BD982** - High-precision, RTK-capable
2. **Hemisphere Atlas** - Rugged, military-grade
3. **NovAtel SPAN** - Integrated INS + GPS
4. **U-blox F9P (2x)** - Budget-friendly, DIY option

**For TriAD C2:**
- Position accuracy: <2m CEP (better with RTK/SBAS)
- Heading accuracy: <0.5° (with 1m baseline)
- Output format: NMEA 0183 (GGA, RMC, HDT, VTG)

---

## Understanding Dual-Antenna GPS

### Why Dual-Antenna?

**Single Antenna (Traditional GPS):**
- ❌ Heading only available while moving
- ❌ Requires several seconds of motion to compute heading
- ❌ Inaccurate at low speeds

**Dual-Antenna (This System):**
- ✅ True heading even when stationary
- ✅ Instant heading on power-up
- ✅ Accurate heading regardless of speed
- ✅ Essential for C-UAS (stationary guard posts)

### How It Works

```
Antenna 1 (Primary)          Antenna 2 (Secondary)
      ↓                              ↓
      ●─────────────────────────────●
      └─── Baseline (0.5m - 2m) ────┘
              │
              │ Phase difference between antennas
              │ determines heading direction
              ▼
        GPS Receiver
              │
              ▼
      NMEA Output Stream:
      - $GPGGA (Position)
      - $GPRMC (Speed)
      - $GPHDT (True Heading) ← Key for dual-antenna
      - $GPVTG (Track/Speed)
```

### NMEA Sentences

**$GPGGA - Position Fix:**
```
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
       └─────┘ └──────────┘ └──────────┘
       Time    Latitude      Longitude
```

**$GPHDT - True Heading:**
```
$GPHDT,90.5,T*2D
       └───┘
       Heading (degrees true)
```

**$GPRMC - Recommended Minimum:**
```
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
                                       └───┘ └───┘
                                       Speed  Track
```

---

## Pre-Integration Checklist

### 1. Hardware Setup

**Antenna Mounting:**
- [ ] Both antennas mounted on rigid, level surface
- [ ] Clear sky view (>150° horizon visibility)
- [ ] Baseline aligned with vehicle/platform axis
- [ ] Secure mounting (vibration-resistant)
- [ ] Proper grounding

**Cabling:**
- [ ] Antenna cables <10m (minimize signal loss)
- [ ] Away from RF sources (radar, transmitters)
- [ ] Proper connectors (TNC, SMA, etc.)
- [ ] Cable strain relief

**Receiver Configuration:**
- [ ] NMEA 0183 output enabled
- [ ] Baud rate configured (typically 9600 or 115200)
- [ ] Required sentences enabled: GGA, RMC, HDT, VTG
- [ ] Update rate set (1-10 Hz)

### 2. Software Requirements

**Install Python Dependencies:**
```bash
pip install pyserial pynmea2
```

**Verify Serial Port Access:**
```bash
# Linux/Mac
ls -l /dev/tty*
# Typical ports: /dev/ttyUSB0, /dev/ttyACM0, /dev/ttyS0

# Grant permissions (Linux)
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### 3. Identify Connection Parameters

**Serial Connection:**
- Port: `/dev/ttyUSB0` (Linux), `COM3` (Windows)
- Baud rate: `9600` or `115200` (check GPS manual)
- Data bits: `8`
- Parity: `None`
- Stop bits: `1`

**Network Connection:**
- IP address of GPS unit (e.g., `192.168.1.100`)
- Port (typically `10001` or `2000`)
- Protocol: TCP or UDP

---

## Step-by-Step Integration

### Step 1: Test GPS Hardware Connection

First, verify the GPS is outputting NMEA data correctly.

**Option A: Serial Connection**
```bash
# Linux/Mac
cat /dev/ttyUSB0

# Windows (use PuTTY or TeraTerm)
# Connect to COM port at specified baud rate
```

**Expected Output:**
```
$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
$GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
$GPHDT,90.5,T*2D
$GPVTG,084.4,T,081.3,M,022.4,N,041.5,K*43
```

✅ **If you see NMEA sentences**, proceed to Step 2.  
❌ **If not**, check:
- Cable connections
- GPS power supply
- Serial port settings (baud rate)
- GPS configuration

### Step 2: Create Production GPS Driver

Create a new file: `/Users/xanderlouw/CascadeProjects/C2/src/drivers/gps_production.py`

```python
"""Production Dual-Antenna GPS driver"""

import serial
import pynmea2
import time
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import GeoPosition


class GPSDriverProduction(BaseDriver):
    """
    Production GPS/Compass driver for dual-antenna systems.
    Reads NMEA sentences from serial port and provides:
    - Position (lat/lon/altitude)
    - True heading (from dual-antenna baseline)
    - Speed and track
    """
    
    def __init__(self, port: str, baudrate: int = 9600, parent=None):
        super().__init__("GPSDriver", parent)
        self.signal_bus = SignalBus.instance()
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        # Current position data
        self.lat = None
        self.lon = None
        self.heading = None  # True heading from HDT
        self.altitude = None
        self.speed_mps = None
        self.track = None  # Course over ground
        
        # Statistics
        self.sentence_count = 0
        self.last_fix_time = None
        
    def run(self):
        """Main thread loop - reads NMEA sentences"""
        print(f"[{self.name}] Starting GPS driver on {self.port} at {self.baudrate} baud")
        
        while self._running:
            try:
                # Open serial port
                if not self.serial:
                    self._open_serial()
                
                # Read NMEA sentence
                line = self.serial.readline().decode('ascii', errors='ignore').strip()
                
                if line.startswith('$'):
                    self._parse_nmea(line)
                    self.sentence_count += 1
                    
                    # Emit position if we have valid fix
                    if self.lat and self.lon:
                        position = GeoPosition(
                            lat=self.lat,
                            lon=self.lon,
                            heading=self.heading if self.heading is not None else 0.0,
                            altitude_m=self.altitude if self.altitude else 0.0,
                            speed_mps=self.speed_mps if self.speed_mps else 0.0,
                            timestamp=time.time()
                        )
                        self.signal_bus.emit_ownship(position)
                        self.set_online(True)
                        self.last_fix_time = time.time()
                
                # Check for fix timeout
                if self.last_fix_time and (time.time() - self.last_fix_time) > 5.0:
                    self.set_online(False)
                    self.emit_error("GPS fix lost (timeout)")
                
            except serial.SerialException as e:
                self.emit_error(f"Serial error: {str(e)}")
                self.set_online(False)
                if self.serial:
                    self.serial.close()
                    self.serial = None
                time.sleep(5.0)
            except Exception as e:
                self.emit_error(f"GPS error: {str(e)}")
                time.sleep(1.0)
        
        # Cleanup
        if self.serial:
            self.serial.close()
        self.set_online(False)
        print(f"[{self.name}] GPS driver stopped")
    
    def _open_serial(self):
        """Open serial port"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1.0
            )
            print(f"[{self.name}] ✓ Opened {self.port} at {self.baudrate} baud")
        except Exception as e:
            self.emit_error(f"Failed to open serial port: {str(e)}")
            raise
    
    def _parse_nmea(self, sentence: str):
        """Parse NMEA sentence"""
        try:
            msg = pynmea2.parse(sentence)
            
            # GGA - Position fix data
            if isinstance(msg, pynmea2.GGA):
                if msg.latitude and msg.longitude:
                    self.lat = msg.latitude
                    self.lon = msg.longitude
                    self.altitude = msg.altitude if msg.altitude else 0.0
                    # print(f"[GPS] Position: {self.lat:.6f}, {self.lon:.6f}, {self.altitude:.1f}m")
            
            # RMC - Recommended minimum
            elif isinstance(msg, pynmea2.RMC):
                if msg.latitude and msg.longitude:
                    self.lat = msg.latitude
                    self.lon = msg.longitude
                if msg.spd_over_grnd:
                    self.speed_mps = msg.spd_over_grnd * 0.514444  # knots to m/s
                if msg.true_course:
                    self.track = msg.true_course
            
            # HDT - True heading (KEY for dual-antenna systems)
            elif isinstance(msg, pynmea2.HDT):
                if msg.heading:
                    self.heading = msg.heading
                    # print(f"[GPS] True Heading: {self.heading:.1f}°")
            
            # VTG - Velocity and track
            elif isinstance(msg, pynmea2.VTG):
                if msg.true_track:
                    self.track = msg.true_track
                    # If no HDT available, use track as heading (less accurate)
                    if self.heading is None:
                        self.heading = msg.true_track
                if msg.spd_over_grnd_kmph:
                    self.speed_mps = msg.spd_over_grnd_kmph / 3.6  # km/h to m/s
                    
        except pynmea2.ParseError as e:
            pass  # Ignore parse errors (common with corrupt sentences)
        except Exception as e:
            self.emit_error(f"NMEA parse error: {str(e)}")
```

### Step 3: Update Configuration

Edit `/Users/xanderlouw/CascadeProjects/C2/config/settings.json`:

```json
{
  "sensors": {
    "gps": {
      "enabled": true,
      "driver": "production",
      "port": "/dev/ttyUSB0",
      "baudrate": 9600
    }
  }
}
```

**Adjust Parameters:**
- `port`: Your GPS serial port
- `baudrate`: Match your GPS configuration

### Step 4: Modify Main Application

Edit `/Users/xanderlouw/CascadeProjects/C2/triad_c2.py` to use production GPS driver:

```python
# Near the top, add import
from src.drivers.gps_production import GPSDriverProduction

# In the initialization section, replace mock GPS with production:
# OLD:
# from src.drivers.gps import GPSDriver
# gps = GPSDriver()

# NEW:
config = json.load(open('config/settings.json'))
if config['sensors']['gps']['enabled']:
    port = config['sensors']['gps']['port']
    baudrate = config['sensors']['gps']['baudrate']
    gps = GPSDriverProduction(port=port, baudrate=baudrate)
    gps.start()
    print(f"[INIT] GPS driver started on {port}")
```

### Step 5: Test the Integration

Run the application:

```bash
python3 triad_c2.py
```

**Expected Console Output:**
```
[GPSDriver] Starting GPS driver on /dev/ttyUSB0 at 9600 baud
[GPSDriver] ✓ Opened /dev/ttyUSB0 at 9600 baud
[GPS] Position: -25.841105, 28.180340, 1339.5m
[GPS] True Heading: 90.5°
[BRIDGE] Ownship updated: lat=-25.841105 lon=28.180340 hdg=90.5°
```

**In the UI:**
- Check the GPS status indicator (should be green/online)
- Verify ownship position on tactical display
- Confirm heading arrow points correctly

---

## Testing & Validation

### Test 1: Position Accuracy

**Procedure:**
1. Note GPS-reported position
2. Check against known location (Google Maps, survey data)
3. Verify position accuracy within specifications

**Expected:**
- Without SBAS/RTK: <5m horizontal accuracy
- With SBAS (WAAS/EGNOS): <2m horizontal accuracy
- With RTK: <0.1m horizontal accuracy

### Test 2: Heading Accuracy

**Procedure:**
1. Align antenna baseline with known direction (compass, landmark)
2. Compare GPS heading to actual bearing
3. Rotate platform and verify heading follows

**Expected:**
- Heading accuracy: <1° (with 1m baseline)
- Instant heading update on rotation
- Stable heading when stationary

### Test 3: Update Rate

**Procedure:**
1. Monitor position updates in console
2. Count updates per second

**Expected:**
- Update rate matches GPS configuration (1-10 Hz)
- No dropped messages
- Consistent timing

### Test 4: Signal Loss Recovery

**Procedure:**
1. Cover antennas (block GPS signals)
2. Wait for fix loss (~30 seconds)
3. Uncover antennas
4. Verify reacquisition time

**Expected:**
- Fix loss detected within 5-10 seconds
- Reacquisition within 30-60 seconds
- Status indicator reflects online/offline state

---

## Troubleshooting

### No NMEA Output

**Symptoms:** No data on serial port

**Solutions:**
- ✅ Check GPS power supply
- ✅ Verify serial cable connections
- ✅ Confirm baud rate (try 4800, 9600, 19200, 38400, 115200)
- ✅ Test with different terminal (PuTTY, minicom)
- ✅ Check GPS configuration (may need vendor software)

### No Position Fix

**Symptoms:** NMEA sentences but no position data

**Solutions:**
- ✅ Verify clear sky view (needs 4+ satellites)
- ✅ Allow warm-up time (1-2 minutes for cold start)
- ✅ Check for RF interference
- ✅ Verify antennas are connected
- ✅ Check GPS configuration (may be in demo mode)

### No Heading Output

**Symptoms:** Position works, but no heading

**Solutions:**
- ✅ Verify dual-antenna mode enabled in GPS config
- ✅ Check HDT sentence is enabled
- ✅ Confirm both antennas connected and functioning
- ✅ Check antenna baseline (minimum 0.5m)
- ✅ Verify antennas are not swapped

### Incorrect Heading

**Symptoms:** Heading present but wrong

**Solutions:**
- ✅ Check antenna orientation (primary vs. secondary)
- ✅ Verify antenna baseline configuration in GPS
- ✅ Check for magnetic vs. true heading confusion
- ✅ Calibrate GPS heading (some units require initialization)
- ✅ Verify antennas are level

### Intermittent Dropouts

**Symptoms:** GPS works but loses fix periodically

**Solutions:**
- ✅ Check antenna mounting (vibration, loose cables)
- ✅ Verify power supply stability
- ✅ Check for RF interference sources
- ✅ Inspect antenna cables for damage
- ✅ Update GPS firmware

---

## Advanced Configuration

### High-Precision Mode (RTK)

For <0.1m position accuracy:

**Requirements:**
- RTK-capable GPS receiver
- Base station or NTRIP correction service
- Network connection for corrections

**Configuration:**
```json
"gps": {
  "enabled": true,
  "rtk_enabled": true,
  "ntrip_server": "rtk.example.com",
  "ntrip_port": 2101,
  "ntrip_mountpoint": "BASE1",
  "ntrip_username": "user",
  "ntrip_password": "pass"
}
```

### Custom NMEA Sentences

Some GPS units use proprietary sentences:

```python
# In _parse_nmea(), add custom handling:
elif sentence.startswith('$PTNL'):  # Trimble proprietary
    # Parse custom format
    pass
```

### Network Connection (TCP/UDP)

For GPS units with Ethernet:

```python
class GPSDriverNetwork(BaseDriver):
    def __init__(self, host: str, port: int, protocol='TCP'):
        # ... setup socket connection
        pass
    
    def run(self):
        # Similar to serial, but use socket.recv()
        pass
```

### Multi-GNSS Support

Enable GPS + GLONASS + Galileo + BeiDou:

**Benefits:**
- More satellites visible
- Better urban canyon performance
- Faster fix acquisition

**Configuration:** Check GPS manual for command sequences

---

## Integration Checklist

- [ ] Hardware mounted and connected
- [ ] Serial port identified and accessible
- [ ] Python dependencies installed
- [ ] Production driver created
- [ ] Configuration updated
- [ ] Application modified to use production driver
- [ ] Position accuracy verified
- [ ] Heading accuracy verified
- [ ] Update rate confirmed
- [ ] Signal loss recovery tested
- [ ] Documentation updated

---

## Next Steps

After GPS integration:

1. **Verify ownship data in UI** - Check tactical display
2. **Integrate with threat assessment** - Use accurate heading for threat vectors
3. **Enable coordinate transforms** - Convert sensor data to geo-referenced coordinates
4. **Add map overlay** - Display on satellite/terrain maps
5. **Proceed to radar integration** - Next sensor in the chain

---

## Additional Resources

**NMEA 0183 Specification:**
- https://www.nmea.org/content/STANDARDS/NMEA_0183_Standard

**PySerial Documentation:**
- https://pyserial.readthedocs.io/

**PyNMEA2 Documentation:**
- https://github.com/Knio/pynmea2

**GPS Basics:**
- https://www.gps.gov/systems/gps/performance/accuracy/

---

**Questions?** Contact the TriAD C2 development team or refer to `/docs/integration/` for more guides.
