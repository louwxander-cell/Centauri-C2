# Septentrio Mosaic-H - 30-Minute Quick Start

**Goal:** Get your Mosaic-H integrated with TriAD C2 in 30 minutes.

---

## Prerequisites

- ✅ Holybro H-RTK Mosaic-H unit
- ✅ Two antennas (included)
- ✅ USB Type-C cable
- ✅ Computer with TriAD C2 installed
- ✅ Python 3.8+ with pip

---

## Step 1: Physical Setup (5 minutes)

### Antenna Mounting

```
ANT1 (Primary) ────────► ANT2 (Secondary)
     └──── 1.0m baseline ─────┘
     (Align with vehicle forward axis)
```

**Requirements:**
- Rigid mounting platform
- 1m separation (minimum 0.5m)
- Clear sky view (>150° horizon)
- Level mounting (±5° tolerance)
- Away from metal obstructions

**Connect:**
1. ANT1 → Primary SMA connector (usually labeled "ANT1")
2. ANT2 → Secondary SMA connector (labeled "ANT2")
3. USB Type-C → Computer
4. Power (if external supply needed)

---

## Step 2: Install Dependencies (2 minutes)

```bash
pip install pyserial pynmea2
```

---

## Step 3: Test Connection (5 minutes)

```bash
# Run hardware test
cd /Users/xanderlouw/CascadeProjects/C2
python3 test_gps_connection.py /dev/ttyACM0 115200
```

**Expected Output:**
```
✓ GPS is outputting NMEA sentences
✓ Position fix acquired
  → Latitude: -25.841105°
  → Longitude: 28.180340°
✓ True heading available (dual-antenna mode)  ← CRITICAL
  → Heading: 90.5°
✓ Update rate is adequate (5.0 Hz)

✓ GPS READY FOR INTEGRATION
```

**If test fails:** See troubleshooting section below.

---

## Step 4: Web Configuration (Optional - 5 minutes)

**Access Web Interface:**
```
URL: http://192.168.3.1
```

### Recommended Settings

**Communication → NMEA/SBF:**
- Port: USB1
- Baud Rate: 115200
- Update Rate: 5 Hz
- Enable Sentences:
  - ✅ GGA (position)
  - ✅ RMC (speed/track)
  - ✅ HDT (heading)
  - ✅ VTG (velocity)
  - ✅ PSAT,HPR (Septentrio heading/pitch/roll)

**Attitude → Heading Setup:**
- Mode: Dual-Antenna / Moving Baseline
- Baseline Length: `1.0` meters (your actual measurement)
- Baseline Orientation: `0` degrees (forward)

**Save Configuration:**
- Click "Current → Boot"
- Power cycle to verify persistence

---

## Step 5: Create Driver (3 minutes)

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
    """Production driver for Septentrio Mosaic-H"""
    
    def __init__(self, port: str, baudrate: int = 115200, parent=None):
        super().__init__("SeptentrioGPS", parent)
        self.signal_bus = SignalBus.instance()
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        self.lat = None
        self.lon = None
        self.heading = None
        self.altitude = None
        self.speed_mps = None
        self.last_fix_time = None
        
    def run(self):
        """Main loop - read NMEA"""
        print(f"[{self.name}] Starting on {self.port} at {self.baudrate} baud")
        
        while self._running:
            try:
                if not self.serial:
                    self.serial = serial.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        timeout=1.0
                    )
                    print(f"[{self.name}] ✓ Opened {self.port}")
                
                line = self.serial.readline().decode('ascii', errors='ignore').strip()
                
                if line.startswith('$'):
                    self._parse_nmea(line)
                    
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
                
                if self.last_fix_time and (time.time() - self.last_fix_time) > 5.0:
                    self.set_online(False)
                    
            except Exception as e:
                self.emit_error(f"Error: {str(e)}")
                if self.serial:
                    self.serial.close()
                    self.serial = None
                time.sleep(5.0)
        
        if self.serial:
            self.serial.close()
        self.set_online(False)
    
    def _parse_nmea(self, sentence: str):
        """Parse NMEA sentence"""
        try:
            msg = pynmea2.parse(sentence)
            
            if isinstance(msg, pynmea2.GGA):
                if msg.latitude and msg.longitude:
                    self.lat = msg.latitude
                    self.lon = msg.longitude
                    self.altitude = msg.altitude if msg.altitude else 0.0
            
            elif isinstance(msg, pynmea2.RMC):
                if msg.spd_over_grnd:
                    self.speed_mps = msg.spd_over_grnd * 0.514444
            
            elif isinstance(msg, pynmea2.HDT):
                if msg.heading:
                    self.heading = msg.heading
            
            elif isinstance(msg, pynmea2.VTG):
                if msg.true_track and self.heading is None:
                    self.heading = msg.true_track
                    
        except pynmea2.ParseError:
            pass
```

---

## Step 6: Update Configuration (2 minutes)

Edit `config/settings.json`:

```json
{
  "sensors": {
    "gps": {
      "enabled": true,
      "driver": "production",
      "model": "septentrio_mosaic_h",
      "port": "/dev/ttyACM0",
      "baudrate": 115200
    }
  }
}
```

---

## Step 7: Integrate with TriAD C2 (3 minutes)

Edit `triad_c2.py`:

```python
# Add import at top
from src.drivers.gps_septentrio import SeptentrioMosaicDriver
import json

# In initialization section
config = json.load(open('config/settings.json'))

if config['sensors']['gps']['enabled']:
    gps = SeptentrioMosaicDriver(
        port=config['sensors']['gps']['port'],
        baudrate=config['sensors']['gps']['baudrate']
    )
    gps.start()
    print(f"[INIT] Septentrio GPS started")
```

---

## Step 8: Run & Verify (5 minutes)

```bash
python3 triad_c2.py
```

### Console Verification

**Look for:**
```
[SeptentrioGPS] Starting on /dev/ttyACM0 at 115200 baud
[SeptentrioGPS] ✓ Opened /dev/ttyACM0
[BRIDGE] Ownship updated: lat=-25.841 lon=28.180 hdg=90.5°
```

### UI Verification

1. **GPS Status Indicator** - Should be GREEN/Online
2. **Ownship Position** - Visible on tactical display
3. **Heading Arrow** - Points in correct direction
4. **Sensor Panel** - Shows "GPS: ONLINE"

---

## Troubleshooting

### Test Failed - No NMEA Output

**Check:**
- USB cable connected
- GPS powered on
- Try different port: `/dev/ttyUSB0`, `COM3`, etc.
- Try different baud: `230400`, `9600`

**List ports:**
```bash
ls -l /dev/tty* | grep -i usb
```

### Test Failed - No Position Fix

**Wait:** GPS needs 30-60 seconds for first fix

**Check:**
- Clear sky view
- Antennas connected
- No RF interference

### Test Failed - No Heading (HDT)

**Wait:** Dual-antenna heading can take 30-60 seconds

**Check:**
- Both antennas connected (ANT1 and ANT2)
- Baseline configured in web interface
- HDT sentence enabled

**Access web UI:** `http://192.168.3.1` → Status → Attitude

### Heading is 180° Off

**Solution:** Swap ANT1 ↔ ANT2 cables

Or in web UI:
- Attitude → Heading → Orientation: `180`

### Permission Denied (Linux)

```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### USB Not Recognized

**Check:**
- USB cable (try different cable)
- USB port (try different port)
- Power LED on Mosaic-H

---

## Quick Reference

### Default Settings

| Parameter | Value |
|-----------|-------|
| Port | `/dev/ttyACM0` |
| Baud | `115200` |
| Update Rate | `5 Hz` |
| Protocol | `NMEA 0183` |
| Web UI | `http://192.168.3.1` |

### Key NMEA Sentences

| Sentence | Data |
|----------|------|
| `$GPGGA` | Position (lat/lon/alt) |
| `$GPHDT` | True heading (dual-antenna) |
| `$GPRMC` | Speed and track |
| `$GPVTG` | Velocity |
| `$PSAT,HPR` | Septentrio heading/pitch/roll |

### Antenna Setup

```
Baseline: 1.0m (min 0.5m, max 5m)
Heading Accuracy: 0.15° (1m baseline)
Mounting: Rigid, level platform
Clearance: >10cm from metal
```

---

## Next Steps

✅ **GPS Working** - Proceed to:
1. Verify position accuracy
2. Test heading updates while rotating platform
3. Configure RTK (optional, for cm-level accuracy)
4. Integrate next sensor (Radar or RF)

📚 **More Info:**
- Full guide: `INTEGRATION_GUIDE.md`
- Specifications: `OVERVIEW_SPECIFICATIONS.md`
- Troubleshooting: `TROUBLESHOOTING.md` (coming soon)

---

## Success Checklist

- [ ] Hardware test passed
- [ ] Web UI accessible (optional)
- [ ] Driver created
- [ ] Configuration updated
- [ ] TriAD C2 modified
- [ ] Console shows GPS online
- [ ] UI shows ownship position
- [ ] Heading arrow correct

**All checks passed?** ✅ GPS integration complete!

---

**Total Time:** ~30 minutes  
**Difficulty:** Easy  
**Status:** Production Ready
