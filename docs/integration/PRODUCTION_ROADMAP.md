# TriAD C2 - Production Roadmap (Updated)

**Based on Clarified Architecture: C2 = Detection/Tracking, Gunner Station = Weapon Control**

---

## 🎯 **System Responsibilities**

### **C2 System (This Project)**
- ✅ Detect UAVs (Radar + RF)
- ✅ Fuse multi-sensor tracks
- ✅ Assign track IDs and priorities
- ✅ Stream continuous position data to Gunner Station(s)
- ✅ Provide re-cue capability if visual lost
- ✅ Assess kill confirmation (track disappears)
- ✅ Display tactical picture to operators
- ❌ **NOT** firing authority
- ❌ **NOT** weapon safety interlocks (Gunner's responsibility)

### **Gunner Station (External System)**
- Receives track stream from C2
- RWS control (auto-slew to track)
- EO/IR visual acquisition
- Visual drone tracking software (keeps UAV centered)
- Weapon selection (CRx-30 or CRx-40)
- Fire control + safety interlocks
- Ammunition management
- **Makes final firing decision**

---

## 📊 **Current Status**

### ✅ **What's Working**
- [x] Echoguard radar driver (production-ready)
- [x] SkyView RF driver (production-ready)
- [x] GPS/heading (production-ready)
- [x] RWS slew commands (production-ready)
- [x] Track fusion engine (functional, needs Kalman)
- [x] Coordinate transformations (tested)
- [x] QML UI with radar display (60 FPS)
- [x] Mock engine with realistic sensor simulation
- [x] Hybrid architecture (Engine → Orchestration → UI)

### 🟡 **What Needs Work**
- [ ] Continuous track streaming protocol (gunner interface)
- [ ] Multi-gunner station support
- [ ] C++ engine migration (for real-time performance)
- [ ] gRPC implementation (Engine ↔ Orchestration)
- [ ] Production Kalman fusion
- [ ] Kill assessment logic
- [ ] Visual lock status feedback from gunner
- [ ] Re-cue workflow

### 🔴 **What's Blocking**
- [ ] Gunner station interface specification (port numbers)
- [ ] Hardware testing (live sensors + gunner station)
- [ ] RWS command structure (CRx-30/40 specifics)

---

## 🚀 **Phase-by-Phase Roadmap**

### **PHASE 1: Gunner Interface Implementation (3-4 weeks)**

**Goal:** Enable continuous track streaming to Gunner Station(s)

#### 1.1 Track Streaming Service
**Status:** Protocol defined (`gunner_protocol.proto`)

**Tasks:**
- [ ] Compile protobuf → Python stubs
  ```bash
  python3 -m grpc_tools.protoc -I. \
    --python_out=. --grpc_python_out=. gunner_protocol.proto
  ```

- [ ] Implement UDP broadcast (simple start)
  ```python
  # Send TracksSnapshot at 10 Hz via UDP
  class TrackStreamer:
      def __init__(self, broadcast_port=5100):
          self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
          self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
      
      def stream_tracks(self, tracks):
          snapshot = TracksSnapshot(tracks=tracks, ...)
          data = snapshot.SerializeToString()
          self.sock.sendto(data, ('<broadcast>', self.broadcast_port))
  ```

- [ ] OR implement gRPC bidirectional streaming (production)
  ```python
  class GunnerInterface(gunner_pb2_grpc.GunnerInterfaceServicer):
      def StreamTracks(self, request_iterator, context):
          # C2 streams tracks to gunner
          # Gunner streams status back to C2
          while True:
              snapshot = self.get_tracks_snapshot()
              yield snapshot
              
              # Receive gunner status
              gunner_status = next(request_iterator)
              self.handle_gunner_status(gunner_status)
  ```

- [ ] Track Priority Assignment
  ```python
  def calculate_priority(track):
      # Closest + highest confidence = highest priority
      range_score = 1.0 - (track.range_m / 3000.0)  # Normalize
      confidence_score = track.confidence
      
      # Threat bonus
      threat_bonus = 0.2 if track.type == "UAV" else 0.0
      
      # Fused bonus
      fused_bonus = 0.1 if track.source == "FUSED" else 0.0
      
      priority_score = (range_score + confidence_score + 
                       threat_bonus + fused_bonus) / 2.2
      
      if priority_score > 0.8:
          return "CRITICAL"
      elif priority_score > 0.6:
          return "HIGH"
      elif priority_score > 0.4:
          return "MEDIUM"
      else:
          return "LOW"
  ```

#### 1.2 Multi-Gunner Support

- [ ] Gunner Station Registry
  ```python
  class GunnerStationManager:
      def __init__(self):
          self.stations = {}  # {station_id: GunnerStatus}
      
      def register_station(self, station_id, address):
          self.stations[station_id] = {
              'address': address,
              'last_seen': time.time(),
              'cued_track': None,
              'visual_lock': False
          }
      
      def update_status(self, status: GunnerStatus):
          if status.station_id in self.stations:
              self.stations[status.station_id].update({
                  'cued_track': status.cued_track_id,
                  'visual_lock': status.visual_lock,
                  'last_seen': time.time()
              })
  ```

- [ ] Track Assignment Coordination
  ```python
  # Prevent multiple gunners cueing same track
  def assign_track_to_gunner(self, track_id, station_id):
      # Check if already assigned
      for sid, info in self.stations.items():
          if info['cued_track'] == track_id and sid != station_id:
              return False, f"Track {track_id} already cued by {sid}"
      
      # Assign
      self.stations[station_id]['cued_track'] = track_id
      return True, "Track assigned"
  ```

#### 1.3 Visual Lock Feedback Integration

- [ ] Receive gunner status updates
- [ ] Update UI to show which tracks have visual lock
- [ ] Highlight visually-locked tracks differently
- [ ] Show which gunner has which track

#### 1.4 Re-Cue Workflow

- [ ] Gunner sends "VISUAL_LOST" command
- [ ] C2 continues streaming position
- [ ] Gunner RWS slews back to C2 position data
- [ ] Gunner re-acquires visual
- [ ] Sends "VISUAL_LOCK" confirmation

**Deliverables:**
- ✅ `gunner_protocol.proto` (done)
- ⏳ Track streaming service (UDP or gRPC)
- ⏳ Multi-gunner coordination
- ⏳ Priority calculation
- ⏳ Visual lock status in UI

---

### **PHASE 2: Kill Assessment & Intelligence (2-3 weeks)**

**Goal:** Automatically assess engagement outcomes

#### 2.1 Kill Assessment Logic

```python
class KillAssessmentEngine:
    def __init__(self):
        self.engaged_tracks = {}  # {track_id: engagement_time}
    
    def on_gunner_fires(self, track_id):
        """Called when gunner fires at a track"""
        self.engaged_tracks[track_id] = time.time()
        print(f"[KILL ASSESSMENT] Track {track_id} engaged at {time.time()}")
    
    def on_track_lost(self, track_id):
        """Called when track disappears"""
        if track_id in self.engaged_tracks:
            engage_time = self.engaged_tracks[track_id]
            time_since_engage = time.time() - engage_time
            
            if time_since_engage < 3.0:
                # Track lost shortly after engage → likely kill
                assessment = "KILL_CONFIRMED"
            elif time_since_engage < 10.0:
                # Track lost within 10s → probable kill
                assessment = "KILL_PROBABLE"
            else:
                # Track may have left area
                assessment = "UNCLEAR"
            
            print(f"[KILL ASSESSMENT] Track {track_id}: {assessment}")
            print(f"  Time since engage: {time_since_engage:.1f}s")
            
            return KillAssessment(
                track_id=track_id,
                track_lost=True,
                time_since_engage_sec=time_since_engage,
                assessment=assessment
            )
        
        return None  # Not an engaged track
    
    def on_track_persists(self, track_id, time_since_engage):
        """Track still visible after engagement"""
        if time_since_engage > 5.0:
            return KillAssessment(
                track_id=track_id,
                track_lost=False,
                time_since_engage_sec=time_since_engage,
                assessment="MISS_PRESUMED"
            )
```

#### 2.2 RF Intelligence Enhancements

- [ ] Pilot position tracking
  - Display pilot location on map
  - Calculate pilot-drone distance
  - Track pilot movement patterns (stationary vs mobile)

- [ ] Drone identification database
  - Store known aircraft models
  - Link to threat profiles
  - Flag military/commercial/DIY

- [ ] RF signature analysis
  - Frequency hopping detection
  - Multiple controller detection
  - Swarm coordination detection

#### 2.3 Post-Engagement Tracking

```python
class EngagementLogger:
    def log_engagement(self, track_id, gunner_id, weapon, outcome):
        entry = {
            'timestamp': time.time(),
            'track_id': track_id,
            'gunner_station': gunner_id,
            'weapon_used': weapon,  # CRx-30 or CRx-40
            'target_range_m': track.range_m,
            'target_type': track.type,
            'confidence': track.confidence,
            'outcome': outcome,  # KILL_CONFIRMED, MISS, etc.
            'pilot_location': (track.pilot_lat, track.pilot_lon) if available,
            'aircraft_model': track.aircraft_model
        }
        
        # Save to database
        self.db.insert('engagements', entry)
        
        # Generate AAR data
        self.generate_after_action_report()
```

**Deliverables:**
- Kill assessment engine
- Pilot position visualization
- Engagement logging
- After-action reporting

---

### **PHASE 3: C++ Engine Migration (4-6 weeks)**

**Goal:** Real-time deterministic performance

#### 3.1 Core Engine in C++

**Why C++:**
- Deterministic latency (no garbage collection)
- Multi-threading with fine control
- Direct hardware access
- Military-grade reliability

**Structure:**
```cpp
class TriadEngine {
public:
    void Start();
    void Stop();
    
private:
    // Sensor threads
    std::unique_ptr<RadarDriver> radar_;
    std::unique_ptr<RFDriver> rf_;
    std::unique_ptr<GPSDriver> gps_;
    
    // Fusion thread
    std::unique_ptr<FusionEngine> fusion_;
    
    // Publishing thread
    std::unique_ptr<TrackPublisher> publisher_;
    
    // Thread-safe queues
    ThreadSafeQueue<RadarMeasurement> radar_queue_;
    ThreadSafeQueue<RFDetection> rf_queue_;
    ThreadSafeQueue<Track> track_queue_;
};
```

#### 3.2 Production Kalman Fusion

**Extended Kalman Filter for each track:**
```cpp
class TrackFilter {
    // State vector: [x, y, z, vx, vy, vz]
    Eigen::VectorXd state_;
    Eigen::MatrixXd covariance_;
    
    void Predict(double dt);
    void UpdateRadar(const RadarMeasurement& meas);
    void UpdateRF(const RFDetection& det);
};
```

**Multi-Hypothesis Tracking:**
- Track initiation logic
- Association gating (chi-squared test)
- Track confirmation (N of M)
- Track deletion (M of N)

#### 3.3 gRPC Server

```cpp
class TriadGrpcServer : public TriadEngine::Service {
    grpc::Status StreamTracks(
        grpc::ServerContext* context,
        const Empty* request,
        grpc::ServerWriter<TracksSnapshot>* writer) override {
        
        while (running_) {
            TracksSnapshot snapshot = GetTracksSnapshot();
            writer->Write(snapshot);
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        }
        return grpc::Status::OK;
    }
};
```

**Deliverables:**
- C++ engine with multi-threading
- Production Kalman filters
- gRPC server implementation
- Performance targets met (<100ms latency)

---

### **PHASE 4: UI Enhancements (2-3 weeks)**

**Goal:** Operational UI for C2 operators

#### 4.1 Gunner Station Status Display

```qml
// GunnerStationCard.qml
Rectangle {
    width: 280
    height: 180
    
    Column {
        Text { 
            text: "GUNNER STATION 1"
            font.bold: true
        }
        
        Row {
            Text { text: "Status:" }
            Text { 
                text: gunnerStatus.connected ? "ONLINE" : "OFFLINE"
                color: gunnerStatus.connected ? "#00ff00" : "#ff0000"
            }
        }
        
        Row {
            Text { text: "Cued Track:" }
            Text { text: gunnerStatus.cuedTrackId || "NONE" }
        }
        
        Rectangle {
            width: 200
            height: 40
            color: gunnerStatus.visualLock ? "#00ff00" : "#333333"
            Text {
                text: gunnerStatus.visualLock ? "VISUAL LOCK" : "NO LOCK"
                anchors.centerIn: parent
            }
        }
        
        Row {
            Text { text: "Weapon:" }
            Text { text: gunnerStatus.selectedWeapon || "NONE" }
        }
        
        Row {
            Text { text: "Rounds:" }
            Text { text: gunnerStatus.roundsRemaining }
        }
    }
}
```

#### 4.2 Pilot Position Map Overlay

- Show pilot marker on map (from RF precision detection)
- Draw line from pilot to drone
- Calculate distance
- Track pilot movement history

#### 4.3 Track Priority Visualization

- Color-code tracks by priority
  - RED: CRITICAL (close + high confidence)
  - ORANGE: HIGH
  - YELLOW: MEDIUM
  - GRAY: LOW

- Priority sorting in track list
- Flashing indicators for critical threats

#### 4.4 Engagement History Panel

```qml
ListView {
    model: engagementHistoryModel
    
    delegate: Rectangle {
        Row {
            Text { text: modelData.timestamp }
            Text { text: "Track " + modelData.trackId }
            Text { text: modelData.gunnerStation }
            Text { text: modelData.weapon }
            Text { 
                text: modelData.outcome
                color: modelData.outcome === "KILL_CONFIRMED" ? "#00ff00" : "#ff9900"
            }
        }
    }
}
```

**Deliverables:**
- Gunner station status cards
- Pilot position mapping
- Priority-based visualization
- Engagement history log

---

### **PHASE 5: Testing & Validation (6-8 weeks)**

#### 5.1 Component Testing

**Sensor Drivers:**
- [ ] Test Echoguard with live radar
- [ ] Test SkyView with live RF sensor
- [ ] Validate coordinate transformations
- [ ] Verify 10 Hz update rate

**Track Streaming:**
- [ ] Test UDP broadcast to gunner
- [ ] Verify 10 Hz stream consistency
- [ ] Test with multiple gunners
- [ ] Measure latency (sensor → gunner < 100ms)

**Fusion Engine:**
- [ ] Validate association logic
- [ ] Test track initiation/deletion
- [ ] Verify single-sensor tracks (radar-only, RF-only)
- [ ] Test multi-sensor fusion

#### 5.2 Integration Testing

**End-to-End Scenarios:**

1. **Single Target Detection**
   - RF detects drone
   - C2 creates track
   - Streams to gunner
   - Gunner cues track
   - Visual lock achieved
   - Engagement → kill confirmed

2. **Multiple Targets**
   - 5 simultaneous tracks
   - 2 gunners, each cues different tracks
   - Verify no overlap
   - Prioritization working

3. **Visual Lost & Re-Cue**
   - Gunner loses visual
   - C2 continues streaming
   - Gunner re-cues from C2 data
   - Visual re-acquired

4. **Single-Sensor Tracks**
   - Radar-only track (no RF)
   - RF-only track (no radar)
   - Both stream to gunner correctly

5. **Kill Assessment**
   - Track engaged
   - Track disappears within 3s → KILL_CONFIRMED
   - Track persists → MISS_PRESUMED
   - Log correctly

#### 5.3 Performance Validation

**Metrics:**
| Metric | Target | Test Result |
|--------|--------|-------------|
| Sensor → C2 latency | < 50ms | TBD |
| C2 → Gunner latency | < 50ms | TBD |
| Total: Sensor → Gunner | < 100ms | TBD |
| Stream update rate | 10 Hz | TBD |
| UI frame rate | 60 FPS | ✓ (achieved) |
| Simultaneous tracks | 20+ | TBD |
| Gunner stations supported | 4+ | TBD |

#### 5.4 Stress Testing

- [ ] 50 simultaneous tracks
- [ ] Rapid track churn (appearing/disappearing)
- [ ] Network disruption recovery
- [ ] Sensor failure scenarios
- [ ] 24-hour endurance test

**Deliverables:**
- Test procedures document
- Performance validation report
- Issue tracking and resolution
- Acceptance test results

---

### **PHASE 6: Deployment Prep (3-4 weeks)**

#### 6.1 Configuration Management

```json
// deployment_config.json
{
  "sensors": {
    "radar": {
      "host": "192.168.1.100",
      "port": 23000,
      "protocol": "TCP"
    },
    "rf": {
      "host": "192.168.1.217",
      "port": 59898,
      "protocol": "TLS",
      "cert_dir": "/etc/triad/certs"
    },
    "gps": {
      "port": "/dev/ttyUSB0",
      "baudrate": 9600
    }
  },
  "gunner_interface": {
    "broadcast_port": 5100,
    "update_rate_hz": 10,
    "protocol": "UDP"  // or "GRPC"
  },
  "fusion": {
    "association_threshold_m": 50.0,
    "track_timeout_sec": 5.0,
    "require_n_of_m_confirm": [3, 5]  // 3 of 5 detections
  },
  "deployment": {
    "installation_type": "VEHICLE_MOUNTED",  // or "FIXED_SITE"
    "vehicle_id": "VEHICLE_01"
  }
}
```

#### 6.2 Documentation

- [ ] **Operator Manual**
  - System startup/shutdown procedures
  - Normal operations
  - Track selection and cueing
  - Emergency procedures
  - Troubleshooting

- [ ] **Maintainer Manual**
  - Hardware installation
  - Network configuration
  - Sensor calibration
  - Software updates
  - Diagnostics

- [ ] **System Architecture Document**
  - Component overview
  - Data flow diagrams
  - Interface specifications
  - Performance characteristics

- [ ] **API Reference**
  - Gunner protocol specification
  - Track data structures
  - Command formats
  - Status codes

#### 6.3 Training Materials

- [ ] Operator training slides
- [ ] Video tutorials
- [ ] Practice scenarios
- [ ] Quick reference cards

#### 6.4 Deployment Checklist

**Pre-Deployment:**
- [ ] All sensors tested and calibrated
- [ ] Network configuration verified
- [ ] Gunner stations connected and tested
- [ ] End-to-end test with live hardware
- [ ] Backup/recovery procedures tested
- [ ] Operator training completed

**Installation:**
- [ ] Mount sensors (radar, RF, GPS)
- [ ] Run network cables
- [ ] Install C2 computer
- [ ] Configure IP addresses
- [ ] Test connectivity
- [ ] Calibrate GPS heading
- [ ] Verify coordinate alignment

**Acceptance:**
- [ ] Detection range test
- [ ] Tracking accuracy test
- [ ] Multi-target test
- [ ] Gunner interface test
- [ ] Kill assessment test
- [ ] 24-hour operational test
- [ ] Sign-off by customer

**Deliverables:**
- Complete documentation package
- Training materials
- Deployment checklist
- Acceptance test plan

---

## 📋 **Outstanding Information Needed**

### **From You (Critical):**

1. **Gunner Interface Ports**
   - What port(s) for track streaming? (e.g., UDP 5100)
   - What port for gunner status feedback? (e.g., UDP 5101)
   - UDP broadcast or TCP point-to-point?
   - Or gRPC bidirectional stream?

2. **RWS Command Structure (CRx-30/40)**
   - Command packet format?
   - How to select weapon (30mm vs 40mm)?
   - How does gunner station send slew commands?
   - Any existing API/SDK?

3. **Gunner Station Software**
   - Who develops the gunner station software?
   - Do they have API documentation?
   - What data format do they expect?
   - Visual tracking software vendor?

4. **Timeline**
   - Target deployment date?
   - Hardware availability for testing?
   - Training schedule?

### **Assumptions (Please Confirm):**

- ✅ C2 streams ALL tracks (gunner selects which to cue)
- ✅ Single-sensor tracks are valid (don't need fusion)
- ✅ Kill confirmation = track disappears after engagement
- ✅ C2 doesn't control weapons (gunner does)
- ✅ No geographic fencing in C2
- ✅ Multiple gunner stations supported
- ❓ UDP broadcast acceptable for track streaming?
- ❓ 10 Hz update rate sufficient?
- ❓ Ethernet only (no radio links)?

---

## 📊 **Revised Timeline**

| Phase | Duration | Dependencies | Status |
|-------|----------|--------------|--------|
| **Phase 1: Gunner Interface** | 3-4 weeks | Port specs | 🟡 Can start with UDP prototype |
| **Phase 2: Kill Assessment** | 2-3 weeks | Phase 1 | 🟡 Can start in parallel |
| **Phase 3: C++ Engine** | 4-6 weeks | None | 🟢 Can start now |
| **Phase 4: UI Enhancements** | 2-3 weeks | Phase 1 | 🟡 Depends on gunner status |
| **Phase 5: Testing** | 6-8 weeks | Phases 1-4, hardware | 🔴 Needs hardware access |
| **Phase 6: Deployment** | 3-4 weeks | Phase 5 | 🔴 Needs customer site |
| **TOTAL** | **20-28 weeks** | | |

**With parallel work: 16-20 weeks**

---

## 🎯 **Immediate Next Steps (This Week)**

1. **Clarify gunner interface** (need port/protocol specs)
2. **Start C++ engine port** (can begin immediately)
3. **Implement UDP track streaming prototype**
4. **Design kill assessment logic**
5. **Schedule hardware testing session**

---

## ✅ **What's Clear Now**

- C2 role is detection/tracking/streaming (NOT weapon control)
- Gunner makes all firing decisions
- Safety interlocks are gunner's responsibility
- Kill confirmation via track disappearance
- Support multiple gunner stations
- Single-sensor tracks are valid
- Continuous streaming until track timeout

**This significantly simplifies the C2 system and removes the need for:**
- Firing command protocol
- Ammunition management in C2
- Hardware safety interlocks in C2
- ROE enforcement in C2 (gunner decides)

**Next:** Please provide gunner interface port specifications so we can implement the track streaming service.
