# Active Tracks List - Classification Update

## Overview
Updated the Active Tracks list to display multiclass track classifications instead of the old basic type field, with color-coding matching the tactical display.

## Changes Made

### 1. ✅ Display Classification Field
**Before**: Showed `type` field (UAV, BIRD, UNKNOWN)
**After**: Shows `classification` field with fallback to `type`

### 2. ✅ Formatted Display Names
**Readable Labels**: Converted technical names to user-friendly format

| Technical Name | Display Name |
|----------------|--------------|
| `UAV_MULTI_ROTOR` | Multi-Rotor |
| `UAV_FIXED_WING` | Fixed-Wing |
| `UNDECLARED` | Undeclared |
| `UAV` | UAV |
| `WALKER` | WALKER |
| `PLANE` | PLANE |
| `BIRD` | BIRD |
| `VEHICLE` | VEHICLE |
| `CLUTTER` | CLUTTER |

### 3. ✅ Color-Coded Classifications
**Matches Tactical Display**: Same color scheme for consistency

```javascript
"UAV"              → #DC143C  (Crimson)
"UAV_MULTI_ROTOR"  → #8B0000  (Dark Red)
"UAV_FIXED_WING"   → #FF6600  (Bright Orange)
"WALKER"           → #4169E1  (Royal Blue)
"PLANE"            → #FFD700  (Gold)
"BIRD"             → #00CED1  (Dark Turquoise)
"VEHICLE"          → #9370DB  (Medium Purple)
"CLUTTER"          → #808080  (Gray)
"UNDECLARED"       → #D3D3D3  (Light Gray)
"UNKNOWN"          → #00E5FF  (Cyan - fallback)
```

### 4. ✅ Increased Width
**Column Width**: 70px → 85px to accommodate longer classification names

## Implementation

### Code Changes

**File**: `ui/components/CustomTrackList.qml` (lines 309-342)

```qml
// Classification badge - multiclass (matches tactical display colors)
Text {
    text: {
        if (!trackContainer.trackData) return ""
        // Use classification if available, fallback to type
        var classification = trackContainer.trackData.classification || trackContainer.trackData.type
        // Format for display
        if (classification === "UAV_MULTI_ROTOR") return "Multi-Rotor"
        if (classification === "UAV_FIXED_WING") return "Fixed-Wing"
        if (classification === "UNDECLARED") return "Undeclared"
        return classification
    }
    font.family: Theme.fontFamily
    font.pixelSize: 10
    font.weight: Font.Medium
    color: {
        if (!trackContainer.trackData) return Theme.textTertiary
        var classification = trackContainer.trackData.classification || trackContainer.trackData.type
        // Match track classification colors
        if (classification === "UAV") return "#DC143C"
        if (classification === "UAV_MULTI_ROTOR") return "#8B0000"
        if (classification === "UAV_FIXED_WING") return "#FF6600"
        if (classification === "WALKER") return "#4169E1"
        if (classification === "PLANE") return "#FFD700"
        if (classification === "BIRD") return "#00CED1"
        if (classification === "VEHICLE") return "#9370DB"
        if (classification === "CLUTTER") return "#808080"
        if (classification === "UNDECLARED") return "#D3D3D3"
        if (classification === "UNKNOWN") return "#00E5FF"
        return Theme.textSecondary
    }
    Layout.preferredWidth: 85
    horizontalAlignment: Text.AlignLeft
}
```

## Visual Comparison

### Before:
```
ID    TYPE      SENSOR  RANGE  CONF
5101  UAV       ◉       1200m  ●
5102  BIRD      ◉       800m   ●
5103  UNKNOWN   ≋       1500m  ●
```
**Limited classifications** (only 3 types)

### After:
```
ID    CLASSIFICATION  SENSOR  RANGE  CONF
5101  Multi-Rotor     ◉       1200m  ●
5102  Fixed-Wing      ◉       800m   ●
5103  BIRD            ◉       1500m  ●
5104  WALKER          ◉       600m   ●
5105  PLANE           ◈       2000m  ●
5106  VEHICLE         ◉       400m   ●
5107  CLUTTER         ◉       300m   ●
5108  Undeclared      ≋       1800m  ●
```
**Full 9-class system** with color-coding

## Benefits

### Consistency
- ✅ **Matches tactical display** - Same colors throughout UI
- ✅ **Matches legend** - Colors align with Track Class Legend
- ✅ **Unified system** - One classification scheme everywhere

### Clarity
- ✅ **More specific** - Distinguishes Multi-Rotor from Fixed-Wing
- ✅ **Color-coded** - Quick visual identification
- ✅ **Readable labels** - User-friendly names

### Functionality
- ✅ **Backward compatible** - Falls back to `type` if `classification` not available
- ✅ **Dynamic** - Updates when classification changes
- ✅ **Filtered** - Works with classification visibility filters

## Integration

### Works With:
1. **Track Class Legend** - Colors match exactly
2. **Tactical Display** - Same color scheme
3. **Classification Filters** - Respects visibility settings
4. **Threat Prioritization** - Shows only allowed classes

### Data Flow:
```
Mock Engine
    ↓
Track Data (with classification field)
    ↓
Bridge (exposes classification property)
    ↓
Active Tracks List (displays with color)
```

## Testing

### Scenario 5 (Stress Test)
With 25 tracks, Active Tracks list should show:

1. **Multi-Rotor** tracks in dark red
2. **Fixed-Wing** tracks in bright orange
3. **BIRD** tracks in turquoise
4. **WALKER** tracks in blue
5. **PLANE** tracks in gold
6. **VEHICLE** tracks in purple
7. **CLUTTER** tracks in gray
8. **Undeclared** tracks in light gray

### Visual Verification:
- ✅ Each track shows correct classification name
- ✅ Colors match tactical display dots
- ✅ Colors match Track Class Legend
- ✅ No "UAV" generic labels (except for UAV class)

## Files Modified

**`ui/components/CustomTrackList.qml`** (lines 309-342):
- Changed from `trackData.type` to `trackData.classification`
- Added fallback to `type` for backward compatibility
- Added display name formatting
- Updated color mapping to match new palette
- Increased column width from 70px to 85px
- Reduced font size from 11px to 10px (to fit longer names)

## Future Enhancements

Potential additions:
1. **Confidence indicator** - Show classification confidence %
2. **Tooltip** - Hover to see all class probabilities
3. **Sorting by class** - Group tracks by classification
4. **Class icons** - Visual symbols for each class
5. **Color legend** - Mini legend in Active Tracks header
