# Track Classification - Quick Reference

## 🎨 Track Class Colors

| Class | Color | Hex | Use Case |
|-------|-------|-----|----------|
| **UAV** | 🔴 Red | #EF4444 | General UAV |
| **UAV Multi-Rotor** | 🟠 Orange | #F97316 | Quadcopters (DJI, etc.) |
| **UAV Fixed-Wing** | 🟧 Light Orange | #FB923C | Fixed-wing drones |
| **Walker** | 🔵 Blue | #3B82F6 | Pedestrians |
| **Plane** | 🟡 Yellow | #EAB308 | Crewed aircraft |
| **Bird** | 🔷 Cyan | #06B6D4 | Avian targets |
| **Vehicle** | 🟣 Purple | #A855F7 | Ground vehicles |
| **Clutter** | ⚫ Gray | #6B7280 | Environmental noise |
| **Undeclared** | ⚪ White | #FFFFFF | Unknown/low confidence |

## ⚙️ Configuration

### Operation Modes
- **0 - Walkers**: Optimized for pedestrians (classifier disabled)
- **1 - Drones**: Optimized for small UAVs (classifier enabled) ← **Default**
- **2 - Aircraft**: Optimized for crewed aircraft (classifier enabled)

### Class Declaration Threshold
- **Default**: 90%
- **Range**: 0-100%
- **Meaning**: Minimum confidence to declare a class
- **Lower**: More classifications, less strict
- **Higher**: Fewer classifications, more strict

### Default Visibility
```
✅ UAV
✅ UAV Multi-Rotor
✅ UAV Fixed-Wing
❌ Walker
❌ Plane
✅ Bird
❌ Vehicle
✅ Clutter
✅ Undeclared
```

## 🎯 Quick Actions

### Show Only UAVs
1. Open Radar Config
2. Uncheck all except UAV classes
3. Click OK

### Show Everything
1. Open Radar Config
2. Check all 9 classes
3. Click OK

### Adjust Sensitivity
1. Open Radar Config
2. Slide threshold left (less strict) or right (more strict)
3. Click OK

### Collapse Legend
- Click ▲/▼ arrow in legend top-right

## 📍 UI Locations

- **Legend**: Top-left of tactical display
- **Config**: Radar status indicator → Configure → "Track Classification" section
- **Track Colors**: Automatically applied to all tracks on display

## 🧪 Testing

**Load Stress Test**: TEST button → Scenario 5
- 25 tracks with varied classifications
- Tests all 9 classes
- Good for verifying colors and filtering

## 💡 Tips

1. **C-UAS Mission**: Show only UAV classes, hide birds/clutter
2. **Border Security**: Show walkers and vehicles, hide birds
3. **Airspace Monitoring**: Show planes and UAVs, hide ground targets
4. **Reduce Clutter**: Increase threshold to 95%+
5. **See Everything**: Lower threshold to 50-70%
