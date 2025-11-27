// RadarView.qml
// Main tactical radar display with sweep, tracks, and effects
import QtQuick
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: root
    color: Theme.base1
    radius: Theme.radiusMedium
    
    property var tracksModel: null
    property int selectedTrackId: -1
    property var ownship: null
    property real maxRange: 3000  // meters
    property real sweepAngle: 0
    
    signal trackSelected(int trackId)
    
    // Sweep animation
    NumberAnimation on sweepAngle {
        from: 0
        to: 360
        duration: Theme.durationSweep
        loops: Animation.Infinite
        running: true
    }
    
    // Radar canvas
    Canvas {
        id: radarCanvas
        anchors.fill: parent
        anchors.margins: 40
        
        property real centerX: width / 2
        property real centerY: height / 2
        property real radius: Math.min(width, height) / 2
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.reset()
            
            // Draw vignette background
            var gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius)
            gradient.addColorStop(0, Qt.rgba(Theme.base0.r, Theme.base0.g, Theme.base0.b, 1.0))
            gradient.addColorStop(1, Qt.rgba(Theme.base0.r, Theme.base0.g, Theme.base0.b, 0.85))
            ctx.fillStyle = gradient
            ctx.fillRect(0, 0, width, height)
            
            // Draw range rings
            drawRangeRings(ctx)
            
            // Draw bearing lines
            drawBearingLines(ctx)
            
            // Draw cardinal labels
            drawCardinalLabels(ctx)
            
            // Draw radar sweep
            drawSweep(ctx)
        }
        
        function drawRangeRings(ctx) {
            var ringCount = 6
            var maxAlpha = 0.25
            var minAlpha = 0.10
            
            for (var i = 1; i <= ringCount; i++) {
                var r = radius * i / ringCount
                var alpha = i > (ringCount - 2) ? maxAlpha : minAlpha
                
                ctx.beginPath()
                ctx.arc(centerX, centerY, r, 0, 2 * Math.PI)
                ctx.strokeStyle = Qt.rgba(1, 1, 1, alpha)
                ctx.lineWidth = 1
                ctx.stroke()
                
                // Range label
                if (i % 2 === 0) {
                    var rangeM = Math.round(maxRange * i / ringCount)
                    ctx.fillStyle = Qt.rgba(1, 1, 1, 0.4)
                    ctx.font = "10px 'SF Mono'"
                    ctx.fillText(rangeM + "m", centerX + 5, centerY - r + 12)
                }
            }
        }
        
        function drawBearingLines(ctx) {
            for (var angle = 0; angle < 360; angle += 30) {
                var rad = angle * Math.PI / 180
                var x = centerX + radius * Math.cos(rad - Math.PI / 2)
                var y = centerY + radius * Math.sin(rad - Math.PI / 2)
                
                ctx.beginPath()
                ctx.moveTo(centerX, centerY)
                ctx.lineTo(x, y)
                ctx.strokeStyle = Qt.rgba(1, 1, 1, 0.08)
                ctx.lineWidth = 1
                ctx.setLineDash([4, 4])
                ctx.stroke()
                ctx.setLineDash([])
            }
        }
        
        function drawCardinalLabels(ctx) {
            var labels = ["N", "E", "S", "W"]
            var angles = [0, 90, 180, 270]
            
            ctx.fillStyle = Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.8)
            ctx.font = "12px 'Inter'"
            ctx.textAlign = "center"
            ctx.textBaseline = "middle"
            
            for (var i = 0; i < 4; i++) {
                var rad = angles[i] * Math.PI / 180
                var labelDist = radius * 0.92
                var x = centerX + labelDist * Math.cos(rad - Math.PI / 2)
                var y = centerY + labelDist * Math.sin(rad - Math.PI / 2)
                ctx.fillText(labels[i], x, y)
            }
        }
        
        function drawSweep(ctx) {
            var sweepRad = root.sweepAngle * Math.PI / 180
            
            // Create gradient for sweep tail
            var sweepGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius)
            sweepGradient.addColorStop(0, Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.15))
            sweepGradient.addColorStop(1, Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0))
            
            ctx.save()
            ctx.translate(centerX, centerY)
            ctx.rotate(sweepRad - Math.PI / 2)
            
            ctx.beginPath()
            ctx.moveTo(0, 0)
            ctx.arc(0, 0, radius, -Math.PI / 6, 0)
            ctx.closePath()
            ctx.fillStyle = sweepGradient
            ctx.fill()
            
            // Sweep line
            ctx.beginPath()
            ctx.moveTo(0, 0)
            ctx.lineTo(radius, 0)
            ctx.strokeStyle = Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.6)
            ctx.lineWidth = 2
            ctx.stroke()
            
            ctx.restore()
        }
        
        // Repaint when sweep angle changes
        Connections {
            target: root
            function onSweepAngleChanged() { radarCanvas.requestPaint() }
        }
    }
    
    // Center marker (ownship)
    Rectangle {
        anchors.centerIn: radarCanvas
        width: 16
        height: 16
        radius: 8
        color: Theme.accentCyan
        
        // Cross hairs
        Rectangle {
            anchors.centerIn: parent
            width: 20
            height: 2
            color: Theme.accentCyan
        }
        Rectangle {
            anchors.centerIn: parent
            width: 2
            height: 20
            color: Theme.accentCyan
        }
        
        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: Theme.accentCyan
            shadowOpacity: 0.8
            shadowBlur: 1.0
        }
    }
    
    // Track markers repeater
    Repeater {
        model: root.tracksModel
        
        TrackMarker {
            required property var modelData
            required property int index
            
            trackData: modelData
            isSelected: root.selectedTrackId === modelData.id
            centerX: radarCanvas.centerX + radarCanvas.anchors.leftMargin
            centerY: radarCanvas.centerY + radarCanvas.anchors.topMargin
            radarRadius: radarCanvas.radius
            maxRange: root.maxRange
            
            onClicked: root.trackSelected(modelData.id)
        }
    }
    
    // Legend overlay (lower right)
    Rectangle {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Theme.cardPadding
        width: 140
        height: legendColumn.height + 24
        color: Qt.rgba(Theme.base2.r, Theme.base2.g, Theme.base2.b, 0.9)
        radius: Theme.radiusMedium
        border.width: 1
        border.color: Theme.borderCard
        
        opacity: legendMouseArea.containsMouse ? 1.0 : 0.6
        Behavior on opacity { NumberAnimation { duration: Theme.durationFast } }
        
        Column {
            id: legendColumn
            anchors.centerIn: parent
            spacing: 8
            
            Text {
                text: "LEGEND"
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeSmall
                font.weight: Theme.fontWeightSemiBold
                color: Theme.textSecondary
                anchors.horizontalCenter: parent.horizontalCenter
            }
            
            LegendItem { label: "Critical"; color: Theme.statusCritical; symbol: "▲" }
            LegendItem { label: "High"; color: Theme.statusHigh; symbol: "▲" }
            LegendItem { label: "Medium"; color: Theme.statusMed; symbol: "▲" }
            LegendItem { label: "Friendly"; color: Theme.statusFriendly; symbol: "●" }
        }
        
        MouseArea {
            id: legendMouseArea
            anchors.fill: parent
            hoverEnabled: true
        }
    }
    
    // Zoom controls
    Column {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Theme.cardPadding
        spacing: Theme.tightSpacing
        
        ZoomButton { text: "+"; onClicked: root.maxRange = Math.max(1000, root.maxRange - 500) }
        ZoomButton { text: "−"; onClicked: root.maxRange = Math.min(5000, root.maxRange + 500) }
    }
    
    // View toggle button
    Button {
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: Theme.tightSpacing
        
        text: "SWITCH TO MAP VIEW"
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSmall
        font.weight: Theme.fontWeightSemiBold
        
        background: Rectangle {
            implicitWidth: 160
            implicitHeight: 32
            color: parent.pressed ? Theme.base2 : (parent.hovered ? Theme.base1 : "transparent")
            border.width: 1
            border.color: parent.hovered ? Theme.borderFocus : Theme.borderCard
            radius: Theme.radiusMedium
            
            Behavior on color { ColorAnimation { duration: Theme.durationFast } }
            Behavior on border.color { ColorAnimation { duration: Theme.durationFast } }
        }
        
        contentItem: Text {
            text: parent.text
            font: parent.font
            color: Theme.textPrimary
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
