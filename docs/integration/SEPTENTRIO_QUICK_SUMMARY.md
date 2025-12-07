# Septentrio Mosaic-H - Quick Summary

**Model:** Holybro H-RTK Mosaic-H  
**Type:** Dual-Antenna RTK GNSS Receiver  
**Integration Status:** ✅ Ready  

---

## What It Does

Provides **ownship position and true heading** for the TriAD C2 system without requiring vehicle motion.

**Key Capability:** GPS-based heading (compass-less) eliminates magnetic interference issues.

---

## Key Specifications

| Feature | Specification |
|---------|---------------|
| **Position Accuracy** | RTK: 0.6 cm + 0.5 ppm |
| **Heading Accuracy** | 0.15° (1m baseline) |
| **Update Rate** | Up to 100 Hz (5-10 Hz typical) |
| **Constellations** | GPS, GLONASS, Galileo, BeiDou |
| **Anti-Jamming** | AIM+ technology |
| **Connection** | USB Type-C (115200 baud) |
| **Interface** | NMEA 0183 / Septentrio SBF |

---

## Why It Matters for C-UAS

✅ **Accurate Bearing** - True heading for threat vector calculations  
✅ **Stationary Operation** - Works without vehicle motion  
✅ **Jam Resistant** - AIM+ protects in contested environments  
✅ **High Precision** - RTK for cm-level threat localization  
✅ **Low Latency** - <10ms for real-time updates  

---

## Connection Quick Reference

**Default Settings:**
- Port: `/dev/ttyACM0` (USB)
- Baud: `115200`
- Update: `5 Hz`
- Protocol: `NMEA 0183`

**Web Interface:**
- URL: `http://192.168.3.1`
- Access: Direct via USB

**Key NMEA Sentences:**
- `$GPGGA` - Position
- `$GPHDT` - True heading (dual-antenna)
- `$GPRMC` - Speed/track
- `$PSAT,HPR` - Septentrio heading/pitch/roll

---

## Integration Path

1. **Test Hardware** → `/test_gps_connection.py`
2. **Configure** → Web UI or NMEA settings
3. **Integrate** → Follow `/docs/integration/septentrio/INTEGRATION_GUIDE.md`
4. **Verify** → Position + heading in TriAD C2

---

## Advanced Features

**RTK Correction Sources:**
- NTRIP (network corrections)
- Base station (local)
- SBAS (free, 0.6m accuracy)

**Technologies:**
- **AIM+** - Anti-jamming/anti-spoofing
- **LOCK+** - Vibration/shock resistance
- **APME+** - Multipath mitigation
- **RAIM+** - Integrity monitoring
- **OSNMA** - Galileo authentication

---

## Documentation

**Complete Docs:** `/docs/integration/septentrio/`

| Document | Purpose |
|----------|---------|
| `OVERVIEW_SPECIFICATIONS.md` | Full specs and features (Holybro model) |
| `INTEGRATION_GUIDE.md` | Septentrio-specific integration |
| `GPS_INTEGRATION_GUIDE.md` | Generic dual-antenna GPS guide |
| `QUICKSTART.md` | 30-minute setup |

**Test Script:** `/test_gps_connection.py`

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| No NMEA output | Check USB connection, verify `/dev/ttyACM0`, try 115200 baud |
| Position but no heading | Wait 30-60s for dual-antenna lock, check web UI attitude status |
| Heading 180° off | Swap ANT1 ↔ ANT2 or set orientation to 180° in web UI |
| Permission denied | Linux: `sudo usermod -a -G dialout $USER` then logout/login |
| Can't access web UI | USB creates `192.168.3.1` network, browse to that IP |

---

## Status

**Hardware:** ✅ Holybro H-RTK Mosaic-H specified  
**Driver:** ✅ Production driver template ready  
**Testing:** ✅ Test script available (`test_gps_connection.py`)  
**Documentation:** ✅ Complete (4 core docs)  

**Ready for integration!**

---

## Next Steps After Integration

1. **Verify accuracy** - Check position and heading precision
2. **Configure RTK** (optional) - For cm-level accuracy
3. **Integrate radar** - Proceed to Echoguard radar sensor
4. **Integrate RF** - Add BlueHalo SkyView RF detection

---

**See Full Documentation:** `/docs/integration/septentrio/README.md`
