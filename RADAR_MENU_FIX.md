# Radar Menu Fix - Dropdown Implementation

## Issue
The dropdown menu was not appearing when clicking the radar status indicator.

## Root Cause
The custom `StatusIndicator.qml` component had compatibility issues with the Menu system in Qt6.

## Solution
Replaced the custom component with an inline implementation directly in `Main.qml` using:
- `Menu` with `popup()` method
- Direct `MouseArea` with click handling
- Inline status color logic

## Implementation

### Radar Status Indicator (Main.qml)

```qml
RowLayout {
    spacing: 6
    
    // Status dot with color based on status
    Rectangle {
        width: 7
        height: 7
        radius: 3.5
        color: {
            if (systemStatus.radarStatus === "online") return "#10B981"  // Green
            if (systemStatus.radarStatus === "standby") return "#F59E0B" // Orange
            return "#64748B"  // Gray
        }
        
        // Pulse animations for online/standby
    }
    
    // Sensor name text
    Text {
        text: "ECHOGUARD"
        // ... color matches dot
    }
    
    // Mouse area for clicking
    MouseArea {
        anchors.fill: parent
        enabled: systemStatus && (systemStatus.radarStatus === "standby" || systemStatus.radarStatus === "online")
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        
        onClicked: {
            radarMenu.popup()  // Show menu
        }
    }
    
    // Dropdown menu
    Menu {
        id: radarMenu
        
        MenuItem {
            text: "Connect"
            visible: systemStatus && systemStatus.radarStatus === "standby"
            onTriggered: {
                bridge.connect_radar()
            }
        }
        
        MenuItem {
            text: "Disconnect"
            visible: systemStatus && systemStatus.radarStatus === "online"
            onTriggered: {
                bridge.disconnect_radar()
            }
        }
    }
}
```

## How to Use

1. **Start Application**
   - ECHOGUARD indicator shows **ORANGE** (standby)
   - Cursor changes to pointer when hovering

2. **Click the Indicator**
   - Click anywhere on the ECHOGUARD text or dot
   - Dropdown menu appears

3. **Select Action**
   - **Standby (Orange)**: Shows "Connect" option
   - **Online (Green)**: Shows "Disconnect" option

4. **Console Output**
   ```
   [UI] Radar indicator clicked, status: standby
   [UI] Radar connect requested
   [BRIDGE] Radar connect requested
   [BRIDGE] Connected to radar command port
   [BRIDGE] Radar initialized
   [BRIDGE] ✓ Radar started and streaming
   [UI] Connect result: true
   ```

## Testing Checklist

- [ ] Click orange ECHOGUARD indicator
- [ ] Verify dropdown menu appears
- [ ] Select "Connect"
- [ ] Verify indicator turns green
- [ ] Click green indicator
- [ ] Verify "Disconnect" option appears
- [ ] Select "Disconnect"
- [ ] Verify indicator returns to orange

## Status Colors

- **Gray (#64748B)**: Offline - not clickable
- **Orange (#F59E0B)**: Standby - clickable, shows "Connect"
- **Green (#10B981)**: Online - clickable, shows "Disconnect"

## Files Modified

1. `ui/Main.qml` - Inline radar status indicator with menu
2. `ui/components/StatusIndicator.qml` - Original component (not used for radar)
3. `ui/components/StatusIndicatorSimple.qml` - Simplified version (backup)

## Notes

- GPS, SKYVIEW, and GUNNER still use the `StatusIndicator` component (non-interactive)
- Only ECHOGUARD uses the inline implementation with menu
- Menu appears at cursor position when clicked
- Menu automatically closes when clicking outside or selecting an option

## Future Improvements

- Make StatusIndicator component work properly with Menu
- Add keyboard shortcuts (e.g., Ctrl+R to connect radar)
- Add confirmation dialog for disconnect
- Show connection progress indicator
