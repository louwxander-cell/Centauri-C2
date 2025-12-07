# Holybro H-RTK Mosaic-H - Overview & Specifications

## Overview

The **Holybro mosaic-H** is a cutting-edge RTK GPS module that harnesses the power of Septentrio's elite mosaic-H GNSS receiver. It comes with an IST8310 magnetometer, two high-performance antennas, and an aluminum CNC enclosure. It is packed with versatile features such as effortless configuration, spectrum analysis, data logging, and post-processing for a wide range of applications.

With its **dual-antenna input**, mosaic-H can provide compass-less YAW information to the controller (commonly called GPS Heading or Moving Baseline Yaw). By employing GPS as the yaw source instead of a traditional compass it eliminates the inaccuracies caused by magnetic interference from vehicle motors, electrical systems, and environmental sources like metallic structures or power lines, ensuring precise yaw reports to the controller and enhancing overall navigation reliability and performance in challenging environments.

Septentrio's mosaic-H GNSS receiver module boasts a suite of proprietary technologies that set it apart from the competition. Septentrio's [AIM+ (Advanced Interference Mitigation) technology](https://www.septentrio.com/en/learn-more/advanced-positioning-technology/aim-jamming-protection) safeguards against intentional and unintentional jamming sources, ensuring consistent and reliable performance even in challenging RF environments.

Septentrio's [LOCK+ technology](https://www.septentrio.com/en/learn-more/Advanced-positioning-technology/gnss-technology/robust-gnss-signal-tracking) ensures optimal tracking even under rapid antenna displacement in the event of high vibrations or shocks, maintaining high accuracy and stable operation in high-dynamic situations. It is ideal for demanding applications such as UAVs and robotics. Furthermore, Septentrio's advanced [RAIM+ (Receiver Autonomous Integrity Monitoring) algorithm](https://www.septentrio.com/en/receiver-autonomous-integrity-monitoring) delivers unmatched integrity and reliability, providing a safety net for mission-critical applications.

---

## Features

* ✅ Advanced anti-jamming, anti-spoofing solutions with [AIM+ technology](https://www.septentrio.com/en/learn-more/advanced-positioning-technology/aim-jamming-protection) & [OSNMA](https://www.septentrio.com/en/learn-more/insights/osnma-latest-gnss-anti-spoofing-security)
* ✅ Dual antenna support for moving baseline yaw (GPS Heading) with just one GPS module
* ✅ All-in-view satellite tracking: multi-constellation, multi-frequency (Supports L1/L2/E5)
* ✅ Best-in-class RTK performance
* ✅ Integrated magnetometer (IST8310) for backup compass
* ✅ High-performance antennas included (2x)
* ✅ Aluminum CNC enclosure for rugged environments
* ✅ USB Type-C and dual UART interfaces
* ✅ On-board data logging with SD card support
* ✅ Web-based configuration interface

---

## Technical Specifications

### Product Information

| Parameter | Value |
|-----------|-------|
| **Product** | Holybro H-RTK Mosaic-H |
| **GNSS Receiver** | Septentrio mosaic-H |
| **Magnetometer** | IST8310 |
| **Enclosure** | Aluminum CNC |

### Application Modes

* **Rover** - Mobile RTK receiver
* **Moving Baseline Rover** - Dual-antenna heading
* **Base Station** - RTK corrections provider
* **PPK** - Post-processed kinematic

---

### GNSS Constellation Support

| Constellation | Frequencies |
|--------------|-------------|
| **GPS** | L1, L2 |
| **Galileo** | E1, E5b |
| **GLONASS** | L1, L2 |
| **BeiDou** | B1, B2, B3 |
| **QZSS** | L1C/A, L1C/B, L2 |
| **SBAS** | EGNOS, WAAS, GAGAN, MSAS, SDCM (L1) |

**Multi-frequency support:** L1/L2/E5 for enhanced accuracy and multipath rejection

---

### RTK Performance

| Parameter | Specification |
|-----------|---------------|
| **Horizontal Accuracy** | 0.6 cm + 0.5 ppm |
| **Vertical Accuracy** | 1.0 cm + 1 ppm |

---

### Positioning Accuracy by Mode

| Mode | Horizontal | Vertical |
|------|-----------|----------|
| **Standalone** | 1.2 m | 1.9 m |
| **SBAS** | 0.6 m | 0.8 m |
| **DGNSS** | 0.4 m | 0.7 m |
| **RTK** | 0.6 cm + 0.5 ppm | 1.0 cm + 1 ppm |

---

### GNSS Attitude Accuracy (Dual-Antenna)

| Antenna Separation | Heading | Pitch/Roll |
|-------------------|---------|-----------|
| **1 m** | 0.15° | 0.25° |
| **5 m** | 0.03° | 0.05° |

**Note:** Longer baseline = better heading accuracy. For TriAD C2, 1m baseline is recommended.

---

### Time-To-First Fix (TTFF)

| Condition | Time |
|-----------|------|
| **Cold Start** | ≤ 45 seconds |
| **Hot Start** | ≤ 20 seconds |
| **Re-acquisition** | 1 second |

---

### Performance Metrics

| Parameter | Specification |
|-----------|---------------|
| **Latency** | < 10 ms |
| **Time Precision (xPPS)** | 5 ns |
| **Event Accuracy** | < 20 ns |

---

### Update Rates

| Mode | Maximum Update Rate |
|------|-------------------|
| **Measurements Only** | 100 Hz |
| **Standalone, SBAS, DGPS + Attitude** | 50 Hz |
| **RTK + Attitude** | 20 Hz |

**For TriAD C2:** 5-10 Hz recommended for optimal balance of accuracy and system load.

---

### Antennas

| Parameter | Specification |
|-----------|---------------|
| **Type** | High-performance GNSS (2x included) |
| **Connection** | SMA male (board has SMA female) |
| **Peak Gain** | 2 dBi (MAX) |
| **LNA Gain** | 33 ± 2 dB |
| **Diameter** | 40 mm |
| **Height** | 76 mm |

---

### Interfaces & Connections

#### Ports

| Port | Type | Connector | Default Use |
|------|------|-----------|-------------|
| **Port 1** | USB Type-C | USB-C | Primary data/power/config |
| **Port 2** | UART1 | GH1.25 10-pin | Secondary telemetry |
| **Port 3** | UART2 | GH1.25 6-pin | Optional serial |

#### Antenna Connections

* **Board:** 2x SMA female
* **Antenna:** SMA male
* **Labeling:** ANT1 (primary), ANT2 (secondary)

---

### Buttons & Controls

| Button | Function |
|--------|----------|
| **LOG BUTTON** | Short press: Start/stop recording<br>Long press: Mount/unmount SD card |
| **SAFETY SWITCH** | Press and hold: Unlock/lock flight controller |

---

### Communication Settings

| Parameter | Default | Range |
|-----------|---------|-------|
| **Baud Rate** | 230400 | Adjustable |
| **Update Rate** | 5 Hz | Up to 100 Hz |
| **Protocol** | NMEA 0183 / SBF | Configurable |

**For TriAD C2:** 115200 baud, 5-10 Hz, NMEA 0183

---

### Power Specifications

| Parameter | Specification |
|-----------|---------------|
| **Operating Voltage** | 4.75V - 5.25V |
| **Power Consumption (Typical)** | 0.6 W |
| **Power Consumption (Maximum)** | 1.1 W |

**Note:** Can be powered via USB Type-C or external power supply.

---

### Environmental Specifications

| Parameter | Range |
|-----------|-------|
| **Operating Temperature** | -40°C to +85°C |
| **Storage Temperature** | -40°C to +85°C |

**Rugged design** suitable for harsh C-UAS deployment environments.

---

### Physical Specifications

#### Board Dimensions
* **Length:** 71.8 mm
* **Width:** 42.7 mm
* **Height:** 13.3 mm

#### Weight
* **Board Only:** 54.5 g (without antennas)
* **Complete System:** ~150 g (with antennas and cables)

---

## Advanced Technologies

### AIM+ (Advanced Interference Mitigation)

The most advanced **anti-jamming and anti-spoofing** on-board interference mitigation technology on the market.

**Protects Against:**
* Narrow-band jammers
* Wide-band jammers
* Chirp jammers
* Spoofing attacks (with OSNMA)

**Benefits:**
* Maintains positioning in high-interference environments
* Critical for military/security applications
* Automatic detection and mitigation

[Learn more about AIM+](https://www.septentrio.com/en/advanced-interference-monitoring-mitigation-aim)

---

### LOCK+ (Robust Tracking)

Ensures optimal tracking even under **rapid antenna displacement** during high vibrations or shocks.

**Features:**
* Maintains lock during high dynamics
* Ideal for UAVs and robotics
* High-vibration tolerance
* Shock-resistant tracking

**Benefits:**
* Stable operation in demanding conditions
* Reduced signal loss
* Better performance on mobile platforms

[Learn more about LOCK+](https://www.septentrio.com/en/lock-robust-tracking-under-rapid-signal-changes)

---

### APME+ (Multipath Mitigation)

Advanced **multipath mitigation** technology to disentangle direct signals from those reflected by nearby structures.

**Features:**
* Distinguishes direct vs. reflected signals
* Reduces urban canyon errors
* Better performance near buildings/structures

**Benefits:**
* More accurate positioning in complex environments
* Essential for C-UAS in urban deployments
* Improved reliability

[Learn more about APME+](https://www.septentrio.com/en/apme-multipath-mitigation-technology)

---

### IONO+ (Ionospheric Protection)

Provides advanced protection against **ionospheric scintillation**.

**Features:**
* Monitors ionospheric conditions
* Adaptive tracking strategies
* Scintillation mitigation

**Benefits:**
* Reliable positioning during solar events
* Better performance at high latitudes
* Reduced atmospheric errors

[Learn more about IONO+](https://www.septentrio.com/en/iono-ionospheric-scintillation-monitoring)

---

### RAIM+ (Integrity Monitoring)

**Receiver Autonomous Integrity Monitoring** delivers unmatched integrity and reliability.

**Features:**
* Automatic fault detection
* Satellite health monitoring
* Position integrity assessment

**Benefits:**
* Safety net for mission-critical applications
* Early warning of degraded accuracy
* Enhanced reliability

[Learn more about RAIM+](https://www.septentrio.com/en/receiver-autonomous-integrity-monitoring)

---

### OSNMA (Open Service Navigation Message Authentication)

Galileo's **anti-spoofing** security feature supported by mosaic-H.

**Features:**
* Authentication of GNSS signals
* Spoofing detection
* Secure positioning

**Benefits:**
* Protection against spoofing attacks
* Enhanced security for critical applications
* Future-proof technology

[Learn more about OSNMA](https://www.septentrio.com/en/learn-more/insights/osnma-latest-gnss-anti-spoofing-security)

---

## TriAD C2 Integration Summary

### Why This GPS is Excellent for C-UAS

✅ **Dual-Antenna Heading** - True heading without motion (critical for stationary guard posts)  
✅ **Anti-Jamming** - AIM+ protects against hostile RF interference  
✅ **High Accuracy** - RTK capable for precise threat localization  
✅ **Multi-GNSS** - More satellites = better availability  
✅ **Low Latency** - <10ms for real-time threat response  
✅ **Rugged** - Designed for harsh environments  

### Key Integration Points

| Feature | TriAD C2 Use Case |
|---------|-------------------|
| **Dual-Antenna** | Ownship heading for bearing calculations |
| **High Accuracy** | Precise threat geo-referencing |
| **Anti-Jamming** | Reliability in contested environments |
| **Low Latency** | Real-time track updates |
| **Multi-GNSS** | Availability in urban/complex terrain |

---

## Next Steps

1. **Read QUICKSTART.md** - 30-minute setup guide
2. **Follow INTEGRATION_GUIDE.md** - Complete integration steps
3. **Test Hardware** - Use `/test_gps_connection.py`
4. **Configure** - Access web UI at `http://192.168.3.1`

---

## References

**Manufacturer Resources:**
* [Holybro H-RTK Mosaic-H Product Page](https://holybro.com/products/h-rtk-mosaic-h)
* [Septentrio mosaic-H Documentation](https://www.septentrio.com/en/support/mosaic/mosaic-h)
* [Septentrio Technology Overview](https://www.septentrio.com/en/learn-more/advanced-positioning-technology)

**TriAD C2 Resources:**
* Integration Guide: `INTEGRATION_GUIDE.md`
* Quick Start: `QUICKSTART.md`
* Test Script: `/test_gps_connection.py`

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2025  
**Status:** Ready for Integration
