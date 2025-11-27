# TriAD C2 - Testing Guide

## 🧪 **Testing the Track Streaming Service**

### **Quick Start: Test Locally**

**Terminal 1: Start C2 System**
```bash
cd /Users/xanderlouw/CascadeProjects/C2
python3 triad_c2.py
```

This will:
- Start mock engine (with realistic sensor data)
- Start orchestration bridge
- Enable gunner interface (UDP broadcast on port 5100)
- Launch QML UI
- Begin streaming tracks @ 10 Hz

**Terminal 2: Start Gunner Simulator**
```bash
cd /Users/xanderlouw/CascadeProjects/C2
python3 tools/gunner_simulator.py
```

Prompts:
- Station ID: Press Enter for `GUNNER_1`
- C2 IP: Enter `localhost` (will use broadcast for local testing)

---

## 📡 **What You Should See**

### **C2 System Output:**
```
======================================================================
  TriAD C2 - Counter-UAS Command & Control
======================================================================
  Architecture: Engine → Orchestration → UI
  Engine: Mock (Python prototype) - WITH REAL SENSOR SPECS
  UI: Qt Quick (QML) GPU-accelerated
======================================================================

[INIT] Starting mock engine...
[INIT] Creating orchestration bridge...
[GUNNER INTERFACE] Initialized
  Track stream: UDP broadcast to 192.168.10.255:5100
  Status receive: UDP listen on port 5101
  Update rate: 10.0 Hz
[GUNNER INTERFACE] ✓ Track stream socket ready
[GUNNER INTERFACE] ✓ Status receive socket ready on port 5101
[GUNNER INTERFACE] ✓ Service started
[BRIDGE] Gunner interface enabled and started
[GUNNER INTERFACE] Track streaming started
[GUNNER INTERFACE] Status receiver started
[INIT] Exposing data models to QML...
[INIT] Loading QML from: /Users/xanderlouw/CascadeProjects/C2/ui/Main.qml

======================================================================
  TriAD C2 - RUNNING
======================================================================

[GUNNER STREAM] Broadcasting 5 tracks to 192.168.10.255:5100
```

### **Gunner Simulator Output:**
```
======================================================================
  GUNNER_1 - TRACK DISPLAY
======================================================================
ID     TYPE   RANGE    AZ      PRIORITY   RECOMMENDED
----------------------------------------------------------------------
1000   UAV    1200     45.3    HIGH       CRx-30
2001   UAV    680      244.5   HIGH       CRx-30
2002   UAV    150      120.2   CRITICAL   CRx-40
1003   UAV    8500     310.1   LOW        OUT_OF_RANGE
----------------------------------------------------------------------
Total tracks: 4
Cued track: NONE
Visual lock: NO
Weapon: NONE
======================================================================
```

---

## 🎮 **Interactive Testing**

### **Scenario 1: Cue a Track**

In gunner simulator terminal:
```
[GUNNER_1]> cue 2001 CRx-30
```

Expected output:
```
[GUNNER_1] OPERATOR ACTION:
  1. SELECT WEAPON: CRx-30
  2. CUE TRACK: 2001
  3. RWS SLEWING to Az=244.5°, El=14.2°

[GUNNER_1] ✓ VISUAL LOCK ACHIEVED on Track 2001
  Ready to fire: CRx-30
```

C2 system should show:
```
[GUNNER STATUS] GUNNER_1: CUED Track 2001 (Weapon: CRx-30)
[GUNNER STATUS] GUNNER_1: VISUAL LOCK on Track 2001
[BRIDGE] Gunner status: GUNNER_1 - Track 2001, Weapon: CRx-30, Visual: True
```

### **Scenario 2: Fire**

In gunner simulator terminal:
```
[GUNNER_1]> fire
```

Expected output:
```
[GUNNER_1] 🔥 FIRING CRx-30 at Track 2001
  Range: 680m
  Position: Az=244.5°, El=14.2°
  Rounds remaining: 115
```

### **Scenario 3: Release Track**

In gunner simulator terminal:
```
[GUNNER_1]> release
```

Expected output:
```
[GUNNER_1] RELEASE TRACK 2001
```

C2 should show track released.

### **Scenario 4: Check Status**

In gunner simulator terminal:
```
[GUNNER_1]> status
```

Expected output:
```
Station: GUNNER_1
Cued track: NONE
Visual lock: False
Weapon: NONE
RWS: Az=244.5°, El=14.2°
Rounds: 115
```

---

## 🔬 **Advanced Testing**

### **Test Multiple Gunners**

**Terminal 3: Second Gunner**
```bash
python3 tools/gunner_simulator.py
```

Enter:
- Station ID: `GUNNER_2`
- C2 IP: `localhost`

Now both gunners receive all tracks. Test coordination:

**Gunner 1:**
```
[GUNNER_1]> cue 2001 CRx-30
```

**Gunner 2:**
```
[GUNNER_2]> cue 2002 CRx-40
```

Both should work independently. C2 should track both engagements.

---

### **Test Effector Recommendations**

Watch track ranges and recommendations:

| Range | Recommended | Reason |
|-------|-------------|--------|
| 1200m | CRx-30 | RANGE_1200M_LONG_RANGE |
| 680m | CRx-30 | RANGE_680M_LONG_RANGE |
| 280m | CRx-30 | RANGE_280M_TRANSITION_USE_30MM |
| 150m | CRx-40 | RANGE_150M_OPTIMAL_40MM |
| 8500m | OUT_OF_RANGE | RANGE_8500M_TOO_FAR |

Gunner can override recommendations. Test override:
```
[GUNNER_1]> cue 280 CRx-40
```

This overrides the CRx-30 recommendation (C2 will log this).

---

### **Test Track Priority**

Priority calculation:
- **CRITICAL:** Close range + high confidence + UAV
- **HIGH:** Medium range + fused track
- **MEDIUM:** Longer range or lower confidence
- **LOW:** Very far or BIRD type

Watch the priority field in track display.

---

## 📊 **Performance Validation**

### **Measure Update Rate**

In gunner simulator, track displays update every 5 seconds. You should see:
- Tracks updating positions smoothly
- Range values changing
- Azimuth values evolving
- 10 Hz stream consistent (no gaps)

### **Check Latency**

Add timestamps to track data and compare:
1. Engine generates track @ T0
2. Bridge builds snapshot @ T1
3. Gunner receives @ T2

Target: T2 - T0 < 100ms

### **Stress Test: Many Tracks**

Modify mock engine to generate 50 tracks, verify:
- [ ] All tracks streamed
- [ ] No packet loss
- [ ] UI remains responsive
- [ ] 10 Hz rate maintained

---

## 🐛 **Troubleshooting**

### **Problem: Gunner not receiving tracks**

**Check 1: Firewall**
```bash
# macOS
sudo pfctl -d  # Temporarily disable firewall

# Or allow UDP port 5100
sudo pfctl -a com.apple/250.TriadC2Allow -f - <<EOF
pass in proto udp from any to any port 5100
EOF
```

**Check 2: Network interface**
```bash
# Verify UDP broadcast working
sudo tcpdump -i any -n udp port 5100
```

You should see packets being sent every 100ms.

**Check 3: Binding address**
In `gunner_interface.py`, verify broadcast address:
- `255.255.255.255` for local testing
- `192.168.10.255` for production subnet

---

### **Problem: C2 not receiving gunner status**

**Check:** Gunner simulator is sending to correct IP and port.

Default: `192.168.10.10:5101`

For local testing, change to `localhost` or `127.0.0.1`.

**Fix:** Edit gunner simulator:
```python
c2_address = "127.0.0.1"  # For local testing
```

---

### **Problem: Port already in use**

```
OSError: [Errno 48] Address already in use
```

**Fix:**
```bash
# Find process using port
lsof -i :5100

# Kill it
kill -9 <PID>
```

Or change ports in configuration.

---

## ✅ **Success Criteria**

### **Minimum:**
- [x] C2 system starts without errors
- [x] Gunner simulator receives track broadcasts
- [x] Tracks display correctly in simulator
- [x] Effector recommendations appear
- [x] Gunner can cue a track
- [x] C2 receives gunner status
- [x] Visual lock simulation works

### **Optimal:**
- [ ] 10 Hz update rate stable
- [ ] Latency < 100ms (sensor → gunner)
- [ ] Multiple gunners work independently
- [ ] UI shows gunner status (TODO)
- [ ] Kill assessment works (TODO)
- [ ] No packet loss over 1 hour
- [ ] Handles 50+ tracks smoothly

---

## 📝 **Test Report Template**

After testing, document results:

```markdown
# TriAD C2 Test Report

**Date:** 2025-11-26
**Tester:** [Your Name]
**Configuration:** Local (localhost), 1 C2 + 2 gunners

## Test Results

### Track Streaming
- [x] Tracks received by gunner
- [x] 10 Hz rate: PASS (measured 10.02 Hz avg)
- [x] Data correctness: PASS
- [ ] Latency: UNKNOWN (need timestamping)

### Gunner Interface
- [x] Cue track: PASS
- [x] Visual lock simulation: PASS
- [x] Fire simulation: PASS
- [x] Release track: PASS
- [x] Multi-gunner: PASS (2 gunners tested)

### Effector Recommendations
- [x] Range-based recommendations: PASS
- [x] Correct weapon selection: PASS
- [ ] Override logging: TODO (need to verify)

### Issues Found
1. None

### Performance
- Update rate: 10.02 Hz (target: 10 Hz) ✓
- CPU usage: 15% ✓
- Memory: Stable ✓

### Recommendations
- Add UI display for gunner status
- Implement kill assessment
- Test with live hardware
```

---

## 🚀 **Next: Test with Live Hardware**

Once local testing passes:

1. **Configure production network**
   - C2: 192.168.10.10
   - Gunner 1: 192.168.10.20
   - Gunner 2: 192.168.10.21

2. **Deploy to hardware**
   - Install on mission computer
   - Connect sensors
   - Configure firewall rules

3. **Validate end-to-end**
   - Echoguard → C2 → Gunner
   - SkyView → C2 → Gunner
   - Real RWS slewing

4. **Measure real-world performance**
   - Actual latencies
   - Coordinate transformation accuracy
   - Association correctness

---

**Ready to test? Run the commands above and report results!**
