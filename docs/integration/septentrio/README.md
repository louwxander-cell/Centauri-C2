# Septentrio Mosaic-H GNSS Integration Documentation

This folder contains all integration documentation for the **Holybro H-RTK Mosaic-H** dual-antenna GNSS receiver.

---

## 📁 Document Structure

### Core Documentation
- **`OVERVIEW_SPECIFICATIONS.md`** ✅ - Product overview, features, and specifications
- **`INTEGRATION_GUIDE.md`** ✅ - Complete integration guide for TriAD C2 (Septentrio-specific)
- **`GPS_INTEGRATION_GUIDE.md`** ✅ - Generic dual-antenna GPS integration guide
- **`QUICKSTART.md`** ✅ - 30-minute quick start guide

### Reference Materials
- **`RXTOOLS_USER_MANUAL_EXTRACT.md`** ✅ - Key extracts from RxTools v25.0.0 manual (NMEA, heading, commands)
- **`RXTOOLS_RELEASE_NOTES.md`** ✅ - Release notes v25.0.0 (complete)
- **`NMEA_REFERENCE.md`** - NMEA sentence formats and examples (to be added)
- **`WEB_INTERFACE_GUIDE.md`** - Web UI configuration screenshots (to be added)
- **`DRIVER_IMPLEMENTATION.md`** - Production driver code details (to be added)

### Troubleshooting & Support (To Be Added)
- **`TROUBLESHOOTING.md`** - Common issues and solutions
- **`FAQ.md`** - Frequently asked questions
- **`CONFIGURATION_EXAMPLES.md`** - Sample configurations for different use cases

---

## 🎯 Quick Links

**First Time Setup:**
1. Start with `OVERVIEW_SPECIFICATIONS.md` - Understand the hardware
2. Follow `QUICKSTART.md` - Get running in 30 minutes
3. Reference `INTEGRATION_GUIDE.md` - Complete integration details

**Configuration:**
- Web interface: `http://192.168.3.1`
- Default baud: 115200
- Default port: `/dev/ttyACM0` (USB)

**Key Features:**
- ✅ Dual-antenna GPS heading (no compass needed)
- ✅ RTK support (cm-level accuracy)
- ✅ Multi-GNSS (GPS/GLONASS/Galileo/BeiDou)
- ✅ Advanced interference mitigation (AIM+)
- ✅ Up to 100 Hz update rate

---

## 📊 Hardware Overview

**Model:** Holybro H-RTK Mosaic-H  
**Receiver:** Septentrio mosaic-H  
**Type:** Dual-antenna RTK GNSS  
**Antennas:** 2x high-performance (included)  
**Magnetometer:** IST8310 (backup compass)  

**Connections:**
- USB Type-C (primary)
- UART1 (GH1.25 10-pin)
- UART2 (GH1.25 6-pin)
- 2x SMA antenna connectors

---

## 🚀 Integration Status

**Status:** ✅ Ready for integration  
**Driver:** Production driver available  
**Testing:** Hardware test script included  
**Documentation:** Complete

---

## 📞 Support Resources

**Septentrio:**
- Website: https://www.septentrio.com
- Support: support@septentrio.com
- Manual: https://www.septentrio.com/en/support/mosaic/mosaic-h

**Holybro:**
- Website: https://holybro.com
- Product Page: https://holybro.com/products/h-rtk-mosaic-h

**TriAD C2:**
- Main docs: `/docs/integration/`
- Test script: `/test_gps_connection.py`
- Quick start: `/GPS_QUICKSTART.md`

---

**Last Updated:** December 2, 2025
