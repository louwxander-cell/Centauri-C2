// TrackDetailsCard.qml
// Detailed track information panel
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: Theme.base2
    radius: Theme.radiusMedium
    
    property int trackId: -1
    property var tracksModel: null
    property var selectedTrack: null
    
    // Find selected track in model
    onTrackIdChanged: {
        if (tracksModel && trackId >= 0) {
            for (var i = 0; i < tracksModel.count; i++) {
                var track = tracksModel.get(i)
                if (track.id === trackId) {
                    selectedTrack = track
                    return
                }
            }
        }
        selectedTrack = null
    }
    
    ScrollView {
        anchors.fill: parent
        anchors.margins: Theme.cardPadding
        clip: true
        
        ScrollBar.vertical.policy: ScrollBar.AsNeeded
        
        GridLayout {
            width: parent.width
            columns: 2
            rowSpacing: 12
            columnSpacing: 16
            
            // No track selected
            Text {
                Layout.columnSpan: 2
                Layout.fillWidth: true
                visible: root.selectedTrack === null
                text: "No track selected"
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                color: Theme.textTertiary
                horizontalAlignment: Text.AlignHCenter
                topPadding: 40
            }
            
            // Track details when selected
            Column {
                Layout.columnSpan: 2
                Layout.fillWidth: true
                visible: root.selectedTrack !== null
                spacing: 16
                
                // Basic Info Section
                Text {
                    text: "BASIC INFO"
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSmall
                    font.weight: Theme.fontWeightSemiBold
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 0.8
                    color: Theme.textSecondary
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 8
                    
                    DetailLabel { text: "Track ID:" }
                    DetailValue { text: root.selectedTrack ? root.selectedTrack.id : "N/A" }
                    
                    DetailLabel { text: "Type:" }
                    DetailValue { text: root.selectedTrack ? root.selectedTrack.type : "N/A" }
                    
                    DetailLabel { text: "Source:" }
                    DetailValue { text: root.selectedTrack ? root.selectedTrack.source : "N/A" }
                }
                
                // Separator
                Rectangle {
                    width: parent.width
                    height: 1
                    color: Theme.borderSubtle
                }
                
                // Position Section
                Text {
                    text: "POSITION"
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSmall
                    font.weight: Theme.fontWeightSemiBold
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 0.8
                    color: Theme.textSecondary
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 8
                    
                    DetailLabel { text: "Range:" }
                    DetailValue { text: root.selectedTrack ? (root.selectedTrack.range + " m") : "N/A" }
                    
                    DetailLabel { text: "Azimuth:" }
                    DetailValue { text: root.selectedTrack ? (root.selectedTrack.azimuth.toFixed(1) + "°") : "N/A" }
                    
                    DetailLabel { text: "Elevation:" }
                    DetailValue { text: root.selectedTrack && root.selectedTrack.elevation !== undefined ? 
                                       (root.selectedTrack.elevation.toFixed(1) + "°") : "N/A" }
                }
                
                // Separator
                Rectangle {
                    width: parent.width
                    height: 1
                    color: Theme.borderSubtle
                }
                
                // Tracking Section
                Text {
                    text: "TRACKING"
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSmall
                    font.weight: Theme.fontWeightSemiBold
                    font.capitalization: Font.AllUppercase
                    font.letterSpacing: 0.8
                    color: Theme.textSecondary
                }
                
                GridLayout {
                    width: parent.width
                    columns: 2
                    columnSpacing: 16
                    rowSpacing: 8
                    
                    DetailLabel { text: "Confidence:" }
                    DetailValue { text: root.selectedTrack ? (Math.round(root.selectedTrack.confidence * 100) + "%") : "N/A" }
                    
                    DetailLabel { text: "Velocity:" }
                    DetailValue { text: root.selectedTrack && root.selectedTrack.velocity !== undefined ? 
                                       (root.selectedTrack.velocity.toFixed(1) + " m/s") : "N/A" }
                    
                    DetailLabel { text: "Heading:" }
                    DetailValue { text: root.selectedTrack && root.selectedTrack.heading !== undefined ? 
                                       (root.selectedTrack.heading.toFixed(1) + "°") : "N/A" }
                }
            }
        }
    }
}
