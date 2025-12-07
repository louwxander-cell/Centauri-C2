# GPS Integration - Quick Reference

**Hardware:** Holybro H-RTK Mosaic-H (Septentrio)  
**Type:** Dual-Antenna RTK GNSS  
**Status:** ✅ Ready for Integration

---

## 🚀 Quick Start

**First time?** Follow these steps:

1. **Read Overview** → `/docs/integration/septentrio/OVERVIEW_SPECIFICATIONS.md`
2. **Quick Setup** → `/docs/integration/septentrio/QUICKSTART.md` (30 min)
3. **Test Hardware** → `python3 test_gps_connection.py /dev/ttyACM0 115200`
4. **Full Integration** → `/docs/integration/septentrio/INTEGRATION_GUIDE.md`

---

## 📁 Documentation Location

**All GPS documentation:** `/docs/integration/septentrio/`

### Core Documents

| Document | Description |
|----------|-------------|
| **OVERVIEW_SPECIFICATIONS.md** | Hardware specs, features, technologies |
| **QUICKSTART.md** | 30-minute integration guide |
| **INTEGRATION_GUIDE.md** | Complete Septentrio-specific guide |
| **GPS_INTEGRATION_GUIDE.md** | Generic dual-antenna GPS principles |

### Quick Summary

**At-a-glance:** `/docs/integration/SEPTENTRIO_QUICK_SUMMARY.md`

---

## ⚡ Default Settings

```json
{
  "port": "/dev/ttyACM0",
  "baudrate": 115200,
  "update_rate": 5,
  "protocol": "NMEA 0183"
}
```

**Web Interface:** `http://192.168.3.1` (via USB)

---

## 🔧 Test Hardware First

**Before integration, verify hardware:**

```bash
# Install dependencies
pip install pyserial pynmea2

# Test connection
python3 test_gps_connection.py /dev/ttyACM0 115200
```

**Expected:** ✅ Position fix + ✅ True heading (HDT)

---

## 📊 Key Specifications

| Feature | Specification |
|---------|---------------|
| **Position (RTK)** | 0.6 cm + 0.5 ppm |
| **Heading (1m baseline)** | 0.15° accuracy |
| **Update Rate** | Up to 100 Hz |
| **Constellations** | GPS, GLONASS, Galileo, BeiDou |
| **Anti-Jamming** | AIM+ technology |
| **Latency** | < 10 ms |

---

## ⚠️ Common Issues

| Issue | Quick Fix |
|-------|-----------|
| No output | Check `/dev/ttyACM0`, try 115200 baud |
| No heading | Wait 60s, verify both antennas connected |
| Wrong heading | Swap ANT1 ↔ ANT2 cables |
| Permission denied | `sudo usermod -a -G dialout $USER` |

---

## 🎯 Why This GPS?

✅ **Dual-antenna heading** - No compass, no magnetic interference  
✅ **RTK capable** - cm-level accuracy for threat localization  
✅ **Anti-jamming** - AIM+ for contested environments  
✅ **Professional grade** - Septentrio mosaic-H receiver  
✅ **Multi-GNSS** - Maximum satellite availability  

**Perfect for C-UAS applications.**

---

## 📞 Support

**Manufacturer:**
- Holybro: https://holybro.com
- Septentrio: https://www.septentrio.com

**TriAD C2:**
- Documentation: `/docs/integration/septentrio/`
- Test script: `/test_gps_connection.py`
- Quick summary: `/docs/integration/SEPTENTRIO_QUICK_SUMMARY.md`

---

**Last Updated:** December 2, 2025
