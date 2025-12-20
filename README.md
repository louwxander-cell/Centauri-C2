# TriAD Counter-UAS Command & Control System

A mission-critical desktop application for the TriAD Counter-UAS system, built with Python 3.11+ and Qt6 QML.

## System Overview

The TriAD C2 system provides real-time threat assessment and engagement control for counter-drone operations with an advanced tactical display interface.

### Current Architecture

- **Engine Layer**: Python-based threat prioritization and sensor fusion
- **Orchestration Layer**: Qt bridge connecting backend to UI
- **UI Layer**: GPU-accelerated QML tactical display
- **Sensor Integration**: EchoGuard radar with full C2 control
- **Gunner Interface**: UDP broadcast for external weapon systems

### Integrated Sensors

- ✅ **EchoGuard Radar** - Echodyne MESA radar with automatic control
  - Full C2 control (no external software required)
  - Track data streaming at 10 Hz
  - UAS classification and tracking
  - 900m range, 120° azimuth FOV

## Features

### Tactical Display
- ✅ **GPU-Accelerated QML UI**: Smooth 60 FPS rendering
- ✅ **Radar-Style Visualization**: Polar display with range rings and FOV wedge
- ✅ **Track Selection System**: Dual ring indicators (red=priority, white=selected)
- ✅ **Auto-Selection**: Instant highest-threat prioritization (<10ms latency)
- ✅ **Dynamic Zoom**: 0.25x to 8x zoom with consistent range ring display
- ✅ **Track Tails**: 15-second movement history visualization

### Threat Assessment
- ✅ **Hybrid Prioritization Algorithm**: Range + velocity + approach scoring
- ✅ **Real-Time Updates**: 10 Hz track update rate
- ✅ **Type Classification**: UAV (threat), BIRD (neutral), UNKNOWN
- ✅ **Confidence Tracking**: Visual confidence indicators per track

### Engagement Control
- ✅ **Active Track List**: Sorted by threat priority
- ✅ **Manual Selection**: Override auto-selection for 10 seconds
- ✅ **Engagement Panel**: Track details and engage button
- ✅ **Gunner Interface**: UDP broadcast (5100) for weapon systems

### Simulation
- ✅ **Test Scenarios**: 5 built-in scenarios with varying complexity
- ✅ **Realistic Movement**: Physics-based track simulation
- ✅ **Multi-Track Support**: Tested with 25+ simultaneous tracks

## Quick Start

### Requirements
- Python 3.11+
- Qt 6.5+
- PyQt6

### Installation

```bash
# Install dependencies
pip install PyQt6
```

### Running the Application

```bash
python triad_c2.py
```

The application launches with **Scenario 5** (25 tracks) by default for stress testing.

## Project Structure

```
C2/
├── triad_c2.py                 # Application entry point
├── engine/
│   ├── mock_engine_updated.py  # Track simulation engine
│   └── test_scenarios.py       # 5 test scenarios
├── orchestration/
│   ├── bridge.py               # Qt bridge (TracksModel, Ownship)
│   └── gunner_interface.py     # UDP broadcast for gunner systems
├── ui/
│   ├── Main.qml                # Tactical display UI
│   ├── EngagementPanel.qml     # Engagement controls
│   └── Theme.qml               # Design tokens
└── docs/
    ├── user-guides/            # Operator documentation
    ├── technical/              # Technical specifications
    └── integration/            # Sensor integration guides
```

## Architecture

### Three-Layer Design

**1. Engine Layer (Python)**
- Track simulation and generation
- Threat priority calculation
- Test scenario management

**2. Orchestration Layer (Qt/Python)**
- `TracksModel`: Qt model for QML binding
- `OrchestrationBridge`: Updates UI from engine
- `GunnerInterface`: UDP broadcast for external systems

**3. UI Layer (QML)**
- GPU-accelerated Qt Quick rendering
- Tactical radar display
- Engagement panel
- Theme system

### Data Flow

```
Engine → Bridge → QML UI
  ↓
Gunner Interface (UDP:5100)
```

### Track Model

```python
class Track(QObject):
    # Properties exposed to QML
    id: int
    type: str  # UAV, BIRD, UNKNOWN
    range: float  # meters
    azimuth: float  # degrees
    velocity_x, velocity_y: float
    tail: list  # position history
    threat_priority: float  # 0-100 score
```

## User Interface

### Main Window Layout

- **Left Panel (300px)**: Active track list sorted by threat priority
- **Center Panel**: Radar-style tactical display with zoom controls
- **Right Panel (380px)**: Engagement panel showing selected track details

### Tactical Display Controls

| Control | Action |
|---------|--------|
| **Mouse Wheel** | Zoom in/out (0.25x to 8x) |
| **+ Button** | Zoom in 1.5x |
| **- Button** | Zoom out 1.5x |
| **⟲ Button** | Reset zoom to 1.0x |
| **Click Track** | Manual selection (10s override) |

### Color Coding

**Track Dots:**
- 🔴 **Red**: UAV (threat)
- 🟢 **Green**: BIRD (neutral)
- 🟡 **Yellow**: UNKNOWN

**Selection Rings:**
- 🔴 **Red ring (22px)**: Highest priority threat
- ⚪ **White ring (28px)**: Selected track
- 🔴⚪ **Both rings**: Highest priority is also selected

### Test Scenarios

Load scenarios via scenario buttons (1-5):

1. **Single Close Threat** - Basic functionality test
2. **Multiple Range Bands** - Close, mid, far tracks
3. **Mixed Types** - UAVs, birds, unknowns
4. **Rapid Movement** - Fast-moving threats
5. **Stress Test** - 25 tracks for performance testing

## Testing

### Performance Metrics
- **60 FPS** rendering with 25 tracks
- **<10ms** selection latency
- **10 Hz** track update rate
- **Smooth animations** at 5 Hz tail rendering

### Keyboard Shortcuts
- **1-5**: Load test scenarios
- **R**: Reset zoom to 1.0x
- **?**: Toggle keyboard shortcuts help

## Documentation

### User Guides
- `docs/user-guides/OPERATOR_GUIDE.md` - How to operate the system
- `docs/user-guides/TESTING_GUIDE.md` - Testing procedures
- `docs/user-guides/TEST_SCENARIOS_IMPLEMENTED.md` - Scenario details

### Technical Documentation
- `docs/technical/TACTICAL_DISPLAY.md` - Display implementation
- `docs/technical/THREAT_PRIORITIZATION_ALGORITHM.md` - Priority algorithm
- `docs/technical/DESIGN_SYSTEM_GUIDE.md` - UI design tokens
- `docs/technical/PORT_SPECIFICATIONS.md` - Network ports

### Integration
- `docs/integration/SENSOR_INTEGRATION.md` - Sensor integration guide
- `docs/integration/PRODUCTION_QUICKSTART.md` - Production deployment
- See `docs/integration/` for sensor-specific guides

## Production Deployment

For real sensor integration:

1. **Replace mock engine** with production sensor drivers
2. **Update bridge** to process real sensor data
3. **Configure network ports** in sensor integration modules
4. **Test gunner interface** UDP broadcast (port 5100)

See `docs/integration/PRODUCTION_ROADMAP.md` for detailed steps.

## Dependencies

- **PyQt6**: Qt 6 framework with QML support
- **Python 3.11+**: Runtime environment

## System Requirements

- **OS**: macOS, Linux, or Windows
- **GPU**: OpenGL 3.3+ for hardware acceleration
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Display**: 1920x1080 or higher resolution

## License

Proprietary - Defense Systems Application

## Support

For technical support or questions:
- Review documentation in `docs/`
- Check `OUTSTANDING_TASKS.md` for known issues
- See `QUICKSTART.md` for common setup problems

---

**⚠️ NOTICE**: This is a mission-critical defense system. All modifications must be reviewed and tested thoroughly before deployment.

**Current Status:** ✅ Stable & Production Ready (Simulation Mode)
