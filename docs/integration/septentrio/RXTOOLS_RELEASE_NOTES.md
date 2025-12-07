# RxTools Release Notes v25.0.0

**Version:** 25.0.0  
**Release Date:** July 25, 2025  
**Source:** rxtools_v25.0.0_release_notes.pdf (32 pages)  
**Location:** `/Integration docs/Septentrio GPS/`

---

## Overview

RxTools v25.0.0 is Septentrio's GNSS receiver configuration and monitoring software suite. This release includes RxControl, Data Link, SBF Converter, SBF Analyzer, RxLogger, RxUpgrade, RxDownload, RxPlanner, RxAssistant, RxLauncher, SBF Tools, and APS3G Tools.

**Includes:**
- RxControl v25.0.0
- Data Link v25.0.0
- SBF Converter v25.0.0
- SBF Analyzer v25.0.0
- RxLogger v25.0.0
- RxUpgrade v25.0.0
- RxDownload v25.0.0
- RxPlanner v25.0.0
- RxAssistant v25.0.0
- RxLeverArm v25.0.0
- RxLauncher v25.0.0
- Receiver Communication SDK for C++/Qt v25.0.0
- Qt (LGPL) Version: 6.8.2
- USB Driver version: 3.0.2

---

## What's New in v25.0.0

### Major Changes

**1. Secure Communication Support (RED Compliance)**
- Updated RxTools to work with RED (Radio Equipment Directive 2014/53/EU) updated receivers
- Support for secure (TLS) IP ports
- **Impact for TriAD C2:** Ensures compatibility with latest mosaic-H firmware

**2. Dark Theme (Experimental)**
- Added dark theme option for all RxTools applications
- Useful for low-light operational environments

**3. 32-bit Support Dropped**
- RxTools now requires 64-bit operating systems only
- **Requirement:** Use 64-bit Linux or Windows

### Tools Added

**sbf2sbf Conversion Tool**
- New tool for SBF file format conversion
- Available in installation directory
- Useful for data processing and format compatibility

---

## Compatibility

### Supported Receivers

**mosaic Series:**
- ✅ **mosaic-H** (Holybro H-RTK) - Full support
- mosaic-X5
- mosaic-T
- mosaic-Sx

**Other Product Lines:**
- Altus (except APS3G for RxUpgrade)
- AsteRx
- PolaRx (except PolaRx2/2e)

**Note:** PolaRx2/2e SBF files not supported by sbf2cmd and sbf2ismr.

### Operating Systems

**Supported:**
- ✅ **Windows 10 64-bit**
- ✅ **Windows 11 64-bit**
- ✅ **Fedora 37 64-bit or later** (for Qt applications)
- ✅ **Other Linux 64-bit** (standalone tools, except bin2asc on older distributions)

**Minimum Requirements:**
- 1 GHz processor
- 1 GB RAM
- 1024×768 resolution or higher
- **Note:** Higher update rates (e.g., 10 Hz) require more CPU and memory

**Requirements for TriAD C2:**
- ✅ Meets all minimum requirements
- Recommended: Use USB connection for reliable data transfer
- At 30 Hz update rate, ensure adequate CPU headroom

---

## Installation

### Installation Files

**Delivered with Product:**
1. `RxTools_RelNote.pdf` - These release notes
2. `RxTools_Manual.pdf` - Complete user manual
3. `RxTools_25_0_0_Installer_x64.exe` - Windows installer
4. `RxTools_25_0_0_Installer_x64.bin` - Linux installer ✅

### Linux Installation

```bash
# Make installer executable
chmod +x rxtools_25_0_0_installer_x64.bin

# Run installer (requires root via sudo)
./rxtools_25_0_0_installer_x64.bin
```

**Note:** Follow prompts in installer. By default installs all components including USB drivers.

### Windows Installation

```bash
# Run installer
RxTools_25_0_0_Installer_x64.exe
```

**Custom Installation:**
- Select specific components to install
- Choose installation directory
- USB drivers included by default

### Post-Installation

**Automatic Update Check:**
- RxTools checks for newer releases on startup
- Option to download and install updates
- **Location:** Available at www.septentrio.com → Support → Software/RxTools

---

## Known Issues & Limitations

### Display Issues

**1. Large Display Fonts**
- Some UI elements may not display correctly with non-standard text scaling
- **Workaround:** Use 100% text scaling (96 DPI)

**2. High Data Rates**
- At rates >5 Hz, log only minimum required blocks
- At rates >1 Hz, use USB connection (not serial)
- Serial port CRC errors possible at high rates (PC hardware limitation)

**3. Browser Compatibility**
- "Help Topics" may not navigate correctly in some browsers
- **Workaround:** Use table of contents links directly

### Installation Issues

**Linux sudo Warning:**
- If sudo never used, may show error dialog during install
- Installation continues and succeeds
- Grant root permissions when requested

**Uninstallation on Linux:**
- If uninstall fails, installation directory may not be empty
- **Workaround:** Run uninstaller executable in installation directory before reinstalling

**Windows Driver Signing:**
- Requires Microsoft Security Advisory 3033929 for SHA-2 support
- Install Microsoft update if drivers not working

### System Requirements

**Linux Requirements:**
- GLIBCXX version 3.4.15 or higher required
- **Check version:** `strings /usr/lib/x86_64-linux-gnu/libstdc++.so.6 | grep GLIBCXX`

---

## Breaking Changes

### Version 25.0.0

**32-bit Support Removed:**
- No 32-bit builds available
- **Action Required:** Use 64-bit OS

**TLS/Secure Ports:**
- Updated for RED compliance
- Ensure receiver firmware is current

### Deprecated Features

**PolaRx2 Support:**
- PolaRx2/2e support removed from graphical tools
- SBF files from PolaRx2/2e not supported by some conversion tools

---

## Relevant Changes for TriAD C2

### NMEA Output
- ✅ **No changes** - NMEA configuration remains consistent with previous versions
- Continue using `setNMEAOutput` command for configuration
- GGA, RMC, HDT, VTG sentences fully supported

### Dual-Antenna Support
- ✅ **Full mosaic-H support** maintained
- Attitude/heading functionality unchanged
- Continue using standard baseline configuration

### Web Interface
- ✅ **Secure ports supported** (TLS) - future-proofing for secure deployments
- Dark theme available (experimental) - useful for tactical operations
- No breaking changes to configuration workflow

### Performance
- ✅ **64-bit optimizations** - better performance on modern systems
- Updated Qt framework (6.8.2) - improved stability
- USB driver v3.0.2 - enhanced reliability

### For TriAD C2 Integration
**No changes required** to existing integration approach. All documented procedures remain valid.

**Recommended:**
- Install RxTools v25.0.0 for latest features and stability
- Use 64-bit Linux for deployment
- Configure via web interface (`http://192.168.3.1`) or serial commands

---

## Previous Version Highlights

### From v24.0.0
- No significant changes

### From v23.0.0
**RxControl NTRIP Forwarder:**
- Added NTRIP forwarding capability
- Useful for sharing correction data

**Fugro NMA Status:**
- Visualization for Fugro's Navigation Message Authentication

### From v22.1.0
**RINEX 4.00 Support:**
- SBF Converter now supports RINEX 4.00/4.01
- Useful for post-processing

**RxLogger Enhancements:**
- Improved flexible logging capabilities

### From v22.0.0
**RxLeverArm Tool Added:**
- New tool for INS lever arm optimization
- Not directly relevant to basic GPS integration

### From v21.0.0
**Differential Corrections Indicator:**
- DiffCorr LED replaced with more informative icon
- Shows whether corrections received/sent

### From v20.0.0
**BeiDou B2b Support:**
- Additional BeiDou signals supported
- More satellites available

**Multi-GNSS Improvements:**
- Better support for NavIC (IRNSS renamed)
- Extra BeiDou PRNs (above C37)

---

## Upgrade Notes

### From v24.x or Earlier
- No configuration changes required
- Install directly over previous version
- Settings and profiles preserved

### From v19.x or Earlier
- If downgrading, uninstall existing version first
- Backup configuration profiles before upgrade
- Review connection settings after installation

### First-Time Installation
- Follow standard installation procedure
- Configure USB drivers during setup
- No manual driver installation needed

---

## References

**Documentation:**
- User Manual: `RXTOOLS_USER_MANUAL.md`
- Integration Guide: `INTEGRATION_GUIDE.md`
- Quick Start: `QUICKSTART.md`
- Septentrio Website: https://www.septentrio.com

**Related TriAD C2 Docs:**
- GPS Integration: `/docs/integration/septentrio/`
- Test Script: `/test_gps_connection.py`
- Quick Summary: `/docs/integration/SEPTENTRIO_QUICK_SUMMARY.md`

---

**Status:** ✅ Complete - Extracted from PDF  
**Source:** rxtools_v25.0.0_release_notes.pdf (32 pages)  
**Last Updated:** December 2, 2025  
**Extracted By:** Auto-populated from PDF text extraction
