# TriAD Counter-UAS Command & Control System

A mission-critical desktop application for the TriAD Counter-UAS system, built with Python 3.11+ and PyQt6.

## System Overview

The TriAD C2 system fuses data from multiple sensors to provide real-time situational awareness and weapon control for counter-drone operations:

- **Echodyne Radar**: Primary tracking sensor (TCP stream)
- **BlueHalo RF Sensor**: Drone RF signature detection (REST/Socket API)
- **GPS/Compass**: Ownship position and heading (Serial NMEA)
- **Remote Weapon Station (RWS)**: Weapon pointing control (UDP)

## Features

- ✅ **Multi-Sensor Fusion**: Combines radar and RF tracks for enhanced accuracy
- ✅ **Real-Time Display**: Tactical dark-mode UI with polar radar scope
- ✅ **Track Management**: Automatic track correlation and timeout handling
- ✅ **Weapon Control**: Slew-to-cue functionality for RWS engagement
- ✅ **Mock Drivers**: Fully functional simulation mode for testing

## Quick Start

### Installation

```bash
# Using Poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### Running the Application

```bash
# With Poetry
poetry run python main.py

# Or directly
python main.py
```

The application will start with all mock drivers active, generating simulated target data immediately.

## Project Structure

```
TriAD_C2/
├── main.py                     # Application entry point
├── pyproject.toml              # Poetry dependencies
├── config/
│   ├── settings.json           # System configuration
│   └── zones.geojson           # Geographic zones
├── src/
│   ├── core/
│   │   ├── bus.py              # Central signal bus
│   │   ├── datamodels.py       # Pydantic data models
│   │   └── fusion.py           # Track fusion logic
│   ├── drivers/
│   │   ├── base.py             # Abstract driver base class
│   │   ├── radar.py            # Mock Echodyne radar
│   │   ├── rf.py               # Mock BlueHalo RF sensor
│   │   ├── gps.py              # Mock GPS/Compass
│   │   └── rws.py              # Mock RWS controller
│   └── ui/
│       ├── main_window.py      # Main application window
│       ├── radar_scope.py      # Polar radar display
│       └── styles.py           # Tactical dark theme
└── tests/
    └── test_fusion.py          # Unit tests
```

## Architecture

### Signal Bus Pattern

All components communicate through a central `SignalBus` using Qt signals:

```python
from src.core.bus import SignalBus

bus = SignalBus.instance()
bus.sig_track_updated.connect(handler)
bus.emit_track(track)
```

### Data Models

Type-safe data models using Pydantic:

```python
from src.core.datamodels import Track, TargetType, SensorSource

track = Track(
    id=1,
    azimuth=45.0,
    elevation=10.0,
    range_m=500.0,
    type=TargetType.DRONE,
    confidence=0.8,
    source=SensorSource.RADAR
)
```

### Driver Architecture

All drivers inherit from `BaseDriver` and run in separate threads:

```python
class RadarDriver(BaseDriver):
    def run(self):
        while self._running:
            track = self._generate_track()
            self.signal_bus.emit_track(track)
```

## Configuration

Edit `config/settings.json` to configure network ports and system parameters:

```json
{
  "network": {
    "radar": {"protocol": "TCP", "host": "127.0.0.1", "port": 23000},
    "rws": {"protocol": "UDP", "host": "127.0.0.1", "port": 5000}
  },
  "system": {
    "update_rate_hz": 10,
    "track_timeout_sec": 5.0,
    "fusion_distance_threshold_m": 50.0
  }
}
```

## User Interface

### Main Window Layout

- **Left Panel**: Active track list with ID, range, azimuth, type, source, and confidence
- **Center Panel**: Polar radar scope showing tracks in real-time
- **Right Panel**: System status (sensor health, ownship position)
- **Bottom Panel**: Track selection and engage/slew control

### Color Coding

- 🔴 **Red**: Drone targets
- 🔵 **Blue**: Bird targets  
- 🟠 **Orange**: Unknown targets
- 🟣 **Magenta**: Fused tracks (multi-sensor)

### Operation

1. **Track Selection**: Click on a track in the left panel
2. **Engagement**: Click the red "ENGAGE / SLEW" button
3. **RWS Control**: System automatically slews weapon to selected track

## Testing

Run unit tests:

```bash
# With Poetry
poetry run pytest tests/ -v

# Or directly
pytest tests/ -v
```

## Mock Driver Behavior

### Radar Driver
- Generates 3 simulated targets
- Targets move in circular patterns at different ranges (500m, 800m, 1100m)
- Update rate: 10 Hz

### RF Driver
- Generates 1-2 drone detections intermittently
- Simulates RF sensor characteristics (good bearing, poor range accuracy)
- Update rate: 2 Hz

### GPS Driver
- Simulates vehicle moving in a 100m radius circle
- Starting position: San Francisco (37.7749°N, 122.4194°W)
- Update rate: 1 Hz

### RWS Driver
- Listens for slew commands on signal bus
- Simulates weapon slew with rate limits (30°/s azimuth, 20°/s elevation)
- Logs all commands to console

## Production Deployment

To connect to real hardware:

1. **Radar**: Modify `src/drivers/radar.py` to connect to TCP port 23000 and parse binary/JSON
2. **RF Sensor**: Modify `src/drivers/rf.py` to connect to REST API
3. **GPS**: Modify `src/drivers/gps.py` to read from serial port (e.g., `/dev/ttyUSB0`)
4. **RWS**: Modify `src/drivers/rws.py` to send UDP packets to weapon station

## Dependencies

- **PyQt6**: GUI framework
- **Pydantic**: Data validation and models
- **PyQtGraph**: High-performance plotting
- **NumPy**: Numerical operations
- **PySerial**: Serial communication (for GPS)

## License

Proprietary - Defense Systems Application

## Support

For technical support or questions, contact the TriAD development team.

---

**⚠️ NOTICE**: This is a mission-critical defense system. All modifications must be reviewed and tested thoroughly before deployment.
