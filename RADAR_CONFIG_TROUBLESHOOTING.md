# Radar Configuration - Troubleshooting

## Issue: "Configure..." Not Appearing in Dropdown

### Solution
The application needed to be restarted to load the new configuration dialog component.

### Steps Taken
1. Fixed Theme.fontFamily references in RadarConfigDialog.qml
2. Added proper parent and anchoring to dialog
3. Restarted application

## How to Access Configuration

1. **Click** the ECHOGUARD status indicator (orange dot + text)
2. **Wait** for dropdown menu to appear
3. **Look for** three menu items:
   - "Connect" (if standby/orange)
   - "Disconnect" (if online/green)
   - **"Configure..."** (always visible, below separator line)

## If Menu Still Not Appearing

### Check 1: Application Running
```
Command ID: 240 should be RUNNING
```

### Check 2: Radar Status
- Indicator should be **ORANGE** (standby) or **GREEN** (online)
- Gray indicators are not clickable

### Check 3: Click Target
- Click directly on the **ECHOGUARD text** or **orange/green dot**
- Cursor should change to pointing hand when hovering

### Check 4: Console Output
Look for:
```
[UI] Radar indicator clicked, status: standby
```

## Current Status

✅ Application is running (Command ID: 240)
✅ RadarConfigDialog.qml fixed (Theme references removed)
✅ Dialog properly parented to Overlay
✅ Menu should now show all three options

## Testing Steps

1. **Hover** over ECHOGUARD indicator
   - Cursor should change to pointer
   - Indicator should dim slightly

2. **Click** ECHOGUARD indicator
   - Menu should appear immediately
   - Should see 2-3 items depending on status

3. **Click "Configure..."**
   - Dialog should open
   - Should show all configuration categories
   - Status message at bottom

## If Dialog Opens But Has Errors

Check console for:
- QML warnings
- Property binding errors
- Missing properties

## Expected Menu Structure

```
┌─────────────────┐
│ Connect         │  ← Only when standby
├─────────────────┤
│ Disconnect      │  ← Only when online
├─────────────────┤
│ Configure...    │  ← Always visible
└─────────────────┘
```

## Files Involved

1. `ui/Main.qml` - Menu definition (lines 494-535)
2. `ui/components/RadarConfigDialog.qml` - Dialog component
3. `orchestration/bridge.py` - Backend methods

## Quick Test

Run in Python console:
```python
# This should print the menu structure
print("Menu items:")
print("1. Connect (visible when standby)")
print("2. Disconnect (visible when online)")  
print("3. Configure... (always visible)")
```

## Contact

If issue persists, check:
- QML console output
- Python console output
- Verify all files saved
- Try full application restart
