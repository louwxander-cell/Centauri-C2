# Septentrio Mosaic-H Dual-Antenna Heading Setup

**Mission Critical:** Enable true heading from dual-antenna configuration

---

## **Current Status**

From diagnostic (`diagnose_gps_heading.py`):

- ✅ **Position Fix:** Working (17 satellites!)
- ✅ **HDT Output:** Configured and transmitting
- ✗ **Heading Data:** EMPTY - `$GNHDT,,T*05`

**Root Cause:** Attitude determination (dual-antenna mode) not enabled in GPS.

---

## **Physical Setup Requirements**

### **1. Antenna Placement** ⚠️ **CRITICAL**

```
     ┌─────────────────┐
     │   Mosaic-H GPS   │
     └────────┬─────────┘
              │
       ┌──────┴──────┐
       │             │
    ANT1          ANT2
   (Main)        (Aux)
     🔴            🔴
     │             │
     └─────1.0m────┘
   
   FORWARD →
```

**Requirements:**
- **Baseline:** ≥ 1.0 meters between antennas
- **Alignment:** Antennas in straight line
- **Orientation:** ANT1 forward, ANT2 aft (or side-by-side)
- **Height:** Same height (horizontal plane)
- **Sky View:** Both antennas must see sky clearly
- **NO obstructions:** Trees, buildings, vehicle body

### **2. Connection Verification**

Check GPS receiver ports:
- **ANT1 (Main):** Primary antenna - MUST be connected
- **ANT2 (Aux):** Secondary antenna - MUST be connected
- **Both connectors:** Tight and secure

---

## **Software Configuration**

### **Option A: Web Interface** (RECOMMENDED)

#### **Step 1: Connect via Ethernet**

1. Connect GPS to computer via Ethernet cable
2. GPS default IP: `192.168.3.1`
3. Configure computer's Ethernet adapter:
   - IP: `192.168.3.100`
   - Netmask: `255.255.255.0`

#### **Step 2: Access Web Interface**

1. Open browser: http://192.168.3.1
2. No username/password required
3. You should see Septentrio RxControl interface

#### **Step 3: Enable Attitude Determination**

Navigate through web interface:

```
1. Click: "Receiver" tab
2. Click: "Attitude" section
3. Settings to configure:

   ┌─────────────────────────────────────┐
   │ Attitude Determination              │
   ├─────────────────────────────────────┤
   │ □ Enable: [✓] CHECK THIS BOX       │
   │                                      │
   │ Mode: [Multi-Antenna ▼]            │
   │                                      │
   │ Antenna Configuration:               │
   │   Main:  ANT1                        │
   │   Aux1:  ANT2 [✓] Enable            │
   │                                      │
   │ Baseline Vector (meters):            │
   │   X (Forward): [1.0    ]            │
   │   Y (Right):   [0.0    ]            │
   │   Z (Up):      [0.0    ]            │
   │                                      │
   │ Orientation Offset:                  │
   │   Heading: [0.0  ] degrees          │
   │   Pitch:   [0.0  ] degrees          │
   │   Roll:    [0.0  ] degrees          │
   └─────────────────────────────────────┘

4. Click: "Apply" button
5. Click: "Save Configuration" (top menu)
```

**Important:** Adjust baseline X/Y/Z to match your actual antenna positions:
- **X (Forward):** Distance along forward axis (1.0m typical)
- **Y (Right):** Distance along right axis (0.0 if inline)
- **Z (Up):** Height difference (0.0 if same height)

#### **Step 4: Verify NMEA Output**

```
1. Click: "Communication" tab
2. Click: "NMEA Output" section
3. Select: "COM1" (USB serial)
4. Enable these sentences at 1-5 Hz:
   [✓] GGA - Position
   [✓] HDT - True Heading
   [✓] VTG - Velocity
   [✓] RMC - Recommended Minimum
5. Click: "Apply"
6. Click: "Save Configuration"
```

---

### **Option B: Serial Commands** (Advanced)

If web interface unavailable, use serial commands via Python:

```python
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem38382103', 115200)

# Commands (Septentrio ASCII format)
commands = [
    "setAttitudeMode, MultiAntenna",
    "setAttitudeOffset, 1.0, 0.0, 0.0",  # 1m forward baseline
    "setAntennaPort, Aux1, GPS",
    "saveConfiguration"
]

for cmd in commands:
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(0.5)

ser.close()
```

---

## **Verification Steps**

### **1. Wait for Heading Lock**

After configuration:
- **Time required:** 5-15 minutes
- **Monitor EVT LED:**
  - RED blinking → Still acquiring
  - OFF or GREEN → Heading locked ✓

### **2. Run Diagnostic**

```bash
python3 diagnose_gps_heading.py
```

**Success looks like:**
```
HDT Sample:
  $GPHDT,137.2,T*2E  ← Heading present!
  $GPHDT,137.3,T*2F
  $GPHDT,137.2,T*2E

Current Heading: 137.2° ✓
```

### **3. Test Integration**

```bash
python3 test_gps_integration.py
```

Should show:
```
Heading: 137.2° ✓
Heading Available: True ✓
```

---

## **Troubleshooting**

### **Problem: Still no heading after 15 minutes**

#### **Solution 1: Verify Antenna Connections**

1. Power off GPS
2. Check ANT1 and ANT2 connectors are TIGHT
3. Try swapping ANT1 ↔ ANT2
4. Power on GPS
5. Wait 10 minutes

#### **Solution 2: Check Baseline Configuration**

Measure actual antenna distance:
- **Too short (<0.5m):** Move antennas further apart
- **Too long (>2.0m):** Update baseline in GPS config
- **Not straight:** Align antennas in line

#### **Solution 3: Check Satellite Visibility**

Both antennas need clear sky view:
- Remove any obstructions
- Place antennas on roof/high point
- Avoid multipath (reflections from metal surfaces)

#### **Solution 4: Factory Reset**

If all else fails:
1. Web interface → Tools → Factory Reset
2. Re-run full configuration
3. Wait 30 minutes for complete initialization

---

## **Alternative: Use COG (Course Over Ground)**

If dual-antenna heading cannot be achieved, use GPS course over ground (requires movement):

**Pros:**
- Works with single antenna
- No baseline configuration needed

**Cons:**
- Only accurate when moving (>2 m/s)
- No heading when stationary
- Less accurate than dual-antenna

**Implementation:** VTG sentence provides COG
```
$GPVTG,137.2,T,125.4,M,1.5,N,2.8,K*XX
       ↑
    COG (True)
```

---

## **Mission Critical Checklist**

Before declaring "heading operational":

- [ ] Both antennas connected and secure
- [ ] Baseline ≥ 1.0 meters
- [ ] Clear sky view for both antennas
- [ ] Attitude determination enabled in GPS
- [ ] Baseline vector configured correctly
- [ ] NMEA HDT output enabled
- [ ] Waited ≥ 15 minutes after config
- [ ] EVT LED off or green
- [ ] `diagnose_gps_heading.py` shows heading data
- [ ] TriAD C2 displays ownship heading

---

## **Quick Reference Commands**

```bash
# Full diagnostic
python3 diagnose_gps_heading.py

# Monitor real-time
python3 gps_quick_check.py

# Test integration
python3 test_gps_integration.py

# Reconfigure (if you have script)
python3 configure_dual_antenna.py
```

---

## **Expected Timeline**

| Step | Duration | Status |
|------|----------|--------|
| Physical setup | 10 min | ⏸️ User action |
| Web config | 5 min | ⏸️ User action |
| Position lock | 2-5 min | 🔄 Auto |
| **Heading lock** | **5-15 min** | **🔄 Auto** |
| Verification | 2 min | ⏸️ Run scripts |

**Total:** ~25-40 minutes from start to operational heading

---

**Status:** Configuration guide complete. User must access web interface or run serial configuration, then wait for heading lock.
