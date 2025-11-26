# TriAD C2 System - Integration Requirements Document

## 🎯 Purpose
This document outlines all requirements, APIs, ICDs, and specifications needed to integrate the TriAD C2 system with real hardware sensors and the gunner station.

---

## 📋 Required Documentation & Specifications

### 1. **Echodyne Radar System**

#### Required Documents:
- [ ] **ICD (Interface Control Document)** - Radar to C2 interface specification
- [ ] **API Documentation** - TCP/IP protocol specification
- [ ] **Data Format Specification** - Binary/JSON message formats
- [ ] **Network Configuration** - IP addresses, ports, protocols
- [ ] **Track Message Format** - Track ID, position, velocity, classification
- [ ] **Coordinate System** - Reference frame (ENU, NED, WGS84, etc.)
- [ ] **Update Rate Specification** - Expected message frequency
- [ ] **Error Codes** - Fault conditions and error handling

#### Technical Questions:
1. **Network Protocol**: TCP or UDP? Port number?
2. **Message Format**: Binary (struct format) or JSON or XML?
3. **Coordinate System**: What reference frame for azimuth/elevation/range?
4. **Track Data**: What fields are provided per track?
   - Track ID
   - Position (Az/El/Range or Lat/Lon/Alt)
   - Velocity vector
   - RCS (Radar Cross Section)
   - Classification/Type
   - Confidence/Quality
   - Timestamp
5. **Handshake**: Connection establishment procedure?
6. **Keep-alive**: Heartbeat or status messages?
7. **Authentication**: Any security/encryption requirements?

#### Example Message Format Needed:
```json
{
  "message_type": "track_update",
  "timestamp": 1234567890.123,
  "tracks": [
    {
      "id": 1,
      "azimuth": 45.0,
      "elevation": 10.0,
      "range": 500.0,
      "velocity": 15.0,
      "heading": 90.0,
      "rcs": 0.01,
      "classification": "DRONE",
      "confidence": 0.85
    }
  ]
}
```

---

### 2. **BlueHalo RF Sensor**

#### Required Documents:
- [ ] **API Documentation** - REST API endpoints and WebSocket specification
- [ ] **Authentication Specification** - API keys, OAuth, certificates
- [ ] **Data Schema** - JSON schema for RF detections
- [ ] **Network Configuration** - Base URL, ports, SSL/TLS requirements
- [ ] **Detection Message Format** - RF signature data structure
- [ ] **Polling vs Push** - Real-time WebSocket or polling interval?
- [ ] **Rate Limits** - API call frequency limits

#### Technical Questions:
1. **API Type**: REST polling or WebSocket streaming?
2. **Base URL**: What is the endpoint? (e.g., `https://rf-sensor.local:8080/api/v1`)
3. **Authentication**: API key in header? Token-based?
4. **Endpoints**:
   - `/detections` - Get current detections?
   - `/status` - Sensor health?
   - `/config` - Configuration?
5. **Detection Data**: What fields are provided?
   - Detection ID
   - Frequency
   - Signal strength
   - Direction of arrival (bearing)
   - Drone type/protocol (WiFi, 2.4GHz, 5.8GHz)
   - Confidence
   - Timestamp
6. **Update Rate**: How often to poll or how fast do WebSocket messages arrive?

#### Example REST Response Needed:
```json
{
  "status": "ok",
  "timestamp": 1234567890.123,
  "detections": [
    {
      "id": 100,
      "frequency_mhz": 2400,
      "signal_strength_dbm": -65,
      "bearing": 45.0,
      "bearing_accuracy": 5.0,
      "protocol": "DJI_OCUSYNC",
      "classification": "DRONE",
      "confidence": 0.92,
      "range_estimate": 500.0,
      "range_accuracy": 200.0
    }
  ]
}
```

---

### 3. **GPS/Compass System**

#### Required Documents:
- [ ] **Hardware Specification** - GPS receiver model and capabilities
- [ ] **NMEA Sentence Documentation** - Which NMEA sentences are output?
- [ ] **Serial Configuration** - Baud rate, parity, stop bits
- [ ] **Update Rate** - Position update frequency (1 Hz, 5 Hz, 10 Hz?)
- [ ] **Accuracy Specification** - Expected position/heading accuracy
- [ ] **Coordinate System** - WGS84 datum confirmation

#### Technical Questions:
1. **Serial Port**: Device path (e.g., `/dev/ttyUSB0`, `COM3`)?
2. **Baud Rate**: 4800, 9600, 38400, 115200?
3. **NMEA Sentences**: Which ones are output?
   - `$GPGGA` - Position fix
   - `$GPRMC` - Recommended minimum
   - `$GPVTG` - Velocity and heading
   - `$GPHDT` - True heading
4. **Compass Integration**: Separate compass or integrated?
5. **Magnetic Declination**: Automatic correction or manual?
6. **Datum**: WGS84 confirmed?

#### Example NMEA Sentences Needed:
```
$GPGGA,123519,3723.2475,N,12158.3416,W,1,08,0.9,545.4,M,46.9,M,,*47
$GPRMC,123519,A,3723.2475,N,12158.3416,W,022.4,084.4,230394,003.1,W*6A
$GPHDT,274.07,T*03
```

---

### 4. **Remote Weapon Station (RWS) / Gunner Station**

#### Required Documents:
- [ ] **ICD** - RWS control interface specification
- [ ] **Command Protocol** - UDP/TCP message format for slew commands
- [ ] **Network Configuration** - IP address, port, protocol
- [ ] **Command Set** - Available commands (slew, fire, status, etc.)
- [ ] **Status Feedback** - Current position, ready state, faults
- [ ] **Safety Interlocks** - Authorization requirements, safety zones
- [ ] **Coordinate System** - Reference frame for pointing commands
- [ ] **Rate Limits** - Maximum slew rates, acceleration limits

#### Technical Questions:
1. **Network Protocol**: UDP or TCP? Port number?
2. **Message Format**: Binary or ASCII or JSON?
3. **Command Structure**: How to format slew command?
4. **Coordinate System**: Azimuth/Elevation relative to what reference?
   - Vehicle body frame?
   - True north?
   - Magnetic north?
5. **Feedback**: Does RWS send position updates back?
6. **Authorization**: Any arming/authorization sequence required?
7. **Safety**: Geofencing or no-fire zones enforced where?
8. **Handshake**: Connection establishment and keep-alive?

#### Example Command Format Needed:
```c
// Binary UDP packet structure
struct SlewCommand {
    uint32_t header;        // Magic number: 0x534C4557 ("SLEW")
    float azimuth;          // Degrees, 0-360
    float elevation;        // Degrees, -90 to +90
    uint8_t priority;       // 0=normal, 1=urgent
    uint8_t mode;           // 0=slew, 1=track, 2=engage
    uint16_t checksum;      // CRC16
};
```

OR JSON format:
```json
{
  "command": "slew",
  "azimuth": 45.0,
  "elevation": 10.0,
  "mode": "track",
  "priority": "normal",
  "timestamp": 1234567890.123
}
```

#### Status Feedback Format Needed:
```json
{
  "status": "ready",
  "current_azimuth": 45.2,
  "current_elevation": 10.1,
  "slewing": false,
  "armed": false,
  "faults": [],
  "timestamp": 1234567890.123
}
```

---

## 🗺️ Map Overlay Requirements

### Required for Map Integration:

#### 1. **Base Map Provider**
- [ ] **Choice**: OpenStreetMap, Google Maps, Mapbox, or offline tiles?
- [ ] **API Key**: If using commercial provider
- [ ] **Tile Server**: URL for map tiles
- [ ] **Zoom Levels**: Required zoom range
- [ ] **Offline Support**: Need offline map tiles?

#### 2. **GPS Data Integration**
- [ ] **Coordinate System**: Confirm WGS84 lat/lon
- [ ] **Update Rate**: How often to update ownship position on map?
- [ ] **Track History**: Show breadcrumb trail? How long?
- [ ] **Heading Indicator**: Show vehicle heading arrow?

#### 3. **Track Overlay**
- [ ] **Track Symbols**: Icons for different target types
- [ ] **Track Labels**: Show track ID, type, range?
- [ ] **Track History**: Show past positions (breadcrumbs)?
- [ ] **Velocity Vectors**: Show predicted path?
- [ ] **Range Rings**: Show detection ranges on map?

#### 4. **Geofencing / Zones**
- [ ] **Zone Definitions**: GeoJSON format (already have `zones.geojson`)
- [ ] **Zone Types**: Safe, restricted, no-fire zones
- [ ] **Zone Enforcement**: Where is enforcement logic?
- [ ] **Visual Styling**: Colors and transparency for zones

#### 5. **Map Library Choice**
Recommended options:
- **Folium** (Python, Leaflet.js based) - Easy integration
- **PyQtWebEngine + Leaflet** - Interactive web map in Qt
- **PyQt + Matplotlib Basemap** - Offline, but deprecated
- **PyQt + Cartopy** - Modern, but complex

**Question**: Which map library do you prefer?

---

## 🔧 System Integration Checklist

### Network Configuration
- [ ] **Radar IP/Port**: `___.___.___.___:_____`
- [ ] **RF Sensor URL**: `https://_______________`
- [ ] **RWS IP/Port**: `___.___.___.___:_____`
- [ ] **Network Topology**: All on same subnet? VLANs? Firewalls?
- [ ] **Bandwidth**: Expected data rates per sensor?
- [ ] **Latency**: Maximum acceptable latency?

### Security Requirements
- [ ] **Authentication**: Username/password, certificates, API keys?
- [ ] **Encryption**: TLS/SSL required? Which version?
- [ ] **Authorization**: Role-based access control?
- [ ] **Audit Logging**: What events must be logged?
- [ ] **Data Classification**: Sensitivity level of track data?

### Time Synchronization
- [ ] **NTP Server**: Network time protocol for sync?
- [ ] **GPS Time**: Use GPS time as reference?
- [ ] **Timestamp Format**: Unix epoch, ISO8601, GPS week?
- [ ] **Timezone**: UTC or local time?

### Data Recording
- [ ] **Mission Recording**: Record all sensor data?
- [ ] **Format**: Database (SQLite, PostgreSQL) or files (CSV, JSON)?
- [ ] **Retention**: How long to keep data?
- [ ] **Playback**: Need to replay recorded missions?

### Performance Requirements
- [ ] **Maximum Tracks**: How many simultaneous tracks?
- [ ] **Update Rate**: Minimum UI refresh rate?
- [ ] **Latency**: Maximum sensor-to-display latency?
- [ ] **Reliability**: Uptime requirements (99%, 99.9%)?

---

## 📊 Data Flow Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Echodyne  │         │  BlueHalo   │         │   GPS/      │
│   Radar     │         │  RF Sensor  │         │  Compass    │
│             │         │             │         │             │
│ TCP:23000   │         │ REST/WS     │         │ Serial      │
└──────┬──────┘         └──────┬──────┘         └──────┬──────┘
       │                       │                       │
       │ Track Data            │ RF Detections         │ Position
       │ (10 Hz)               │ (2 Hz)                │ (1 Hz)
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   TriAD C2 System    │
                    │                      │
                    │  • Track Fusion      │
                    │  • Map Overlay       │
                    │  • Threat Assessment │
                    │  • Target Selection  │
                    └──────────┬───────────┘
                               │
                               │ Slew Commands
                               │ (on demand)
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Gunner Station     │
                    │   (RWS)              │
                    │                      │
                    │  UDP:5000            │
                    └──────────────────────┘
```

---

## 🛠️ Implementation Plan

### Phase 1: Documentation Gathering (Week 1)
1. Collect all ICDs, APIs, and specifications
2. Review and clarify requirements
3. Set up test environment with real hardware
4. Establish network connectivity

### Phase 2: Radar Integration (Week 2)
1. Implement TCP client for Echodyne radar
2. Parse binary/JSON messages
3. Convert to internal Track format
4. Test with live radar data
5. Validate coordinate transformations

### Phase 3: RF Sensor Integration (Week 2-3)
1. Implement REST/WebSocket client
2. Handle authentication
3. Parse RF detection messages
4. Integrate with fusion engine
5. Test correlation with radar tracks

### Phase 4: GPS Integration (Week 3)
1. Implement serial NMEA parser
2. Extract position and heading
3. Update ownship display
4. Implement map overlay
5. Add breadcrumb trail

### Phase 5: Map Overlay (Week 3-4)
1. Choose and integrate map library
2. Display ownship position
3. Overlay tracks on map
4. Add geofencing zones
5. Implement range rings

### Phase 6: RWS Integration (Week 4)
1. Implement UDP command protocol
2. Format slew commands correctly
3. Add coordinate transformation
4. Implement status feedback
5. Add safety interlocks

### Phase 7: Testing & Validation (Week 5)
1. End-to-end integration testing
2. Performance validation
3. Latency measurements
4. Stress testing (many tracks)
5. Failure mode testing

---

## 📝 Information Request Form

Please provide the following information for each sensor:

### **Echodyne Radar**
```
IP Address: _________________
Port: _________________
Protocol: [ ] TCP  [ ] UDP
Message Format: [ ] Binary  [ ] JSON  [ ] XML  [ ] Other: _______
Update Rate: _______ Hz
Coordinate System: _________________
Sample Message: (attach file or paste below)


```

### **BlueHalo RF Sensor**
```
Base URL: _________________
Authentication: [ ] API Key  [ ] OAuth  [ ] Certificate  [ ] None
API Key (if applicable): _________________
WebSocket: [ ] Yes  [ ] No
Update Rate: _______ Hz
Sample Response: (attach file or paste below)


```

### **GPS/Compass**
```
Device Path: _________________
Baud Rate: _________________
NMEA Sentences: _________________
Update Rate: _______ Hz
Compass Type: [ ] Integrated  [ ] Separate
Sample NMEA Output: (paste below)


```

### **Gunner Station (RWS)**
```
IP Address: _________________
Port: _________________
Protocol: [ ] TCP  [ ] UDP
Message Format: [ ] Binary  [ ] JSON  [ ] ASCII  [ ] Other: _______
Coordinate Reference: _________________
Authorization Required: [ ] Yes  [ ] No
Sample Command: (attach file or paste below)


```

### **Map Requirements**
```
Map Provider Preference: [ ] OpenStreetMap  [ ] Mapbox  [ ] Google  [ ] Offline
API Key (if needed): _________________
Offline Tiles Required: [ ] Yes  [ ] No
Coverage Area: _________________
```

---

## 🚀 Next Steps

1. **Fill out the Information Request Form** above
2. **Provide all ICDs and API documentation**
3. **Schedule hardware access** for integration testing
4. **Confirm network configuration** and connectivity
5. **Review and approve implementation plan**

Once documentation is received, I can:
- Create production driver implementations
- Set up proper coordinate transformations
- Implement map overlay with GPS integration
- Add gunner station communication protocol
- Configure all network interfaces

---

## 📞 Contact & Support

**Questions about this document?**
- Review each section carefully
- Mark any unclear items
- Provide as much detail as possible
- Include sample data/messages where available

**Ready to proceed?**
Once you provide the required information, I'll implement the production drivers and map integration.

---

*Document Version: 1.0*  
*Date: November 25, 2024*  
*Status: Awaiting Sensor Documentation*
