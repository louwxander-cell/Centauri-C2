# Septentrio Mosaic-H Documentation Index

Complete documentation for integrating the **Holybro H-RTK Mosaic-H** dual-antenna GNSS receiver with TriAD C2.

---

## 📚 Complete Document List

### 1. Overview & Specifications

**File:** `OVERVIEW_SPECIFICATIONS.md`  
**Purpose:** Complete hardware specifications and feature overview  
**Read First:** Yes - understand what you're working with

**Contents:**
- Product overview and key features
- Complete technical specifications
- GNSS constellation support
- RTK performance metrics
- Positioning accuracy by mode
- Dual-antenna heading accuracy
- Advanced technologies (AIM+, LOCK+, APME+, RAIM+, OSNMA)
- TriAD C2 integration summary

**When to use:** Before purchasing hardware or starting integration

---

### 2. Quick Start Guide

**File:** `QUICKSTART.md`  
**Purpose:** Get running in 30 minutes  
**Read First:** If you have hardware and want to get started immediately

**Contents:**
- Physical setup (5 min)
- Dependency installation (2 min)
- Connection testing (5 min)
- Web configuration (5 min)
- Driver creation (3 min)
- Configuration update (2 min)
- Integration with TriAD C2 (3 min)
- Verification (5 min)
- Troubleshooting quick reference

**When to use:** First-time setup with hardware in hand

---

### 3. Integration Guide (Septentrio-Specific)

**File:** `INTEGRATION_GUIDE.md`  
**Purpose:** Complete Septentrio Mosaic-H specific integration guide  
**Read First:** For detailed Septentrio-specific features and configuration

**Contents:**
- Hardware setup
- Web interface configuration
- NMEA sentence configuration
- Dual-antenna mode setup
- Production driver implementation
- Testing and validation
- Advanced features (RTK, high update rate)
- Troubleshooting
- Septentrio proprietary sentences ($PSAT,HPR)

**When to use:** After quick start, for advanced configuration or troubleshooting

---

### 4. Generic GPS Integration Guide

**File:** `GPS_INTEGRATION_GUIDE.md`  
**Purpose:** Universal dual-antenna GPS integration principles  
**Read First:** If you want to understand dual-antenna GPS technology in general

**Contents:**
- Understanding dual-antenna GPS technology
- Why dual-antenna for C-UAS
- NMEA sentence formats and parsing
- Generic serial communication setup
- Hardware requirements (any dual-antenna GPS)
- General troubleshooting
- Theory and concepts

**When to use:** Learning about GPS technology or adapting to different GPS models

---

### 5. README

**File:** `README.md`  
**Purpose:** Folder overview and navigation guide  
**Read First:** Yes - start here for orientation

**Contents:**
- Document structure overview
- Quick links to key documents
- Hardware overview
- Integration status
- Support resources

**When to use:** First visit to this folder

---

## 🎯 Document Usage Flow

### New User (First Time)

```
1. README.md (orientation)
   ↓
2. OVERVIEW_SPECIFICATIONS.md (understand hardware)
   ↓
3. QUICKSTART.md (get running in 30 min)
   ↓
4. Test with test_gps_connection.py
   ↓
5. INTEGRATION_GUIDE.md (complete integration)
```

### Experienced User (Setup New System)

```
1. QUICKSTART.md (fast setup)
   ↓
2. Test with test_gps_connection.py
   ↓
3. INTEGRATION_GUIDE.md (reference as needed)
```

### Troubleshooting

```
1. QUICKSTART.md (troubleshooting section)
   ↓
2. INTEGRATION_GUIDE.md (detailed troubleshooting)
   ↓
3. GPS_INTEGRATION_GUIDE.md (general GPS issues)
```

### Learning / Research

```
1. OVERVIEW_SPECIFICATIONS.md (hardware capabilities)
   ↓
2. GPS_INTEGRATION_GUIDE.md (GPS theory)
   ↓
3. INTEGRATION_GUIDE.md (implementation details)
```

---

## 📁 File Locations

### This Folder (`/docs/integration/septentrio/`)

```
septentrio/
├── README.md                      # Folder overview
├── DOCUMENTATION_INDEX.md         # This file
├── OVERVIEW_SPECIFICATIONS.md     # Hardware specs (Holybro)
├── QUICKSTART.md                  # 30-min setup
├── INTEGRATION_GUIDE.md           # Septentrio-specific guide
└── GPS_INTEGRATION_GUIDE.md       # Generic dual-antenna guide
```

### Parent Folder (`/docs/integration/`)

```
integration/
├── septentrio/                    # This folder
├── SEPTENTRIO_QUICK_SUMMARY.md    # One-page summary
├── BLUEHALO_QUICK_SUMMARY.md      # RF sensor
├── ECHOGUARD_QUICK_SUMMARY.md     # Radar sensor
└── [other integration docs]
```

### Root Folder (`/`)

```
C2/
├── GPS_INTEGRATION.md             # Quick reference (points here)
├── test_gps_connection.py         # Hardware test script
└── docs/integration/septentrio/   # Full documentation
```

---

## 🔍 Quick Reference by Topic

### Hardware Specifications
→ `OVERVIEW_SPECIFICATIONS.md`

### First-Time Setup
→ `QUICKSTART.md`

### Web Interface Configuration
→ `INTEGRATION_GUIDE.md` (Step 2)

### NMEA Sentence Format
→ `GPS_INTEGRATION_GUIDE.md` (NMEA Sentences section)
→ `INTEGRATION_GUIDE.md` (NMEA Output section)

### Driver Implementation
→ `INTEGRATION_GUIDE.md` (Step 5: Create Production Driver)
→ `QUICKSTART.md` (Step 5: Create Driver)

### Testing Hardware
→ Root: `/test_gps_connection.py`
→ `QUICKSTART.md` (Step 3: Test Connection)

### Troubleshooting
→ `QUICKSTART.md` (Troubleshooting section)
→ `INTEGRATION_GUIDE.md` (Troubleshooting section)
→ `GPS_INTEGRATION_GUIDE.md` (Troubleshooting section)

### RTK Configuration
→ `INTEGRATION_GUIDE.md` (Advanced Configuration → RTK Mode)
→ `OVERVIEW_SPECIFICATIONS.md` (RTK Performance)

### Anti-Jamming Features
→ `OVERVIEW_SPECIFICATIONS.md` (Advanced Technologies → AIM+)

### Dual-Antenna Theory
→ `GPS_INTEGRATION_GUIDE.md` (Understanding Dual-Antenna GPS)
→ `OVERVIEW_SPECIFICATIONS.md` (GNSS Attitude Accuracy)

---

## 📊 Document Comparison

| Document | Length | Depth | Septentrio-Specific | Generic | Best For |
|----------|--------|-------|-------------------|---------|----------|
| **OVERVIEW_SPECIFICATIONS** | Long | Deep | ✅ Yes | ❌ No | Hardware research |
| **QUICKSTART** | Medium | Quick | ✅ Yes | ❌ No | Fast setup |
| **INTEGRATION_GUIDE** | Long | Deep | ✅ Yes | ❌ No | Complete integration |
| **GPS_INTEGRATION_GUIDE** | Long | Deep | ❌ No | ✅ Yes | GPS theory/principles |
| **README** | Short | Overview | ✅ Yes | ❌ No | Navigation |

---

## 🎓 Additional Resources

### External Documentation
- **Holybro Product Page:** https://holybro.com/products/h-rtk-mosaic-h
- **Septentrio Support:** https://www.septentrio.com/en/support/mosaic/mosaic-h
- **NMEA 0183 Standard:** https://www.nmea.org/content/STANDARDS/NMEA_0183_Standard

### TriAD C2 Resources
- **Test Script:** `/test_gps_connection.py`
- **Quick Summary:** `/docs/integration/SEPTENTRIO_QUICK_SUMMARY.md`
- **Root Quick Ref:** `/GPS_INTEGRATION.md`

### Manufacturer Manuals
**To be added:**
- Official Holybro user manual
- Septentrio mosaic-H reference manual
- Web interface guide with screenshots

---

### 6. RxTools User Manual Extract

**File:** `RXTOOLS_USER_MANUAL_EXTRACT.md`  
**Purpose:** Key extracts from 219-page manual relevant to TriAD C2  
**Read First:** For NMEA commands, heading configuration, and troubleshooting

**Contents:**
- NMEA configuration commands
- Dual-antenna/heading setup
- Connection methods (USB, serial, network)
- RxControl Expert Console usage
- Command reference
- Troubleshooting guide
- Best practices for TriAD C2

**When to use:** Reference for specific configuration tasks or troubleshooting

---

### 7. RxTools Release Notes

**File:** `RXTOOLS_RELEASE_NOTES.md`  
**Purpose:** What's new in RxTools v25.0.0  
**Read First:** To understand version changes and compatibility

**Contents:**
- New features in v25.0.0
- Breaking changes
- Installation instructions
- Known issues and workarounds
- Compatibility information
- Upgrade notes

**When to use:** Before installing/upgrading RxTools, or understanding version differences

---

## ✅ Documentation Status

| Document | Status | Pages/Size | Last Updated |
|----------|--------|------------|--------------|
| README.md | ✅ Complete | 2.7 KB | Dec 2, 2025 |
| OVERVIEW_SPECIFICATIONS.md | ✅ Complete | 11.8 KB | Dec 2, 2025 |
| QUICKSTART.md | ✅ Complete | 9.5 KB | Dec 2, 2025 |
| INTEGRATION_GUIDE.md | ✅ Complete | 17.0 KB | Dec 2, 2025 |
| GPS_INTEGRATION_GUIDE.md | ✅ Complete | 18.4 KB | Dec 2, 2025 |
| DOCUMENTATION_INDEX.md | ✅ Complete | 8.4 KB | Dec 2, 2025 |
| RXTOOLS_USER_MANUAL_EXTRACT.md | ✅ Complete | ~18 KB | Dec 2, 2025 |
| RXTOOLS_RELEASE_NOTES.md | ✅ Complete | ~12 KB | Dec 2, 2025 |

**Total:** 8 complete documents (~97 KB of documentation)  
**Source PDFs:** 2 files (13.1 MB, 251 pages total)  
**Extraction:** Auto-populated via PyPDF2

**All core documentation complete and ready for use.**

---

## 📝 Additional Documentation

### Reference Materials (Extracted from PDFs)

**Source Files Located:** `/Integration docs/Septentrio GPS/`
- ✅ `rxtools_v25.0.0_user_manual.pdf` (12.9 MB, 219 pages)
- ✅ `rxtools_v25.0.0_release_notes.pdf` (208 KB, 32 pages)
- ✅ `rxtools_25_0_0_installer_x64.bin` (96.5 MB)

**Extracted Text Files:**
- ✅ `rxtools_manual.txt` (343,496 characters, 6,161 lines)
- ✅ `rxtools_notes.txt` (53,863 characters, 1,160 lines)

**Completed Documents:**
- ✅ `RXTOOLS_USER_MANUAL_EXTRACT.md` - Key extracts for TriAD C2 (NMEA, heading, commands)
- ✅ `RXTOOLS_RELEASE_NOTES.md` - Complete release notes v25.0.0

**Still To Create:**
- [ ] `NMEA_REFERENCE.md` - Complete NMEA sentence reference
- [ ] `WEB_INTERFACE_GUIDE.md` - Web UI with screenshots
- [ ] `TROUBLESHOOTING.md` - Dedicated troubleshooting guide
- [ ] `FAQ.md` - Frequently asked questions
- [ ] `CONFIGURATION_EXAMPLES.md` - Sample configs for different use cases
- [ ] `DRIVER_IMPLEMENTATION.md` - Detailed driver architecture

**Extraction Method:**
PDFs converted to text using PyPDF2, then relevant sections extracted and formatted into markdown documents.

---

## 🚀 Quick Start (From This Document)

**If you're reading this for the first time:**

1. **Close this file**
2. **Open:** `QUICKSTART.md`
3. **Follow:** The 8-step guide
4. **Test:** Run `test_gps_connection.py`
5. **Verify:** GPS working in TriAD C2

**Total time:** ~30 minutes

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2025  
**Maintained By:** TriAD C2 Integration Team
