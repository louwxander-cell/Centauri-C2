// StatusIndicatorSimple.qml - Simple clickable status indicator
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

RowLayout {
    id: root
    
    // Properties
    property string sensorName: "SENSOR"
    property string status: "offline"  // "offline", "standby", "online"
    property bool interactive: false
    
    // Signals
    signal clicked()
    
    spacing: 6
    
    // Status color mapping
    function getStatusColor() {
        if (status === "online") return "#10B981"      // Green
        if (status === "standby") return "#F59E0B"     // Orange
        return "#64748B"                                // Gray
    }
    
    // Status dot
    Rectangle {
        width: 7
        height: 7
        radius: 3.5
        color: getStatusColor()
        
        // Pulse animation for online
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
        font.family: "SF Pro Display"
        font.pixelSize: 10
        font.weight: Font.Medium
        color: getStatusColor()
    }
    
    // Mouse area for interaction
    MouseArea {
        anchors.fill: parent
        enabled: root.interactive && (status === "standby" || status === "online")
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        hoverEnabled: true
        
        onClicked: {
            console.log("[StatusIndicator] Clicked:", root.sensorName, "Status:", status)
            root.clicked()
        }
        
        onEntered: {
            if (enabled) {
                parent.opacity = 0.7
            }
        }
        
        onExited: {
            parent.opacity = 1.0
        }
    }
}
