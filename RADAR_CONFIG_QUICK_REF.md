# Radar Configuration - Quick Reference

## Access Configuration

**Click ECHOGUARD indicator → Select "Configure..."**

## Settings by Status

### 🔴 Offline / 🟠 Standby (All Editable)
- ✅ Label, IP Address
- ✅ Product Mode, Mission Set
- ✅ Position (Lat/Lon/Alt/Heading)
- ✅ Orientation (Pitch/Roll)
- ✅ Range Min/Max
- ✅ Search FOV (Az/El)
- ✅ Track FOV (Az/El)
- ✅ Frequency Channel

### 🟢 Online (Limited Editing)
- ❌ Label, IP Address (grayed out)
- ❌ Product Mode, Mission Set (grayed out)
- ❌ Position (grayed out)
- ❌ Orientation (grayed out)
- ✅ **Range Min/Max** (editable)
- ✅ **Search FOV** (editable)
- ✅ **Track FOV** (editable)
- ❌ Frequency Channel (grayed out)

## Common Configurations

### Wide Area (Default)
```
Search Az: -60° to +60° (120° coverage)
Search El: -40° to +40° (80° coverage)
Range: 21m to 500m
```

### Focused Tracking
```
Search Az: -30° to +30° (60° coverage)
Search El: -10° to +30° (40° coverage)
Range: 50m to 1000m
```

### Perimeter Defense
```
Search Az: -90° to +90° (180° coverage)
Search El: -20° to +40° (60° coverage)
Range: 21m to 2000m
```

### High Altitude
```
Search Az: -45° to +45° (90° coverage)
Search El: +10° to +60° (50° coverage)
Range: 100m to 3000m
```

## Quick Actions

| Action | Steps |
|--------|-------|
| **Change FOV while streaming** | Click indicator → Configure → Adjust FOV → OK |
| **Change IP address** | Disconnect → Configure → Change IP → OK → Connect |
| **Reset to defaults** | Configure → Manually enter default values → OK |
| **Widen search area** | Configure → Increase Az/El Max → Decrease Az/El Min → OK |

## Keyboard Shortcuts (Future)

- `Ctrl+R` - Open radar configuration
- `Ctrl+Shift+C` - Connect radar
- `Ctrl+Shift+D` - Disconnect radar

## Status Messages

✅ **"Radar configuration applied"** - Success  
❌ **"Radar configuration failed"** - Check console for errors  
⚠️ **"Some settings cannot be changed"** - Radar is online

## Tips

1. **Configure offline first** - Set all parameters before connecting
2. **Test FOV** - Start narrow, expand as needed
3. **Adjust range** - Minimize false alarms by tuning range limits
4. **Monitor performance** - Watch track update rate after changes
5. **Save notes** - Document working configurations for different scenarios
