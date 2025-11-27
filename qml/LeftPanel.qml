// LeftPanel.qml
// Active Tracks table and Track Details
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: Theme.base1
    radius: Theme.radiusMedium
    
    property var tracksModel: null
    property int selectedTrackId: -1
    signal trackSelected(int trackId)
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.cardPadding
        spacing: Theme.itemSpacing
        
        // Header
        Text {
            text: "ACTIVE TRACKS"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeHeading
            font.weight: Theme.fontWeightSemiBold
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.8
            color: Theme.textSecondary
        }
        
        // Tracks Table
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 300
            color: "transparent"
            clip: true
            
            // Table Header
            Row {
                id: tableHeader
                width: parent.width
                height: 36
                spacing: 0
                
                TableHeaderCell { text: "ID"; width: 50 }
                TableHeaderCell { text: "TYPE"; width: 70 }
                TableHeaderCell { text: "SOURCE"; width: 70 }
                TableHeaderCell { text: "RANGE"; width: 80 }
                TableHeaderCell { text: "AZ"; width: 60 }
                TableHeaderCell { text: "CONF"; width: 130 }
            }
            
            // Table Body
            ListView {
                id: tracksList
                anchors.top: tableHeader.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                anchors.topMargin: 4
                
                model: root.tracksModel
                spacing: 0
                clip: true
                
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    width: 8
                    
                    contentItem: Rectangle {
                        implicitWidth: 8
                        radius: 4
                        color: Theme.borderCard
                        opacity: parent.pressed ? 0.3 : (parent.hovered ? 0.2 : 0.1)
                        
                        Behavior on opacity { NumberAnimation { duration: 150 } }
                    }
                    
                    background: Rectangle {
                        color: "transparent"
                    }
                }
                
                delegate: TrackRow {
                    width: tracksList.width - 8
                    height: Theme.tableRowHeight
                    trackData: modelData || model
                    isSelected: root.selectedTrackId === (modelData ? modelData.id : model.id)
                    
                    onClicked: {
                        root.trackSelected(modelData ? modelData.id : model.id)
                    }
                }
                
                // Smooth scrolling
                flickDeceleration: 5000
                maximumFlickVelocity: 2500
            }
        }
        
        // Track Details Card
        Text {
            text: "TRACK DETAILS"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeHeading
            font.weight: Theme.fontWeightSemiBold
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.8
            color: Theme.textSecondary
        }
        
        TrackDetailsCard {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            trackId: root.selectedTrackId
            tracksModel: root.tracksModel
        }
    }
}
