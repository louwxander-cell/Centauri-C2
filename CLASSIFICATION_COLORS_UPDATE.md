# Track Classification - Color Update

## Color Palette Changed to Match RadarUI

### New Colors (Exact Match to RadarUI)

| Class | Old Color | New Color | Hex | Description |
|-------|-----------|-----------|-----|-------------|
| **UAV** | Bright Red | Crimson Red | `#DC143C` | More distinct, classic crimson |
| **UAV Multi-Rotor** | Orange | Dark Red | `#8B0000` | Darker red, distinguishable from UAV |
| **UAV Fixed-Wing** | Light Orange | Dark Orange | `#FF8C00` | True orange, clear distinction |
| **Walker** | Blue | Royal Blue | `#4169E1` | Brighter, more visible blue |
| **Plane** | Yellow | Gold | `#FFD700` | Rich gold, easier to see |
| **Bird** | Cyan | Dark Turquoise | `#00CED1` | Deeper turquoise, better contrast |
| **Vehicle** | Purple | Medium Purple | `#9370DB` | Softer purple, more visible |
| **Clutter** | Gray | Gray | `#808080` | Standard gray (unchanged) |
| **Undeclared** | White | Light Gray | `#D3D3D3` | Light gray, better visibility on dark background |

## Improvements

### Before (Original Colors):
- ❌ Some colors too similar (bright red, orange, light orange)
- ❌ White undeclared hard to see with borders
- ❌ Colors not matching industry standard (RadarUI)

### After (RadarUI Colors):
- ✅ Better color separation and distinction
- ✅ Improved visibility on dark backgrounds
- ✅ Matches RadarUI color scheme
- ✅ More professional appearance
- ✅ Easier to identify track types at a glance

## Color Psychology

- **Red Tones** (UAV, Multi-Rotor): Threat/attention
- **Orange** (Fixed-Wing): Caution
- **Blue** (Walker): Neutral/ground
- **Gold** (Plane): High-value/aircraft
- **Turquoise** (Bird): Natural/non-threat
- **Purple** (Vehicle): Ground/non-aerial
- **Gray** (Clutter): Low priority/noise
- **Light Gray** (Undeclared): Unknown/uncertain

## Files Modified

1. **`ui/Main.qml`** (lines 26-38)
   - Updated `trackClassColors` property
   - Applied to all track dots and tails

2. **`ui/components/TrackClassLegend.qml`** (lines 18-28)
   - Updated `classColors` property
   - Legend now shows exact RadarUI colors

## Testing

1. **Load Scenario 5**: Click TEST → Scenario 5
2. **Expand Legend**: Click arrow to see all colors
3. **Verify Colors**: Compare with RadarUI image
4. **Check Visibility**: All colors should be clearly distinguishable

## Color Accessibility

All colors have been chosen for:
- ✅ High contrast on dark backgrounds
- ✅ Distinguishable from each other
- ✅ Colorblind-friendly (where possible)
- ✅ Professional military/tactical appearance

## Reference

Colors match the official EchoGuard RadarUI classification palette as shown in the radar configuration interface.
