// MainViewSimple.qml
// Simplified version without Theme dependency
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

Window {
    id: root
    visible: true
    width: 1800
    height: 960
    title: "TriAD C2 - Counter-UAS Command & Control"
    color: "#0F1113"
    
    // Data models (connected from Python backend)
    property var tracksModel: null
    property var ownship: null
    property var systemMode: null
    property var rwsState: null
    property int selectedTrackId: -1
    
    // Main layout
    Rectangle {
        anchors.fill: parent
        color: "#0F1113"
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 24
            
            // Header
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 80
                color: "#15181A"
                radius: 12
                
                Text {
                    anchors.centerIn: parent
                    text: "TriAD C2 - COUNTER-UAS COMMAND & CONTROL"
                    font.pixelSize: 18
                    font.bold: true
                    color: "#EBEBEB"
                }
            }
            
            // Main content row
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 24
                
                // Left Panel - Tracks
                Rectangle {
                    Layout.preferredWidth: 460
                    Layout.fillHeight: true
                    color: "#15181A"
                    radius: 12
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16
                        
                        Text {
                            text: "ACTIVE TRACKS"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#999999"
                        }
                        
                        ListView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            model: root.tracksModel
                            clip: true
                            spacing: 2
                            
                            delegate: Rectangle {
                                width: ListView.view.width
                                height: 44
                                color: root.selectedTrackId === modelData.id ? "#38E6E020" : "#FFFFFF05"
                                
                                Row {
                                    anchors.fill: parent
                                    anchors.leftMargin: 8
                                    spacing: 12
                                    
                                    Text {
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: "ID:" + modelData.id
                                        font.pixelSize: 12
                                        color: "#EBEBEB"
                                        width: 60
                                    }
                                    
                                    Text {
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.type
                                        font.pixelSize: 12
                                        color: "#F2B46E"
                                        width: 70
                                    }
                                    
                                    Text {
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.range + "m"
                                        font.pixelSize: 12
                                        font.family: "Courier"
                                        color: "#EBEBEB"
                                        width: 80
                                    }
                                    
                                    Text {
                                        anchors.verticalCenter: parent.verticalCenter
                                        text: modelData.azimuth.toFixed(1) + "°"
                                        font.pixelSize: 12
                                        font.family: "Courier"
                                        color: "#EBEBEB"
                                    }
                                }
                                
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: root.selectedTrackId = modelData.id
                                }
                            }
                        }
                    }
                }
                
                // Center - Radar
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#15181A"
                    radius: 12
                    
                    Text {
                        anchors.centerIn: parent
                        text: "RADAR VIEW\n\n" + (root.tracksModel ? root.tracksModel.count + " tracks" : "0 tracks")
                        font.pixelSize: 24
                        color: "#38E6E0"
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    // Simple rotating indicator
                    Rectangle {
                        anchors.centerIn: parent
                        anchors.verticalCenterOffset: 80
                        width: 200
                        height: 200
                        radius: 100
                        color: "transparent"
                        border.width: 2
                        border.color: "#38E6E040"
                        
                        Rectangle {
                            anchors.centerIn: parent
                            width: 4
                            height: 100
                            color: "#38E6E0"
                            transformOrigin: Item.Bottom
                            
                            RotationAnimation on rotation {
                                from: 0
                                to: 360
                                duration: 3000
                                loops: Animation.Infinite
                            }
                        }
                    }
                }
                
                // Right Panel - Controls
                Rectangle {
                    Layout.preferredWidth: 360
                    Layout.fillHeight: true
                    color: "#15181A"
                    radius: 12
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16
                        
                        Text {
                            text: "SYSTEM STATUS"
                            font.pixelSize: 14
                            font.bold: true
                            color: "#999999"
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            color: "#1B1F22"
                            radius: 12
                            
                            Column {
                                anchors.centerIn: parent
                                spacing: 8
                                
                                Text {
                                    text: "Ownship Position"
                                    font.pixelSize: 12
                                    color: "#999999"
                                }
                                Text {
                                    text: root.ownship ? 
                                          "Lat: " + root.ownship.lat.toFixed(6) + "\nLon: " + root.ownship.lon.toFixed(6) :
                                          "No GPS data"
                                    font.pixelSize: 11
                                    font.family: "Courier"
                                    color: "#EBEBEB"
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                        
                        Button {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 60
                            text: root.selectedTrackId >= 0 ? "ENGAGE ID:" + root.selectedTrackId : "ENGAGE TARGET"
                            enabled: root.selectedTrackId >= 0
                            
                            background: Rectangle {
                                color: parent.enabled ? (parent.pressed ? "#CC484C" : "#E84855") : "#333333"
                                radius: 30
                            }
                            
                            contentItem: Text {
                                text: parent.text
                                font.pixelSize: 15
                                font.bold: true
                                color: parent.enabled ? "#FFFFFF" : "#666666"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }
            }
            
            // Footer
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 44
                color: "#15181A"
                radius: 12
                
                Text {
                    anchors.centerIn: parent
                    text: "System Operational • " + Qt.formatDateTime(new Date(), "hh:mm:ss UTC")
                    font.pixelSize: 11
                    color: "#38E6E0"
                    
                    Timer {
                        interval: 1000
                        running: true
                        repeat: true
                        onTriggered: parent.text = "System Operational • " + Qt.formatDateTime(new Date(), "hh:mm:ss UTC")
                    }
                }
            }
        }
    }
}
