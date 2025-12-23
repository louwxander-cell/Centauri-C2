# EchoGuard Radar Configuration Limits

## Official Specifications from Developer Manual SW16.4.0

### Field of View (FOV) Limits

#### Azimuth FOV
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Search Az Min** | -60 | +60 | -60 | degrees | Must be < Az Max |
| **Search Az Max** | -60 | +60 | +60 | degrees | Must be > Az Min |
| **SWT Search Az Min** | -60 | +60 | -60 | degrees | Must be ≤ Az Max |
| **SWT Search Az Max** | -60 | +60 | +60 | degrees | Must be ≥ Az Min |
| **SWT Track Az Min** | -60 | +60 | -60 | degrees | Must be ≤ Az Max |
| **SWT Track Az Max** | -60 | +60 | +60 | degrees | Must be ≥ Az Min |

**Total Azimuth Field of Regard:** ±60° (120° total)

#### Elevation FOV
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Search El Min** | -40 | +40 | -40 | degrees | Must be ≤ El Max |
| **Search El Max** | -40 | +40 | +40 | degrees | Must be ≥ El Min |
| **SWT Search El Min** | -40 | +40 | 0 | degrees | Must be ≤ El Max |
| **SWT Search El Max** | -40 | +40 | +12 | degrees | Must be ≥ El Min |
| **SWT Track El Min** | -40 | +40 | -40 | degrees | Must be ≤ El Max |
| **SWT Track El Max** | -40 | +40 | +40 | degrees | Must be ≥ El Min |

**Total Elevation Field of Regard:** ±40° (80° total)

**Important Notes:**
- Scheduled beams will be multiples of 2° even if set to odd values
- Beam width increases 30-50% at FOV edges
- Beam step resolution: 2° minimum

### Range Limits

#### EchoGuard (Standard)
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Range Min** | 20 | 5987 | 21 | meters | Operational minimum |
| **Range Max** | 20 | 5987 | 500 | meters | Operational maximum |
| **Instrumented Range** | - | ~6000 | - | meters | Hardware limit |

#### EchoGuard-CR (Close Range)
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Range Min** | 20 | ~1500 | 21 | meters | Reduced range variant |
| **Range Max** | 20 | ~1500 | 500 | meters | ~1/4 of standard |

**Range Resolution:** 3.25 meters typical

### Platform Orientation Limits

#### Heading
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Heading** | 0 | 359.9 | 30.0 | degrees | Relative to North |

#### Pitch
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Pitch** | -90 | +90 | 19.8 | degrees | Tilt up/down |

#### Roll
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Roll** | -180 | +180 | -0.3 | degrees | Tilt left/right |

### RCS (Radar Cross Section) Masking

| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Min RCS** | -50 | +100 | -30 | dBsm | Must be ≤ Max RCS |
| **Max RCS** | -50 | +100 | +100 | dBsm | Must be ≥ Min RCS |

**Object Detection Range:** -30 to +100 dBsm (user settable window)

### Frequency Channels

| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **DMS Channel** | 0 | 2 | 1 | - | 3 frequency bands |

**Channel Specifications:**
- **Channel 0:** 24.4675 - 24.5125 GHz (Fc = 24.49 GHz)
- **Channel 1:** 24.5275 - 24.5725 GHz (Fc = 24.55 GHz)
- **Channel 2:** 24.5875 - 24.6325 GHz (Fc = 24.61 GHz)
- **Bandwidth:** 45 MHz per channel
- **Guard Band:** 15 MHz between channels

### Operation Modes

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Mode 0** | Pedestrian | Optimized for human targets |
| **Mode 1** | UAS | Optimized for drones |
| **Mode 2** | Plane | Optimized for aircraft |

### Beam Step Parameters

#### Azimuth Step
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Search Az Step** | 2 | 120 | 2 | degrees | Multiples of 2 only |
| **SWT Az Step** | 2 | 120 | 2 | degrees | Multiples of 2 only |

#### Elevation Step
| Parameter | Minimum | Maximum | Default | Units | Notes |
|-----------|---------|---------|---------|-------|-------|
| **Search El Step** | 2 | 80 | 2 | degrees | Multiples of 2 only |
| **SWT El Step** | 2 | 80 | 2 | degrees | Multiples of 2 only |

### Performance Specifications

#### Detection Parameters
- **Velocity Resolution:** 0.91 m/s typical
- **Angular Resolution:** ±1° Az, ±3° El (Search Mode)
- **Track Updates:** 5-10 updates/sec per track
- **Max Simultaneous Tracks:** 20
- **Track Acquisition Time:** < 1 second

#### Beam Characteristics
- **Azimuth Beamwidth (HPBW):** 2° at broadside
- **Elevation Beamwidth (HPBW):** 6° at broadside
- **Beam Pointing Accuracy:** ≤1°
- **Beam Transition Time:** < 1 microsecond
- **Next-Beam Buffer Time:** < 100 microseconds

### Physical & Environmental Limits

#### Operating Conditions
- **Temperature:** -40°C to +75°C continuous operation
- **Storage Temperature:** -55°C to +95°C
- **Humidity:** < 95% non-condensing
- **Altitude:** 0 - 30,000 ft (0 - 9.1 km) AGL
- **Moisture Resistance:** IP67 rated

#### Power Requirements
**EchoGuard Standard:**
- **Recommended:** +15 to +28 VDC @ 45W typical
- **Absolute Min/Max:** +12 to +32 VDC @ 50W max
- **Standby:** ≤10 watts

**EchoGuard-CR:**
- **Recommended:** +12 to +30 VDC @ 23W typical
- **Absolute Min/Max:** +12 to +32 VDC @ 24W max
- **Standby:** ≤10 watts

## Recommended Configuration Constraints

### For UI Implementation

```json
{
  "search_az_min": {
    "min": -60,
    "max": 60,
    "default": -60,
    "step": 1,
    "validation": "Must be < search_az_max"
  },
  "search_az_max": {
    "min": -60,
    "max": 60,
    "default": 60,
    "step": 1,
    "validation": "Must be > search_az_min"
  },
  "search_el_min": {
    "min": -40,
    "max": 40,
    "default": -40,
    "step": 1,
    "validation": "Must be ≤ search_el_max"
  },
  "search_el_max": {
    "min": -40,
    "max": 40,
    "default": 40,
    "step": 1,
    "validation": "Must be ≥ search_el_min"
  },
  "track_az_min": {
    "min": -60,
    "max": 60,
    "default": -60,
    "step": 1,
    "validation": "Must be ≤ track_az_max"
  },
  "track_az_max": {
    "min": -60,
    "max": 60,
    "default": 60,
    "step": 1,
    "validation": "Must be ≥ track_az_min"
  },
  "track_el_min": {
    "min": -40,
    "max": 40,
    "default": -40,
    "step": 1,
    "validation": "Must be ≤ track_el_max"
  },
  "track_el_max": {
    "min": -40,
    "max": 40,
    "default": 40,
    "step": 1,
    "validation": "Must be ≥ track_el_min"
  },
  "range_min": {
    "min": 20,
    "max": 5987,
    "default": 21,
    "step": 1,
    "validation": "Must be < range_max"
  },
  "range_max": {
    "min": 20,
    "max": 5987,
    "default": 500,
    "step": 1,
    "validation": "Must be > range_min"
  },
  "heading": {
    "min": 0,
    "max": 359.9,
    "default": 30.0,
    "step": 0.1,
    "validation": "0-360 degrees from North"
  },
  "pitch": {
    "min": -90,
    "max": 90,
    "default": 19.8,
    "step": 0.1,
    "validation": "Platform tilt up/down"
  },
  "roll": {
    "min": -180,
    "max": 180,
    "default": -0.3,
    "step": 0.1,
    "validation": "Platform tilt left/right"
  },
  "freq_channel": {
    "min": 0,
    "max": 2,
    "default": 1,
    "step": 1,
    "validation": "0, 1, or 2 only"
  }
}
```

## Critical Constraints

### 1. FOV Relationships
- **Azimuth:** Min must be < Max
- **Elevation:** Min must be ≤ Max
- **Total FOV:** Cannot exceed ±60° Az, ±40° El
- **Beam Steps:** Must be multiples of 2°

### 2. Range Relationships
- **Range Min < Range Max**
- **Both within 20m - 5987m**
- **Practical minimum:** 20m (hardware limitation)
- **Resolution:** 3.25m (cannot detect objects closer than this)

### 3. Orientation
- **Heading:** 0-360° (wraps around)
- **Pitch:** ±90° (straight up/down limits)
- **Roll:** ±180° (full rotation)

### 4. RCS Masking
- **Min RCS ≤ Max RCS**
- **Range:** -50 to +100 dBsm
- **Default window:** -30 to +100 dBsm

## Validation Rules

### Pre-Submit Validation
```python
def validate_config(config):
    errors = []
    
    # Azimuth FOV
    if config['search_az_min'] >= config['search_az_max']:
        errors.append("Search Az Min must be < Az Max")
    if config['search_az_min'] < -60 or config['search_az_min'] > 60:
        errors.append("Search Az Min must be between -60 and 60")
    if config['search_az_max'] < -60 or config['search_az_max'] > 60:
        errors.append("Search Az Max must be between -60 and 60")
    
    # Elevation FOV
    if config['search_el_min'] > config['search_el_max']:
        errors.append("Search El Min must be ≤ El Max")
    if config['search_el_min'] < -40 or config['search_el_min'] > 40:
        errors.append("Search El Min must be between -40 and 40")
    if config['search_el_max'] < -40 or config['search_el_max'] > 40:
        errors.append("Search El Max must be between -40 and 40")
    
    # Range
    if config['range_min'] >= config['range_max']:
        errors.append("Range Min must be < Range Max")
    if config['range_min'] < 20 or config['range_min'] > 5987:
        errors.append("Range Min must be between 20 and 5987 meters")
    if config['range_max'] < 20 or config['range_max'] > 5987:
        errors.append("Range Max must be between 20 and 5987 meters")
    
    # Orientation
    if config['heading'] < 0 or config['heading'] >= 360:
        errors.append("Heading must be between 0 and 359.9 degrees")
    if config['pitch'] < -90 or config['pitch'] > 90:
        errors.append("Pitch must be between -90 and 90 degrees")
    if config['roll'] < -180 or config['roll'] > 180:
        errors.append("Roll must be between -180 and 180 degrees")
    
    # Frequency channel
    if config['freq_channel'] not in [0, 1, 2]:
        errors.append("Frequency channel must be 0, 1, or 2")
    
    return errors
```

## Summary Table

| Category | Parameter | Min | Max | Default | Modifiable Online |
|----------|-----------|-----|-----|---------|-------------------|
| **Azimuth** | Search Az Min | -60° | +60° | -60° | ❌ No |
| | Search Az Max | -60° | +60° | +60° | ❌ No |
| | Track Az Min | -60° | +60° | -60° | ✅ Yes |
| | Track Az Max | -60° | +60° | +60° | ✅ Yes |
| **Elevation** | Search El Min | -40° | +40° | -40° | ❌ No |
| | Search El Max | -40° | +40° | +40° | ❌ No |
| | Track El Min | -40° | +40° | -40° | ✅ Yes |
| | Track El Max | -40° | +40° | +40° | ✅ Yes |
| **Range** | Range Min | 20m | 5987m | 21m | ✅ Yes (dynamic) |
| | Range Max | 20m | 5987m | 500m | ✅ Yes (dynamic) |
| **Orientation** | Heading | 0° | 359.9° | 30° | ❌ No |
| | Pitch | -90° | +90° | 19.8° | ❌ No |
| | Roll | -180° | +180° | -0.3° | ❌ No |
| **Frequency** | Channel | 0 | 2 | 1 | ❌ No |
| **RCS** | Min RCS | -50 dBsm | +100 dBsm | -30 dBsm | ✅ Yes |
| | Max RCS | -50 dBsm | +100 dBsm | +100 dBsm | ✅ Yes |

## References

- **Document:** EchoGuard Radar Developer Manual SW16.4.0
- **Doc #:** 700-0005-461 Rev21
- **Release Date:** 2023-May
- **Sections Referenced:** 3.1, 3.2, 8.19-8.32, 8.33-8.34

## Notes for Implementation

1. **Enforce limits in UI spinboxes/sliders**
2. **Validate before sending to radar**
3. **Show warning messages for invalid combinations**
4. **Gray out non-modifiable fields when online**
5. **Use step sizes appropriate for each parameter**
6. **Consider adding "presets" for common configurations**
