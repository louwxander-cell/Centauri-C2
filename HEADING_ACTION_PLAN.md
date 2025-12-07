# GPS Heading - MISSION CRITICAL ACTION PLAN

**Date:** December 4, 2025  
**Priority:** 🔴 **CRITICAL**  
**Status:** ⚠️ **BLOCKED - Configuration Required**

---

## **Current Situation**

### ✅ **What's Working:**
- Position fix: **EXCELLENT** (17 satellites)
- Latitude/Longitude: **ACCURATE**  
- Altitude: **1425.4m**
- Update rate: **9.8 Hz**
- HDT sentences: **CONFIGURED** and transmitting

### ✗ **What's NOT Working:**
- **Heading data: EMPTY**
- HDT output: `$GNHDT,,T*05` ← No heading value
- Dual-antenna attitude determination: **NOT ENABLED**

---

## **Root Cause**

The GPS is outputting HDT sentences but the **heading field is empty** because:

1. ❌ **Dual-antenna attitude determination is NOT enabled** in GPS firmware
2. ❓ **Unknown baseline configuration** (may not be set)
3. ❓ **Unknown antenna port assignments** (ANT1/ANT2 may be wrong)

**Serial configuration FAILED** - Septentrio uses web interface or binary SBF commands, not text ASCII commands.

---

## **IMMEDIATE ACTION REQUIRED**

### **Option 1: Web Interface Configuration** ⭐ **RECOMMENDED**

**Time Required:** 15 minutes + 10-15 min wait for heading lock

#### **Prerequisites:**
- Ethernet cable
- Computer with Ethernet port

#### **Steps:**

1. **Connect GPS via Ethernet:**
   ```
   GPS ETH port → Computer ETH port
   ```

2. **Configure computer network:**
   - IP Address: `192.168.3.100`
   - Subnet Mask: `255.255.255.0`
   - Gateway: (leave blank)

3. **Access web interface:**
   - Browser: http://192.168.3.1
   - No password required

4. **Enable Attitude Determination:**
   ```
   Navigate: Receiver → Attitude
   
   Settings:
   ✓ Enable Attitude Determination
   Mode: Multi-Antenna
   Main: ANT1
   Aux1: ANT2 (enable checkbox)
   
   Baseline Vector (meters):
   X (Forward): 1.0  ← Adjust to actual distance!
   Y (Right):   0.0
   Z (Up):      0.0
   
   Click: Apply
   Click: Save Configuration (top menu)
   ```

5. **Wait for heading lock:** 10-15 minutes

6. **Verify:**
   ```bash
   python3 diagnose_gps_heading.py
   ```

---

### **Option 2: Physical Antenna Check** ⚠️ **IF OPTION 1 FAILS**

If configuration doesn't work, the antennas may not be properly connected:

1. **Check ANT1 (Main):** Must be connected and tight
2. **Check ANT2 (Aux):** Must be connected and tight  
3. **Measure baseline:** Should be ≥ 1.0 meters apart
4. **Check placement:**
   - Both horizontal
   - Clear sky view
   - No obstructions
   - Same height

5. **Try antenna swap:** If still no heading after 20 min:
   - Power off GPS
   - Swap ANT1 ↔ ANT2 connectors
   - Power on GPS
   - Wait 10 minutes

---

### **Option 3: Alternative - Use COG** 🔄 **FALLBACK**

If dual-antenna heading cannot be achieved, use Course Over Ground (COG):

**Pros:**
- Works immediately
- No antenna configuration needed

**Cons:**
- **Only works when moving** (≥ 2 m/s)
- **No heading when stationary** ← Major limitation!
- Less accurate than true heading

**Implementation:**
- Modify GPS driver to use VTG sentence
- Extract COG (Course Over Ground) field
- Update ownship heading from COG

**Use case:** Mobile platforms (vehicles, drones)  
**NOT suitable for:** Stationary C2 stations

---

## **Verification Checklist**

After configuration, verify each step:

- [ ] Web interface accessible at http://192.168.3.1
- [ ] Attitude determination enabled
- [ ] Baseline vector configured (≥ 1.0m)
- [ ] Both ANT1 and ANT2 enabled
- [ ] Configuration saved to flash
- [ ] Waited 15+ minutes
- [ ] EVT LED off or green
- [ ] Run: `python3 diagnose_gps_heading.py`
- [ ] HDT shows heading: `$GPHDT,137.2,T*XX`
- [ ] Run: `python3 test_gps_integration.py`
- [ ] Shows: `Heading Available: True ✓`
- [ ] Run TriAD C2 and verify ownship heading updates

---

## **Timeline Estimate**

| Task | Duration | Who |
|------|----------|-----|
| Connect Ethernet | 2 min | **USER** |
| Web config | 5 min | **USER** |
| Save & reboot | 2 min | Auto |
| Wait for heading lock | 10-15 min | Auto |
| Verification | 3 min | **USER** |
| **TOTAL** | **~25 min** | |

---

## **Decision Point**

**If you cannot access web interface:**
1. Use COG (Course Over Ground) - requires movement
2. Defer heading until Ethernet access available
3. Operate with position-only (degraded capability)

**Recommendation:**  
🔴 **Access web interface ASAP** - Dual-antenna heading is mission-critical for:
- Accurate effector pointing
- Track bearing calculations
- Threat assessment geometry
- System operational capability

---

## **Commands for Monitoring**

```bash
# Real-time diagnostic (run in separate terminal)
watch -n 2 "python3 diagnose_gps_heading.py | tail -30"

# Or continuous monitor
while true; do
  python3 gps_quick_check.py
  sleep 5
done
```

Look for HDT sentences to populate:
```
BEFORE: $GNHDT,,T*05        ← Empty (no heading)
AFTER:  $GPHDT,137.2,T*2E   ← Heading present!
```

---

## **Success Criteria**

System is operational when ALL are true:

✅ Position fix (lat/lon/alt)  
✅ **Heading data present** ← **CURRENTLY FAILING**  
✅ Update rate ≥ 5 Hz  
✅ Heading updates in TriAD C2 UI  
✅ Track bearings calculate correctly  

**Current Status:** 4/5 complete (80%)  
**Blocking Issue:** Heading configuration

---

## **Contact Info (if stuck)**

**Septentrio Support:**
- Web: https://www.septentrio.com/support
- Email: support@septentrio.com
- Phone: +32 (0)16 300 845

**Mosaic-H Documentation:**
- User Manual: https://www.septentrio.com/mosaic-h
- Web Interface Guide: https://docs.septentrio.com/

---

## **Bottom Line**

**User must:**
1. Connect GPS via Ethernet
2. Access web interface (http://192.168.3.1)
3. Enable dual-antenna attitude determination
4. Set baseline vector to actual antenna distance
5. Save configuration
6. Wait 15 minutes
7. Verify heading data appears

**Without this:** System operates with position-only (degraded).  
**With this:** Full operational capability with accurate heading.

**PRIORITY:** 🔴 **CRITICAL - RESOLVE IMMEDIATELY**
