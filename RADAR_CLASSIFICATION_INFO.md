# EchoGuard Radar Classification System

## Overview
The EchoGuard radar (SW 17.0+) includes a multiclass classifier that uses machine learning to classify tracks into 7 target classes. SW 18.1 improved the classifier with a random forest model for better UAV recognition.

## Track Classes

### 1. **UAV** (Unmanned Aerial Vehicle)
- **Color**: Red (#EF4444)
- **Description**: Small commercial quadcopters (DJI Phantom, Mavic 2, M600, etc.)
- **Subcategories**:
  - UAV Multi-Rotor: Standard quadcopters/multicopters
  - UAV Fixed-Wing: Fixed-wing drones
- **Default Threshold**: 90% (configurable 0-100)
- **Classification Range**: Full range with B1a waveform
- **RCS**: Typically < -5 dBsm
- **Velocity**: ≤ 30 m/s

### 2. **Bird**
- **Color**: Cyan (#06B6D4)
- **Description**: Avian targets
- **Default Threshold**: 90%
- **Characteristics**: Small RCS, erratic movement patterns

### 3. **Aircraft** (Plane)
- **Color**: Yellow (#EAB308)
- **Description**: Crewed/manned aircraft
- **Default Threshold**: 90%
- **RCS**: Typically > +5 dBsm
- **Velocity**: > 30 m/s

### 4. **Vehicle**
- **Color**: Purple (#A855F7)
- **Description**: Ground vehicles (cars, trucks, etc.)
- **Default Threshold**: 90%
- **Characteristics**: Ground-based, moderate RCS

### 5. **Walker**
- **Color**: Blue (#3B82F6)
- **Description**: Human pedestrians
- **Default Threshold**: 90%
- **Velocity**: Typically < 10 m/s
- **RCS**: Small

### 6. **Clutter**
- **Color**: Gray (#6B7280)
- **Description**: Environmental clutter (waves, vegetation, etc.)
- **Default Threshold**: 90%
- **Characteristics**: Stationary or slow-moving non-targets

### 7. **Undeclared** (Other/Unknown)
- **Color**: White (#FFFFFF)
- **Description**: Targets that don't fit other categories or low confidence
- **Default Threshold**: N/A
- **Note**: Used when classifier cannot confidently assign a class

## Classification Confidence Threshold

**Class Declaration Threshold**: 0-100 (default: 90)
- Tracks are assigned a class only if the probability exceeds this threshold
- Lower threshold = more tracks classified (but potentially less accurate)
- Higher threshold = fewer tracks classified (but higher confidence)
- Threshold of 90 means track must have ≥90% probability to be declared that class

## Radar Commands

### Enable/Disable Classifier
```
CLF:ENABLE <su_pswd> [TRUE/FALSE]
```
- **Default**: TRUE for Operation Modes 1 (drones) and 2 (aircraft)
- **Default**: FALSE for Operation Mode 0 (walkers/pedestrians)
- When disabled, probability fields in track packet report as NaN

### Operation Modes
```
MODE:SWT:OPERATIONMODE <value>
```
- **0**: Walkers/Pedestrians (classifier disabled by default)
- **1**: Small drones/sUAS (classifier enabled, optimized for UAVs)
- **2**: Crewed aircraft (classifier enabled)

## Track Packet Data

Each track update includes classification probabilities:
- `prob_unknown` (float 0.0-1.0 or NaN)
- `prob_uav` (float 0.0-1.0 or NaN)
- Additional probability fields for other classes

## Implementation Notes

1. **Waveform Compatibility**:
   - Fully supported: B1a waveform
   - Not validated: B1b, A1a waveforms (disabled by default)

2. **Classification Range**:
   - Full range with B1a waveform
   - Probabilities update with each track update as more data is collected

3. **Track Filtering**:
   - RadarUI 4.0+ supports native filtering by target class
   - Users can show/hide specific classes
   - Useful for focusing on targets of interest (e.g., only UAVs for C-UAS missions)

## Default Configuration for C2 System

```json
{
  "classifier_enabled": true,
  "operation_mode": 1,
  "class_declaration_threshold": 90,
  "show_classes": {
    "uav": true,
    "uav_multi_rotor": true,
    "uav_fixed_wing": true,
    "walker": false,
    "plane": false,
    "bird": true,
    "vehicle": false,
    "clutter": true,
    "undeclared": true
  }
}
```

## Color Legend (for UI)

| Class | Color Code | RGB |
|-------|------------|-----|
| UAV | #EF4444 | rgb(239, 68, 68) |
| UAV Multi-Rotor | #F97316 | rgb(249, 115, 22) |
| UAV Fixed-Wing | #FB923C | rgb(251, 146, 60) |
| Walker | #3B82F6 | rgb(59, 130, 246) |
| Plane | #EAB308 | rgb(234, 179, 8) |
| Bird | #06B6D4 | rgb(6, 182, 212) |
| Vehicle | #A855F7 | rgb(168, 85, 247) |
| Clutter | #6B7280 | rgb(107, 114, 128) |
| Undeclared | #FFFFFF | rgb(255, 255, 255) |
