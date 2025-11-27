// MainView.qml
// TriAD C2 Main Interface Layout
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects

ApplicationWindow {
    id: root
    visible: true
    width: 1800
    height: 960
    minimumWidth: 1440
    minimumHeight: 850
    title: "TriAD C2 - Counter-UAS Command & Control"
    color: Theme.base0
    
    // Data models (connected from Python backend)
    property var tracksModel: null
    property var ownship: null
    property var systemMode: null
    property var rwsState: null
    property int selectedTrackId: -1
    
    // Main layout
    Rectangle {
        anchors.fill: parent
        color: Theme.base0
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.windowPadding
            spacing: Theme.panelGutter
            
            // HEADER BAR
            Header {
                id: header
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.headerHeight
            }
            
            // MAIN CONTENT AREA
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.panelGutter
                
                // LEFT PANEL - Active Tracks
                LeftPanel {
                    id: leftPanel
                    Layout.preferredWidth: Theme.leftPanelWidth
                    Layout.fillHeight: true
                    tracksModel: root.tracksModel
                    selectedTrackId: root.selectedTrackId
                    onTrackSelected: function(trackId) {
                        root.selectedTrackId = trackId
                    }
                }
                
                // CENTER PANEL - Tactical Radar Display
                RadarView {
                    id: radarView
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    tracksModel: root.tracksModel
                    selectedTrackId: root.selectedTrackId
                    ownship: root.ownship
                    onTrackSelected: function(trackId) {
                        root.selectedTrackId = trackId
                    }
                }
                
                // RIGHT PANEL - System Status & Controls
                RightPanel {
                    id: rightPanel
                    Layout.preferredWidth: Theme.rightPanelWidth
                    Layout.fillHeight: true
                    selectedTrackId: root.selectedTrackId
                    ownship: root.ownship
                    systemMode: root.systemMode
                    rwsState: root.rwsState
                    onEngageClicked: function(trackId) {
                        console.log("Engage track:", trackId)
                        // Emit signal to Python backend
                    }
                    onResetClicked: {
                        root.selectedTrackId = -1
                    }
                }
            }
            
            // FOOTER - Command Chain
            CommandChain {
                id: footer
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.footerHeight
            }
        }
    }
    
    // Global key handlers
    Keys.onEscapePressed: {
        root.selectedTrackId = -1
    }
    
    // FPS Monitor (debug)
    Rectangle {
        visible: false  // Set to true for debugging
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 10
        width: 80
        height: 30
        color: "#80000000"
        radius: 4
        
        Text {
            anchors.centerIn: parent
            color: Theme.textPrimary
            font.pixelSize: 12
            font.family: Theme.fontFamilyMono
            text: "FPS: " + fpsCounter.fps.toFixed(0)
        }
        
        Timer {
            id: fpsCounter
            property int frames: 0
            property real fps: 0
            interval: 1000
            running: true
            repeat: true
            onTriggered: {
                fps = frames
                frames = 0
            }
        }
    }
    
    // Frame counter
    Timer {
        interval: 16  // ~60 FPS
        running: true
        repeat: true
        onTriggered: fpsCounter.frames++
    }
}
