// RightPanel.qml
// System status and engagement controls
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "transparent"
    
    property int selectedTrackId: -1
    property var ownship: null
    property var systemMode: null
    property var rwsState: null
    
    signal engageClicked(int trackId)
    signal resetClicked()
    
    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.baseline
        
        // Ownship Position Card
        StatusCard {
            Layout.fillWidth: true
            cardColor: Theme.base1  // Alternating depth
            title: "OWNSHIP POSITION"
            
            GridLayout {
                width: parent.width
                columns: 2
                columnSpacing: 12
                rowSpacing: 8
                
                DetailLabel { text: "Latitude:" }
                DetailValue { text: root.ownship ? root.ownship.lat.toFixed(6) : "N/A" }
                
                DetailLabel { text: "Longitude:" }
                DetailValue { text: root.ownship ? root.ownship.lon.toFixed(6) : "N/A" }
                
                DetailLabel { text: "Heading:" }
                DetailValue {
                    text: root.ownship ? (root.ownship.heading.toFixed(1) + "°") : "N/A"
                    color: Theme.accentCyan
                }
            }
        }
        
        // System Mode Card
        StatusCard {
            Layout.fillWidth: true
            cardColor: Theme.base2  // Alternating depth
            title: "SYSTEM MODE"
            
            Column {
                width: parent.width
                spacing: 10
                
                ModeToggle {
                    text: "Auto Track"
                    checked: root.systemMode ? root.systemMode.autoTrack : false
                }
                
                ModeToggle {
                    text: "RF Silent"
                    checked: root.systemMode ? root.systemMode.rfSilent : false
                }
                
                ModeToggle {
                    text: "Optical Lock"
                    checked: root.systemMode ? root.systemMode.opticalLock : false
                }
            }
        }
        
        // RWS Position Card
        StatusCard {
            Layout.fillWidth: true
            cardColor: Theme.base1  // Alternating depth
            title: "RWS POSITION"
            visible: root.rwsState !== null
            
            GridLayout {
                width: parent.width
                columns: 2
                columnSpacing: 12
                rowSpacing: 8
                
                DetailLabel { text: "Azimuth:" }
                DetailValue { text: root.rwsState ? (root.rwsState.azimuth.toFixed(1) + "°") : "N/A" }
                
                DetailLabel { text: "Elevation:" }
                DetailValue { text: root.rwsState ? (root.rwsState.elevation.toFixed(1) + "°") : "N/A" }
            }
        }
        
        // Spacer
        Item { Layout.fillHeight: true }
        
        // Reset Button
        Button {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            
            text: "RESET TO HIGHEST THREAT"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            font.weight: Theme.fontWeightSemiBold
            
            background: Rectangle {
                color: parent.pressed ? Theme.base2 : (parent.hovered ? Theme.base1 : "transparent")
                border.width: 1
                border.color: parent.hovered ? Theme.accentCyan : Theme.borderCard
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
            
            onClicked: root.resetClicked()
        }
        
        // Engage Button
        EngageButton {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            trackId: root.selectedTrackId
            onEngageClicked: function(tid) {
                root.engageClicked(tid)
            }
        }
        
        // Threat Info Label
        Text {
            Layout.fillWidth: true
            text: root.selectedTrackId >= 0 ? 
                  ("Target ID:" + root.selectedTrackId + " selected") : 
                  "No threat selected"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.textSecondary
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
        }
    }
}
