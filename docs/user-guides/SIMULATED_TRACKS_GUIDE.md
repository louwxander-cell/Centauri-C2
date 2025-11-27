# TriAD C2 - Simulated Tracks Configuration Guide

**Date:** November 26, 2025  
**Purpose:** Configure and control simulated tracks for UI testing

---

## 📍 **Where Track Simulation Happens**

### **Main File:**
**`/Users/xanderlouw/CascadeProjects/C2/engine/mock_engine_updated.py`**

This file contains three key classes:
1. **`MockRadarSensor`** - Simulates Echoguard radar tracks (lines 13-80)
2. **`MockRFSensor`** - Simulates SkyView RF detections (lines 83-207)
3. **`MockEngine`** - Combines sensors and performs fusion (lines 209-436)

---

## 🎛️ **How to Control Track Generation**

### **Option 1: Disable Specific Sensors**

**Location:** `mock_engine_updated.py`, line 250 in `MockEngine.update()`

**Current Code:**
```python
def update(self):
    """Main update loop - fuses sensor data"""
    # Get sensor data
    radar_tracks = self.radar.generate_tracks()      # ← RADAR TRACKS
    rf_detections = self.rf.generate_detections()    # ← RF TRACKS
```

**To Disable Radar Tracks:**
```python
def update(self):
    """Main update loop - fuses sensor data"""
    # Get sensor data
    radar_tracks = []  # DISABLED: self.radar.generate_tracks()
    rf_detections = self.rf.generate_detections()
```

**To Disable RF Tracks:**
```python
def update(self):
    """Main update loop - fuses sensor data"""
    # Get sensor data
    radar_tracks = self.radar.generate_tracks()
    rf_detections = []  # DISABLED: self.rf.generate_detections()
```

**To Disable All Tracks:**
```python
def update(self):
    """Main update loop - fuses sensor data"""
    # Get sensor data
    radar_tracks = []  # DISABLED
    rf_detections = []  # DISABLED
```

---

### **Option 2: Add Configuration Flags (RECOMMENDED)**

**Step 1:** Add configuration to `MockEngine.__init__()` (around line 214)

**Add these lines:**
```python
def __init__(self):
    self.radar = MockRadarSensor()
    self.rf = MockRFSensor()
    
    # ===== ADD THESE CONFIGURATION FLAGS =====
    self.config = {
        'radar_enabled': True,       # Toggle radar tracks
        'rf_enabled': True,          # Toggle RF tracks
        'fusion_enabled': True,      # Toggle sensor fusion
        'num_radar_tracks': (2, 4),  # Min/max radar tracks
        'num_rf_tracks': (1, 2),     # Min/max RF tracks
    }
    # ==========================================
    
    self.ownship = {
        'lat': -25.841105,
        # ... rest of ownship
```

**Step 2:** Update the `update()` method (around line 250)

**Replace:**
```python
def update(self):
    """Main update loop - fuses sensor data"""
    # Get sensor data
    radar_tracks = self.radar.generate_tracks()
    rf_detections = self.rf.generate_detections()
```

**With:**
```python
def update(self):
    """Main update loop - fuses sensor data"""
    # Get sensor data (respecting config)
    radar_tracks = self.radar.generate_tracks() if self.config['radar_enabled'] else []
    rf_detections = self.rf.generate_detections() if self.config['rf_enabled'] else []
```

**Step 3:** Add method to toggle sensors

**Add this new method to `MockEngine` class (around line 437):**
```python
def set_sensor_config(self, **kwargs):
    """
    Update sensor configuration
    
    Usage:
        engine.set_sensor_config(radar_enabled=False)
        engine.set_sensor_config(rf_enabled=True, fusion_enabled=False)
    """
    for key, value in kwargs.items():
        if key in self.config:
            self.config[key] = value
            print(f"[ENGINE] Sensor config updated: {key} = {value}")
        else:
            print(f"[ENGINE] Unknown config key: {key}")
    
    return {
        'accepted': True,
        'message': 'Sensor configuration updated',
        'config': self.config
    }
```

---

### **Option 3: Create Test Scenarios**

**Add this method to `MockEngine` class:**

```python
def load_test_scenario(self, scenario_name: str):
    """
    Load predefined test scenarios
    
    Available scenarios:
    - 'empty': No tracks
    - 'radar_only': Only radar tracks
    - 'rf_only': Only RF tracks
    - 'single_threat': One high-priority threat
    - 'multiple_threats': Several threats at various ranges
    - 'fused_threat': Radar + RF fused track
    """
    scenarios = {
        'empty': {
            'radar_enabled': False,
            'rf_enabled': False,
        },
        'radar_only': {
            'radar_enabled': True,
            'rf_enabled': False,
        },
        'rf_only': {
            'radar_enabled': False,
            'rf_enabled': True,
        },
        'single_threat': {
            'radar_enabled': True,
            'rf_enabled': False,
            'num_radar_tracks': (1, 1),
        },
        'multiple_threats': {
            'radar_enabled': True,
            'rf_enabled': True,
            'num_radar_tracks': (4, 6),
            'num_rf_tracks': (2, 3),
        },
        'fused_threat': {
            'radar_enabled': True,
            'rf_enabled': True,
            'fusion_enabled': True,
            'num_radar_tracks': (2, 2),
            'num_rf_tracks': (1, 1),
        }
    }
    
    if scenario_name not in scenarios:
        print(f"[ENGINE] Unknown scenario: {scenario_name}")
        print(f"[ENGINE] Available: {list(scenarios.keys())}")
        return {'accepted': False, 'message': 'Unknown scenario'}
    
    # Apply scenario config
    self.config.update(scenarios[scenario_name])
    print(f"[ENGINE] Loaded scenario: {scenario_name}")
    print(f"[ENGINE] Config: {self.config}")
    
    return {
        'accepted': True,
        'message': f'Scenario {scenario_name} loaded',
        'config': self.config
    }
```

---

## 🎮 **How to Use in the Application**

### **Method 1: Modify at Startup**

**File:** `/Users/xanderlouw/CascadeProjects/C2/triad_c2.py`

**Add after engine initialization (around line 37):**

```python
# Initialize engine (mock for now)
print("[INIT] Starting mock engine...")
engine = MockEngine()

# ===== ADD THIS TO CONFIGURE TRACKS =====
# Disable RF tracks for testing
engine.set_sensor_config(rf_enabled=False)

# OR load a specific scenario
# engine.load_test_scenario('single_threat')
# ========================================
```

### **Method 2: Interactive Toggle via QML**

**Step 1:** Expose method to QML (in `triad_c2.py`, around line 51)

```python
# Expose models to QML
print("[INIT] Exposing data models to QML...")
qml_engine.rootContext().setContextProperty("tracksModel", bridge.tracks_model)
qml_engine.rootContext().setContextProperty("ownship", bridge.ownship)
qml_engine.rootContext().setContextProperty("systemMode", bridge.system_mode)
qml_engine.rootContext().setContextProperty("bridge", bridge)
qml_engine.rootContext().setContextProperty("engine", engine)  # ← ADD THIS
```

**Step 2:** Add toggle buttons in QML

**File:** `ui/Main.qml` (in footer or header)

**Add this to footer (around line 930):**

```qml
// Footer
Rectangle {
    Layout.fillWidth: true
    Layout.preferredHeight: 44
    color: Theme.base1
    radius: Theme.radiusMedium
    border.width: 1
    border.color: Theme.borderSubtle
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 20
        anchors.rightMargin: 20
        spacing: 12
        
        Text {
            text: "SYSTEM OPERATIONAL"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSmall
            font.weight: Theme.fontWeightSemiBold
            font.capitalization: Font.AllUppercase
            color: Theme.accentCyan
        }
        
        Item { Layout.fillWidth: true }
        
        // ===== ADD THESE TEST CONTROLS =====
        Text {
            text: "TEST:"
            font.family: Theme.fontFamily
            font.pixelSize: 10
            color: Theme.textSecondary
        }
        
        Button {
            text: "NO TRACKS"
            font.pixelSize: 9
            onClicked: engine.load_test_scenario('empty')
            Layout.preferredWidth: 80
            Layout.preferredHeight: 26
        }
        
        Button {
            text: "RADAR ONLY"
            font.pixelSize: 9
            onClicked: engine.load_test_scenario('radar_only')
            Layout.preferredWidth: 80
            Layout.preferredHeight: 26
        }
        
        Button {
            text: "RF ONLY"
            font.pixelSize: 9
            onClicked: engine.load_test_scenario('rf_only')
            Layout.preferredWidth: 80
            Layout.preferredHeight: 26
        }
        
        Button {
            text: "ALL SENSORS"
            font.pixelSize: 9
            onClicked: engine.load_test_scenario('multiple_threats')
            Layout.preferredWidth: 80
            Layout.preferredHeight: 26
        }
        // ===================================
    }
}
```

---

## 📝 **Quick Configuration Examples**

### **Example 1: No Tracks (Empty Screen)**
**File:** `mock_engine_updated.py`, line 250

```python
def update(self):
    radar_tracks = []
    rf_detections = []
```

### **Example 2: Single High-Priority Threat**
**File:** `mock_engine_updated.py`, line 32

```python
# In MockRadarSensor.generate_tracks()
for i in range(1):  # Changed from range(random.randint(2, 4))
```

### **Example 3: Many Tracks (Stress Test)**
**File:** `mock_engine_updated.py`, line 32 and line 115

```python
# In MockRadarSensor.generate_tracks()
for i in range(10):  # Generate 10 radar tracks

# In MockRFSensor.generate_detections()
for i in range(5):   # Generate 5 RF detections
```

### **Example 4: Static Tracks (No Movement)**
**File:** `mock_engine_updated.py`, line 47

```python
# In MockRadarSensor.generate_tracks()
# Comment out these lines:
# track['azimuth_deg'] += random.uniform(-0.5, 0.5)
# track['range_m'] += random.uniform(-10, 10)
```

---

## 🎯 **Recommended Testing Workflow**

### **Phase 1: UI Layout Testing**
```python
# In triad_c2.py after engine initialization
engine.load_test_scenario('empty')
```
**Purpose:** Test UI with no tracks, verify labels, buttons, layout

### **Phase 2: Single Track Interaction**
```python
engine.load_test_scenario('single_threat')
```
**Purpose:** Test track selection, detail panel, engagement button

### **Phase 3: Multi-Track Prioritization**
```python
engine.load_test_scenario('multiple_threats')
```
**Purpose:** Test priority algorithm, track list sorting, override selection

### **Phase 4: Sensor Fusion Validation**
```python
engine.load_test_scenario('fused_threat')
```
**Purpose:** Test FUSED badge display, RF intelligence fields

### **Phase 5: Sensor Toggle Testing**
```python
# Test radar only
engine.set_sensor_config(radar_enabled=True, rf_enabled=False)

# Test RF only
engine.set_sensor_config(radar_enabled=False, rf_enabled=True)

# Test all sensors
engine.set_sensor_config(radar_enabled=True, rf_enabled=True)
```
**Purpose:** Verify UI handles different sensor combinations

---

## 📋 **Complete Implementation Checklist**

### **To Add Full Toggle Support:**

- [ ] **Step 1:** Add `config` dictionary to `MockEngine.__init__()` (line ~214)
- [ ] **Step 2:** Add `set_sensor_config()` method to `MockEngine` (line ~437)
- [ ] **Step 3:** Add `load_test_scenario()` method to `MockEngine` (line ~450)
- [ ] **Step 4:** Update `MockEngine.update()` to respect config flags (line ~250)
- [ ] **Step 5:** Expose `engine` to QML in `triad_c2.py` (line ~51)
- [ ] **Step 6:** Add toggle buttons to UI footer in `Main.qml` (line ~930)

### **Files to Modify:**
1. ✅ `/Users/xanderlouw/CascadeProjects/C2/engine/mock_engine_updated.py`
2. ✅ `/Users/xanderlouw/CascadeProjects/C2/triad_c2.py`
3. ✅ `/Users/xanderlouw/CascadeProjects/C2/ui/Main.qml`

---

## 🚀 **Quick Start**

### **Minimal Change (Fastest):**

**File:** `mock_engine_updated.py`, line 250

```python
# ORIGINAL:
radar_tracks = self.radar.generate_tracks()
rf_detections = self.rf.generate_detections()

# TO DISABLE ALL TRACKS:
radar_tracks = []
rf_detections = []

# TO ENABLE AGAIN:
radar_tracks = self.radar.generate_tracks()
rf_detections = self.rf.generate_detections()
```

**Restart the application after each change:**
```bash
cd /Users/xanderlouw/CascadeProjects/C2
python3 triad_c2.py
```

---

## 📊 **Track Count Reference**

**Current Defaults:**
- **Radar tracks:** 2-4 tracks (random)
- **RF detections:** 1-2 detections (random)
- **Update rate:** 10 Hz
- **Track movement:** ±0.5° azimuth, ±10m range per update

**Locations:**
- Radar count: `mock_engine_updated.py` line 32
- RF count: `mock_engine_updated.py` line 115
- Movement: `mock_engine_updated.py` lines 47, 53

---

## 💡 **Tips**

1. **Start Simple:** Begin with `empty` scenario, then add one track at a time
2. **Test Extremes:** Try 0 tracks, 1 track, and 20+ tracks
3. **Static Testing:** Disable track movement to test UI without distractions
4. **Sensor Isolation:** Test each sensor individually before testing fusion
5. **Save Scenarios:** Create custom scenarios for specific test cases

---

## ❓ **Quick Reference**

| What | Where | Line |
|------|-------|------|
| Total tracks on/off | `mock_engine_updated.py` | 250-254 |
| Radar track count | `mock_engine_updated.py` | 32 |
| RF detection count | `mock_engine_updated.py` | 115 |
| Track movement | `mock_engine_updated.py` | 47, 53 |
| Engine startup | `triad_c2.py` | 37 |
| Main UI file | `ui/Main.qml` | - |

---

**Ready to implement?** Let me know which method you'd like to use, and I can make the changes for you!
