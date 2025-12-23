# RADAR FOV Box - Collapsible Feature

## Overview
Made the RADAR FOV information box collapsible with a default collapsed state to reduce screen clutter and maximize tactical display space.

## Changes Made

### 1. ✅ Added Collapse/Expand Button
**Location**: Top-right corner of RADAR FOV box

**Features**:
- ▼ Down arrow when collapsed
- ▲ Up arrow when expanded
- Hover effect (background changes)
- Clickable to toggle state
- Smooth animation (200ms)

### 2. ✅ Default State: Collapsed
**Initial State**: Collapsed (showing only header)
```qml
property bool fovCollapsed: true  // Default collapsed
```

**Collapsed Height**: 32px (just the header)
**Expanded Height**: 115px (full content)

### 3. ✅ Smooth Animation
**Animation**: Height transitions smoothly when toggling
```qml
Behavior on height {
    NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
}
```

### 4. ✅ Content Visibility
**When Collapsed**:
- ✅ "RADAR FOV" header visible
- ✅ Collapse button visible
- ❌ Separator line hidden
- ❌ FOV data hidden

**When Expanded**:
- ✅ Full content visible
- ✅ Az, Total, Range, Heading data shown

## Implementation Details

### Code Structure

**File**: `ui/Main.qml` (lines 1791-1934)

```qml
Rectangle {
    id: fovInfoBox
    width: 180
    height: fovCollapsed ? 32 : 115
    
    property bool fovCollapsed: true  // Default collapsed
    
    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
    }
    
    ColumnLayout {
        // Header with collapse button
        RowLayout {
            Text { text: "RADAR FOV" }
            
            Rectangle {
                // Collapse button
                Text { text: fovCollapsed ? "▼" : "▲" }
                MouseArea {
                    onClicked: fovCollapsed = !fovCollapsed
                }
            }
        }
        
        // Separator (hidden when collapsed)
        Rectangle {
            visible: !fovCollapsed
        }
        
        // FOV Data (hidden when collapsed)
        GridLayout {
            visible: !fovCollapsed
            // Az, Total, Range, Heading
        }
    }
}
```

## User Experience

### Before:
```
┌─────────────────────┐
│ RADAR FOV           │
├─────────────────────┤
│ Az: -50° to 50°     │
│ Total: 100°         │
│ Range: 21m - 1000m  │
│ Heading: 0.0°       │
└─────────────────────┘
```
**Always visible** - Takes up 115px of screen space

### After (Default - Collapsed):
```
┌─────────────────────┐
│ RADAR FOV        ▼  │
└─────────────────────┘
```
**Collapsed by default** - Takes up only 32px

### After (Expanded):
```
┌─────────────────────┐
│ RADAR FOV        ▲  │
├─────────────────────┤
│ Az: -50° to 50°     │
│ Total: 100°         │
│ Range: 21m - 1000m  │
│ Heading: 0.0°       │
└─────────────────────┘
```
**Click to expand** - Full 115px when needed

## Benefits

### Space Optimization
- ✅ **Saves 83px** of vertical space when collapsed
- ✅ More room for tactical display
- ✅ Less visual clutter
- ✅ Cleaner interface

### User Control
- ✅ Operator can expand when needed
- ✅ Quick access to FOV data
- ✅ Smooth, professional animation
- ✅ Consistent with Track Class Legend behavior

### Default State Rationale
**Why collapsed by default?**
1. FOV data is **static** (doesn't change frequently)
2. Operator knows FOV from configuration
3. Tactical display space is **premium**
4. Can expand when verification needed

## Comparison with Track Class Legend

| Feature | Track Class Legend | RADAR FOV Box |
|---------|-------------------|---------------|
| **Collapsible** | ✅ Yes | ✅ Yes |
| **Default State** | Collapsed | Collapsed |
| **Collapsed Height** | 32px | 32px |
| **Expanded Height** | 240px | 115px |
| **Button Style** | ▼/▲ arrows | ▼/▲ arrows |
| **Animation** | 200ms | 200ms |
| **Location** | Top-left | Bottom-left |

Both boxes now have **consistent behavior**!

## Testing

1. **Start Application**
   - ✅ RADAR FOV box should be collapsed (32px height)
   - ✅ Only "RADAR FOV ▼" header visible

2. **Click Expand Button**
   - ✅ Box smoothly expands to 115px
   - ✅ Arrow changes to ▲
   - ✅ FOV data becomes visible

3. **Click Collapse Button**
   - ✅ Box smoothly collapses to 32px
   - ✅ Arrow changes to ▼
   - ✅ FOV data hidden

4. **Hover Button**
   - ✅ Background color changes (hover effect)
   - ✅ Cursor changes to pointer

## Files Modified

**`ui/Main.qml`** (lines 1791-1934):
- Added `fovCollapsed` property (default: true)
- Added collapse button with MouseArea
- Added height animation behavior
- Added visibility controls for content
- Reduced margins from 10px to 8px (consistency)

## Future Enhancements

Potential additions:
1. **Remember state** - Save collapsed/expanded preference
2. **Keyboard shortcut** - Toggle with hotkey
3. **Auto-expand** - When FOV changes
4. **Tooltip** - Show FOV summary on hover when collapsed
