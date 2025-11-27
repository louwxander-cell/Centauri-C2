// SensorIndicator.qml
// Pill-shaped sensor status indicator with LED
import QtQuick
import QtQuick.Effects

Rectangle {
    id: root
    implicitWidth: 80
    implicitHeight: 28
    radius: Theme.radiusPill
    color: isOnline ? Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.08) : Qt.rgba(1, 1, 1, 0.02)
    border.width: 1
    border.color: isOnline ? Qt.rgba(statusColor.r, statusColor.g, statusColor.b, 0.15) : Theme.borderSubtle
    
    property string sensorName: "SENSOR"
    property bool isOnline: true
    property color statusColor: Theme.accentCyan
    
    // Smooth color transition
    Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
    Behavior on border.color { ColorAnimation { duration: Theme.durationMedium } }
    
    Row {
        anchors.centerIn: parent
        spacing: 6
        
        // LED indicator
        Rectangle {
            width: 8
            height: 8
            radius: 4
            anchors.verticalCenter: parent.verticalCenter
            color: root.isOnline ? root.statusColor : Theme.textTertiary
            
            // Glow effect when online
            layer.enabled: root.isOnline
            layer.effect: MultiEffect {
                shadowEnabled: true
                shadowColor: root.statusColor
                shadowOpacity: 0.8
                shadowBlur: 1.0
            }
            
            // Pulse animation when online
            SequentialAnimation on opacity {
                running: root.isOnline
                loops: Animation.Infinite
                NumberAnimation { to: 0.6; duration: 1000; easing.type: Easing.InOutSine }
                NumberAnimation { to: 1.0; duration: 1000; easing.type: Easing.InOutSine }
            }
            
            Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
        }
        
        // Sensor name
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: root.sensorName
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSmall
            font.weight: Theme.fontWeightSemiBold
            color: root.isOnline ? Theme.textPrimary : Theme.textTertiary
            
            Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
        }
    }
    
    // Hover effect
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        
        onEntered: {
            root.scale = 1.05
        }
        onExited: {
            root.scale = 1.0
        }
    }
    
    Behavior on scale {
        NumberAnimation { duration: Theme.durationFast; easing.type: Theme.easingStandard }
    }
}
