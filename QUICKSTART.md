# TriAD C2 - Quick Start Guide

## 🚀 Get Running in 60 Seconds

### Step 1: Install Dependencies

```bash
cd /Users/xanderlouw/CascadeProjects/C2
pip3 install -r requirements.txt
```

### Step 2: Run the Application

```bash
python3 main.py
```

**OR**

```bash
./run.sh
```

### Step 3: See It In Action

Within seconds, you'll see:
- ✅ Main window with tactical dark theme
- ✅ 3 simulated targets moving on radar scope
- ✅ Track list updating in real-time
- ✅ All sensors showing ONLINE status

## 🎯 Try It Out

1. **Click on a track** in the left panel
2. **Click the red "ENGAGE / SLEW" button**
3. **Watch the console** for slew command output

## 📁 Project Structure

```
TriAD_C2/
├── main.py              ← START HERE
├── requirements.txt     ← Dependencies
├── README.md           ← Full documentation
├── ARCHITECTURE.md     ← System design
├── OPERATOR_GUIDE.md   ← User manual
├── config/
│   ├── settings.json   ← Configuration
│   └── zones.geojson   ← Geographic zones
├── src/
│   ├── core/           ← Data models, signal bus, fusion
│   ├── drivers/        ← Sensor drivers (mock)
│   └── ui/             ← GUI components
└── tests/
    └── test_fusion.py  ← Unit tests
```

## 🎨 What You'll See

### Main Window
- **Left Panel**: Track list with ID, range, azimuth, type, source, confidence
- **Center Panel**: Polar radar scope with moving targets
- **Right Panel**: System status (sensors, GPS position)
- **Bottom**: Engage button (red, becomes active when track selected)

### Color Coding
- 🔴 Red dots = Drones
- 🔵 Blue dots = Birds
- 🟠 Orange dots = Unknown
- 🟣 Magenta dots = Fused tracks (multi-sensor)

## 🧪 Run Tests

```bash
pytest tests/ -v
```

## 🛠️ Mock Drivers

All drivers are in **simulation mode** and generate realistic data:

- **Radar**: 3 targets rotating at different ranges (500m, 800m, 1100m)
- **RF**: Intermittent drone detections with RF signatures
- **GPS**: Vehicle moving in 100m circle
- **RWS**: Logs slew commands to console

## 📊 System Requirements

- **Python**: 3.11+ (tested on 3.9+)
- **OS**: macOS, Linux, Windows
- **RAM**: 200 MB
- **CPU**: Any modern processor

## 🔧 Configuration

Edit `config/settings.json` to change:
- Network ports
- Update rates
- Fusion parameters
- Timeout values

## 📚 Documentation

- **README.md**: Complete project overview
- **ARCHITECTURE.md**: Technical design details
- **OPERATOR_GUIDE.md**: User manual with procedures
- **This file**: Quick start

## 🐛 Troubleshooting

### Dependencies Not Installing?

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Then try again
pip3 install -r requirements.txt
```

### Application Won't Start?

```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check dependencies
pip3 list | grep -E 'PyQt6|pydantic|pyqtgraph'
```

### No Tracks Appearing?

- **Normal**: Tracks appear within 1-2 seconds
- **Check console**: Look for driver startup messages
- **Restart**: Press Ctrl+C and run again

## 🎓 Next Steps

1. ✅ Run the application and explore the UI
2. 📖 Read OPERATOR_GUIDE.md for detailed procedures
3. 🏗️ Read ARCHITECTURE.md to understand the design
4. 🧪 Run tests to verify functionality
5. 🔧 Modify mock drivers for your use case

## 💡 Key Features

- ✨ **Real-time tracking**: 10 Hz radar updates
- 🎯 **Multi-sensor fusion**: Combines radar + RF
- 🖥️ **Tactical UI**: Dark theme, color-coded targets
- 🔫 **Weapon control**: Slew-to-cue engagement
- 🧵 **Multi-threaded**: Responsive, non-blocking
- 🛡️ **Type-safe**: Pydantic data models
- 🧪 **Tested**: Unit tests for fusion logic

## 🚨 Important Notes

- This is a **SIMULATION** with mock drivers
- For **production**, replace mock drivers with real hardware interfaces
- All data is **generated locally** - no external connections
- **Safe to run** - no destructive operations

## 📞 Support

- **Issues**: Check console output for error messages
- **Questions**: Review documentation files
- **Bugs**: Check tests with `pytest tests/ -v`

---

## One-Line Start

```bash
cd /Users/xanderlouw/CascadeProjects/C2 && python3 main.py
```

**That's it! You're now running a Counter-UAS C2 system! 🎉**
