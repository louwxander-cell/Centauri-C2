# Septentrio H-RTK Mosaic-H Integration Guide

## Hardware Overview

**Model:** Septentrio H-RTK Mosaic-H  
**Type:** Dual-antenna GNSS receiver  
**RTK Capable:** Yes  
**Update Rate:** Up to 100 Hz  
**Constellations:** GPS, GLONASS, Galileo, BeiDou

---

## Specifications

### Key Features
- **Dual-antenna heading** - True heading without motion
- **High precision** - RTK capable (<2cm horizontal)
- **Multi-GNSS** - All major constellations
- **Web interface** - Easy configuration via browser
- **USB + Serial + Ethernet** - Multiple connection options

### Heading Performance
- **Baseline:** 0.5m - 2m (longer = better accuracy)
- **Heading accuracy:** 0.2° RMS (1m baseline)
- **Heading update rate:** Same as position (up to 100 Hz)

### Position Performance
- **Standalone:** 1.5m CEP
- **SBAS (WAAS/EGNOS):** <1m
- **RTK:** <2cm horizontal, <3cm vertical

---

## Default Configuration

### Connection Options

**Option 1: USB (Recommended for initial setup)**
- Port: `/dev/ttyACM0` (Linux) or `COM#` (Windows)
- Baud rate: **115200** (default)
- Protocol: NMEA 0183

**Option 2: Ethernet**
- Default IP: `192.168.3.1`
- NMEA port: `28784` (TCP)
- Web interface: `http://192.168.3.1`

**Option 3: Serial (COM1/COM2)**
- Baud rate: Configurable (typically 115200)
- Default: COM1 for NMEA output

### NMEA Output (Default)

The Mosaic-H outputs these sentences by default:
- **$GPGGA** - Position fix (1 Hz)
- **$GPRMC** - Recommended minimum (1 Hz)
- **$GPGSA** - Satellite status
- **$GPGSV** - Satellites in view
- **$GPHDT** - True heading ← **KEY for dual-antenna**
- **$GPVTG** - Track and speed

**Custom Septentrio Sentences:**
- **$PSAT,HPR** - High-precision heading/pitch/roll

---

## Quick Start Integration

### Step 1: Hardware Setup

**Antenna Mounting:**
1. Mount both antennas on rigid platform
2. Align baseline with vehicle axis:
   ```
   ANT1 (Primary) ───► ANT2 (Secondary)
        └─── Direction of travel ───►
   ```
3. Minimum separation: 0.5m (1m recommended)
4. Clear sky view (>150° horizon)
5. Level mounting (±5° tolerance)

**Connections:**
1. Connect ANT1 to **Primary** port (usually labeled "ANT1" or "MAIN")
2. Connect ANT2 to **Secondary** port (labeled "ANT2" or "AUX")
3. Connect USB cable to computer
4. Apply power (12-24V DC, or USB power if supported)

### Step 2: Web Configuration (Optional but Recommended)

**Access Web Interface:**
1. Connect via USB or Ethernet
2. Open browser: `http://192.168.3.1`
3. Default login: No password (or check manual)

**Configure for C2 Integration:**
1. **NMEA Output:**
   - Go to: **Communication → NMEA/SBF**
   - Enable port: **USB1** or **COM1**
   - Baud rate: **115200**
   - Update rate: **5 Hz** (or 10 Hz if needed)

2. **Enable Required Sentences:**
   - Check: **GGA** (position)
   - Check: **RMC** (speed/track)
   - Check: **HDT** (heading) ← **CRITICAL**
   - Check: **VTG** (velocity)
   - Optional: **PSAT,HPR** (Septentrio heading)

3. **Dual-Antenna Mode:**
   - Go to: **Attitude → Heading Setup**
   - Enable: **Moving Base** or **Dual-Antenna**
   - Set baseline length: `1.0` (meters, your actual distance)
   - Set baseline orientation: `0` (forward)

4. **Save Configuration:**
   - Click **"Current → Boot"** to save settings
   - Power cycle to verify settings persist

### Step 3: Test Connection

**Run Test Script:**
```bash
# Install dependencies (if not already done)
pip install pyserial pynmea2

# Test USB connection
python3 test_gps_connection.py /dev/ttyACM0 115200

# Or test serial port
python3 test_gps_connection.py /dev/ttyUSB0 115200
```

**Expected Output:**
```
✓ GPS is outputting NMEA sentences
✓ Position fix acquired
  → Latitude: -25.841105°
  → Longitude: 28.180340°
✓ True heading available (dual-antenna mode)
  → Heading: 90.5°
✓ Update rate is adequate (5.0 Hz)
✓ GPS READY FOR INTEGRATION
```

### Step 4: Configure TriAD C2

**Update `/config/settings.json`:**
```json
{
  "sensors": {
    "gps": {
      "enabled": true,
      "driver": "production",
      "model": "septentrio_mosaic_h",
      "port": "/dev/ttyACM0",
      "baudrate": 115200,
      "update_rate_hz": 5
    }
  }
}
```

### Step 5: Create Production Driver

Create `/src/drivers/gps_septentrio.py`:

```python
"""Septentrio Mosaic-H GPS driver"""

import serial
import pynmea2
import time
from .base import BaseDriver
from ..core.bus import SignalBus
from ..core.datamodels import GeoPosition


class SeptentrioMosaicDriver(BaseDriver):
    """
    Production driver for Septentrio H-RTK Mosaic-H dual-antenna GPS.
    Supports NMEA 0183 output with true heading (HDT) and position (GGA/RMC).
    """
    
    def __init__(self, port: str, baudrate: int = 115200, parent=None):
        super().__init__("SeptentrioGPS", parent)
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
        self.fix_quality = None
        
        # Septentrio-specific
        self.heading_baseline = None  # From PSAT,HPR
        self.pitch = None
        self.roll = None
        
        # Statistics
        self.sentence_count = 0
        self.heading_count = 0
        self.last_fix_time = None
        
    def run(self):
        """Main thread loop - reads NMEA sentences"""
        print(f"[{self.name}] Starting Septentrio Mosaic-H on {self.port} at {self.baudrate} baud")
        
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
        print(f"[{self.name}] Septentrio GPS driver stopped")
    
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
            print(f"[{self.name}] Waiting for dual-antenna heading lock...")
        except Exception as e:
            self.emit_error(f"Failed to open serial port: {str(e)}")
            raise
    
    def _parse_nmea(self, sentence: str):
        """Parse NMEA sentence (standard and Septentrio-specific)"""
        try:
            # Handle Septentrio proprietary sentences first
            if sentence.startswith('$PSAT'):
                self._parse_septentrio(sentence)
                return
            
            # Parse standard NMEA
            msg = pynmea2.parse(sentence)
            
            # GGA - Position fix data
            if isinstance(msg, pynmea2.GGA):
                if msg.latitude and msg.longitude:
                    self.lat = msg.latitude
                    self.lon = msg.longitude
                    self.altitude = msg.altitude if msg.altitude else 0.0
                    self.fix_quality = msg.gps_qual
            
            # RMC - Recommended minimum
            elif isinstance(msg, pynmea2.RMC):
                if msg.latitude and msg.longitude:
                    self.lat = msg.latitude
                    self.lon = msg.longitude
                if msg.spd_over_grnd:
                    self.speed_mps = msg.spd_over_grnd * 0.514444  # knots to m/s
            
            # HDT - True heading (KEY for dual-antenna)
            elif isinstance(msg, pynmea2.HDT):
                if msg.heading:
                    self.heading = msg.heading
                    self.heading_count += 1
                    
                    # Log first heading lock
                    if self.heading_count == 1:
                        print(f"[{self.name}] ✓ Dual-antenna heading lock acquired: {self.heading:.1f}°")
            
            # VTG - Velocity and track
            elif isinstance(msg, pynmea2.VTG):
                if msg.true_track:
                    # Use as backup if HDT not available
                    if self.heading is None:
                        self.heading = msg.true_track
                if msg.spd_over_grnd_kmph:
                    self.speed_mps = msg.spd_over_grnd_kmph / 3.6  # km/h to m/s
                    
        except pynmea2.ParseError:
            pass  # Ignore parse errors
        except Exception as e:
            self.emit_error(f"NMEA parse error: {str(e)}")
    
    def _parse_septentrio(self, sentence: str):
        """Parse Septentrio proprietary sentences"""
        try:
            parts = sentence.split(',')
            
            # $PSAT,HPR - Heading, Pitch, Roll
            if len(parts) > 1 and parts[1] == 'HPR':
                # Format: $PSAT,HPR,timestamp,heading,pitch,roll,baseline,mode*checksum
                if len(parts) >= 7:
                    heading = float(parts[3])
                    pitch = float(parts[4])
                    roll = float(parts[5])
                    baseline = float(parts[6]) if parts[6] else None
                    
                    self.heading = heading
                    self.pitch = pitch
                    self.roll = roll
                    self.heading_baseline = baseline
                    self.heading_count += 1
                    
                    # Log first heading
                    if self.heading_count == 1:
                        print(f"[{self.name}] ✓ Septentrio HPR acquired: H={heading:.1f}° P={pitch:.1f}° R={roll:.1f}°")
                        if baseline:
                            print(f"[{self.name}]   Baseline: {baseline:.2f}m")
                    
        except (ValueError, IndexError) as e:
            pass  # Ignore parse errors
```

### Step 6: Update Main Application

Modify `/triad_c2.py`:

```python
# Near top, add import
from src.drivers.gps_septentrio import SeptentrioMosaicDriver
import json

# In initialization section:
config = json.load(open('config/settings.json'))
if config['sensors']['gps']['enabled']:
    port = config['sensors']['gps']['port']
    baudrate = config['sensors']['gps']['baudrate']
    
    gps = SeptentrioMosaicDriver(port=port, baudrate=baudrate)
    gps.start()
    print(f"[INIT] Septentrio GPS started on {port}")
```

---

## Verification

### Console Output

**Successful Initialization:**
```
[SeptentrioGPS] Starting Septentrio Mosaic-H on /dev/ttyACM0 at 115200 baud
[SeptentrioGPS] ✓ Opened /dev/ttyACM0 at 115200 baud
[SeptentrioGPS] Waiting for dual-antenna heading lock...
[SeptentrioGPS] ✓ Dual-antenna heading lock acquired: 90.5°
[SeptentrioGPS] ✓ Septentrio HPR acquired: H=90.5° P=1.2° R=-0.3°
[SeptentrioGPS]   Baseline: 1.00m
[BRIDGE] Ownship updated: lat=-25.841105 lon=28.180340 hdg=90.5°
```

### UI Verification

1. **GPS Status Indicator** - Green/Online
2. **Ownship Icon** - Correct position on tactical display
3. **Heading Arrow** - Points in correct direction
4. **Sensor Panel** - Shows "GPS: ONLINE"

---

## Advanced Configuration

### High Update Rate (10 Hz)

**Via Web Interface:**
1. Go to: **Communication → NMEA/SBF**
2. Set **Output interval:** `0.1` seconds (10 Hz)
3. Save and reboot

**Update config:**
```json
"update_rate_hz": 10
```

### RTK Mode (Centimeter Accuracy)

**Option 1: NTRIP (Internet corrections)**
```json
"gps": {
  "rtk_enabled": true,
  "ntrip_server": "your-ntrip-server.com",
  "ntrip_port": 2101,
  "ntrip_mountpoint": "RTCM3_BASE",
  "ntrip_username": "user",
  "ntrip_password": "pass"
}
```

Configure via web interface:
1. **Corrections → NTRIP Client**
2. Enter server details
3. Enable correction stream

**Option 2: Base Station (Local RTK)**
- Set up second Mosaic-H as base station
- Configure radio link or network connection
- 10-20km range typical

### Multi-GNSS Configuration

Enable all constellations for best performance:
1. **Satellite Tracking → Tracking**
2. Enable: GPS, GLONASS, Galileo, BeiDou
3. More satellites = faster fix, better accuracy

---

## Troubleshooting

### No Heading Output

**Symptoms:** Position works, but HDT sentences missing

**Solutions:**
1. **Check web interface:**
   - **Attitude → Status** - Should show "Fixed" or "Float"
   - Verify baseline length matches physical setup
2. **Antenna connections:**
   - Swap ANT1/ANT2 if heading is 180° off
   - Check cable connections
3. **Wait for initialization:**
   - Dual-antenna can take 30-60 seconds for first fix
4. **Enable PSAT,HPR output:**
   - More robust than HDT for Septentrio units

### Heading Jumps/Unstable

**Causes:**
- Baseline too short (<0.5m)
- Antennas not rigid (vibration)
- Multipath (reflections from metal surfaces)

**Solutions:**
- Increase baseline to 1m or longer
- Mount on rigid platform
- Ensure 10cm+ clearance from metal surfaces

### RTK Not Working

**Check:**
1. Internet connection for NTRIP
2. Correction stream in web interface status
3. Base station within range (<20km)
4. Correct mountpoint/credentials

---

## Septentrio-Specific Features

### Advantages

✅ **High-quality receiver** - Excellent multipath rejection  
✅ **Fast heading acquisition** - Typically <30 seconds  
✅ **Web interface** - Easy configuration without special software  
✅ **Multi-frequency** - L1/L2/L5 for best accuracy  
✅ **GNSS+** - Advanced algorithms for urban environments  

### Web Interface Access

**USB Connection:**
- Mosaic creates network interface: `192.168.3.1/24`
- Computer gets IP: `192.168.3.2` (automatic)
- Browse to: `http://192.168.3.1`

**Useful Pages:**
- **Status → Attitude** - Check heading status
- **View → Skyplot** - See satellite visibility
- **Data Logging** - Record for analysis
- **Diagnostics → Console** - Send commands

---

## Quick Reference

### Connection Cheat Sheet

| Interface | Port/IP | Baud/Protocol | Default |
|-----------|---------|---------------|---------|
| USB | `/dev/ttyACM0` | 115200 baud | ✅ |
| COM1 (Serial) | Configurable | 115200 baud | Optional |
| Ethernet | `192.168.3.1` | TCP:28784 | Alternative |
| Web UI | `192.168.3.1` | HTTP | Configuration |

### NMEA Sentences

| Sentence | Data | Required? |
|----------|------|-----------|
| $GPGGA | Position | ✅ Yes |
| $GPRMC | Speed/Track | ✅ Yes |
| $GPHDT | True Heading | ✅ **CRITICAL** |
| $GPVTG | Velocity | Optional |
| $PSAT,HPR | Sep. Heading/Pitch/Roll | Recommended |

### Commands (via Console)

```
sso, Stream1, NMEA, USB1, on          # Enable NMEA on USB
setHeadingBaseline, 1.0, 0.0          # Set 1m baseline, 0° offset
saveConfiguration, Boot               # Save settings
reboot                                 # Restart receiver
```

---

## Next Steps

✅ **GPS Integrated** - Proceed to next sensor:
1. Radar (Echodyne Echoguard)
2. RF Detection (BlueHalo SkyView)

---

**Support:**
- Septentrio Support: support@septentrio.com
- Mosaic-H Manual: [Septentrio Downloads](https://www.septentrio.com/en/support/mosaic/mosaic-h)
- TriAD C2 Integration: See `/docs/integration/`
