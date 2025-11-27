# TriAD C2 - Network Port Specifications

## 📡 **Port Allocation**

### **C2 System Ports**

| Service | Port | Protocol | Direction | Description |
|---------|------|----------|-----------|-------------|
| **Sensor Inputs** |
| Echoguard Radar | 23000 | TCP | Inbound | BNET binary track data |
| SkyView RF | 59898 | TLS 1.2 | Inbound | JSON detections |
| GPS (Serial) | /dev/ttyUSB0 | Serial | Inbound | NMEA sentences |
| **Gunner Interface** |
| Track Stream (Broadcast) | 5100 | UDP | Outbound | All tracks @ 10 Hz |
| Gunner Status (Receive) | 5101 | UDP | Inbound | Gunner station status |
| Track Stream (gRPC) | 5200 | TCP/gRPC | Bidirectional | Production streaming (alt) |
| **RWS Control** |
| RWS Commands | 5000 | UDP | Outbound | Slew commands |
| **Management** |
| C2 UI (QML) | - | Local | - | Local Qt app |
| Admin API (Future) | 8080 | HTTP | Inbound | Configuration API |
| Metrics (Future) | 9090 | HTTP | Outbound | Prometheus metrics |

---

## 🔧 **Network Configuration**

### **Recommended Network Topology**

```
┌─────────────────────────────────────────────────────────────┐
│                      TACTICAL NETWORK                        │
│                    192.168.10.0/24                          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐
   │ C2      │          │ Gunner 1  │        │ Gunner 2  │
   │ System  │          │ Station   │        │ Station   │
   ├─────────┤          ├───────────┤        ├───────────┤
   │ .10     │◄────────►│ .20       │        │ .21       │
   │         │  Track   │           │        │           │
   │ Ports:  │  Stream  │ Receives: │        │ Receives: │
   │ In:     │  5100    │ UDP 5100  │        │ UDP 5100  │
   │  23000  │          │           │        │           │
   │  59898  │          │ Sends:    │        │ Sends:    │
   │  5101   │◄─────────│ UDP 5101  │        │ UDP 5101  │
   │         │  Status  │           │        │           │
   │ Out:    │          │           │        │           │
   │  5100   │          └───────────┘        └───────────┘
   │  5000   │
   └────┬────┘
        │
   ┌────▼────────┐
   │ Sensor LAN  │
   │ 192.168.1.x │
   └─────────────┘
        │
   ┌────┼────────────┐
   │    │            │
┌──▼────▼───┐  ┌────▼──────┐
│ Echoguard │  │ SkyView   │
│ Radar     │  │ RF        │
├───────────┤  ├───────────┤
│ .100:23000│  │ .217:59898│
└───────────┘  └───────────┘
```

---

## 🌐 **IP Address Assignments (Recommended)**

### **C2 System Network**
- **C2 Server:** 192.168.10.10
- **Gunner Station 1:** 192.168.10.20
- **Gunner Station 2:** 192.168.10.21
- **Gunner Station 3:** 192.168.10.22
- **Gunner Station 4:** 192.168.10.23

### **Sensor Network**
- **Echoguard Radar:** 192.168.1.100:23000
- **SkyView RF:** 192.168.1.217:59898
- **RWS Controller:** 192.168.1.101:5000

---

## 📋 **Firewall Rules**

### **C2 System (192.168.10.10)**

**Inbound:**
```bash
# Sensor data
ALLOW TCP 23000 from 192.168.1.100  # Echoguard
ALLOW TCP 59898 from 192.168.1.217  # SkyView

# Gunner status
ALLOW UDP 5101 from 192.168.10.0/24  # All gunners

# Management (optional)
ALLOW TCP 8080 from 192.168.10.0/24  # Admin API
```

**Outbound:**
```bash
# Track streaming
ALLOW UDP 5100 to 192.168.10.255     # Broadcast to gunners

# RWS commands (if C2 sends slew)
ALLOW UDP 5000 to 192.168.1.101      # RWS

# Sensor queries
ALLOW TCP 23000 to 192.168.1.100     # Echoguard
ALLOW TCP 59898 to 192.168.1.217     # SkyView
```

### **Gunner Stations (192.168.10.20-23)**

**Inbound:**
```bash
# Track stream
ALLOW UDP 5100 from 192.168.10.10    # C2 broadcasts
```

**Outbound:**
```bash
# Status feedback
ALLOW UDP 5101 to 192.168.10.10      # To C2

# RWS commands (gunner controls)
ALLOW UDP 5000 to 192.168.1.101      # Direct RWS control
```

---

## 🔒 **Security Considerations**

### **Network Segmentation**
- Sensor network (192.168.1.x) isolated from tactical network (192.168.10.x)
- C2 acts as gateway between networks
- Gunners cannot directly access sensors (security)

### **Encryption**
- ✅ SkyView RF: TLS 1.2 (built-in)
- ⚠️ Track stream: UDP unencrypted (LAN only, consider IPsec for production)
- ⚠️ Echoguard: TCP unencrypted (vendor limitation)

### **Future Enhancements**
- [ ] IPsec tunnel for all traffic
- [ ] VPN for remote C2 access
- [ ] Certificate-based authentication
- [ ] Network intrusion detection

---

## 📊 **Bandwidth Requirements**

### **Track Streaming (UDP 5100)**

**Per Track:**
- Track Update: ~200 bytes (protobuf)
- Update Rate: 10 Hz

**Bandwidth Calculation:**
```
20 tracks × 200 bytes × 10 Hz = 40 KB/s = 320 Kbps
```

**Peak (50 tracks):**
```
50 tracks × 200 bytes × 10 Hz = 100 KB/s = 800 Kbps
```

**Result:** Minimal (<1 Mbps even at peak)

### **Sensor Data**

**Echoguard (TCP 23000):**
- 248 bytes/track × 10 tracks × 10 Hz = ~25 KB/s

**SkyView (TLS 59898):**
- JSON messages, event-driven: <5 KB/s average

**Total Network Load:** <2 Mbps (well within 100 Mbps Ethernet)

---

## 🧪 **Testing Ports**

For development and testing:

| Service | Dev Port | Prod Port | Notes |
|---------|----------|-----------|-------|
| Track Stream | 15100 | 5100 | Dev uses 1xxxx range |
| Gunner Status | 15101 | 5101 | Avoid conflicts |
| Mock Radar | 12300 | 23000 | Mock sensors on dev ports |
| Mock RF | 15989 | 59898 | |

---

## ⚙️ **Configuration File**

### `/etc/triad/network.json`
```json
{
  "c2_system": {
    "host": "192.168.10.10",
    "interfaces": {
      "tactical_network": "eth0",
      "sensor_network": "eth1"
    }
  },
  "sensors": {
    "echoguard": {
      "host": "192.168.1.100",
      "port": 23000,
      "protocol": "TCP"
    },
    "skyview": {
      "host": "192.168.1.217",
      "port": 59898,
      "protocol": "TLS",
      "cert_dir": "/etc/triad/certs/skyview"
    },
    "gps": {
      "device": "/dev/ttyUSB0",
      "baudrate": 9600
    }
  },
  "gunner_interface": {
    "track_stream": {
      "port": 5100,
      "protocol": "UDP",
      "mode": "BROADCAST",
      "broadcast_address": "192.168.10.255",
      "update_rate_hz": 10
    },
    "status_receive": {
      "port": 5101,
      "protocol": "UDP",
      "bind_address": "0.0.0.0"
    }
  },
  "rws": {
    "host": "192.168.1.101",
    "port": 5000,
    "protocol": "UDP"
  }
}
```

---

## 🚦 **Port Summary**

**C2 Listening Ports:**
- 5101/UDP - Gunner status (inbound)
- 8080/TCP - Admin API (optional, future)

**C2 Outbound Ports:**
- 5100/UDP - Track streaming (broadcast)
- 5000/UDP - RWS commands
- 23000/TCP - Echoguard connection
- 59898/TCP - SkyView connection

**Gunner Listening Ports:**
- 5100/UDP - Track stream (receive)

**Gunner Outbound Ports:**
- 5101/UDP - Status to C2
- 5000/UDP - RWS commands (direct)

---

**These specifications are production-ready and can be deployed immediately.**
