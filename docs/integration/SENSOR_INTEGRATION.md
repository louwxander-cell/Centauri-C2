# TriAD C2 - Sensor Integration Guide

## Overview

This document describes the integration of real sensor systems based on ICDs and existing driver implementations.

## Sensor Systems

### 1. Echodyne Echoguard Radar

**ICD:** `Integration docs/Echoguard_2025-11-25_1908/ICD, EchoGuard, 700-0005-203_Rev05.pdf`

**Driver:** `src/drivers/radar_production.py`

#### Connection

- **Protocol:** TCP
- **Data Format:** Binary BNET protocol
- **Packet Size:** 28-byte header + 248 bytes per track
- **Update Rate:** 10 Hz
- **Coordinate Frame:** Vehicle-relative (0° = forward)

#### Data Structure

```python
# Track data (248 bytes)
struct track {
    uint32 id;
    uint32 state;
    float azest, elest, rest;            # Spherical position
    float xest, yest, zest;              # Cartesian position
    float velxest, velyest, velzest;     # Velocity vector
    uint32 assocMeas_id_main[3];         # Associated measurements
    float assocMeas_chi2_main[3];        # Chi-squared values
    int32 TOCA_days, TOCA_ms;            # Time of closest approach
    float DOCA;                          # Distance of closest approach
    float lifetime;                      # Track age
    uint32 lastUpdateTime_days, lastUpdateTime_ms;
    uint32 lastAssociatedDataTime_days, lastAssociatedDataTime_ms;
    uint32 acquiredTime_days, acquiredTime_ms;
    float estConfidence;                 # Tracking confidence
    uint32 numAssocMeasurements;
    float estRCS;                        # Radar cross-section
    float probabilityOther, probabilityUAV;  # Classification
}
```

#### Key Features

- **UAV Classification:** Uses `probabilityUAV` field (0.0-1.0)
- **Track Quality:** `estConfidence` and `numAssocMeasurements`
- **RCS Measurement:** Small UAV typically 0.01-0.1 m²
- **Lifetime Tracking:** Automatic track timeout handling
- **Coordinate System:** Azimuth 0° = vehicle forward, elevation positive = up

#### Configuration

```python
# In production deployment
radar_driver = RadarDriverProduction(
    host="192.168.1.100",  # Radar IP
    port=5000,             # BNET data port
    parent=None
)
```

### 2. BlueHalo SkyView DIVR MkII RF Sensor

**ICD:** `Integration docs/Bluehalo_2025-11-25_1912/Titan-SV ICD v1.0.9.pdf`

**Driver:** `src/drivers/rf_production.py`

#### Connection

- **Protocol:** TLS 1.2 secure socket
- **Data Format:** JSON (newline-delimited messages)
- **Update Rate:** Variable (event-driven)
- **Authentication:** Client certificate + CA chain

#### Data Structure

**Precision Detection (high-accuracy mode):**
```json
{
    "type": "precision_detection",
    "timestamp": 1732653000,
    "drone": {
        "latitude": -25.84523,
        "longitude": 28.18456,
        "model": "DJI Mavic 3",
        "serial_number": "SN123456"
    },
    "pilot": {
        "latitude": -25.84789,
        "longitude": 28.18234
    },
    "rf": {
        "frequency_hz": 2412000000,
        "power_dbm": -65.5,
        "bandwidth_hz": 20000000
    },
    "bearing_deg": 245.3,
    "confidence": 0.92
}
```

**Sector Detection (directional mode):**
```json
{
    "type": "sector_detection",
    "timestamp": 1732653000,
    "sector_id": 3,
    "bearing_deg": 112.5,  # Center of 45° sector
    "model": "DJI Phantom 4 Pro",
    "frequency_hz": 5745000000,
    "power_dbm": -72.3,
    "confidence": 0.75
}
```

#### Key Features

- **Dual Modes:**
  - **Precision:** Lat/lon positions (drone + pilot), serial numbers, ±3° bearing accuracy
  - **Sector:** 45° directional sectors, ±15° bearing accuracy
  
- **DIVR MKII Alignment:** 22.5° sector offset from True North
  - Sector 1: 0-45° (22.5° center)
  - Sector 2: 45-90° (67.5° center)
  - ...etc.

- **Drone Intelligence:**
  - Model identification (DJI Mavic, Phantom, Autel, etc.)
  - Serial number extraction
  - Pilot/controller position
  - Frequency analysis (2.4 GHz, 5.8 GHz)

- **Coordinate Conversion:** Requires ownship heading for vehicle-relative coordinates

#### TLS Configuration

```python
# Certificate files (from OTT package)
cert_dir = "Integration docs/Bluehalo_2025-11-25_1912/ott/"
files = [
    "ott.verustechnologygroup.com.cert.pem",  # Client cert
    "ott.verustechnologygroup.com.key.pem",   # Client key
    "ca-chain.cert.pem"                        # CA chain
]

rf_driver = RFDriverProduction(
    host="ott.verustechnologygroup.com",  # SkyView hostname
    port=443,                              # TLS port
    cert_dir=cert_dir,
    parent=None
)
```

### 3. Remote Weapon Station (RWS)

**Driver:** `src/drivers/rws_production.py`

#### Connection

- **Protocol:** UDP
- **Command Format:** Binary structs
- **Control Loop:** 10 Hz

#### Command Chain

```
┌─────────┐      ┌──────────┐      ┌─────────────┐
│ RF Det. │ ───> │ Slew RWS │ ───> │ Radar Track │
└─────────┘      └──────────┘      └─────────────┘
                  (Radar)           
                                    
┌─────────────┐      ┌──────────────┐      ┌──────────────┐
│ Radar Track │ ───> │ Slew EO/IR   │ ───> │ Optical Lock │
└─────────────┘      └──────────────┘      └──────────────┘
                     (+20° el offset)
```

**Step 1: RF → RWS Slew**
- RF detection provides bearing sector
- RWS slews radar to search that direction
- Radar begins active tracking

**Step 2: Radar → Optics Slew**
- Radar provides precise target position
- RWS slews EO/IR with 20° elevation offset
- Optics acquire and lock target

#### Hardware Configuration

- **Radar Mount:** 20° above optics
- **Slew Rates:**
  - Azimuth: max 30°/s
  - Elevation: max 20°/s
- **Elevation Offset:** Always add 20° when slewing optics from radar coordinates

```python
rws_driver = RWSDriverProduction(
    host="192.168.1.101",    # RWS controller IP
    port=5001,                # UDP command port
    parent=None
)
```

### 4. GPS

**Driver:** `src/drivers/gps.py`

#### Data

```python
{
    'lat': -25.841105,        # Decimal degrees
    'lon': 28.180340,
    'heading': 90.0,          # True heading (0-360°)
    'altitude_m': 1400.0,     # MSL
    'ground_speed_mps': 12.5,
    'satellites': 12,
    'hdop': 1.1
}
```

## Sensor Fusion

### Coordinate Frames

**All sensors must be converted to vehicle-relative frame:**

- **0°**: Vehicle forward
- **90°**: Vehicle right
- **180°**: Vehicle rear
- **270°**: Vehicle left

#### Conversion Formulas

**RF (True North) → Vehicle-Relative:**
```python
vehicle_azimuth = (rf_bearing - rf_sensor_offset - ownship_heading) % 360
```

For DIVR MKII:
```python
rf_sensor_offset = 22.5  # DIVR MKII sector alignment
vehicle_azimuth = (rf_bearing - 22.5 - ownship_heading) % 360
```

**Radar (Vehicle-Relative) → True North:**
```python
true_north_bearing = (radar_azimuth + ownship_heading) % 360
```

### Association Logic

**Simple Range-Azimuth Association:**
```python
def associate(radar_track, rf_detection):
    # Azimuth difference (handle wrap-around)
    az_diff = abs(radar_track.azimuth - rf_detection.azimuth)
    if az_diff > 180:
        az_diff = 360 - az_diff
    
    # For precision RF detections
    if rf_detection.mode == "PRECISION":
        range_diff = abs(radar_track.range_m - rf_detection.range_m)
        if az_diff < 10 and range_diff < 200:
            return True  # Fuse tracks
    
    # For sector RF detections (less precise)
    elif rf_detection.mode == "SECTOR":
        if az_diff < 25:  # Half sector width + margin
            return True  # Associate but lower confidence
    
    return False
```

**Production Fusion (Kalman):**
- State vector: `[x, y, z, vx, vy, vz]`
- Measurement models for each sensor
- Association via chi-squared test
- Track quality scoring

### Data Quality

**Confidence Scoring:**
```python
confidence = (
    sensor_weight * sensor_confidence +
    association_bonus +
    track_age_factor
)

# Sensor weights
RADAR_WEIGHT = 0.4   # Range + velocity accuracy
RF_WEIGHT = 0.3      # Bearing accuracy
FUSED_WEIGHT = 0.6   # Combined sensors

# Bonuses
PRECISION_RF_BONUS = +0.1   # RF precision mode
LONG_TRACK_BONUS = +0.05    # Track age > 5s
```

## Safety & ROE

### Engage Request Validation

```python
def validate_engage(track):
    checks = []
    
    # Type validation
    if track.type in ['BIRD', 'CLUTTER']:
        checks.append('INVALID_TYPE')
    
    # Confidence threshold
    if track.confidence < 0.7:
        checks.append(f'LOW_CONFIDENCE:{track.confidence}')
    
    # Range limits
    if track.range_m < 100:
        checks.append(f'TOO_CLOSE:{track.range_m}m')
    if track.range_m > 2500:
        checks.append(f'OUT_OF_RANGE:{track.range_m}m')
    
    # RF sector mode check
    if track.source == 'RF' and track.detection_mode == 'SECTOR':
        checks.append('RF_SECTOR_NO_PRECISION')
    
    # Require radar confirmation for high-confidence engage
    if track.source == 'RF' and not track.has_radar_confirmation:
        checks.append('NO_RADAR_CONFIRMATION')
    
    return len(checks) == 0, checks
```

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Radar update rate | 10 Hz | BNET protocol |
| RF detection latency | < 1s | Event-driven |
| Fusion latency | < 100ms | Track → UI |
| RWS slew latency | < 50ms | Command → hardware |
| Engage validation | < 50ms | Safety-critical |
| UI frame rate | 60 FPS | QML rendering |

## Integration Checklist

- [ ] Radar TCP connection established
- [ ] BNET binary packets parsing correctly
- [ ] RF TLS connection with client certs
- [ ] JSON message parsing
- [ ] GPS heading updates feeding RF coordinate conversion
- [ ] RWS UDP commands acknowledged
- [ ] Coordinate frame conversions validated
- [ ] Fusion association logic tested
- [ ] Engage safety checks implemented
- [ ] Command chain RF→Radar→Optics tested
- [ ] UI displays all sensor-specific fields
- [ ] Performance targets met (latency, FPS)

## References

- **Echoguard ICD:** `Integration docs/Echoguard_2025-11-25_1908/ICD, EchoGuard, 700-0005-203_Rev05.pdf`
- **Echoguard Developer Manual:** `EchoGuard_Radar_Developer_Manual_SW16.4.0.pdf`
- **SkyView Titan-SV ICD:** `Integration docs/Bluehalo_2025-11-25_1912/Titan-SV ICD v1.0.9.pdf`
- **SkyView Operator Guide:** `SkyView_DIVR-MKII_OperatorGuide_3.0.14.pdf`
- **BNET Manual:** `BNET_11_1_5_Manual.pdf`
- **Sample Data:** `900238_rev01_SW16.3_Sample_Data.zip`

## Next Steps

1. **Test with Real Hardware:**
   - Connect to Echoguard on LAN
   - Configure TLS certs for SkyView
   - Validate RWS UDP protocol

2. **Implement Production Fusion:**
   - Kalman filters for state estimation
   - Chi-squared association tests
   - Track quality management

3. **Deploy C++ Engine:**
   - Port sensor drivers to C++
   - Implement gRPC server from `triad_updated.proto`
   - Multi-threaded pipeline

4. **Field Testing:**
   - Latency measurements
   - Association accuracy
   - False alarm rate
   - Engage workflow validation
