# RF-Silent Drone Detection Mode

## 🎯 Overview

The system now supports **three operational modes** for drone detection and tracking:

1. **Normal Mode** (RF + Radar) - Standard operation
2. **RF-Silent Mode** (Radar-only) - For RF-silent drones
3. **Manual Mode** - Operator override

---

## 🔄 Operational Modes

### **Mode 1: Normal Operation (RF + Radar)**

**Scenario:** Drone transmits RF signals (most common)

**Flow:**
```
1. BlueHalo RF detects drone (6-20 km)
   ↓ Provides: Bearing, pilot position, drone model
   
2. RWS slews RADAR to search direction
   ↓
   
3. Echoguard Radar acquires drone (1-2 km)
   ↓ Provides: Precise Az/El/Range
   
4. RWS slews OPTICS to radar track (with 20° offset)
   ↓
   
5. Visual tracking takes over
```

**Characteristics:**
- ✅ Early warning from RF (long range)
- ✅ Precise tracking from radar
- ✅ Pilot location known
- ✅ Drone model identified

---

### **Mode 2: RF-Silent Mode (Radar-Only)** 🆕

**Scenario:** Drone does NOT transmit RF signals

**Examples:**
- Autonomous drones (no RC link)
- Wired drones
- RF-hardened military drones
- Drones with RF disabled

**Flow:**
```
1. No RF detection (drone is RF-silent)
   ↓
   
2. Echoguard Radar detects drone (1-2 km)
   ↓ First radar detection with no recent RF
   
3. RF-SILENT MODE ACTIVATED
   ↓
   
4. RWS continuously slews OPTICS to radar position
   ↓ Updates every radar frame (10 Hz)
   ↓ Applies 20° elevation offset
   
5. Optics acquire visual lock
   ↓
   
6. Visual tracking takes over
   ↓
   
7. Radar updates stop (optical lock confirmed)
```

**Characteristics:**
- ⚠️ No early warning (radar range only)
- ⚠️ No pilot location
- ⚠️ No drone model
- ✅ Continuous optics updates until lock
- ✅ Automatic mode detection

---

## 🔧 How RF-Silent Mode Works

### **Activation Trigger**

RF-Silent mode activates when:
1. **Radar detects a drone** (track with `source=RADAR`)
2. **No RF detections** for >10 seconds

**Logic:**
```python
time_since_rf = current_time - last_rf_time

if time_since_rf > 10.0:  # 10 seconds
    # Activate RF-silent mode
    rf_silent_mode = True
```

### **Continuous Optics Updates**

In RF-silent mode, the system:

1. **Receives radar track** (10 Hz update rate)
2. **Calculates optics position** (with 20° offset)
3. **Sends slew command** to optics
4. **Repeats** until optical lock

**Every radar frame:**
```
[RWSDriver] 🔴 RF-SILENT TRACKING → Updating OPTICS
[RWSDriver]   Target: Az=45.2°, El=-5.3°
[RWSDriver]   Delta: ΔAz=0.8°, ΔEl=0.3°
[RWSDriver]   Range: 850m, UAV Prob: 0.85
```

### **Optical Lock Detection**

The system detects optical lock when:

**Option 1: Position Convergence**
- Azimuth delta < 0.5°
- Elevation delta < 0.5°
- Suggests optics are on target

**Option 2: External Confirmation** (Recommended)
- Tracking software confirms visual lock
- Calls `rws.set_optical_lock(True)`

```python
# External tracking system confirms lock
rws.set_optical_lock(True)

# Output:
# [RWSDriver] ✅ OPTICAL LOCK CONFIRMED by tracking system
# [RWSDriver]   Stopping radar-based optics updates
```

### **Lock Maintenance**

Once optical lock is confirmed:
- ✅ Radar updates to optics **stop**
- ✅ Visual tracking takes over
- ✅ Radar continues tracking (for situational awareness)

If optical lock is lost:
```python
rws.set_optical_lock(False)

# Output:
# [RWSDriver] ⚠️  OPTICAL LOCK LOST
# [RWSDriver]   Resuming radar-based optics updates
```

---

## 📊 Mode Comparison

| Feature | Normal Mode | RF-Silent Mode | Manual Mode |
|---------|-------------|----------------|-------------|
| **Detection Range** | 6-20 km (RF) | 1-2 km (Radar) | N/A |
| **Early Warning** | ✅ Yes | ❌ No | N/A |
| **Pilot Location** | ✅ Yes | ❌ No | N/A |
| **Drone Model** | ✅ Yes | ❌ No | N/A |
| **Optics Updates** | Once | Continuous | Manual |
| **Activation** | Automatic | Automatic | Operator |
| **Use Case** | Standard drones | RF-silent drones | Override |

---

## 🎮 Operational Examples

### **Example 1: DJI Mavic (Normal Mode)**

```
[RFDriver] Precision detection: Mavic Pro, Serial: 08RDD8K00100E6
[RFDriver] Pilot position: 39.2335, -77.5485
[RWSDriver] RF Detection → Slewing RADAR to Az=45.0°, El=0.0°

[RadarDriver] Track detected: ID=13, Az=45.2°, El=8.5°, Range=850m
[RWSDriver] Radar Detection → Slewing OPTICS to Az=45.2°, El=-11.5°

[TrackingSystem] Visual lock acquired
[RWSDriver] ✅ OPTICAL LOCK CONFIRMED by tracking system
```

**Result:** 
- ✅ Early detection at 15 km (RF)
- ✅ Pilot location known
- ✅ Drone identified (Mavic Pro)
- ✅ Single optics slew command

---

### **Example 2: Autonomous Drone (RF-Silent Mode)**

```
[RadarDriver] Track detected: ID=42, Az=120.5°, El=12.3°, Range=1200m
[RWSDriver] ⚠️  RF-SILENT MODE ACTIVATED
[RWSDriver]   No RF detections for 15.2s
[RWSDriver]   Radar-only tracking enabled

[RWSDriver] 🔴 RF-SILENT TRACKING → Updating OPTICS
[RWSDriver]   Target: Az=120.5°, El=-7.7°
[RWSDriver]   Delta: ΔAz=2.3°, ΔEl=1.8°
[RWSDriver]   Range: 1200m, UAV Prob: 0.82

[RWSDriver] 🔴 RF-SILENT TRACKING → Updating OPTICS
[RWSDriver]   Target: Az=121.2°, El=-7.2°
[RWSDriver]   Delta: ΔAz=0.7°, ΔEl=0.5°
[RWSDriver]   Range: 1150m, UAV Prob: 0.85

[RWSDriver] 🔴 RF-SILENT TRACKING → Updating OPTICS
[RWSDriver]   Target: Az=121.5°, El=-7.0°
[RWSDriver]   Delta: ΔAz=0.3°, ΔEl=0.2°
[RWSDriver]   Range: 1100m, UAV Prob: 0.88

[RWSDriver] 🎯 OPTICAL LOCK ACHIEVED (ΔAz=0.28°, ΔEl=0.15°)
[RWSDriver]   Optics should now be tracking visually

[TrackingSystem] Visual lock confirmed
[RWSDriver] ✅ OPTICAL LOCK CONFIRMED by tracking system
[RWSDriver]   Stopping radar-based optics updates
```

**Result:**
- ⚠️ No early warning (radar range only)
- ⚠️ No pilot location
- ⚠️ Unknown drone model
- ✅ Continuous updates until lock
- ✅ Successful visual acquisition

---

## 🔧 Configuration

### **Timeout Settings**

```python
# In rws_production.py

# RF detection timeout (seconds without RF = RF-silent mode)
self.rf_detection_timeout = 10.0  # Default: 10 seconds

# Optical lock timeout (seconds without radar = assume lock)
self.optical_lock_timeout = 5.0   # Default: 5 seconds
```

**Tuning Recommendations:**

| Environment | RF Timeout | Optical Timeout |
|-------------|------------|-----------------|
| **Urban** | 15 seconds | 3 seconds |
| **Rural** | 10 seconds | 5 seconds |
| **Desert** | 5 seconds | 7 seconds |
| **Testing** | 5 seconds | 2 seconds |

### **Lock Detection Threshold**

```python
# Position convergence threshold for optical lock
if delta_az < 0.5 and delta_el < 0.5:
    # Assume optical lock
```

**Tuning:**
- **Tight threshold** (0.3°): Fewer false locks, slower acquisition
- **Loose threshold** (1.0°): Faster acquisition, more false locks
- **Recommended**: 0.5° (good balance)

---

## 🧪 Testing RF-Silent Mode

### **Test 1: Simulate RF-Silent Drone**

```python
from src.drivers.radar_production import RadarDriverProduction
from src.drivers.rws_production import RWSDriverProduction

# Start radar (no RF driver)
radar = RadarDriverProduction(host="192.168.1.100", port=23000)
radar.start()

# Start RWS
rws = RWSDriverProduction(host="192.168.1.101", port=5000)
rws.start()

# Wait for radar detection
# RF-silent mode should activate after 10 seconds
```

**Expected Output:**
```
[RadarDriver] Track detected: ID=13, Az=45.2°, El=8.5°
[RWSDriver] ⚠️  RF-SILENT MODE ACTIVATED
[RWSDriver] 🔴 RF-SILENT TRACKING → Updating OPTICS
```

### **Test 2: Optical Lock Confirmation**

```python
# Simulate optical lock from tracking system
rws.set_optical_lock(True)

# Expected: Radar updates to optics stop
```

### **Test 3: Lock Loss Recovery**

```python
# Simulate lock loss
rws.set_optical_lock(False)

# Expected: Radar updates resume
```

---

## 🎯 Integration with Tracking Software

Your drone tracking software should:

### **1. Monitor Optical Lock Status**

```python
def on_visual_lock_acquired():
    """Called when tracking software locks onto target"""
    rws.set_optical_lock(True)

def on_visual_lock_lost():
    """Called when tracking software loses target"""
    rws.set_optical_lock(False)
```

### **2. Provide Lock Confidence**

```python
def update_tracking_confidence(confidence: float):
    """Update lock confidence (0.0 - 1.0)"""
    if confidence > 0.8:
        rws.set_optical_lock(True)
    elif confidence < 0.3:
        rws.set_optical_lock(False)
```

### **3. Handle Lock Transitions**

```python
class TrackingSystem:
    def __init__(self, rws):
        self.rws = rws
        self.lock_confidence = 0.0
        self.lock_threshold = 0.8
        self.unlock_threshold = 0.3
    
    def update(self, frame):
        # Your tracking algorithm
        confidence = self.calculate_confidence(frame)
        
        # Hysteresis for lock/unlock
        if confidence > self.lock_threshold:
            self.rws.set_optical_lock(True)
        elif confidence < self.unlock_threshold:
            self.rws.set_optical_lock(False)
```

---

## 📋 Operational Checklist

### **Before Deployment:**
- [ ] Configure RF detection timeout (10s default)
- [ ] Configure optical lock threshold (0.5° default)
- [ ] Test RF-silent mode activation
- [ ] Verify continuous optics updates
- [ ] Test optical lock confirmation
- [ ] Test lock loss recovery

### **During Operation:**
- [ ] Monitor for RF-silent mode activation
- [ ] Verify optics are updating continuously
- [ ] Confirm optical lock when achieved
- [ ] Watch for lock loss and recovery

### **After Engagement:**
- [ ] Review mode transitions
- [ ] Check lock acquisition time
- [ ] Analyze false lock rate
- [ ] Tune thresholds if needed

---

## 🚨 Troubleshooting

### **RF-Silent Mode Not Activating**

**Symptom:** Radar detects but RF-silent mode doesn't activate

**Causes:**
1. RF driver is still detecting (check RF timeout)
2. Radar tracks are too old
3. Mode detection logic disabled

**Fix:**
```python
# Check RF timeout setting
print(f"RF timeout: {rws.rf_detection_timeout}s")

# Reduce timeout for testing
rws.rf_detection_timeout = 5.0
```

### **Optics Not Updating**

**Symptom:** RF-silent mode active but optics not moving

**Causes:**
1. Optical lock already confirmed
2. UDP packets not being sent
3. RWS not receiving commands

**Fix:**
```python
# Check optical lock status
print(f"Optical lock: {rws.optical_lock}")

# Reset lock if stuck
rws.set_optical_lock(False)

# Check UDP socket
# Monitor with: tcpdump -i any port 5000
```

### **False Optical Locks**

**Symptom:** Lock confirmed but optics not actually tracking

**Causes:**
1. Threshold too loose (>1.0°)
2. Position convergence too fast
3. External confirmation not working

**Fix:**
```python
# Tighten threshold
# In _handle_rf_silent_tracking():
if delta_az < 0.3 and delta_el < 0.3:  # Tighter
    # Assume lock
```

---

## 🎉 Summary

### **RF-Silent Mode Features:**

✅ **Automatic Detection** - Activates when no RF for >10s  
✅ **Continuous Updates** - Optics updated every radar frame  
✅ **20° Offset** - Automatic elevation compensation  
✅ **Lock Detection** - Position convergence or external confirmation  
✅ **Lock Maintenance** - Stops updates when locked  
✅ **Recovery** - Resumes updates if lock lost  

### **Use Cases:**

🎯 **Autonomous drones** (no RC link)  
🎯 **Wired drones** (fiber optic control)  
🎯 **Military drones** (RF-hardened)  
🎯 **RF-disabled drones** (intentionally silent)  
🎯 **Backup mode** (if RF sensor fails)  

### **Benefits:**

✅ **No operator intervention** required  
✅ **Seamless mode switching**  
✅ **Robust tracking** even without RF  
✅ **Automatic recovery** from lock loss  

---

**Your system now handles ALL drone types - RF-transmitting AND RF-silent! 🚀**

---

*Implementation Date: November 25, 2024*  
*Status: ✅ RF-Silent Mode Active*
