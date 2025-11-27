# TriAD C2 - Outstanding Tasks

**Last Updated:** November 26, 2025  
**Current Phase:** Track Streaming Implementation

---

## ✅ **Completed Today**

### **Track Streaming Service (CORRECTED: Operator-Initiated)**
- [x] Port specifications defined (`PORT_SPECIFICATIONS.md`)
- [x] Gunner interface service implemented (`orchestration/gunner_interface.py`)
- [x] **Operator engagement control** (streams ONLY engaged track)
- [x] Effector recommendation engine (range-based logic)
- [x] **Threat prioritization algorithm** (6-factor scoring)
- [x] Priority calculation (CRITICAL/HIGH/MEDIUM/LOW)
- [x] Integration with orchestration bridge
- [x] Engagement/disengage methods (operator control)
- [x] Gunner simulator tool (`tools/gunner_simulator.py`)
- [x] UDP broadcast track streaming @ 10 Hz (only when engaged)
- [x] UDP status receive from gunners
- [x] Gunner station registry and management

### **Documentation**
- [x] Port specifications
- [x] Network topology diagrams
- [x] Engagement workflow (weapon selection first)
- [x] Effector recommendation logic
- [x] System understanding confirmation

---

## 🔄 **In Progress**

### **Testing**
- [ ] Test track streaming with gunner simulator
- [ ] Verify 10 Hz update rate consistency
- [ ] Test multi-gunner coordination
- [ ] Validate effector recommendations

---

## 📋 **High Priority (Next Steps)**

### **1. UI Engagement Button (IMMEDIATE - 1-2 days)**

**C2 Operator needs UI to engage tracks!**

**Required UI Elements:**
```qml
// EngagementPanel.qml
Rectangle {
    Column {
        // Threat Prioritization Display
        Text {
            text: "HIGHEST PRIORITY THREAT"
            font.bold: true
        }
        
        Text {
            text: "Track " + bridge.get_highest_priority_track_id()
            color: "#ff0000"  // Critical red
        }
        
        // Track details
        Text { text: "Range: " + highestPriorityTrack.range + "m" }
        Text { text: "Type: " + highestPriorityTrack.type }
        Text { text: "Confidence: " + highestPriorityTrack.confidence }
        Text { text: "Recommended: " + highestPriorityTrack.recommended_effector }
        
        // ENGAGE BUTTON (defaults to highest priority)
        Button {
            text: "ENGAGE TRACK " + bridge.get_highest_priority_track_id()
            enabled: !bridge.is_track_engaged()
            onClicked: {
                var result = bridge.engage_track(
                    bridge.get_highest_priority_track_id(),
                    "OPERATOR_1"
                )
                console.log("Engagement:", result.message)
            }
        }
        
        // Override selection
        ListView {
            model: tracksModel  // All detected tracks
            delegate: RadioButton {
                text: "Track " + modelData.id + " (Override)"
                onClicked: {
                    var result = bridge.engage_track(
                        modelData.id,
                        "OPERATOR_1"
                    )
                }
            }
        }
        
        // DISENGAGE BUTTON
        Button {
            text: "CANCEL ENGAGEMENT"
            enabled: bridge.is_track_engaged()
            onClicked: {
                bridge.disengage_track()
            }
        }
        
        // Current engagement status
        Text {
            text: bridge.is_track_engaged() ? 
                  "ENGAGED: Track " + bridge.get_engaged_track_id() :
                  "NO ENGAGEMENT"
            color: bridge.is_track_engaged() ? "#00ff00" : "#888888"
        }
    }
}
```

**Tasks:**
- [ ] Create `EngagementPanel.qml` component
- [ ] Add to main UI layout
- [ ] Expose bridge methods to QML
- [ ] Test engagement workflow
- [ ] Add visual feedback (flashing for critical threats)
- [ ] Add audio alert for critical threats
- [ ] Log all engagement decisions

### **2. Track Streaming Validation (This Week)**
- [ ] Run C2 system with gunner interface enabled
- [ ] Test engagement workflow (operator clicks ENGAGE)
- [ ] Verify ONLY engaged track streams
- [ ] Test with gunner simulator
- [ ] Test disengage/re-engage
- [ ] Verify UDP broadcast working
- [ ] Test status feedback loop
- [ ] Measure actual latency (sensor → gunner)
- [ ] Handle edge cases:
  - [ ] Engaged track lost (auto-disengage)
  - [ ] Multiple operators (conflict resolution)
  - [ ] Gunner station timeout/disconnection
  - [ ] Network packet loss

### **2. Kill Assessment Engine (1-2 days)**
```python
class KillAssessmentEngine:
    def on_engagement(self, track_id, gunner_id):
        """Log engagement start time"""
    
    def on_track_lost(self, track_id):
        """Assess if loss indicates kill"""
        # If track lost within 3s of engagement → KILL_CONFIRMED
        # If track lost 3-10s after → KILL_PROBABLE
        # If track persists > 10s → MISS_PRESUMED
    
    def generate_report(self):
        """Generate engagement effectiveness report"""
```

**Tasks:**
- [ ] Implement kill assessment logic
- [ ] Track engagement timestamps
- [ ] Correlate track loss with engagement
- [ ] Log all engagements to database
- [ ] Generate after-action reports

### **3. UI Enhancements (2-3 days)**
- [ ] Gunner station status cards in UI
  - [ ] Show connected gunners
  - [ ] Display cued tracks
  - [ ] Visual lock indicators
  - [ ] Weapon selection display
  - [ ] Ammunition counts
- [ ] Track priority visualization
  - [ ] Color-code by priority (RED=CRITICAL, ORANGE=HIGH, etc.)
  - [ ] Sort track list by priority
  - [ ] Flashing for critical threats
- [ ] Effector recommendation display
  - [ ] Show recommended weapon per track
  - [ ] Display recommendation reason
- [ ] Pilot position mapping (from RF)
  - [ ] Show pilot marker on map
  - [ ] Draw line from pilot to drone
  - [ ] Calculate pilot-drone distance

### **4. Sensor Driver Integration (3-4 days)**
- [ ] Test with live Echoguard radar
  - [ ] Validate BNET packet parsing
  - [ ] Verify coordinate system (vehicle-relative)
  - [ ] Test UAV probability classification
- [ ] Test with live SkyView RF
  - [ ] Configure TLS certificates
  - [ ] Test precision vs sector modes
  - [ ] Verify GPS heading correction
  - [ ] Validate pilot position extraction
- [ ] GPS integration
  - [ ] Parse NMEA sentences
  - [ ] Extract heading for RF coordinate conversion
  - [ ] Validate ownship position accuracy

---

## 🎯 **Medium Priority (Next 2-4 Weeks)**

### **5. C++ Engine Migration**
**Why:** Real-time deterministic performance

**Architecture:**
```cpp
class TriadEngine {
    // Sensor threads
    RadarDriver radar_;
    RFDriver rf_;
    GPSDriver gps_;
    
    // Fusion thread
    FusionEngine fusion_;
    
    // Publishing thread
    TrackPublisher publisher_;
    
    // gRPC server
    GrpcServer grpc_server_;
};
```

**Tasks:**
- [ ] Set up C++ project structure (CMake)
- [ ] Port sensor drivers to C++
  - [ ] Echoguard BNET parser
  - [ ] SkyView TLS/JSON parser
  - [ ] GPS NMEA parser
- [ ] Implement production Kalman fusion
  - [ ] Extended Kalman Filter (EKF)
  - [ ] Multi-hypothesis tracking
  - [ ] Association gating (chi-squared)
  - [ ] Track initiation/confirmation/deletion
- [ ] Implement gRPC server
  - [ ] Compile protobuf → C++ stubs
  - [ ] Implement streaming RPCs
  - [ ] Add TLS/mTLS security
- [ ] Multi-threading
  - [ ] Lock-free queues for sensor data
  - [ ] Thread pool for processing
  - [ ] Priority scheduling
- [ ] Performance validation
  - [ ] Target: <100ms sensor→gunner latency
  - [ ] Target: 10-50 Hz update rate
  - [ ] Target: Handle 50+ simultaneous tracks

### **6. gRPC Implementation (Python → C++)**
- [ ] Compile `triad_updated.proto` → stubs
  ```bash
  # C++
  protoc --cpp_out=. --grpc_out=. --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` triad_updated.proto
  
  # Python
  python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. triad_updated.proto
  ```
- [ ] Implement gRPC server (C++ engine)
- [ ] Update orchestration bridge to gRPC client
- [ ] Add TLS certificates
- [ ] Test bidirectional streaming
- [ ] Benchmark latency

### **7. Advanced Fusion**
- [ ] Implement Kalman filters
  - [ ] State vector: [x, y, z, vx, vy, vz]
  - [ ] Prediction step (process model)
  - [ ] Update step (measurement model)
  - [ ] Covariance propagation
- [ ] Association logic
  - [ ] Nearest-neighbor data association
  - [ ] Global nearest neighbor (GNN)
  - [ ] Joint probabilistic data association (JPDA)
- [ ] Track quality scoring
  - [ ] Innovation monitoring
  - [ ] Covariance trace
  - [ ] Hit/miss ratio
- [ ] Track initiation
  - [ ] N of M confirmation (e.g., 3 of 5 detections)
  - [ ] Tentative → confirmed → mature states
- [ ] Track deletion
  - [ ] M of N deletion (e.g., 5 misses in 10 frames)
  - [ ] Covariance divergence check

---

## 🔧 **Low Priority (Future Enhancements)**

### **8. Data Recording & Replay**
- [ ] Time-series database (InfluxDB or similar)
- [ ] Record all sensor data
- [ ] Record all track updates
- [ ] Record all operator actions
- [ ] Replay capability for training
- [ ] Export to KML/CSV/JSON

### **9. Multi-User & Roles**
- [ ] User authentication
- [ ] Role-based access control (RBAC)
  - Commander: Full access
  - Operator: Engage authority
  - Observer: View only
- [ ] Audit logging
- [ ] Session management

### **10. Advanced UI**
- [ ] 3D radar view (Three.js or Qt3D)
- [ ] Track trajectory prediction (extrapolation)
- [ ] Track history trails
- [ ] Engagement replay visualization
- [ ] Heatmap of detection coverage
- [ ] Performance metrics dashboard

### **11. Communication Integration**
- [ ] Radio integration (SATCOM, tactical radio)
- [ ] Remote command capability
- [ ] Status reporting to higher command
- [ ] Alert distribution (SMS, email, radio)

### **12. Machine Learning**
- [ ] UAV classification model (beyond radar probability)
- [ ] Swarm detection
- [ ] Pattern recognition (loitering, surveillance, attack)
- [ ] Pilot location prediction
- [ ] Engagement outcome prediction

---

## 🚧 **Blocked / Waiting on Information**

### **From User:**
1. ⏳ **RWS command structure** (CRx-30/40 specifics)
   - Ethernet packet format?
   - Command codes?
   - SDK/API available?

2. ⏳ **Gunner station software vendor**
   - Who develops it?
   - API documentation?
   - Data format expectations?

3. ⏳ **Deployment timeline**
   - When operational?
   - Hardware availability for testing?

4. ⏳ **Network configuration**
   - Actual IP addresses (production)?
   - VLANs or single LAN?
   - Redundancy requirements?

---

## 📊 **Testing Checklist**

### **Component Testing**
- [x] Mock engine generates realistic tracks
- [x] Effector recommendation logic correct
- [x] Priority calculation sensible
- [ ] Track streaming @ 10 Hz verified
- [ ] Gunner status receive working
- [ ] Kill assessment logic correct
- [ ] UI updates with gunner status

### **Integration Testing**
- [ ] End-to-end: Sensor → C2 → Gunner
- [ ] Multi-gunner coordination (no overlaps)
- [ ] Track priority sorting
- [ ] Effector recommendation accuracy
- [ ] Kill assessment correlation
- [ ] 24-hour stability test

### **Performance Testing**
- [ ] Latency: Sensor → C2 < 50ms
- [ ] Latency: C2 → Gunner < 50ms
- [ ] Total: Sensor → Gunner < 100ms
- [ ] Update rate: 10 Hz sustained
- [ ] Handle 50+ tracks
- [ ] CPU usage < 50%
- [ ] Memory stable (no leaks)

### **Hardware Testing** (When Available)
- [ ] Connect to live Echoguard
- [ ] Connect to live SkyView
- [ ] Test with real RWS
- [ ] Validate coordinate transformations
- [ ] Measure real-world latencies
- [ ] 24-hour operational test

---

## 🎯 **This Week's Focus**

1. **Test track streaming** with gunner simulator ✓ (Ready)
2. **Implement kill assessment** engine
3. **Add gunner status** to UI
4. **Test with live hardware** (if available)

---

## 📅 **Roadmap Timeline**

| Week | Focus | Deliverables |
|------|-------|--------------|
| **Week 1 (Current)** | Track streaming | Gunner interface working, tested |
| **Week 2-3** | Kill assessment + UI | Engagement logging, gunner status display |
| **Week 4-5** | Hardware testing | Live sensor integration, validation |
| **Week 6-9** | C++ engine port | Real-time performance, gRPC |
| **Week 10-12** | Advanced fusion | Production Kalman filters |
| **Week 13-16** | Testing & hardening | Stability, performance, certification |
| **Week 17-20** | Deployment prep | Documentation, training, acceptance |

**Total: ~20 weeks to production deployment**

---

## 🔍 **Known Issues / Tech Debt**

- [ ] UDP broadcast may not work across subnets (need multicast or unicast)
- [ ] JSON serialization not as efficient as protobuf (migrate later)
- [ ] No encryption on track stream (add IPsec or TLS wrapper)
- [ ] Gunner timeout not automated (need periodic cleanup)
- [ ] Track ID collision if engine restarts (need persistent IDs)
- [ ] No sensor health monitoring yet (add watchdogs)
- [ ] UI doesn't show gunner status yet (need QML models)
- [ ] Priority calculation could be tuned (need real-world data)

---

**Next Action:** Test track streaming with gunner simulator, verify 10 Hz rate and data correctness.
