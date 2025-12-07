# Echodyne EchoGuard Radar - Integration Status & Next Steps

**Date:** December 7, 2024  
**Status:** Ready for Hardware Connection Testing  
**GPS Integration:** Parked (heading lock pending)

---

## ✅ Current Status

### **What's Already Built**

| Component | Status | File | Notes |
|-----------|--------|------|-------|
| **Production Driver** | ✅ Complete | `src/drivers/radar_production.py` | TCP + BNET binary protocol |
| **Data Structures** | ✅ Complete | BNET format (248 bytes/track) | Azimuth, elevation, range, velocity |
| **Coordinate Transforms** | ✅ Complete | Vehicle-relative (0° = forward) | Ready for integration |
| **UAV Classification** | ✅ Complete | probabilityUAV field parsing | Auto drone detection |
| **Track Model Integration** | ✅ Complete | Maps to internal Track model | Full data flow |
| **Connection Test Script** | ✅ Complete | `test_radar_connection.py` | New - ready to use |

### **Documentation Available**

| Document | Location | Size | Purpose |
|----------|----------|------|---------|
| **ICD** | Integration docs/Echoguard/.../ICD | 201 KB | Interface specification |
| **Developer Manual** | Integration docs/Echoguard/.../Developer_Manual | 2.4 MB | Full API documentation |
| **BNET Manual** | Integration docs/Echoguard/.../BNET_Manual | 1.4 MB | Protocol specification |
| **Sample Data** | Integration docs/Echoguard/.../Sample_Data.zip | **268 MB** | Real radar tracks |
| **Quick Summary** | docs/integration/ECHOGUARD_QUICK_SUMMARY.md | - | Integration overview |

---

## 🎯 What I Need From You

### **Critical Information** (Required to proceed)

1. **Radar IP Address**
   ```
   IP: ___________________ (e.g., 192.168.1.100)
   ```

2. **Radar TCP Port**
   ```
   Port: _________________ (likely 23000 or check manual)
   ```

3. **Coordinate Reference Frame**
   - [ ] Azimuth 0° = **True North**
   - [ ] Azimuth 0° = **Magnetic North**
   - [ ] Azimuth 0° = **Radar Boresight** (Vehicle forward)
   - [ ] Azimuth 0° = **Other** (specify: _______________)

4. **Radar Installation**
   - [ ] **Fixed mount** (stationary)
   - [ ] **Vehicle mount** (mobile platform)
   - [ ] **Gimbal mount** (steerable)

5. **Network Configuration**
   - Can you ping the radar? **Yes / No**
   - Is radar on same subnet as C2 computer? **Yes / No**
   - Any firewalls between C2 and radar? **Yes / No**

---

## 🚀 Next Steps - Testing Plan

### **Phase 1: Connection Test** (15 minutes)

**Goal:** Verify radar is reachable and transmitting data

```bash
# Step 1: Test network connectivity
ping <radar_ip>

# Step 2: Test TCP connection and data stream
python3 test_radar_connection.py <radar_ip> <radar_port>

# Example:
python3 test_radar_connection.py 192.168.1.100 23000
```

**Expected Output:**
```
✓ Radar is reachable at 192.168.1.100
✓ Connected successfully!
✓ Packets: 45 | Rate: 10.2 pkt/s | Data: 2.5 KB/s
✅ SUCCESS: Radar is transmitting data!
```

**If Successful:** Proceed to Phase 2  
**If Failed:** Troubleshoot network/radar configuration

---

### **Phase 2: Data Format Validation** (30 minutes)

**Goal:** Verify BNET packet structure matches ICD

```python
# Run the production driver in test mode
from src.drivers.radar_production import RadarDriverProduction

radar = RadarDriverProduction(
    host="192.168.1.100",  # Your radar IP
    port=23000              # Your radar port
)

radar.start()

# Monitor console output for:
# - Track IDs
# - Azimuth, Elevation, Range values
# - UAV probability scores
# - Velocity vectors
```

**Expected Output:**
```
[RadarDriver] Connecting to 192.168.1.100:23000...
[RadarDriver] Connected successfully
[RadarDriver] Track detected:
   ID: 13
   Az: 45.2° | El: 10.5° | Range: 850m
   Velocity: 15.3 m/s
   UAV Probability: 0.87
   Confidence: 0.92
```

---

### **Phase 3: Integration with C2 System** (1 hour)

**Goal:** Display radar tracks in TriAD C2 UI

#### **Step 1: Configure Radar in settings.json**

Edit `/Users/xanderlouw/CascadeProjects/C2/config/settings.json`:

```json
{
  "network": {
    "radar": {
      "protocol": "TCP",
      "host": "192.168.1.100",    // ← Your radar IP
      "port": 23000               // ← Your radar port
    }
  }
}
```

#### **Step 2: Launch C2 with Radar**

```bash
# Start C2 system
python3 triad_c2.py

# Watch console for:
# - Radar connection status
# - Track detections
# - UI updates
```

#### **Step 3: Verify UI Display**

Check TriAD C2 interface shows:
- ✅ Radar tracks on tactical display
- ✅ Track list with ranges
- ✅ Azimuth/elevation data
- ✅ UAV type classification
- ✅ Velocity vectors
- ✅ Confidence scores

---

### **Phase 4: Coordinate Frame Validation** (30 minutes)

**Goal:** Ensure coordinates display correctly

**Test Method:**
1. Point radar at known direction (e.g., due North)
2. Place target drone in that direction
3. Verify displayed azimuth matches reality

**Coordinate Conversion:**
- If radar reports True North → Convert to vehicle-relative using GPS heading
- If radar reports vehicle-relative → Use directly

**Validation Checklist:**
- [ ] Azimuth 0° points vehicle forward
- [ ] Azimuth 90° points vehicle right
- [ ] Elevation positive = above horizon
- [ ] Range matches estimated distance

---

## 📊 Radar Data Structure (Quick Reference)

### **BNET Track Packet**

```
Header (28 bytes):
  - Magic identifier
  - Packet metadata
  
Track Data (248 bytes per track):
  - uint32 id               → Track ID
  - float azest             → Azimuth (degrees)
  - float elest             → Elevation (degrees)
  - float rest              → Range (meters)
  - float xest, yest, zest  → Cartesian position
  - float velxest, etc.     → Velocity vector
  - float probabilityUAV    → Drone probability (0-1)
  - float estConfidence     → Tracking confidence (0-1)
  - float estRCS            → Radar cross-section (m²)
  - ... 20+ more fields
```

### **Typical Track Values**

| Field | Typical Range | Example |
|-------|---------------|---------|
| **Azimuth** | 0-360° | 45.2° |
| **Elevation** | -10° to +60° | 12.5° |
| **Range** | 50m to 3000m | 850m |
| **Velocity** | 0-30 m/s | 15.3 m/s |
| **UAV Probability** | 0.0-1.0 | 0.87 (87% drone) |
| **Confidence** | 0.0-1.0 | 0.92 (high quality) |
| **RCS** | 0.001-1.0 m² | 0.05 m² (small drone) |

---

## 🔧 Troubleshooting Guide

### **Problem: Cannot connect to radar**

**Symptoms:**
```
✗ Connection refused
```

**Solutions:**
1. Verify radar is powered on
2. Check IP address is correct
3. Confirm port number (try 23000, 5000, 50000)
4. Test with `nc -zv <radar_ip> <port>`
5. Check firewall settings
6. Verify radar is configured to stream data

---

### **Problem: Connected but no data**

**Symptoms:**
```
✓ Connected successfully!
⚠️  WARNING: No data received
```

**Solutions:**
1. Radar may be in standby mode → Activate scanning
2. Check radar configuration → Enable track output
3. Verify streaming is enabled in radar settings
4. Check if radar needs a "start streaming" command
5. Review radar logs for errors

---

### **Problem: Wrong coordinate frame**

**Symptoms:**
- Tracks appear 90° or 180° rotated
- Azimuth doesn't match visual bearing

**Solutions:**
1. Check coordinate reference in ICD
2. Apply offset correction:
   ```python
   corrected_az = (raw_az + offset) % 360
   ```
3. Use GPS heading for True North conversion:
   ```python
   vehicle_az = (true_north_az - gps_heading) % 360
   ```

---

### **Problem: Data parsing errors**

**Symptoms:**
```
[RadarDriver] Parse error: struct.error
```

**Solutions:**
1. Verify packet size (should be 28 + N×248 bytes)
2. Check byte order (little-endian vs. big-endian)
3. Confirm struct format matches ICD
4. Extract sample data for analysis:
   ```bash
   tcpdump -i any -w radar_capture.pcap port 23000
   ```

---

## 📞 Support & Documentation

### **Key Documents** (All in `/Integration docs/Echoguard/`)

1. **ICD, EchoGuard, 700-0005-203_Rev05.pdf**
   - Official interface specification
   - Data structure definitions
   - Protocol details

2. **EchoGuard_Radar_Developer_Manual_SW16.4.0.pdf**
   - Complete API reference
   - Configuration examples
   - Troubleshooting guide

3. **BNET_11_1_5_Manual.pdf**
   - TCP protocol specification
   - Binary packet format
   - C++ API examples

4. **Sample Data (268 MB)**
   - Real radar track recordings
   - For offline testing/development
   - Binary format examples

### **Online Resources**

- Echodyne Support Portal: [Contact Echodyne]
- BNET Protocol Documentation
- Integration examples in `/docs/integration/`

---

## ✅ Integration Checklist

Before we begin, verify:

- [ ] Radar is powered on
- [ ] Radar is on network (can ping IP)
- [ ] Know radar IP address
- [ ] Know radar TCP port
- [ ] Understand coordinate reference frame
- [ ] Have network access from C2 computer
- [ ] Ready to run test scripts

Once all checked, we can:

1. **Run connection test** (5 min)
2. **Validate data format** (10 min)
3. **Integrate with C2 UI** (30 min)
4. **Test with live targets** (1 hour)

---

## 🎯 Success Criteria

**System is Working When:**

✅ TCP connection established to radar  
✅ Binary BNET packets received  
✅ Track data parsed correctly  
✅ Tracks displayed in UI  
✅ Azimuth/Elevation/Range accurate  
✅ UAV classification working  
✅ Coordinates match reality  
✅ 10 Hz update rate maintained  

---

## 📋 Ready to Begin?

**Please provide:**

1. ☐ Radar IP address: `_______________`
2. ☐ Radar port: `_______________`
3. ☐ Coordinate reference: `_______________`
4. ☐ Confirm radar is accessible: **Yes / No**

**Then we'll:**
1. Run connection test
2. Validate data stream
3. Integrate with C2
4. Test with live targets

**Estimated Time:** 2-3 hours to full integration

---

*Ready when you are! Provide the network details and we'll get started.* 🚀
