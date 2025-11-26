# TriAD C2 - Production Integration Summary

## 🎯 System Architecture

### **Operational Flow**

```
1. BlueHalo RF Detection
   ↓
   Detects drone at long range (6-20 km)
   Provides: Sector (45°) or Precision (lat/lon)
   ↓
2. Slew Command to RWS (Radar Pointing)
   ↓
   RWS slews to RF detection bearing
   Radar searches in that direction
   ↓
3. Echoguard Radar Detection
   ↓
   Radar acquires drone (1-2 km range)
   Provides: Precise Az/El/Range
   ↓
4. Slew Command to EO/IR (Optics Pointing)
   ↓
   RWS slews optics to radar track
   Applies 20° elevation offset
   ↓
5. Visual Tracking
   ↓
   Drone tracking software keeps drone centered
```

---

## 📦 Production Drivers Implemented

### **1. Echoguard Radar Driver** (`radar_production.py`)

**Features:**
- ✅ TCP connection to radar (binary BNET protocol)
- ✅ Binary packet parsing (track header + track data)
- ✅ Vehicle-relative coordinates (0° = forward)
- ✅ UAV probability classification
- ✅ RCS and confidence metrics
- ✅ Velocity vector calculation

**Key Points:**
- Azimuth 0° = Vehicle forward (GPS heading)
- Coordinates are vehicle-relative (not True North)
- Parses 248-byte track data structures
- Classifies targets based on `probabilityUAV` field

**Configuration:**
```python
radar = RadarDriverProduction(
    host="192.168.1.100",  # Radar IP
    port=23000              # BNET port
)
```

---

### **2. BlueHalo RF Driver** (`rf_production.py`)

**Features:**
- ✅ TLS 1.2 secure socket connection
- ✅ Client certificate authentication
- ✅ JSON message parsing
- ✅ Precision detections (lat/lon, pilot position)
- ✅ Sector detections (45° bearing)
- ✅ GPS heading correction for vehicle mounting
- ✅ DIVR MKII sector alignment (22.5° offset)

**Key Points:**
- Connects via TLS with provided certificates
- Converts True North bearings to vehicle-relative
- Extracts pilot position, serial numbers, drone models
- Applies GPS heading correction automatically

**Configuration:**
```python
rf = RFDriverProduction(
    host="192.168.1.217",  # SkyView IP
    port=59898,             # Fixed TLS port
    cert_dir="Integration docs/Bluehalo_2025-11-25_1912/ott"
)
```

---

### **3. RWS Driver** (`rws_production.py`)

**Features:**
- ✅ UDP command protocol
- ✅ Separate radar and optics pointing
- ✅ 20° elevation offset (radar above optics)
- ✅ Automatic command chain execution
- ✅ Rate-limited slewing

**Command Chain:**
1. **RF Detection** → Slew radar to search direction
2. **Radar Detection** → Slew optics to track (with 20° offset)

**Key Points:**
- Radar mounted 20° above EO/IR
- Optics elevation = Radar elevation - 20°
- Separate commands for radar vs optics
- UDP packet format: `SLEW` + command type + Az/El

**Configuration:**
```python
rws = RWSDriverProduction(
    host="192.168.1.101",  # RWS IP
    port=5000               # UDP port
)
```

---

## 🧭 Coordinate Systems

### **Echoguard Radar**
- **Reference**: Vehicle-relative
- **Azimuth 0°**: Forward (GPS heading direction)
- **Elevation 0°**: Horizon
- **Range**: Meters from radar

### **BlueHalo SkyView**
- **Reference**: True North (with GPS correction)
- **Sector Alignment**: DIVR MKII has 22.5° offset
- **Conversion**: True North → Vehicle-relative using GPS heading
- **Formula**: `Vehicle Az = True North Az - GPS Heading`

### **RWS Commands**
- **Reference**: Vehicle-relative (same as radar)
- **Azimuth 0°**: Forward
- **Elevation Offset**: Radar = Optics + 20°

---

## 📊 Data Flow

### **Track Data Model** (Enhanced)

```python
class Track(BaseModel):
    # Basic position
    id: int
    azimuth: float        # Vehicle-relative (0° = forward)
    elevation: float
    range_m: float
    
    # Classification
    type: TargetType      # DRONE, BIRD, UNKNOWN
    confidence: float
    source: SensorSource  # RADAR, RF, FUSED
    
    # RF-specific (BlueHalo)
    pilot_latitude: Optional[float]      # Pilot position!
    pilot_longitude: Optional[float]
    aircraft_model: Optional[str]        # "Mavic Pro", etc.
    serial_number: Optional[str]         # Unique drone ID
    rf_frequency: Optional[int]          # Hz
    rf_power: Optional[float]
    
    # Radar-specific (Echoguard)
    rcs: Optional[float]                 # Radar cross-section
    probability_uav: Optional[float]     # UAV probability (0-1)
    
    # Velocity
    velocity_mps: Optional[float]
    heading: Optional[float]
```

---

## 🔧 Configuration Files

### **Network Configuration** (`config/settings.json`)

```json
{
  "network": {
    "radar": {
      "protocol": "TCP",
      "host": "192.168.1.100",
      "port": 23000
    },
    "rws": {
      "protocol": "UDP",
      "host": "192.168.1.101",
      "port": 5000
    },
    "rf": {
      "protocol": "TLS",
      "host": "192.168.1.217",
      "port": 59898,
      "cert_dir": "Integration docs/Bluehalo_2025-11-25_1912/ott"
    }
  },
  "gps": {
    "port": "/dev/ttyUSB0",
    "baudrate": 9600
  },
  "system": {
    "update_rate_hz": 10,
    "track_timeout_sec": 5.0,
    "fusion_distance_threshold_m": 50.0,
    "radar_elevation_offset": 20.0
  }
}
```

---

## 🚀 Usage Example

### **Initialize Production Drivers**

```python
from src.drivers.radar_production import RadarDriverProduction
from src.drivers.rf_production import RFDriverProduction
from src.drivers.rws_production import RWSDriverProduction
from src.drivers.gps import GPSDriver

# Initialize GPS (provides heading for RF correction)
gps = GPSDriver(port="/dev/ttyUSB0", baudrate=9600)
gps.start()

# Initialize RF sensor
rf = RFDriverProduction(
    host="192.168.1.217",
    port=59898,
    cert_dir="Integration docs/Bluehalo_2025-11-25_1912/ott"
)
rf.start()

# Initialize Radar
radar = RadarDriverProduction(
    host="192.168.1.100",
    port=23000
)
radar.start()

# Initialize RWS (handles command chain automatically)
rws = RWSDriverProduction(
    host="192.168.1.101",
    port=5000
)
rws.start()
```

### **Automatic Command Chain**

The RWS driver automatically handles the command chain:

1. **RF detects drone** → `Track` with `source=RF` emitted
2. **RWS receives RF track** → Slews radar to search direction
3. **Radar acquires drone** → `Track` with `source=RADAR` emitted
4. **RWS receives radar track** → Slews optics to track (with 20° offset)
5. **Optics centered on drone** → Visual tracking takes over

---

## 🎯 Key Features

### **BlueHalo RF Advantages**
✅ **Long Range**: Detects drones 6-20 km away  
✅ **Pilot Location**: Shows where operator is standing  
✅ **Drone Identification**: Model, serial number, frequency  
✅ **Early Warning**: Detects before radar range  
✅ **70+ Drone Types**: DJI, FPV, military, data links  

### **Echoguard Radar Advantages**
✅ **Precision Tracking**: Accurate Az/El/Range  
✅ **UAV Classification**: Probability-based classification  
✅ **Velocity Vector**: 3D velocity for prediction  
✅ **RCS Data**: Target size estimation  
✅ **Vehicle-Relative**: Direct pointing coordinates  

### **Integrated System**
✅ **Automatic Handoff**: RF → Radar → Optics  
✅ **Coordinate Alignment**: GPS heading correction  
✅ **Elevation Offset**: Automatic 20° compensation  
✅ **Track Fusion**: Combines RF + Radar data  
✅ **Pilot Tracking**: Shows both drone and operator  

---

## 📋 Testing Checklist

### **Phase 1: Individual Drivers** (Current)
- [x] Echoguard binary parser (tested with sample data)
- [x] BlueHalo TLS connection (certificates ready)
- [x] RWS command formatting (UDP packets)
- [ ] Test with live Echoguard radar
- [ ] Test with live BlueHalo sensor
- [ ] Test with live RWS

### **Phase 2: Integration**
- [ ] GPS heading updates RF driver
- [ ] RF detections trigger RWS radar slew
- [ ] Radar detections trigger RWS optics slew
- [ ] Verify 20° elevation offset
- [ ] Test coordinate transformations
- [ ] Validate track fusion

### **Phase 3: Operational**
- [ ] End-to-end detection chain
- [ ] Pilot position display on map
- [ ] Multiple simultaneous tracks
- [ ] Performance under load
- [ ] Failure recovery

---

## 🔍 Troubleshooting

### **Echoguard Radar**
- **Connection refused**: Check IP address and port
- **No tracks**: Verify radar is scanning
- **Wrong coordinates**: Confirm GPS heading is correct

### **BlueHalo RF**
- **TLS error**: Verify certificate files exist and are valid
- **No detections**: Check if sensor is powered and scanning
- **Wrong bearing**: Verify GPS heading correction is working

### **RWS**
- **No slew**: Check UDP packets are being sent
- **Wrong pointing**: Verify 20° elevation offset
- **Slow response**: Check network latency

---

## 📞 Next Steps

1. **Test with Live Hardware**
   - Connect to actual Echoguard radar
   - Connect to actual BlueHalo sensor
   - Connect to actual RWS

2. **Validate Coordinate Transforms**
   - Verify GPS heading correction
   - Test sector-to-azimuth conversion
   - Validate elevation offset

3. **Tune Parameters**
   - Adjust confidence thresholds
   - Tune fusion distance threshold
   - Optimize slew rates

4. **Add UI Features**
   - Display pilot positions on map
   - Show command chain status
   - Add manual override controls

---

## 🎉 Status

**Production Drivers**: ✅ Complete  
**Coordinate Systems**: ✅ Implemented  
**Command Chain**: ✅ Implemented  
**Data Models**: ✅ Enhanced  
**Ready for Testing**: ✅ Yes  

**Next**: Test with live hardware and validate end-to-end operation.

---

*Implementation Date: November 25, 2024*  
*Status: Ready for Hardware Testing*
