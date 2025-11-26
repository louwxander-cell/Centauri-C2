# TriAD C2 System Architecture

## System Overview

The TriAD Counter-UAS C2 system is a multi-threaded, event-driven application built on PyQt6 that integrates multiple sensor inputs for real-time target tracking and weapon control.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Main Application                          │
│                         (main.py)                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ├──────────────────────────────────────┐
                         │                                      │
                         ▼                                      ▼
              ┌──────────────────┐                  ┌──────────────────┐
              │   Signal Bus     │◄─────────────────│   Main Window    │
              │   (Singleton)    │                  │   (PyQt6 GUI)    │
              └────────┬─────────┘                  └──────────────────┘
                       │                                      │
       ┌───────────────┼───────────────┬──────────────────────┤
       │               │               │                      │
       ▼               ▼               ▼                      ▼
┌────────────┐  ┌────────────┐  ┌────────────┐      ┌──────────────┐
│   Radar    │  │     RF     │  │    GPS     │      │ Radar Scope  │
│  Driver    │  │  Driver    │  │  Driver    │      │  (PyQtGraph) │
│ (Thread)   │  │ (Thread)   │  │ (Thread)   │      └──────────────┘
└────────────┘  └────────────┘  └────────────┘
       │               │               │
       └───────────────┴───────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Track Fusion    │
              │     Engine       │
              └──────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   RWS Driver     │
              │   (Thread)       │
              └──────────────────┘
```

## Component Details

### 1. Signal Bus (`src/core/bus.py`)

**Purpose**: Central communication hub using Qt signals/slots pattern

**Key Signals**:
- `sig_track_updated`: New or updated track data
- `sig_ownship_updated`: Vehicle position update
- `sig_slew_command`: Weapon pointing command
- `sig_system_status`: System health updates
- `sig_track_selected`: User selected a track in UI

**Pattern**: Singleton to ensure single instance across application

### 2. Data Models (`src/core/datamodels.py`)

**Purpose**: Type-safe data structures using Pydantic

**Key Models**:
- `Track`: Target track with position, classification, confidence
- `GeoPosition`: Ownship lat/lon/heading
- `SlewCommand`: Weapon pointing command
- `SystemStatus`: Overall system health

**Enums**:
- `TargetType`: DRONE, BIRD, UNKNOWN, AIRCRAFT, CLUTTER
- `SensorSource`: RADAR, RF, FUSED, GPS

### 3. Track Fusion (`src/core/fusion.py`)

**Purpose**: Correlate and merge tracks from multiple sensors

**Algorithm**:
1. Convert tracks to Cartesian coordinates
2. Calculate 3D distance between tracks
3. If distance < threshold and different sensors → FUSE
4. Use weighted average based on confidence
5. Boost confidence for multi-sensor tracks
6. Remove stale tracks (timeout)

**Parameters**:
- `distance_threshold_m`: 50m (configurable)
- `timeout_sec`: 5.0s (configurable)

### 4. Driver Architecture (`src/drivers/`)

**Base Class** (`base.py`):
- Inherits from `QThread` for threading
- Abstract `run()` method for main loop
- Status management (online/offline)
- Error handling and logging

**Radar Driver** (`radar.py`):
- Simulates 3 targets in circular motion
- 10 Hz update rate
- Range: 500-1100m
- Azimuth: 360° rotation

**RF Driver** (`rf.py`):
- Simulates drone RF detections
- 2 Hz update rate
- Good bearing accuracy, poor range accuracy
- High confidence for drone classification

**GPS Driver** (`gps.py`):
- Simulates vehicle position
- 1 Hz update rate
- Circular motion pattern (100m radius)
- NMEA-style output

**RWS Driver** (`rws.py`):
- Listens for slew commands
- Simulates weapon pointing
- Rate limits: 30°/s azimuth, 20°/s elevation
- UDP protocol (mock)

### 5. User Interface (`src/ui/`)

**Main Window** (`main_window.py`):
- 3-pane layout with splitters
- Track list table (left)
- Radar scope (center)
- System status (right)
- Engage button (bottom)

**Radar Scope** (`radar_scope.py`):
- PyQtGraph polar plot
- Real-time track visualization
- Color-coded by target type
- Range rings at 500m intervals

**Styles** (`styles.py`):
- Tactical dark theme (#1e1e1e background)
- Green status indicators
- Red engage button
- Monospace fonts

## Data Flow

### Track Update Flow

```
1. Sensor Driver (Thread)
   └─► Generate/Receive Track Data
       └─► SignalBus.sig_track_updated.emit(track)
           └─► Track Fusion Engine
               └─► Correlate with existing tracks
                   └─► SignalBus.sig_track_updated.emit(fused_track)
                       └─► Main Window
                           ├─► Update Track Table
                           └─► Update Radar Scope
```

### Engage Flow

```
1. User clicks track in table
   └─► MainWindow._on_track_selected()
       └─► Enable Engage Button
           └─► User clicks Engage Button
               └─► MainWindow._on_engage_clicked()
                   └─► SignalBus.sig_slew_command.emit(az, el)
                       └─► RWS Driver
                           └─► Calculate slew time
                               └─► Send UDP command (production)
```

## Threading Model

### Main Thread (Qt Event Loop)
- UI rendering and user interaction
- Signal/slot connections
- Timer-based updates

### Driver Threads (QThread)
- Radar Driver: 100ms cycle (10 Hz)
- RF Driver: 500ms cycle (2 Hz)
- GPS Driver: 1000ms cycle (1 Hz)
- RWS Driver: Event-driven (waits for commands)

### Thread Safety
- All inter-thread communication via Qt signals (thread-safe)
- No shared mutable state
- Each driver has independent data

## Configuration

### Network Settings (`config/settings.json`)
```json
{
  "network": {
    "radar": {"protocol": "TCP", "host": "127.0.0.1", "port": 23000},
    "rws": {"protocol": "UDP", "host": "127.0.0.1", "port": 5000},
    "rf": {"protocol": "REST", "base_url": "http://127.0.0.1:8080/api"}
  }
}
```

### Geographic Zones (`config/zones.geojson`)
- GeoJSON format for safe/restricted zones
- Polygon definitions
- Future: Geofencing logic

## Performance Characteristics

### Update Rates
- Radar: 10 Hz (100ms)
- RF: 2 Hz (500ms)
- GPS: 1 Hz (1000ms)
- UI: 10 Hz (100ms)

### Latency
- Sensor → UI: < 50ms (typical)
- Engage → RWS: < 100ms (typical)

### Resource Usage
- Memory: ~100-200 MB
- CPU: < 5% (idle), < 20% (active tracking)
- Threads: 5 (main + 4 drivers)

## Error Handling

### Driver Errors
- Try/catch in main loop
- Emit error signal to UI
- Continue operation (resilient)
- Log to console

### Track Timeout
- Automatic removal after 5 seconds
- Prevents stale data display
- Configurable timeout

### Graceful Shutdown
- Ctrl+C handler
- Stop all driver threads
- Wait for thread completion (2s timeout)
- Clean exit

## Future Enhancements

### Production Readiness
1. Replace mock drivers with real hardware interfaces
2. Add data recording/playback
3. Implement geofencing logic
4. Add engagement authorization workflow
5. Network security (encryption, authentication)

### Features
1. Multi-target engagement
2. Threat prioritization
3. Automatic tracking
4. Historical track playback
5. Mission planning tools

### Performance
1. GPU acceleration for radar scope
2. Database for track history
3. Distributed processing
4. Cloud integration

## Testing Strategy

### Unit Tests
- Track fusion logic (`tests/test_fusion.py`)
- Data model validation
- Coordinate transformations

### Integration Tests
- Driver → SignalBus → UI flow
- Multi-sensor correlation
- Engage workflow

### System Tests
- End-to-end scenarios
- Performance benchmarks
- Stress testing (many tracks)

## Security Considerations

### Current (Mock Mode)
- No authentication
- Local network only
- No encryption

### Production Requirements
1. **Authentication**: User login, role-based access
2. **Encryption**: TLS for network, encrypted storage
3. **Audit**: Log all commands and actions
4. **Authorization**: Multi-level approval for engagement
5. **Physical Security**: Secure hardware, tamper detection

## Deployment

### Development
```bash
python3 main.py
```

### Production
1. Package as standalone executable (PyInstaller)
2. Deploy on hardened OS (Linux RT)
3. Configure real sensor endpoints
4. Enable logging and monitoring
5. Implement backup/redundancy

## Maintenance

### Logs
- Console output for all events
- Future: File-based logging with rotation

### Monitoring
- System status panel in UI
- Sensor health indicators
- Track count and age

### Updates
- Version control (Git)
- Semantic versioning
- Change log documentation

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Author**: TriAD Development Team
