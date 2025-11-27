# TriAD C2 Documentation Index

**Last Updated:** November 27, 2024  
**Status:** ✅ Current & Organized

---

## 📖 Getting Started

**Start Here:**
1. **[README.md](README.md)** - System overview and quick start
2. **[QUICKSTART.md](QUICKSTART.md)** - Installation and first run
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture overview

---

## 👤 User Guides

Located in `docs/user-guides/`:

### Operation
- **[OPERATOR_GUIDE.md](docs/user-guides/OPERATOR_GUIDE.md)** - How to operate the tactical display
- **[RF_SILENT_MODE_GUIDE.md](docs/user-guides/RF_SILENT_MODE_GUIDE.md)** - RF-silent operations
- **[SIMULATED_TRACKS_GUIDE.md](docs/user-guides/SIMULATED_TRACKS_GUIDE.md)** - Working with simulated tracks

### Testing
- **[TESTING_GUIDE.md](docs/user-guides/TESTING_GUIDE.md)** - Testing procedures
- **[TEST_SCENARIOS_IMPLEMENTED.md](docs/user-guides/TEST_SCENARIOS_IMPLEMENTED.md)** - Test scenario details
- **[OFFLINE_MAPS_GUIDE.md](docs/user-guides/OFFLINE_MAPS_GUIDE.md)** - Offline map integration

---

## 🔧 Technical Documentation

Located in `docs/technical/`:

### Core Systems
- **[TACTICAL_DISPLAY.md](docs/technical/TACTICAL_DISPLAY.md)** - Tactical display implementation ⭐
- **[THREAT_PRIORITIZATION_ALGORITHM.md](docs/technical/THREAT_PRIORITIZATION_ALGORITHM.md)** - Priority algorithm details
- **[ALGORITHM_ANALYSIS_REPORT.md](docs/technical/ALGORITHM_ANALYSIS_REPORT.md)** - Algorithm analysis and performance

### Design & Specifications
- **[DESIGN_SYSTEM_GUIDE.md](docs/technical/DESIGN_SYSTEM_GUIDE.md)** - UI design tokens and theme
- **[PORT_SPECIFICATIONS.md](docs/technical/PORT_SPECIFICATIONS.md)** - Network port assignments
- **[CHANGELOG_SENSOR_ICD.md](docs/technical/CHANGELOG_SENSOR_ICD.md)** - Sensor interface changes

---

## 🔌 Integration Guides

Located in `docs/integration/`:

### Production Deployment
- **[PRODUCTION_QUICKSTART.md](docs/integration/PRODUCTION_QUICKSTART.md)** - Production deployment guide
- **[PRODUCTION_ROADMAP.md](docs/integration/PRODUCTION_ROADMAP.md)** - Production roadmap
- **[PRODUCTION_DRIVER_TEMPLATE.md](docs/integration/PRODUCTION_DRIVER_TEMPLATE.md)** - Driver template
- **[TRANSITION_GUIDE.md](docs/integration/TRANSITION_GUIDE.md)** - Mock to production transition

### Sensor Integration
- **[SENSOR_INTEGRATION.md](docs/integration/SENSOR_INTEGRATION.md)** - General sensor integration
- **[INTEGRATION_REQUIREMENTS.md](docs/integration/INTEGRATION_REQUIREMENTS.md)** - Requirements checklist
- **[INTEGRATION_CHECKLIST.md](docs/integration/INTEGRATION_CHECKLIST.md)** - Step-by-step checklist

### Specific Sensors
- **[BLUEHALO_QUICK_SUMMARY.md](docs/integration/BLUEHALO_QUICK_SUMMARY.md)** - BlueHalo RF sensor
- **[ECHOGUARD_QUICK_SUMMARY.md](docs/integration/ECHOGUARD_QUICK_SUMMARY.md)** - Echodyne radar

---

## 🗂️ Project Management

Located in root directory:

- **[OUTSTANDING_TASKS.md](OUTSTANDING_TASKS.md)** - Current tasks and known issues

---

## 📁 Documentation Organization

```
C2/
├── README.md                          # Main documentation
├── QUICKSTART.md                      # Getting started
├── ARCHITECTURE.md                    # System architecture
├── DOCUMENTATION_INDEX.md             # This file
├── OUTSTANDING_TASKS.md               # Current tasks
│
└── docs/
    ├── user-guides/                   # Operator documentation
    │   ├── OPERATOR_GUIDE.md
    │   ├── TESTING_GUIDE.md
    │   ├── TEST_SCENARIOS_IMPLEMENTED.md
    │   ├── SIMULATED_TRACKS_GUIDE.md
    │   ├── RF_SILENT_MODE_GUIDE.md
    │   └── OFFLINE_MAPS_GUIDE.md
    │
    ├── technical/                     # Technical specifications
    │   ├── TACTICAL_DISPLAY.md        ⭐ Current display impl
    │   ├── THREAT_PRIORITIZATION_ALGORITHM.md
    │   ├── ALGORITHM_ANALYSIS_REPORT.md
    │   ├── DESIGN_SYSTEM_GUIDE.md
    │   ├── PORT_SPECIFICATIONS.md
    │   └── CHANGELOG_SENSOR_ICD.md
    │
    └── integration/                   # Sensor integration
        ├── SENSOR_INTEGRATION.md
        ├── INTEGRATION_REQUIREMENTS.md
        ├── INTEGRATION_CHECKLIST.md
        ├── PRODUCTION_QUICKSTART.md
        ├── PRODUCTION_ROADMAP.md
        ├── PRODUCTION_DRIVER_TEMPLATE.md
        ├── TRANSITION_GUIDE.md
        ├── BLUEHALO_QUICK_SUMMARY.md
        └── ECHOGUARD_QUICK_SUMMARY.md
```

---

## 🔍 Quick Reference

### Common Questions

**"How do I run the system?"**
→ See [QUICKSTART.md](QUICKSTART.md)

**"How does the tactical display work?"**
→ See [TACTICAL_DISPLAY.md](docs/technical/TACTICAL_DISPLAY.md)

**"How do I integrate real sensors?"**
→ See [PRODUCTION_QUICKSTART.md](docs/integration/PRODUCTION_QUICKSTART.md)

**"What are the test scenarios?"**
→ See [TEST_SCENARIOS_IMPLEMENTED.md](docs/user-guides/TEST_SCENARIOS_IMPLEMENTED.md)

**"How does threat prioritization work?"**
→ See [THREAT_PRIORITIZATION_ALGORITHM.md](docs/technical/THREAT_PRIORITIZATION_ALGORITHM.md)

**"What network ports are used?"**
→ See [PORT_SPECIFICATIONS.md](docs/technical/PORT_SPECIFICATIONS.md)

---

## 📊 Documentation Statistics

- **Total Documents:** 24 (down from 77)
- **User Guides:** 6
- **Technical Docs:** 6
- **Integration Guides:** 9
- **Root Level:** 3

**Cleanup Summary:**
- ✅ Removed 53 outdated session/iteration documents
- ✅ Consolidated tactical display documentation
- ✅ Organized into logical categories
- ✅ Updated README with current functionality
- ✅ Created comprehensive index (this file)

---

## 🎯 Documentation Standards

### File Naming
- Use `UPPERCASE_SNAKE_CASE.md` for consistency
- Be descriptive but concise
- Use prefixes for categories (e.g., PRODUCTION_, INTEGRATION_)

### Content Structure
- Start with metadata (date, status)
- Include overview/summary
- Use clear section headings
- Add examples and code snippets
- Include testing/verification sections

### Maintenance
- Update last modified date when editing
- Mark status (✅ Current, ⚠️ Needs Update, ❌ Deprecated)
- Remove outdated information promptly
- Consolidate related documents

---

**Documentation Status:** 🟢 **Clean & Organized**  
**Last Cleanup:** November 27, 2024  
**Next Review:** When major features added or changed
