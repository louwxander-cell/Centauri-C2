// TrackRow.qml
// Single track row in the table with confidence bar
import QtQuick
import QtQuick.Effects

Rectangle {
    id: root
    color: {
        if (isSelected) return Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.10)
        if (mouseArea.containsMouse) return Qt.rgba(1, 1, 1, 0.04)
        if (index % 2 === 0) return Qt.rgba(1, 1, 1, 0.02)
        return "transparent"
    }
    
    property var trackData: null
    property bool isSelected: false
    property int index: 0
    signal clicked()
    
    // Left accent bar (threat level indicator)
    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 3
        visible: root.isSelected
        color: Theme.getStatusColor(trackData ? trackData.status : "MED")
        
        Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
    }
    
    // Bottom border
    Rectangle {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
        color: Theme.borderSubtle
    }
    
    // Row content
    Row {
        anchors.fill: parent
        anchors.leftMargin: root.isSelected ? 6 : 3
        spacing: 0
        
        // ID
        Text {
            width: 50
            height: parent.height
            text: trackData ? trackData.id : ""
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            font.weight: Theme.fontWeightMedium
            color: Theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            leftPadding: 8
        }
        
        // Type
        Text {
            width: 70
            height: parent.height
            text: trackData ? trackData.type : ""
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            color: Theme.getStatusColor(trackData ? trackData.status : "MED")
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
            
            Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
        }
        
        // Source
        Text {
            width: 70
            height: parent.height
            text: trackData ? trackData.source : ""
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            color: trackData ? (trackData.source === "RADAR" ? Theme.accentCyan : 
                                trackData.source === "RF" ? Theme.accentGreen : Theme.accentAmber) : Theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
        }
        
        // Range
        Text {
            width: 80
            height: parent.height
            text: trackData ? (trackData.range + "m") : ""
            font.family: Theme.fontFamilyMono
            font.pixelSize: Theme.fontSizeMono
            color: Theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
        }
        
        // Azimuth
        Text {
            width: 60
            height: parent.height
            text: trackData ? (trackData.azimuth.toFixed(1) + "°") : ""
            font.family: Theme.fontFamilyMono
            font.pixelSize: Theme.fontSizeMono
            color: Theme.textPrimary
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignLeft
        }
        
        // Confidence (gradient bar + percentage)
        Item {
            width: 130
            height: parent.height
            
            // Background bar
            Rectangle {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 4
                width: 70
                height: 8
                radius: 4
                color: Qt.rgba(1, 1, 1, 0.03)
                
                // Filled portion with gradient
                Rectangle {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width * (trackData ? trackData.confidence : 0)
                    height: parent.height
                    radius: parent.radius
                    
                    gradient: Gradient {
                        orientation: Gradient.Horizontal
                        GradientStop { position: 0.0; color: Theme.accentAmber }
                        GradientStop { position: 0.5; color: Theme.accentCyan }
                        GradientStop { position: 1.0; color: Theme.accentGreen }
                    }
                    
                    Behavior on width { NumberAnimation { duration: Theme.durationMedium; easing.type: Theme.easingStandard } }
                }
            }
            
            // Percentage text
            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 8
                text: trackData ? (Math.round(trackData.confidence * 100) + "%") : ""
                font.family: Theme.fontFamilyMono
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textPrimary
            }
        }
    }
    
    // Mouse interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
    
    // Smooth transitions
    Behavior on color {
        ColorAnimation { duration: Theme.durationFast }
    }
    
    // Selection glow effect
    layer.enabled: root.isSelected
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowColor: Theme.accentCyan
        shadowOpacity: 0.15
        shadowBlur: 0.5
    }
}
