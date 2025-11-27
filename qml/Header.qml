// Header.qml
// Top navigation bar with title and sensor indicators
import QtQuick
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: root
    color: "transparent"
    
    property bool radarOnline: true
    property bool rfOnline: true
    property bool gpsOnline: true
    property bool rwsOnline: true
    
    // Background with blur effect
    Rectangle {
        anchors.fill: parent
        color: Theme.base1
        radius: Theme.radiusMedium
        opacity: 0.8
        
        layer.enabled: true
        layer.effect: MultiEffect {
            blurEnabled: true
            blur: 0.4
            blurMax: 16
            blurMultiplier: 0.5
        }
    }
    
    // Drop shadow
    layer.enabled: true
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowOpacity: 0.3
        shadowBlur: 0.6
        shadowVerticalOffset: 4
    }
    
    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Theme.cardPadding
        anchors.rightMargin: Theme.cardPadding
        spacing: Theme.itemSpacing
        
        // Title
        Text {
            Layout.fillWidth: true
            text: "TRIAD C2 — Counter-UAS Command & Control"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeTitle
            font.weight: Theme.fontWeightSemiBold
            color: Theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            
            // Subtle text glow
            layer.enabled: true
            layer.effect: MultiEffect {
                shadowEnabled: true
                shadowColor: Theme.accentCyan
                shadowOpacity: 0.1
                shadowBlur: 0.3
            }
        }
        
        // Sensor Status Indicators
        RowLayout {
            spacing: Theme.tightSpacing
            
            SensorIndicator {
                sensorName: "RADAR"
                isOnline: root.radarOnline
                statusColor: Theme.accentCyan
            }
            
            SensorIndicator {
                sensorName: "RF"
                isOnline: root.rfOnline
                statusColor: Theme.accentGreen
            }
            
            SensorIndicator {
                sensorName: "GPS"
                isOnline: root.gpsOnline
                statusColor: Theme.accentAmber
            }
            
            SensorIndicator {
                sensorName: "RWS"
                isOnline: root.rwsOnline
                statusColor: Theme.accentRed
            }
        }
    }
}
