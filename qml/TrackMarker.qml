// TrackMarker.qml
// Individual track marker on radar with halo and pulse
import QtQuick
import QtQuick.Effects

Item {
    id: root
    
    property var trackData: null
    property bool isSelected: false
    property real centerX: 0
    property real centerY: 0
    property real radarRadius: 200
    property real maxRange: 3000
    
    signal clicked()
    
    // Calculate position from polar coordinates
    property real rangeRatio: trackData ? (trackData.range / maxRange) : 0
    property real azimuthRad: trackData ? ((trackData.azimuth - 90) * Math.PI / 180) : 0
    property real pixelRadius: radarRadius * Math.min(rangeRatio, 1.0)
    
    x: centerX + pixelRadius * Math.cos(azimuthRad) - width / 2
    y: centerY + pixelRadius * Math.sin(azimuthRad) - height / 2
    
    width: 40
    height: 40
    
    // Smooth position animation
    Behavior on x { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
    Behavior on y { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
    
    // Halo glow
    Rectangle {
        anchors.centerIn: parent
        width: Theme.getThreatGlow(trackData ? trackData.status : "MED") * 2
        height: width
        radius: width / 2
        color: Theme.getStatusColor(trackData ? trackData.status : "MED")
        opacity: 0.3
        
        Behavior on width { NumberAnimation { duration: Theme.durationMedium } }
        Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
        
        layer.enabled: true
        layer.effect: MultiEffect {
            blurEnabled: true
            blur: 1.0
            blurMax: 32
            blurMultiplier: 1.0
        }
    }
    
    // Triangle marker
    Canvas {
        id: markerCanvas
        anchors.centerIn: parent
        width: 14
        height: 14
        rotation: trackData ? trackData.heading || 0 : 0
        
        Behavior on rotation {
            RotationAnimation { duration: Theme.durationMedium; direction: RotationAnimation.Shortest }
        }
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            
            var statusColor = Theme.getStatusColor(trackData ? trackData.status : "MED")
            
            // Triangle path
            ctx.beginPath()
            ctx.moveTo(width / 2, 0)  // Top
            ctx.lineTo(width, height)  // Bottom right
            ctx.lineTo(0, height)  // Bottom left
            ctx.closePath()
            
            // Fill
            ctx.fillStyle = statusColor
            ctx.fill()
            
            // Stroke
            ctx.strokeStyle = Qt.rgba(0, 0, 0, 0.5)
            ctx.lineWidth = 1
            ctx.stroke()
        }
        
        // Repaint when status changes
        Connections {
            target: root
            function onTrackDataChanged() { markerCanvas.requestPaint() }
        }
    }
    
    // Velocity vector
    Rectangle {
        visible: trackData && trackData.velocity > 0.1
        anchors.centerIn: parent
        width: Math.min(30, (trackData ? trackData.velocity : 0) * 2)
        height: 2
        radius: 1
        color: Theme.getStatusColor(trackData ? trackData.status : "MED")
        opacity: 0.8
        rotation: trackData ? trackData.heading || 0 : 0
        transformOrigin: Item.Left
        
        Behavior on width { NumberAnimation { duration: Theme.durationMedium } }
        Behavior on rotation { RotationAnimation { duration: Theme.durationMedium; direction: RotationAnimation.Shortest } }
    }
    
    // Label capsule
    Rectangle {
        anchors.left: parent.right
        anchors.leftMargin: 8
        anchors.verticalCenter: parent.verticalCenter
        implicitWidth: labelText.width + 12
        implicitHeight: 20
        radius: 10
        color: Qt.rgba(Theme.base2.r, Theme.base2.g, Theme.base2.b, 0.85)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.1)
        visible: root.isSelected || mouseArea.containsMouse
        opacity: root.isSelected ? 1.0 : 0.8
        
        Behavior on opacity { NumberAnimation { duration: Theme.durationFast } }
        
        Text {
            id: labelText
            anchors.centerIn: parent
            text: trackData ? ("ID:" + trackData.id + "  " + trackData.status) : ""
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeTiny
            color: Theme.textPrimary
        }
    }
    
    // Pulsing ring for selected track
    Rectangle {
        visible: root.isSelected
        anchors.centerIn: parent
        width: 20 + pulseScale * 18
        height: width
        radius: width / 2
        color: "transparent"
        border.width: 2
        border.color: Theme.statusCritical
        opacity: 1.0 - pulseScale * 0.5
        
        property real pulseScale: 0
        
        SequentialAnimation on pulseScale {
            running: root.isSelected
            loops: Animation.Infinite
            NumberAnimation { to: 1.0; duration: Theme.durationPulse; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.0; duration: 0 }
        }
    }
    
    // Mouse interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        anchors.margins: -8  // Larger hit area
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
    
    // Hover scale
    scale: mouseArea.containsMouse ? 1.15 : 1.0
    Behavior on scale {
        NumberAnimation { duration: Theme.durationFast; easing.type: Easing.OutBack }
    }
}
