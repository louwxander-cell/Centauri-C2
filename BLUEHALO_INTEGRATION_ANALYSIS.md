# BlueHalo SkyView DIVR MkII - Integration Analysis

## 📋 Documentation Review Summary

Based on the provided BlueHalo SkyView DIVR MkII documentation, here's what I've extracted:

---

## 🔍 Key Findings

### **Available Documentation**
✅ **API Documentation**: `skyview_api.html` - Complete REST/WebSocket API reference  
✅ **ICD Document**: `Titan-SV ICD v1.0.9.pdf` (4.3 MB)  
✅ **Operator Guide**: `SkyView_DIVR-MKII_OperatorGuide_3.0.14.pdf` (2.3 MB)  
✅ **Overview Guide**: `SkyView_DIVR-MKII_OverviewGuide-3.0.X.pdf` (1.4 MB)  
✅ **Product Sheet**: `BlueHalo_SkyView_DIVR_Product Sheet_2023.pdf`  
✅ **TLS Certificates**: Client certificates for secure connection  
✅ **Sample Detections**: 70+ example JSON messages for different drone types  

---

## 🌐 Network Configuration

### **Connection Details**
- **Protocol**: TLS/SSL Secure Socket (WebSocket-like)
- **Default IP**: `192.168.1.217`
- **Port**: `59898` (fixed, cannot be changed)
- **TLS Version**: TLS 1.2
- **Buffer Size**: Minimum 8192 bytes recommended

### **Authentication**
- **Method**: TLS Client Certificates
- **Certificates Provided**:
  - `ca-chain.cert.pem` - Certificate Authority chain
  - `ott.verustechnologygroup.com.cert.pem` - Client certificate
  - `ott.verustechnologygroup.com.key.pem` - Private key
  - `ott.verustechnologygroup.com.p12` - PKCS#12 bundle

---

## 📊 Detection Data Structure

### **Message Types**
1. **DetectionPublication** (Primary) - New drone detections
2. **TechniqueStatus** - Sensor status updates
3. **GPSStatus** - GPS position information
4. **SignalStates** - Signal processing states

### **Detection Types**

#### **1. Fact-Of Detection**
- Signal detected and characterized
- **No location information**
- Technology type and frequency only

#### **2. Directional-Indication (Sector) Detection**
- Signal isolated to a **45-degree sector** (1-8)
- **DIVR MKII**: Sector 1 center is **22.5° offset from True North**
- Provides bearing information but not precise location

#### **3. Precision Detection** (Best!)
- **Full telemetry data** extracted from drone signals
- Available for DJI OcuSync and other advanced protocols
- Includes:
  - Aircraft lat/lon/altitude
  - Pilot lat/lon
  - Home point lat/lon
  - Velocity vector (N/E/Up)
  - Attitude (pitch/roll/yaw)
  - Serial number
  - Aircraft model
  - Battery status (in some protocols)

---

## 🎯 JSON Detection Message Format

### **Example: Precision Detection (DJI Mavic Pro)**

```json
{
  "DetectionPublication": {
    "systemName": "SVMPV3-9999",
    "systemSerial": "SVMPV3-9999",
    "header": {
      "messageId": "2a46cb36-baec-4a1e-bbc8-9bff2b19ff6d",
      "messageType": "DetectionPublication",
      "timestamp": "2024-10-25T20:11:27.951Z",
      "signature": null,
      "originator": "sv-controller"
    },
    "omniDetections": [
      {
        "detectionType": "OCUSYNC",
        "detectionLabel": "DJI Ocusync",
        "signalType": "UAS",
        "expired": false,
        "expirationSeconds": 60,
        "sector": 1,
        "power": 417.137451171875,
        "channel": 2400,
        "frequency": 2400000000,
        
        // Precision Data (when available)
        "serial": "08RDD8K00100E6",
        "aircraftModel": "Mavic Pro",
        "aircraftLatitude": 39.23351287841797,
        "aircraftLongitude": -77.54838562011719,
        "aircraftAltitude": 133,
        "aircraftHeightAboveGround": 0,
        "aircraftVelocityNorth": -0.012,
        "aircraftVelocityEast": 0.039,
        "aircraftVelocityUp": -0.001,
        "aircraftPitch": -14358,
        "aircraftRoll": 1562,
        "aircraftYaw": -25693,
        "pilotLatitude": 39.23351287841797,
        "pilotLongitude": -77.54850769042969,
        "homeLatitude": 39.2335319519043,
        "homeLongitude": -77.54840087890625
      }
    ],
    "sectorDetections": []
  }
}
```

### **Example: Sector Detection (45° bearing)**

```json
{
  "DetectionPublication": {
    "sectorDetections": [
      {
        "detectionType": "OCUSYNC",
        "detectionLabel": "DJI Ocusync",
        "signalType": "UAS",
        "sector": 1,  // 45-degree sector number (1-8)
        "power": 2.011,
        "channel": 5800,
        "frequency": 5800000000,
        
        // No precision data for sector-only detections
        "aircraftLatitude": 0,
        "aircraftLongitude": 0,
        "serial": null
      }
    ]
  }
}
```

---

## 🧭 Sector Alignment (DIVR MKII)

**Critical**: DIVR MKII has **22.5° offset** from True North!

```
Sector Layout (DIVR MKII):
         N (0°)
    8  |  1  |  2
   ----+-----+----
    7  |  X  |  3
   ----+-----+----
    6  |  5  |  4

Sector 1 Center: 22.5° (NNE)
Sector 2 Center: 67.5° (ENE)
Sector 3 Center: 112.5° (ESE)
Sector 4 Center: 157.5° (SSE)
Sector 5 Center: 202.5° (SSW)
Sector 6 Center: 247.5° (WSW)
Sector 7 Center: 292.5° (WNW)
Sector 8 Center: 337.5° (NNW)

Each sector = 45° wide
```

**Formula**: `Azimuth = (sector - 1) * 45 + 22.5`

---

## 🔌 API Commands

### **Enable/Disable Message Types**

```json
// Enable detection messages (default: true)
{"detectionStatusEnabled": true}

// Enable GPS status (default: false)
{"gpsStatusEnabled": true}

// Enable technique status (default: true)
{"techniqueStatusEnabled": true}

// Enable signal states (default: false)
{"getSignalStates": true}
```

**Important**: Send commands as single line with `\n` at the end.

---

## 🎨 Supported Drone Types

The system can detect **70+ drone/RF signatures** including:

### **DJI Drones**
- OcuSync (Mavic, Phantom 4 Pro, etc.)
- Lightbridge (2.4 GHz and 5.8 GHz)
- Mavic Air

### **FPV/RC Systems**
- Crossfire
- ExpressLRS (ELRS)
- Spektrum
- Futaba (FASST, FHSS)
- Taranis X8R
- Graupner

### **Video Transmission**
- NTSC (Low/Mid/High/Extended)
- PAL (Low/Mid/High/Extended)

### **Military/Commercial**
- Orlan-10
- Lancet
- Fisherman
- Pixhawk

### **Data Links**
- Digi XBee
- Digi XTend
- Microhard (Nano, Pico)
- FreeWave FGR3
- Herelink HD VTX

### **Remote ID**
- Bluetooth Remote ID

---

## 🔧 Integration Requirements

### **What We Need from You**

1. ✅ **Network Configuration**
   ```
   SkyView IP Address: _______________  (default: 192.168.1.217)
   Port: 59898 (fixed)
   Network accessible: Yes/No?
   ```

2. ✅ **Certificates** (Already provided!)
   - You have the TLS certificates in the `ott/` folder
   - These are required for authentication

3. ❓ **Coordinate Reference**
   - Is the DIVR MKII **fixed** or **vehicle-mounted**?
   - If vehicle-mounted: Do we need to apply heading offset?
   - Current implementation assumes sensor faces True North

4. ❓ **Detection Preferences**
   - Use **precision detections** when available? (Yes - recommended)
   - Fall back to **sector detections** when precision unavailable? (Yes)
   - Ignore **fact-of detections** (no location)? (Probably yes)

---

## 🐍 Python Integration Approach

### **Recommended: Python SSL Socket Client**

```python
import ssl
import socket
import json

# Load certificates
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(
    certfile='ott/ott.verustechnologygroup.com.cert.pem',
    keyfile='ott/ott.verustechnologygroup.com.key.pem'
)
context.load_verify_locations('ott/ca-chain.cert.pem')

# Connect to SkyView
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(sock, server_hostname='192.168.1.217')
ssl_sock.connect(('192.168.1.217', 59898))

# Enable detection messages
command = '{"detectionStatusEnabled":true}\n'
ssl_sock.sendall(command.encode('utf-8'))

# Receive detections
buffer = b''
while True:
    data = ssl_sock.recv(8192)
    buffer += data
    
    # Parse JSON messages (newline-delimited)
    while b'\n' in buffer:
        line, buffer = buffer.split(b'\n', 1)
        if line:
            message = json.loads(line.decode('utf-8'))
            process_detection(message)
```

---

## 📊 Mapping to Our Track Model

| SkyView Field | Our Track Field | Notes |
|--------------|-----------------|-------|
| `detectionId` | `id` | Unique detection ID (hash to int) |
| `sector` | `azimuth` | Convert: `(sector-1)*45 + 22.5` |
| `aircraftLatitude/Longitude` | Calculate Az/El/Range | If precision available |
| `detectionType` | `type` | All are `TargetType.DRONE` |
| `power` | `confidence` | Normalize signal power |
| `frequency` | Additional info | Store for reference |
| `serial` | Track metadata | Unique drone identifier |
| `aircraftModel` | Track metadata | Drone model |
| `timestamp` | `timestamp` | ISO8601 to Unix time |

---

## 🎯 Detection Quality Levels

### **Priority 1: Precision Detections**
- Use `aircraftLatitude`, `aircraftLongitude`, `aircraftAltitude`
- Calculate azimuth/elevation/range from ownship position
- High confidence (0.9+)
- **Best for targeting**

### **Priority 2: Sector Detections**
- Use `sector` to calculate azimuth: `(sector-1)*45 + 22.5`
- No range information (assume max detection range ~6 km)
- Medium confidence (0.6-0.8)
- **Good for situational awareness**

### **Priority 3: Omni Detections**
- Fact-of detection only
- No directional information
- Low confidence (0.3-0.5)
- **Minimal value for C2**

---

## 🚀 Implementation Plan

### **Phase 1: SSL Socket Client** (1 day)
- Implement TLS socket connection
- Load and use provided certificates
- Handle JSON message parsing
- Test connection to SkyView

### **Phase 2: Detection Parser** (1 day)
- Parse DetectionPublication messages
- Extract precision data (lat/lon/alt)
- Extract sector data (bearing)
- Map to our `Track` model

### **Phase 3: Coordinate Transformation** (1 day)
- Convert precision lat/lon to Az/El/Range
- Handle sector-to-azimuth conversion
- Apply DIVR MKII 22.5° offset
- Handle vehicle heading (if mounted)

### **Phase 4: Integration** (1 day)
- Integrate with fusion engine
- Correlate with radar tracks
- Test with live data
- Tune confidence thresholds

**Total: ~4 days**

---

## 💡 Key Advantages

### **Rich Data Available**
✅ Precision lat/lon/alt for many drone types  
✅ Drone serial numbers and models  
✅ Pilot location (for DJI drones)  
✅ Velocity and attitude data  
✅ 70+ drone type signatures  

### **Easy Integration**
✅ JSON format (easy to parse)  
✅ TLS certificates provided  
✅ Well-documented API  
✅ Sample messages for testing  

### **Complementary to Radar**
✅ RF detects drones radar might miss  
✅ Provides drone type/model  
✅ Can detect at longer ranges (20+ km fact-of)  
✅ Works in cluttered environments  

---

## 🔍 Questions for You

1. **Network Configuration:**
   - What is the SkyView IP address? (default: `192.168.1.217`)
   - Can you ping the SkyView system?
   - Is it on the same network as the C2 system?

2. **Mounting Configuration:**
   - Is the DIVR MKII **fixed** or **vehicle-mounted**?
   - If vehicle-mounted, do we have vehicle heading from GPS?
   - Should we apply heading correction?

3. **Detection Preferences:**
   - Use precision detections when available? (Recommended: Yes)
   - Use sector detections as fallback? (Recommended: Yes)
   - Ignore omni detections (no location)? (Recommended: Yes)

4. **Current Access:**
   - Is the SkyView powered on and accessible?
   - Can you test the TLS connection?

---

## 📝 Summary

### **What We Have:**
✅ Complete API documentation  
✅ TLS certificates for authentication  
✅ 70+ sample detection messages  
✅ Clear data structure (JSON)  
✅ Sector alignment specification  

### **What We Need:**
❓ SkyView IP address (or confirm default)  
❓ Mounting configuration (fixed/vehicle)  
❓ Detection preference settings  
❓ Confirm network accessibility  

### **Next Action:**
**Please provide:**
1. SkyView IP address
2. Mounting type (fixed/vehicle)
3. Confirm network access
4. Permission to implement driver

Once confirmed, I can implement the production RF driver in **~4 days**.

---

*Analysis Date: November 25, 2024*  
*Status: Ready to implement pending network configuration*
