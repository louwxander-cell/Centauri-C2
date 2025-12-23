// StatusIndicator.qml - Interactive sensor status indicator with dropdown menu
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."  // Import parent to access Theme

Item {
    id: root
    
    // Properties
    property string sensorName: "SENSOR"
    property string status: "offline"  // "offline", "standby", "online"
    property bool interactive: false   // Whether clicking opens menu
    
    // Debug: Log status changes
    onStatusChanged: {
        console.log("[StatusIndicator]", sensorName, "status changed to:", status)
    }
    
    Component.onCompleted: {
        console.log("[StatusIndicator]", sensorName, "initialized - status:", status, "interactive:", interactive)
    }
    
    // Signals
    signal connectRequested()
    signal disconnectRequested()
    signal configureRequested()
    
    width: implicitWidth
    height: implicitHeight
    implicitWidth: layout.implicitWidth
    implicitHeight: layout.implicitHeight
    
    // Status color mapping
    function getStatusColor() {
        switch(status) {
            case "online": return "#10B981"   // Green
            case "standby": return "#F59E0B"  // Orange/Amber
            case "offline": 
            default: return "#64748B"         // Gray
        }
    }
    
    RowLayout {
        id: layout
        spacing: 6
        
        // Status dot
        Rectangle {
            width: 7
            height: 7
            radius: 3.5
            color: getStatusColor()
            
            // Pulse animation for online status
            SequentialAnimation on opacity {
                running: status === "online"
                loops: Animation.Infinite
                NumberAnimation { to: 0.4; duration: 1000 }
                NumberAnimation { to: 1.0; duration: 1000 }
            }
            
            // Slow pulse for standby
            SequentialAnimation on opacity {
                running: status === "standby"
                loops: Animation.Infinite
                NumberAnimation { to: 0.6; duration: 1500 }
                NumberAnimation { to: 1.0; duration: 1500 }
            }
        }
        
        // Sensor name
        Text {
            text: root.sensorName
            font.family: Theme.fontFamily
            font.pixelSize: 10
            font.weight: Theme.fontWeightMedium
            color: getStatusColor()
        }
    }
    
    // Mouse area for interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        enabled: root.interactive && (status === "standby" || status === "online")
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        hoverEnabled: true
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        
        onClicked: (mouse) => {
            console.log("[StatusIndicator] Clicked:", root.sensorName, "Status:", status, "Interactive:", root.interactive)
            
            if (status === "standby" || status === "online") {
                // Position menu below the indicator
                contextMenu.x = 0
                contextMenu.y = root.height
                contextMenu.open()
                console.log("[StatusIndicator] Menu opened")
            } else {
                console.log("[StatusIndicator] Not clickable - status is:", status)
            }
        }
        
        onEntered: {
            if (enabled) {
                layout.opacity = 0.8
            }
        }
        
        onExited: {
            layout.opacity = 1.0
        }
    }
    
    // Context menu
    Menu {
        id: contextMenu
        
        // Position relative to the indicator
        Component.onCompleted: {
            console.log("[StatusIndicator] Menu created for:", root.sensorName)
        }
        
        MenuItem {
            text: "Connect"
            visible: status === "standby"
            height: visible ? implicitHeight : 0
            onTriggered: {
                console.log("[StatusIndicator] Connect triggered")
                root.connectRequested()
            }
        }
        
        MenuItem {
            text: "Disconnect"
            visible: status === "online"
            height: visible ? implicitHeight : 0
            onTriggered: {
                console.log("[StatusIndicator] Disconnect triggered")
                root.disconnectRequested()
            }
        }
        
        MenuSeparator {
            visible: status === "online"
            height: visible ? implicitHeight : 0
        }
        
        MenuItem {
            text: "Configure..."
            enabled: false  // Future feature
            onTriggered: {
                console.log("[StatusIndicator] Configure triggered")
                root.configureRequested()
            }
        }
    }
}
