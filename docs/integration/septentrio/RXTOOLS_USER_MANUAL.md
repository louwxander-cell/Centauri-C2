# RxTools User Manual - Key Extracts

**Version:** 25.0.0  
**Source:** rxtools_v25.0.0_user_manual.pdf  
**Location:** `/Integration docs/Septentrio GPS/`

---

## Overview

RxTools is Septentrio's GNSS receiver configuration and monitoring software for the mosaic-H receiver.

**Note:** This document contains key extracts from the official PDF user manual relevant to TriAD C2 integration.

---

## Quick Reference

### Default Connection Settings

**USB Connection:**
- Port: `/dev/ttyACM0` (Linux), `COM#` (Windows)
- Baud Rate: 115200
- Protocol: NMEA 0183 / SBF (Septentrio Binary Format)

**Network Connection:**
- Default IP: `192.168.3.1`
- Web Interface: `http://192.168.3.1`
- NMEA TCP Port: 28784

---

## Configuration for TriAD C2

### Required Settings

**[Content to be added from PDF]**

Topics needed:
1. Dual-antenna configuration
2. NMEA output setup
3. Heading/attitude configuration
4. Update rate settings
5. RTK configuration (if applicable)

---

## Web Interface Guide

**[Screenshots and instructions to be added]**

### Accessing Web Interface
1. Connect via USB
2. Open browser: `http://192.168.3.1`
3. Navigate to configuration sections

### Key Configuration Pages
- **Communication → NMEA/SBF** - Output settings
- **Attitude → Heading Setup** - Dual-antenna mode
- **Corrections → NTRIP** - RTK corrections (optional)

---

## NMEA Configuration

### Enabling Required Sentences

**[Details to be added from manual]**

**Required for TriAD C2:**
- `$GPGGA` - Position
- `$GPRMC` - Recommended minimum
- `$GPHDT` - True heading (critical for dual-antenna)
- `$GPVTG` - Velocity

**Optional Septentrio Sentences:**
- `$PSAT,HPR` - Heading, Pitch, Roll (high precision)

---

## Dual-Antenna Setup

### Baseline Configuration

**[Instructions to be added]**

1. Measure antenna separation distance
2. Configure in web interface
3. Set orientation angle
4. Verify heading lock

---

## Troubleshooting

### Common Issues

**[To be populated from manual]**

**No Position Fix:**
- Check antenna connections
- Verify clear sky view
- Check satellite count

**No Heading Output:**
- Verify dual-antenna mode enabled
- Check baseline configuration
- Confirm both antennas connected

---

## Command Reference

### Serial Commands

**[Command list to be added]**

Example commands for configuration via serial:
```
sso, Stream1, NMEA, USB1, on
setHeadingBaseline, 1.0, 0.0
saveConfiguration, Boot
```

---

## Advanced Features

### RTK Configuration

**[RTK setup to be added]**

### Multi-GNSS Setup

**[Constellation configuration to be added]**

---

## Appendix

### Supported NMEA Sentences

**[Complete list to be added from manual]**

### Septentrio Proprietary Messages

**[SBF and PSAT sentences to be added]**

---

## References

**Official Documentation:**
- RxTools User Manual v25.0.0 (PDF)
- Release Notes v25.0.0 (PDF)
- Web: https://www.septentrio.com

**TriAD C2 Documentation:**
- Integration Guide: `INTEGRATION_GUIDE.md`
- Quick Start: `QUICKSTART.md`
- Overview: `OVERVIEW_SPECIFICATIONS.md`

---

**Status:** ⏳ Awaiting PDF content extraction  
**Last Updated:** December 2, 2025

---

## How to Populate This Document

**From the PDF user manual, extract:**
1. Chapter on NMEA configuration
2. Dual-antenna/heading setup sections
3. Web interface screenshots
4. Command reference tables
5. Troubleshooting sections
6. Configuration examples

**Provide content as:**
- Copy/paste text from PDF
- Screenshots of web interface
- Command examples
- Configuration screenshots
