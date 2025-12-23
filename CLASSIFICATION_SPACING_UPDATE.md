# Track Classification - Spacing & Color Update

## Changes Made

### 1. ✅ UAV Fixed-Wing Color - More Orange
**Problem**: UAV Fixed-Wing (#FF8C00 dark orange) was too similar to Plane (#FFD700 gold)

**Fix**: Changed to bright orange `#FF6600`
- **Before**: `#FF8C00` (Dark Orange) - rgb(255, 140, 0)
- **After**: `#FF6600` (Bright Orange) - rgb(255, 102, 0)

**Result**: Much clearer distinction between Fixed-Wing (orange) and Plane (gold)

---

### 2. ✅ Increased Spacing Between Classifications
**Problem**: Items too close together, hard to read

**Fix**: Increased item spacing from 4px to 6px
```qml
spacing: 6  // Was 4
```

**Result**: Better readability, easier to distinguish individual items

---

### 3. ✅ Reduced Top/Bottom Margins
**Problem**: Unnecessary space above UAV and below Undeclared

**Fix**: Reduced top and bottom margins from 8px to 6px
```qml
anchors.topMargin: 6      // Was 8
anchors.bottomMargin: 6   // Was 8
```

**Result**: More compact legend, less wasted space

---

### 4. ✅ Adjusted Total Height
**Fix**: Increased expanded height from 235px to 250px to accommodate the increased item spacing
```qml
height: collapsed ? 32 : 250  // Was 235
```

---

## Summary of Spacing Changes

| Element | Before | After | Change |
|---------|--------|-------|--------|
| **Top Margin** | 8px | 6px | -2px |
| **Bottom Margin** | 8px | 6px | -2px |
| **Item Spacing** | 4px | 6px | +2px |
| **Expanded Height** | 235px | 250px | +15px |

---

## Color Comparison

### UAV Fixed-Wing
- **Old**: `#FF8C00` - Dark Orange
- **New**: `#FF6600` - Bright Orange ⭐
- **Difference**: More saturated, more red, clearly orange vs gold

### Visual Distinction
```
🔴 UAV              #DC143C  Crimson
🔴 UAV Multi-Rotor  #8B0000  Dark Red
🟠 UAV Fixed-Wing   #FF6600  Bright Orange ⭐ NEW
🔵 Walker           #4169E1  Royal Blue
🟡 Plane            #FFD700  Gold
```

Now Fixed-Wing is clearly **orange** while Plane is clearly **gold/yellow**!

---

## Files Modified

1. **`ui/Main.qml`** (line 30)
   - Updated UAV_FIXED_WING color to `#FF6600`

2. **`ui/components/TrackClassLegend.qml`**
   - Line 21: Updated color to `#FF6600`
   - Line 37: Added `anchors.topMargin: 6`
   - Line 38: Added `anchors.bottomMargin: 6`
   - Line 92: Increased spacing to `6`
   - Line 11: Increased height to `250`

---

## Visual Result

### Before:
- ❌ Fixed-Wing and Plane colors too similar
- ❌ Items cramped together
- ❌ Extra space at top and bottom

### After:
- ✅ Fixed-Wing clearly orange, Plane clearly gold
- ✅ Better spacing between items
- ✅ Tighter top/bottom margins
- ✅ More readable and professional

---

## Testing

1. **Load Scenario 5**: Click TEST → Scenario 5
2. **Expand Legend**: Click arrow
3. **Verify**:
   - ✅ Fixed-Wing is bright orange
   - ✅ Plane is gold/yellow
   - ✅ Clear distinction between them
   - ✅ Good spacing between all items
   - ✅ Compact top/bottom margins
