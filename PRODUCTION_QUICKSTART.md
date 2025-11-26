# Production System - Quick Start Guide

## 🚀 Ready to Test with Live Hardware!

All production drivers have been implemented and are ready for testing with actual sensors.

---

## 📦 What's Been Implemented

### **✅ Production Drivers**

1. **`radar_production.py`** - Echoguard Radar
   - TCP binary protocol (BNET)
   - Vehicle-relative coordinates
   - UAV probability classification
   - 248-byte track parsing

2. **`rf_production.py`** - BlueHalo SkyView DIVR MkII
   - TLS 1.2 secure connection
   - JSON message parsing
   - GPS heading correction
   - Pilot position extraction

3. **`rws_production.py`** - Remote Weapon Station
   - UDP command protocol
   - Automatic command chain (RF→Radar→Optics)
   - 20° elevation offset
   - Separate radar/optics pointing

### **✅ Enhanced Features**

- Pilot position tracking (lat/lon)
- Drone model and serial number
- RF frequency and power
- Radar cross-section (RCS)
- UAV probability scores
- Coordinate transformations

---

## 🔧 Configuration Required

### **1. Network Addresses**

Edit `config/settings.json`:

```json
{
  "network": {
    "radar": {
      "host": "192.168.1.100",  // ← Your Echoguard IP
      "port": 23000
    },
    "rf": {
      "host": "192.168.1.217",  // ← Your SkyView IP (or default)
      "port": 59898,
      "cert_dir": "Integration docs/Bluehalo_2025-11-25_1912/ott"
    },
    "rws": {
      "host": "192.168.1.101",  // ← Your RWS IP
      "port": 5000
    }
  },
  "gps": {
    "port": "/dev/ttyUSB0",     // ← Your GPS serial port
    "baudrate": 9600
  }
}
```

### **2. Verify Certificates**

Check that BlueHalo certificates exist:
```bash
ls -la "Integration docs/Bluehalo_2025-11-25_1912/ott/"
```

Should see:
- `ca-chain.cert.pem`
- `ott.verustechnologygroup.com.cert.pem`
- `ott.verustechnologygroup.com.key.pem`

---

## 🧪 Testing Steps

### **Phase 1: Individual Driver Testing**

#### **Test Echoguard Radar**

```python
from src.drivers.radar_production import RadarDriverProduction

# Initialize
radar = RadarDriverProduction(
    host="192.168.1.100",  # Your radar IP
    port=23000
)

# Start driver
radar.start()

# Monitor console for:
# - Connection status
# - Track detections
# - Az/El/Range data
```

**Expected Output:**
```
[RadarDriver] Connecting to 192.168.1.100:23000...
[RadarDriver] Connected successfully
[RadarDriver] Track detected: ID=13, Az=45.2°, El=10.5°, Range=850m
```

#### **Test BlueHalo RF**

```python
from src.drivers.rf_production import RFDriverProduction

# Initialize
rf = RFDriverProduction(
    host="192.168.1.217",
    port=59898,
    cert_dir="Integration docs/Bluehalo_2025-11-25_1912/ott"
)

# Start driver
rf.start()

# Monitor console for:
# - TLS connection
# - Detection messages
# - Pilot positions
```

**Expected Output:**
```
[RFDriver] Connecting to 192.168.1.217:59898 via TLS...
[RFDriver] TLS connection established
[RFDriver] Detection messages enabled
[RFDriver] Precision detection: Mavic Pro, Serial: 08RDD8K00100E6
[RFDriver] Pilot position: 39.2335, -77.5485
```

#### **Test RWS**

```python
from src.drivers.rws_production import RWSDriverProduction

# Initialize
rws = RWSDriverProduction(
    host="192.168.1.101",
    port=5000
)

# Start driver
rws.start()

# Test manual slew
from src.core.bus import SignalBus
bus = SignalBus.instance()
bus.sig_slew_command.emit(45.0, 10.0)  # Az=45°, El=10°
```

**Expected Output:**
```
[RWSDriver] Manual Slew → Az=45.0°, El=10.0°
[RWSDriver] Sent RADAR slew command: Az=45.0°, El=10.0°
[RWSDriver] Sent OPTICS slew command: Az=45.0°, El=-10.0°
```

---

### **Phase 2: Integrated Testing**

#### **Full System Test**

```python
from src.drivers.radar_production import RadarDriverProduction
from src.drivers.rf_production import RFDriverProduction
from src.drivers.rws_production import RWSDriverProduction
from src.drivers.gps import GPSDriver
from src.core.bus import SignalBus

# Initialize signal bus
bus = SignalBus.instance()

# Start GPS (provides heading for RF correction)
gps = GPSDriver(port="/dev/ttyUSB0", baudrate=9600)
gps.start()

# Start RF sensor
rf = RFDriverProduction(
    host="192.168.1.217",
    port=59898,
    cert_dir="Integration docs/Bluehalo_2025-11-25_1912/ott"
)
rf.start()

# Start Radar
radar = RadarDriverProduction(
    host="192.168.1.100",
    port=23000
)
radar.start()

# Start RWS (handles command chain)
rws = RWSDriverProduction(
    host="192.168.1.101",
    port=5000
)
rws.start()

# System is now running!
# Watch for automatic command chain:
# 1. RF detects drone → RWS slews radar
# 2. Radar acquires → RWS slews optics
```

**Expected Flow:**
```
[GPSDriver] Position: 39.2335, -77.5485, Heading: 90.0°
[RFDriver] Sector detection: Sector 3, Az=112.5° (True North)
[RFDriver] Converting to vehicle-relative: Az=22.5° (vehicle)
[RWSDriver] RF Detection → Slewing RADAR to Az=22.5°, El=0.0°
[RadarDriver] Track detected: ID=13, Az=23.1°, El=8.5°, Range=850m
[RWSDriver] Radar Detection → Slewing OPTICS to Az=23.1°, El=-11.5°
```

---

## 🔍 Verification Checklist

### **Echoguard Radar**
- [ ] TCP connection established
- [ ] Binary packets received
- [ ] Tracks parsed correctly
- [ ] Azimuth is vehicle-relative (0° = forward)
- [ ] UAV probability displayed
- [ ] Velocity calculated

### **BlueHalo RF**
- [ ] TLS connection established
- [ ] JSON messages received
- [ ] Precision detections parsed (lat/lon)
- [ ] Pilot positions extracted
- [ ] Sector detections converted to azimuth
- [ ] GPS heading correction applied

### **RWS**
- [ ] UDP packets sent
- [ ] RF detections trigger radar slew
- [ ] Radar detections trigger optics slew
- [ ] 20° elevation offset applied
- [ ] Commands logged correctly

### **Integration**
- [ ] GPS provides heading updates
- [ ] RF coordinates converted to vehicle-relative
- [ ] Command chain executes automatically
- [ ] Track fusion combines RF + Radar
- [ ] Pilot positions displayed

---

## 🐛 Troubleshooting

### **Connection Issues**

**Radar won't connect:**
```bash
# Test network connectivity
ping 192.168.1.100

# Check if port is open
nc -zv 192.168.1.100 23000
```

**RF TLS error:**
```bash
# Verify certificates
openssl x509 -in "Integration docs/Bluehalo_2025-11-25_1912/ott/ott.verustechnologygroup.com.cert.pem" -text -noout

# Test TLS connection
openssl s_client -connect 192.168.1.217:59898 \
  -cert "Integration docs/Bluehalo_2025-11-25_1912/ott/ott.verustechnologygroup.com.cert.pem" \
  -key "Integration docs/Bluehalo_2025-11-25_1912/ott/ott.verustechnologygroup.com.key.pem" \
  -CAfile "Integration docs/Bluehalo_2025-11-25_1912/ott/ca-chain.cert.pem"
```

### **Coordinate Issues**

**Wrong azimuth:**
- Check GPS heading is correct
- Verify vehicle is pointed forward (0°)
- Confirm RF sector conversion formula

**Wrong elevation:**
- Verify 20° offset is applied
- Check radar mounting angle
- Confirm optics pointing

### **No Detections**

**Radar:**
- Verify radar is scanning
- Check if targets are in range
- Confirm radar is powered on

**RF:**
- Verify sensor is scanning
- Check if drones are transmitting
- Confirm frequency bands are monitored

---

## 📊 Performance Monitoring

### **Key Metrics**

```python
# Track update rate
print(f"Radar update rate: {radar_updates_per_sec} Hz")
print(f"RF update rate: {rf_updates_per_sec} Hz")

# Latency
print(f"RF → RWS latency: {rf_to_rws_latency_ms} ms")
print(f"Radar → RWS latency: {radar_to_rws_latency_ms} ms")

# Track quality
print(f"Radar confidence: {radar_confidence:.2f}")
print(f"RF confidence: {rf_confidence:.2f}")
```

### **Expected Performance**

- **Radar Update Rate**: 10 Hz
- **RF Update Rate**: 1-2 Hz
- **Command Latency**: <100 ms
- **Track Fusion**: <50 ms
- **GPS Update**: 1 Hz

---

## 🎯 Success Criteria

### **System is Working When:**

1. ✅ RF detects drone at long range (6-20 km)
2. ✅ RWS slews radar to RF bearing
3. ✅ Radar acquires drone at close range (1-2 km)
4. ✅ RWS slews optics to radar track (with 20° offset)
5. ✅ Pilot position displayed on map
6. ✅ Drone model and serial number shown
7. ✅ Track fusion combines RF + Radar data
8. ✅ All coordinates are vehicle-relative

---

## 📞 Support

### **If You Encounter Issues:**

1. Check network connectivity
2. Verify IP addresses and ports
3. Confirm certificates are valid
4. Review console logs for errors
5. Test individual drivers first
6. Validate coordinate transformations

### **Useful Commands:**

```bash
# Check network
ping <sensor_ip>
nc -zv <sensor_ip> <port>

# Monitor traffic
tcpdump -i any port 23000  # Radar
tcpdump -i any port 59898  # RF
tcpdump -i any port 5000   # RWS

# View logs
tail -f /var/log/triad_c2.log
```

---

## 🎉 Ready to Test!

All production drivers are implemented and ready. Just:

1. **Configure network addresses** in `config/settings.json`
2. **Connect to hardware** (radar, RF, RWS, GPS)
3. **Run the system** and monitor console output
4. **Verify command chain** executes correctly
5. **Test with live drones** for end-to-end validation

**Good luck with testing! 🚀**

---

*Implementation Complete: November 25, 2024*  
*Status: Ready for Hardware Testing*
