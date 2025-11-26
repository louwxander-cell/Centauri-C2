# Modern Tactical GUI - User Guide

## 🎨 **Ultra-Modern Interface Design**

The TriAD C2 system now features a completely redesigned ultra-modern tactical interface with:

- **Dark tactical theme** - Professional military-grade appearance
- **Custom fonts** - Nex Sphere (caps) + Bahnschrift (normal text)
- **Real-time sensor data** - All capabilities from Radar and RF
- **Intuitive layout** - User-friendly 3-panel design
- **Command chain visualization** - Live status of detection-to-engagement flow
- **Pilot position display** - Shows drone operator location
- **RF-silent mode indicator** - Visual feedback for radar-only tracking

---

## 🖥️ **Interface Layout**

### **Top Bar - System Status**
```
┌─────────────────────────────────────────────────────────────┐
│ TRIAD C2 SYSTEM    [●RADAR] [●RF] [●GPS] [●RWS]            │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Large system title (Nex Sphere font)
- Real-time sensor status indicators
- Color-coded status dots (green=online, gray=offline)

---

### **Left Panel - Track List & Details**

#### **Active Tracks Table**
```
┌─────────────────────────────────────────┐
│ ACTIVE TRACKS                           │
├────┬──────┬────────┬───────┬─────┬──────┤
│ ID │ TYPE │ SOURCE │ RANGE │ AZ  │ CONF │
├────┼──────┼────────┼───────┼─────┼──────┤
│ 13 │DRONE │ RADAR  │ 850m  │45.2°│ 0.85 │
│ 42 │DRONE │   RF   │3200m  │120° │ 0.92 │
└────┴──────┴────────┴───────┴─────┴──────┘
```

**Features:**
- Sortable columns
- Color-coded track types (red=drone, blue=bird, yellow=unknown)
- Color-coded sources (cyan=radar, green=RF, purple=fused)
- Click to select track

#### **Track Details Panel**
```
┌─────────────────────────────────────────┐
│ TRACK DETAILS                           │
├─────────────────────────────────────────┤
│ TRACK ID:          13                   │
│ Type:              DRONE                │
│ Source:            RADAR                │
│ ─────────────────────────────────────── │
│ Range:             850 m                │
│ Azimuth:           45.2°                │
│ Elevation:         8.5°                 │
│ ─────────────────────────────────────── │
│ Drone Model:       Mavic Pro            │
│ Serial Number:     08RDD8K00100E6       │
│ RF Frequency:      2.40 GHz             │
│ RF Power:          417.1 dBm            │
│ ─────────────────────────────────────── │
│ Pilot Lat:         39.233532            │
│ Pilot Lon:         -77.548508           │
│ ─────────────────────────────────────── │
│ RCS:               -23.92 m²            │
│ UAV Probability:   85.00%               │
│ ─────────────────────────────────────── │
│ Velocity:          8.6 m/s              │
│ Heading:           125.3°               │
└─────────────────────────────────────────┘
```

**Features:**
- Complete track information
- RF-specific data (drone model, serial, pilot position)
- Radar-specific data (RCS, UAV probability)
- Monospace font for values (easy to read)
- Cyan accent borders

---

### **Center Panel - Tactical Display**

#### **Radar Scope**
```
              N (0°)
               ↑
               │
    W ←───────●───────→ E
               │
               ↓
              S (180°)
```

**Features:**
- Polar plot (range/bearing)
- Range rings (1km, 2km, 3km, 4km, 5km)
- Bearing lines (every 30°)
- Forward indicator (cyan arrow)
- Track symbols:
  - **○** Circle = RF detection
  - **△** Triangle = Radar detection
  - **□** Square = Fused track
- Track colors:
  - **Red** = Drone (hostile)
  - **Blue** = Bird (neutral)
  - **Yellow** = Unknown
  - **Purple** = Fused
- **★** Yellow star = Pilot position
- Track trails (motion history)

---

### **Right Panel - System Info & Controls**

#### **Ownship Position**
```
┌─────────────────────────────────────────┐
│ OWNSHIP POSITION                        │
├─────────────────────────────────────────┤
│ Latitude:          39.233532            │
│ Longitude:         -77.548508           │
│ Heading:           90.0°                │
└─────────────────────────────────────────┘
```

#### **System Mode**
```
┌─────────────────────────────────────────┐
│ SYSTEM MODE                             │
├─────────────────────────────────────────┤
│ ● RF-SILENT MODE                        │
│ ● OPTICAL LOCK                          │
└─────────────────────────────────────────┘
```

**Indicators:**
- **Green dot** = Mode active
- **Gray dot** = Mode inactive
- **Yellow** = RF-Silent Mode (warning color)
- **Green** = Optical Lock (success color)

#### **RWS Position**
```
┌─────────────────────────────────────────┐
│ RWS POSITION                            │
├─────────────────────────────────────────┤
│ RADAR                                   │
│ Azimuth:           45.2°                │
│ Elevation:         8.5°                 │
│ ─────────────────────────────────────── │
│ OPTICS                                  │
│ Azimuth:           45.2°                │
│ Elevation:         -11.5°               │
└─────────────────────────────────────────┘
```

**Shows:**
- Radar pointing direction
- Optics pointing direction
- 20° elevation offset visible

#### **Engage Button**
```
┌─────────────────────────────────────────┐
│                                         │
│          ENGAGE TARGET                  │
│                                         │
└─────────────────────────────────────────┘
```

**Features:**
- Large red button (Nex Sphere font)
- Disabled when no track selected
- Glowing effect on hover
- Sends slew command when clicked

---

### **Bottom Bar - Command Chain Status**

```
┌─────────────────────────────────────────────────────────────┐
│ COMMAND CHAIN:                                              │
│ [RF DETECT] → [RADAR SLEW] → [RADAR TRACK] →               │
│ [OPTICS SLEW] → [OPTICAL LOCK]                  12:34:56   │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Live command chain visualization
- Active steps highlighted in color:
  - **Green** = RF Detect
  - **Orange** = Radar/Optics Slew
  - **Cyan** = Radar Track
  - **Green** = Optical Lock
- Inactive steps grayed out
- System time display (UTC)

---

## 🎨 **Color Scheme**

### **Background Colors**
- **Primary**: `#0a0e14` (Deep space black)
- **Secondary**: `#151b24` (Dark slate)
- **Panel**: `#0f1419` (Panel background)

### **Accent Colors**
- **Cyan**: `#00d9ff` (Primary accent, headings)
- **Green**: `#10b981` (Success, online status)
- **Red**: `#ef4444` (Danger, drones, engage)
- **Yellow**: `#fbbf24` (Warning, unknown)
- **Orange**: `#f97316` (Alert, RWS)
- **Purple**: `#a855f7` (Fused tracks)

### **Text Colors**
- **Primary**: `#f9fafb` (Almost white)
- **Secondary**: `#9ca3af` (Light gray)
- **Tertiary**: `#6b7280` (Medium gray)

---

## 🔤 **Typography**

### **Nex Sphere** (ALL CAPS)
Used for:
- System title
- Panel headings
- Button labels
- Table headers
- Status indicators
- Command chain steps

**Example:**
```
TRIAD C2 SYSTEM
ACTIVE TRACKS
ENGAGE TARGET
```

### **Bahnschrift** (Normal Text)
Used for:
- Field labels
- Descriptive text
- Body content

**Example:**
```
Type:
Drone Model:
Pilot position:
```

### **Consolas** (Monospace)
Used for:
- Numeric values
- Coordinates
- Measurements
- Table data

**Example:**
```
39.233532
-77.548508
850 m
45.2°
```

---

## 📊 **Data Display**

### **Track Information**

#### **Basic Position**
- **Range**: Meters (e.g., "850 m")
- **Azimuth**: Degrees (e.g., "45.2°")
- **Elevation**: Degrees (e.g., "8.5°")

#### **RF-Specific** (BlueHalo SkyView)
- **Drone Model**: "Mavic Pro", "Phantom 4", etc.
- **Serial Number**: Unique drone ID
- **RF Frequency**: GHz (e.g., "2.40 GHz", "5.80 GHz")
- **RF Power**: dBm (signal strength)
- **Pilot Latitude**: Decimal degrees
- **Pilot Longitude**: Decimal degrees

#### **Radar-Specific** (Echoguard)
- **RCS**: Radar cross-section in m²
- **UAV Probability**: Percentage (0-100%)
- **Velocity**: m/s
- **Heading**: Degrees

---

## 🎮 **User Interactions**

### **Track Selection**
1. Click on track in table
2. Track details populate in details panel
3. Track highlighted on radar scope
4. Engage button becomes enabled

### **Manual Slew**
1. Select track
2. Click "ENGAGE TARGET" button
3. RWS slews to track position
4. Command chain activates

### **Mode Monitoring**
- Watch **RF-SILENT MODE** indicator
  - Green = Radar-only tracking active
  - Gray = Normal RF+Radar mode
- Watch **OPTICAL LOCK** indicator
  - Green = Visual tracking locked
  - Gray = No optical lock

### **Command Chain Monitoring**
Watch bottom bar for active steps:
1. **RF DETECT** - RF sensor detected drone
2. **RADAR SLEW** - RWS slewing radar
3. **RADAR TRACK** - Radar acquired target
4. **OPTICS SLEW** - RWS slewing optics
5. **OPTICAL LOCK** - Visual tracking locked

---

## 🔍 **Visual Indicators**

### **Status Dots**
- **● Green** = Online/Active
- **● Gray** = Offline/Inactive
- **● Yellow** = Warning
- **● Red** = Error

### **Track Colors**
- **Red** = Drone (hostile threat)
- **Blue** = Bird (neutral)
- **Yellow** = Unknown
- **Purple** = Fused (RF + Radar)

### **Sensor Colors**
- **Cyan** = Radar
- **Green** = RF
- **Yellow** = GPS
- **Orange** = RWS

---

## ⌨️ **Keyboard Shortcuts** (Future)

Planned shortcuts:
- **Space** - Engage selected track
- **Esc** - Deselect track
- **↑/↓** - Navigate track list
- **F1** - Help
- **F5** - Refresh display

---

## 🎯 **Best Practices**

### **For Operators**
1. **Monitor sensor status** - Ensure all sensors online
2. **Watch command chain** - Verify automatic handoff
3. **Check track details** - Review drone model, pilot position
4. **Verify optical lock** - Confirm visual tracking before engagement
5. **Monitor RF-silent mode** - Be aware of radar-only tracking

### **For System Administrators**
1. **Font installation** - Install Nex Sphere and Bahnschrift
2. **Display resolution** - Recommended 1920x1080 or higher
3. **Color calibration** - Ensure accurate color representation
4. **Performance** - Monitor UI update rate (should be 10 Hz)

---

## 🚀 **Launch Instructions**

### **With Modern GUI**
```bash
python3 main.py --modern
```

### **With Classic GUI** (fallback)
```bash
python3 main.py
```

---

## 📸 **Screenshots** (Conceptual)

### **Normal Mode**
```
┌────────────────────────────────────────────────────────────┐
│ TRIAD C2 SYSTEM    [●RADAR] [●RF] [●GPS] [●RWS]           │
├──────────┬─────────────────────────────┬──────────────────┤
│ ACTIVE   │   TACTICAL DISPLAY          │ OWNSHIP POSITION │
│ TRACKS   │                             │ Lat: 39.233532   │
│          │         N                   │ Lon: -77.548508  │
│ 13 DRONE │         ↑                   │ Hdg: 90.0°       │
│ 42 DRONE │         │                   │                  │
│          │    ←───●───→                │ SYSTEM MODE      │
│ DETAILS  │         │                   │ ○ RF-SILENT      │
│ ID: 13   │         ↓                   │ ○ OPTICAL LOCK   │
│ Model:   │         S                   │                  │
│ Mavic Pro│                             │ RWS POSITION     │
│ Serial:  │    ●(Drone)  ★(Pilot)       │ RADAR            │
│ 08RDD8K  │                             │ Az: 45.2°        │
│          │                             │ El: 8.5°         │
│          │                             │ OPTICS           │
│          │                             │ Az: 45.2°        │
│          │                             │ El: -11.5°       │
│          │                             │                  │
│          │                             │ [ENGAGE TARGET]  │
├──────────┴─────────────────────────────┴──────────────────┤
│ CHAIN: [RF]→[SLEW]→[TRACK]→[SLEW]→[LOCK]      12:34:56   │
└────────────────────────────────────────────────────────────┘
```

### **RF-Silent Mode**
```
┌────────────────────────────────────────────────────────────┐
│ TRIAD C2 SYSTEM    [●RADAR] [○RF] [●GPS] [●RWS]           │
├──────────┬─────────────────────────────┬──────────────────┤
│ ACTIVE   │   TACTICAL DISPLAY          │ SYSTEM MODE      │
│ TRACKS   │                             │ ● RF-SILENT MODE │
│          │         N                   │ ● OPTICAL LOCK   │
│ 42 DRONE │         ↑                   │                  │
│          │         │                   │ 🔴 RADAR-ONLY    │
│ DETAILS  │    ←───●───→                │    TRACKING      │
│ ID: 42   │         │                   │                  │
│ Source:  │         ↓                   │ Continuous       │
│ RADAR    │         S                   │ optics updates   │
│ Model: — │                             │ until lock       │
│ Serial:— │    ●(Drone)                 │                  │
│ Pilot: — │                             │                  │
└──────────┴─────────────────────────────┴──────────────────┘
```

---

## 🎉 **Summary**

The modern GUI provides:

✅ **Ultra-modern tactical appearance**  
✅ **All sensor capabilities displayed**  
✅ **Intuitive 3-panel layout**  
✅ **Real-time command chain visualization**  
✅ **Pilot position tracking**  
✅ **RF-silent mode awareness**  
✅ **Professional military-grade interface**  
✅ **Custom fonts (Nex Sphere + Bahnschrift)**  
✅ **Color-coded status indicators**  
✅ **Comprehensive track details**  

**Ready for operational deployment! 🚀**

---

*GUI Design Date: November 25, 2024*  
*Status: ✅ Modern Interface Complete*
