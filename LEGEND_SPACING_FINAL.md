# Track Class Legend - Final Spacing Adjustments

## Changes Made

### 1. ✅ Reduced Space Above First Item (UAV)
**Problem**: Excessive space between separator line and first classification item

**Fix**: 
- Added `Layout.topMargin: 2` to legend items container
- Set separator margins to 0
- Reduced from ~8px gap to 2px gap

---

### 2. ✅ Reduced Space Below Last Item (Undeclared)
**Problem**: Excessive space between last classification item and bottom border

**Fix**:
- Added `Layout.bottomMargin: 2` to legend items container
- Reduced from ~8px gap to 2px gap

---

### 3. ✅ Adjusted Total Height
**Fix**: Reduced expanded height from 250px to 240px
```qml
height: collapsed ? 32 : 240  // Was 250
```

---

## Summary of Changes

| Element | Before | After | Change |
|---------|--------|-------|--------|
| **Space Above UAV** | ~8px | 2px | -6px |
| **Space Below Undeclared** | ~8px | 2px | -6px |
| **Expanded Height** | 250px | 240px | -10px |

---

## Code Changes

### TrackClassLegend.qml

**Height:**
```qml
height: collapsed ? 32 : 240  // Reduced from 250
```

**Separator:**
```qml
Rectangle {
    Layout.fillWidth: true
    height: 1
    color: Theme.borderSubtle
    visible: !root.collapsed
    Layout.topMargin: 0      // NEW
    Layout.bottomMargin: 0   // NEW
}
```

**Legend Items Container:**
```qml
ColumnLayout {
    Layout.fillWidth: true
    Layout.topMargin: 2      // NEW - minimal space above UAV
    Layout.bottomMargin: 2   // NEW - minimal space below Undeclared
    spacing: 6
    visible: !root.collapsed
    ...
}
```

---

## Visual Result

### Before:
```
┌─────────────────────┐
│ TRACK CLASS LEGEND  │
├─────────────────────┤
│                     │ ← Extra space
│ 🔴 UAV              │
│ 🔴 UAV Multi-Rotor  │
│ 🟠 UAV Fixed-Wing   │
│ 🔵 Walker           │
│ 🟡 Plane            │
│ 🔷 Bird             │
│ 🟣 Vehicle          │
│ ⚫ Clutter          │
│ ⚪ Undeclared       │
│                     │ ← Extra space
└─────────────────────┘
```

### After:
```
┌─────────────────────┐
│ TRACK CLASS LEGEND  │
├─────────────────────┤
│ 🔴 UAV              │ ← Tight spacing
│ 🔴 UAV Multi-Rotor  │
│ 🟠 UAV Fixed-Wing   │
│ 🔵 Walker           │
│ 🟡 Plane            │
│ 🔷 Bird             │
│ 🟣 Vehicle          │
│ ⚫ Clutter          │
│ ⚪ Undeclared       │ ← Tight spacing
└─────────────────────┘
```

---

## Files Modified

**`ui/components/TrackClassLegend.qml`**
- Line 11: Height reduced to 240px
- Lines 87-88: Added separator margins (0px)
- Lines 94-95: Added container top/bottom margins (2px each)

---

## Result

- ✅ Eliminated wasted space above UAV
- ✅ Eliminated wasted space below Undeclared
- ✅ More compact and professional appearance
- ✅ Total height reduced by 10px
- ✅ Legend fits better on screen
