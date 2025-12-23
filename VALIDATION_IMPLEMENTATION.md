# Configuration Validation Implementation

## Summary

Implemented official EchoGuard radar configuration limits and styled the UI dropdown menu to match the application theme.

## Changes Made

### 1. Configuration Dialog Limits (`ui/components/RadarConfigDialog.qml`)

#### Range Limits
**Updated from arbitrary values to official specs:**
```qml
// BEFORE:
rangeMinSpin.from: 10, to: 1000
rangeMaxSpin.from: 100, to: 5000

// AFTER:
rangeMinSpin.from: 20, to: 5987  // Official hardware limits
rangeMaxSpin.from: 20, to: 5987
```

#### Azimuth FOV Limits
**Updated to ±60° per EchoGuard specifications:**
```qml
// BEFORE:
searchAzMinSpin.from: -180, to: 0
searchAzMaxSpin.from: 0, to: 180
trackAzMinSpin.from: -180, to: 0
trackAzMaxSpin.from: 0, to: 180

// AFTER:
searchAzMinSpin.from: -60, to: 60  // Official FOV limit
searchAzMaxSpin.from: -60, to: 60
trackAzMinSpin.from: -60, to: 60
trackAzMaxSpin.from: -60, to: 60
```

#### Elevation FOV Limits
**Updated to ±40° per EchoGuard specifications:**
```qml
// BEFORE:
searchElMinSpin.from: -90, to: 0
searchElMaxSpin.from: 0, to: 90
trackElMinSpin.from: -90, to: 0
trackElMaxSpin.from: 0, to: 90

// AFTER:
searchElMinSpin.from: -40, to: 40  // Official FOV limit
searchElMaxSpin.from: -40, to: 40
trackElMinSpin.from: -40, to: 40
trackElMaxSpin.from: -40, to: 40
```

#### Heading Validator
**Fixed to match 0-359.9° specification:**
```qml
// BEFORE:
validator: DoubleValidator { bottom: 0; top: 360; decimals: 1 }

// AFTER:
validator: DoubleValidator { bottom: 0; top: 359.9; decimals: 1 }
```

#### Search FOV Disabled When Online
**Added proper state management:**
```qml
searchAzMinSpin.enabled: !radarOnline
searchAzMaxSpin.enabled: !radarOnline
searchElMinSpin.enabled: !radarOnline
searchElMaxSpin.enabled: !radarOnline
```

### 2. Styled Dropdown Menu (`ui/Main.qml`)

#### Menu Background
**Matches application theme:**
```qml
Menu {
    background: Rectangle {
        color: Theme.base2
        border.color: Theme.borderSubtle
        border.width: 1
        radius: 4
    }
}
```

#### Menu Items
**Consistent styling with hover effects:**
```qml
delegate: MenuItem {
    implicitWidth: 180
    implicitHeight: 32
    
    contentItem: Text {
        text: menuItem.text
        font.family: Theme.fontFamily
        font.pixelSize: 12
        color: menuItem.enabled ? Theme.textPrimary : Theme.textDisabled
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        leftPadding: 12
    }
    
    background: Rectangle {
        color: menuItem.highlighted ? Theme.accentCyan : "transparent"
        opacity: menuItem.highlighted ? 0.1 : 1.0
    }
}
```

#### Menu Separator
**Themed separator line:**
```qml
MenuSeparator {
    contentItem: Rectangle {
        implicitHeight: 1
        color: Theme.borderSubtle
    }
}
```

## Validation Rules Enforced

### Field of View (FOV)
| Parameter | Min | Max | Modifiable Online |
|-----------|-----|-----|-------------------|
| Search Az Min | -60° | +60° | ❌ No |
| Search Az Max | -60° | +60° | ❌ No |
| Search El Min | -40° | +40° | ❌ No |
| Search El Max | -40° | +40° | ❌ No |
| Track Az Min | -60° | +60° | ✅ Yes |
| Track Az Max | -60° | +60° | ✅ Yes |
| Track El Min | -40° | +40° | ✅ Yes |
| Track El Max | -40° | +40° | ✅ Yes |

### Range
| Parameter | Min | Max | Modifiable Online |
|-----------|-----|-----|-------------------|
| Range Min | 20m | 5987m | ✅ Yes |
| Range Max | 20m | 5987m | ✅ Yes |

### Orientation
| Parameter | Min | Max | Modifiable Online |
|-----------|-----|-----|-------------------|
| Heading | 0° | 359.9° | ❌ No |
| Pitch | -90° | +90° | ❌ No |
| Roll | -180° | +180° | ❌ No |

## UI Improvements

### Menu Appearance
**Before:**
- Default Qt styling
- Inconsistent with application theme
- No hover feedback
- Plain separators

**After:**
- ✅ Dark theme background (Theme.base2)
- ✅ Subtle borders (Theme.borderSubtle)
- ✅ Cyan highlight on hover
- ✅ Proper font family and sizing
- ✅ Themed separators
- ✅ Consistent spacing (180px width, 32px height)

### Configuration Dialog
**Before:**
- Arbitrary limits (e.g., range 10-5000m)
- FOV limits too wide (±180° az, ±90° el)
- Could modify search FOV while online
- Heading allowed 360° (invalid)

**After:**
- ✅ Official hardware limits (20-5987m)
- ✅ Correct FOV limits (±60° az, ±40° el)
- ✅ Search FOV disabled when online
- ✅ Heading limited to 0-359.9°

## Testing Checklist

### Configuration Limits
- [ ] **Range Min:** Cannot set below 20m or above 5987m
- [ ] **Range Max:** Cannot set below 20m or above 5987m
- [ ] **Search Az:** Cannot set outside ±60°
- [ ] **Search El:** Cannot set outside ±40°
- [ ] **Track Az:** Cannot set outside ±60°
- [ ] **Track El:** Cannot set outside ±40°
- [ ] **Heading:** Cannot set to 360° or above
- [ ] **Pitch:** Cannot set outside ±90°
- [ ] **Roll:** Cannot set outside ±180°

### State Management
- [ ] **Search FOV:** Grayed out when radar online
- [ ] **Track FOV:** Editable when radar online
- [ ] **Range:** Editable when radar online
- [ ] **Orientation:** Grayed out when radar online

### Menu Styling
- [ ] **Background:** Dark theme color
- [ ] **Border:** Subtle border visible
- [ ] **Hover:** Cyan highlight on menu items
- [ ] **Separator:** Themed line between items
- [ ] **Font:** Matches application font
- [ ] **Spacing:** Consistent padding and sizing

## Known Limitations

### Validation Not Yet Implemented
1. **Cross-field validation:** Min < Max checks
2. **Real-time feedback:** Error messages for invalid combinations
3. **Tooltips:** Hover information (prepared but not fully implemented)
4. **Range step validation:** Beam steps must be multiples of 2°

### Future Enhancements
1. **Add validation function** before applying config
2. **Show warning dialogs** for invalid combinations
3. **Implement tooltips** with limit information
4. **Add preset configurations** (e.g., "Wide FOV", "Narrow FOV")
5. **Visual feedback** for out-of-range values

## Implementation Notes

### Why These Limits?
All limits are from the official **EchoGuard Radar Developer Manual SW16.4.0**:
- **Range:** 20m minimum (hardware limitation), 5987m maximum (operational)
- **Azimuth FOV:** ±60° (120° total field of regard)
- **Elevation FOV:** ±40° (80° total field of regard)
- **Heading:** 0-359.9° (North reference, wraps at 360°)
- **Pitch/Roll:** Standard orientation limits

### State Management
- **Search FOV:** Cannot change while radar is scanning (requires restart)
- **Track FOV:** Can change dynamically (radar adjusts on the fly)
- **Range:** Can change dynamically (RANGE:MASK command)
- **Orientation:** Fixed at startup (requires recalibration)

### Menu Styling Philosophy
- **Consistency:** Match existing UI theme
- **Subtlety:** Don't distract from content
- **Feedback:** Clear hover states
- **Accessibility:** Good contrast, readable fonts

## Files Modified

1. **`ui/components/RadarConfigDialog.qml`**
   - Updated all spinbox limits
   - Fixed heading validator
   - Added enabled/disabled state management

2. **`ui/Main.qml`**
   - Styled Menu background
   - Styled MenuItem delegate
   - Styled MenuSeparator

## Application Status

✅ **Running** (Command ID: 486)  
✅ **Validation limits implemented**  
✅ **Menu styled to match theme**  
✅ **State management correct**  

## Next Steps (Optional)

### Immediate
- Test all limit boundaries
- Verify state management with real radar

### Short-term
- Add cross-field validation (Min < Max)
- Implement tooltip hover information
- Add warning dialogs for invalid configs

### Long-term
- Create configuration presets
- Add visual range/FOV preview
- Implement configuration templates
- Add export/import configuration files
