// Main.qml - TriAD C2 Main Interface
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: root
    visible: true
    width: 1800
    height: 960
    title: "TriAD C2 - Counter-UAS Command & Control"
    color: Theme.base0
    
    // Data properties from Python
    property var tracksModel: null
    property var ownship: null
    property var systemMode: null
    property int selectedTrackId: -1
    
    Rectangle {
        anchors.fill: parent
        color: Theme.base0
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 24
            
            // Header
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 80
                color: Theme.base1
                radius: Theme.radiusMedium
                border.width: 1
                border.color: Theme.borderSubtle
                
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 32
                    anchors.rightMargin: 32
                    
                    Text {
                        text: "TriAD C2"
                        font.family: Theme.fontFamily
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: Theme.textPrimary
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Text {
                        text: "COUNTER-UAS COMMAND & CONTROL"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeHeading
                        font.weight: Theme.fontWeightSemiBold
                        font.capitalization: Font.AllUppercase
                        font.letterSpacing: 1.2
                        color: Theme.textSecondary
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    // Status indicator
                    Row {
                        spacing: 8
                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            color: Theme.accentCyan
                            
                            SequentialAnimation on opacity {
                                loops: Animation.Infinite
                                NumberAnimation { to: 0.3; duration: 1200 }
                                NumberAnimation { to: 1.0; duration: 1200 }
                            }
                        }
                        Text {
                            text: "ONLINE"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeSmall
                            font.weight: Theme.fontWeightSemiBold
                            color: Theme.accentCyan
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }
            }
            
            // Main content area
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 24
                
                // Left Panel - Tracks
                Rectangle {
                    Layout.preferredWidth: 460
                    Layout.fillHeight: true
                    color: Theme.base1
                    radius: Theme.radiusMedium
                    border.width: 1
                    border.color: Theme.borderSubtle
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.cardPadding
                        spacing: 16
                        
                        Text {
                            text: "ACTIVE TRACKS"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeHeading
                            font.weight: Theme.fontWeightSemiBold
                            font.capitalization: Font.AllUppercase
                            font.letterSpacing: 0.8
                            color: Theme.textSecondary
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
                                radius: 6
                                color: root.selectedTrackId === modelData.id ? 
                                       Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.15) : 
                                       "transparent"
                                border.width: root.selectedTrackId === modelData.id ? 1 : 0
                                border.color: Theme.accentCyan
                                
                                Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    anchors.rightMargin: 12
                                    spacing: 12
                                    
                                    Text {
                                        text: "ID:" + modelData.id
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeBody
                                        font.weight: Theme.fontWeightSemiBold
                                        color: Theme.textPrimary
                                        Layout.preferredWidth: 60
                                    }
                                    
                                    Text {
                                        text: modelData.type
                                        font.family: Theme.fontFamily
                                        font.pixelSize: Theme.fontSizeBody
                                        color: Theme.accentYellow
                                        Layout.preferredWidth: 70
                                    }
                                    
                                    Text {
                                        text: modelData.range.toFixed(0) + "m"
                                        font.family: "SF Mono"
                                        font.pixelSize: Theme.fontSizeMono
                                        color: Theme.textPrimary
                                        Layout.preferredWidth: 80
                                    }
                                    
                                    Text {
                                        text: modelData.azimuth.toFixed(1) + "°"
                                        font.family: "SF Mono"
                                        font.pixelSize: Theme.fontSizeMono
                                        color: Theme.textPrimary
                                        Layout.fillWidth: true
                                    }
                                    
                                    // Confidence indicator
                                    Rectangle {
                                        Layout.preferredWidth: 60
                                        Layout.preferredHeight: 6
                                        radius: 3
                                        color: Theme.borderSubtle
                                        
                                        Rectangle {
                                            width: parent.width * modelData.confidence
                                            height: parent.height
                                            radius: 3
                                            color: Theme.accentCyan
                                            
                                            Behavior on width { NumberAnimation { duration: Theme.durationNormal } }
                                        }
                                    }
                                }
                                
                                MouseArea {
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    
                                    onEntered: parent.color = Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.08)
                                    onExited: if (root.selectedTrackId !== modelData.id) parent.color = "transparent"
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
                    color: Theme.base1
                    radius: Theme.radiusMedium
                    border.width: 1
                    border.color: Theme.borderSubtle
                    
                    Item {
                        anchors.centerIn: parent
                        width: Math.min(parent.width, parent.height) * 0.8
                        height: width
                        
                        // Range rings
                        Repeater {
                            model: 4
                            Rectangle {
                                anchors.centerIn: parent
                                width: parent.width * (index + 1) / 4
                                height: width
                                radius: width / 2
                                color: "transparent"
                                border.width: 1
                                border.color: Theme.borderSubtle
                            }
                        }
                        
                        // Rotating sweep
                        Rectangle {
                            id: sweepLine
                            anchors.centerIn: parent
                            width: 3
                            height: parent.height / 2
                            color: Theme.accentCyan
                            transformOrigin: Item.Bottom
                            opacity: 0.6
                            
                            gradient: Gradient {
                                GradientStop { position: 0.0; color: "transparent" }
                                GradientStop { position: 0.8; color: Theme.accentCyan }
                            }
                            
                            RotationAnimation on rotation {
                                from: 0
                                to: 360
                                duration: Theme.durationSweep
                                loops: Animation.Infinite
                            }
                        }
                        
                        // Center dot
                        Rectangle {
                            anchors.centerIn: parent
                            width: 8
                            height: 8
                            radius: 4
                            color: Theme.accentCyan
                        }
                        
                        // Tracks on radar
                        Repeater {
                            model: root.tracksModel
                            
                            Item {
                                property real radarRadius: parent.width / 2
                                property real normalizedRange: Math.min(modelData.range / 3000, 1.0)
                                property real angleRad: modelData.azimuth * Math.PI / 180
                                
                                x: parent.width / 2 + Math.sin(angleRad) * normalizedRange * radarRadius - width / 2
                                y: parent.height / 2 - Math.cos(angleRad) * normalizedRange * radarRadius - height / 2
                                
                                width: 12
                                height: 12
                                
                                Rectangle {
                                    anchors.centerIn: parent
                                    width: root.selectedTrackId === modelData.id ? 16 : 12
                                    height: width
                                    radius: width / 2
                                    color: Theme.accentYellow
                                    border.width: root.selectedTrackId === modelData.id ? 2 : 0
                                    border.color: Theme.accentCyan
                                    
                                    Behavior on width { NumberAnimation { duration: Theme.durationFast } }
                                    
                                    // Pulsing effect for selected
                                    SequentialAnimation on scale {
                                        running: root.selectedTrackId === modelData.id
                                        loops: Animation.Infinite
                                        NumberAnimation { to: 1.3; duration: 800 }
                                        NumberAnimation { to: 1.0; duration: 800 }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Radar label
                    Text {
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.margins: 20
                        text: "TACTICAL RADAR"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeHeading
                        font.weight: Theme.fontWeightSemiBold
                        font.capitalization: Font.AllUppercase
                        font.letterSpacing: 0.8
                        color: Theme.textSecondary
                    }
                }
                
                // Right Panel - Controls
                Rectangle {
                    Layout.preferredWidth: 360
                    Layout.fillHeight: true
                    color: Theme.base1
                    radius: Theme.radiusMedium
                    border.width: 1
                    border.color: Theme.borderSubtle
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.cardPadding
                        spacing: 16
                        
                        Text {
                            text: "SYSTEM STATUS"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeHeading
                            font.weight: Theme.fontWeightSemiBold
                            font.capitalization: Font.AllUppercase
                            font.letterSpacing: 0.8
                            color: Theme.textSecondary
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 120
                            color: Theme.base2
                            radius: 8
                            border.width: 1
                            border.color: Theme.borderSubtle
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: 8
                                
                                Text {
                                    text: "OWNSHIP POSITION"
                                    font.family: Theme.fontFamily
                                    font.pixelSize: Theme.fontSizeSmall
                                    font.weight: Theme.fontWeightSemiBold
                                    font.capitalization: Font.AllUppercase
                                    color: Theme.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: root.ownship ? 
                                          "LAT: " + root.ownship.lat.toFixed(6) + "\nLON: " + root.ownship.lon.toFixed(6) :
                                          "NO GPS DATA"
                                    font.family: "SF Mono"
                                    font.pixelSize: Theme.fontSizeMono
                                    color: Theme.textPrimary
                                    horizontalAlignment: Text.AlignHCenter
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                        
                        Item { Layout.fillHeight: true }
                        
                        // Engage button
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 60
                            radius: 30
                            color: root.selectedTrackId >= 0 ? Theme.accentRed : Theme.borderSubtle
                            border.width: 2
                            border.color: root.selectedTrackId >= 0 ? Qt.lighter(Theme.accentRed, 1.3) : Theme.borderSubtle
                            
                            Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                            
                            Text {
                                anchors.centerIn: parent
                                text: root.selectedTrackId >= 0 ? "ENGAGE ID:" + root.selectedTrackId : "SELECT TARGET"
                                font.family: Theme.fontFamily
                                font.pixelSize: 15
                                font.weight: Font.Bold
                                font.capitalization: Font.AllUppercase
                                color: root.selectedTrackId >= 0 ? "#FFFFFF" : Theme.textSecondary
                            }
                            
                            MouseArea {
                                anchors.fill: parent
                                enabled: root.selectedTrackId >= 0
                                cursorShape: enabled ? Qt.PointingHandCursor : Qt.ForbiddenCursor
                                onClicked: console.log("Engage clicked for track:", root.selectedTrackId)
                            }
                        }
                    }
                }
            }
            
            // Footer
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 44
                color: Theme.base1
                radius: Theme.radiusMedium
                border.width: 1
                border.color: Theme.borderSubtle
                
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    
                    Text {
                        text: "SYSTEM OPERATIONAL"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Theme.fontWeightSemiBold
                        font.capitalization: Font.AllUppercase
                        color: Theme.accentCyan
                    }
                    
                    Item { Layout.fillWidth: true }
                    
                    Text {
                        id: timeLabel
                        font.family: "SF Mono"
                        font.pixelSize: Theme.fontSizeMono
                        color: Theme.textSecondary
                        
                        Timer {
                            interval: 1000
                            running: true
                            repeat: true
                            onTriggered: timeLabel.text = Qt.formatDateTime(new Date(), "hh:mm:ss UTC")
                        }
                        
                        Component.onCompleted: text = Qt.formatDateTime(new Date(), "hh:mm:ss UTC")
                    }
                }
            }
        }
    }
}
