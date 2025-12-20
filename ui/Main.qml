// Main.qml - TriAD C2 Main Interface
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import "components"

Window {
    id: root
    visible: true
    width: 1904  // 1920 - 16px for window borders (8px left + 8px right)
    height: 995  // 1080 - 48px taskbar - 37px title bar
    x: 0
    y: 0
    title: "TriAD C2 - Counter-UAS Command & Control"
    color: Theme.base0
    
    // Optimize for Full HD display (accounting for window borders, title bar, taskbar)
    minimumWidth: 1600
    minimumHeight: 850
    
    // Data properties from Python (provided via setContextProperty)
    // tracksModel, ownship, systemMode, bridge, engine
    property int selectedTrackId: -1
    property bool manualSelection: false
    property int highestPriorityTrackId: -1  // Single source of truth
    
    Component.onCompleted: {
        // Select highest priority track on startup
        updateHighestPriority()
    }
    
    // Function to update highest priority immediately
    function updateHighestPriority() {
        if (!bridge) return
        
        var newPriority = bridge.get_highest_priority_track_id()
        if (newPriority !== highestPriorityTrackId) {
            highestPriorityTrackId = newPriority
            
            // Auto-select if not manual
            if (!manualSelection) {
                selectedTrackId = newPriority
                console.log("[UI] Auto-selected highest priority: Track", selectedTrackId)
            }
        }
    }
    
    // Monitor for track updates and update priority immediately
    Connections {
        target: tracksModel
        function onRowsInserted() {
            root.updateHighestPriority()
        }
        function onRowsRemoved() {
            root.updateHighestPriority()
        }
        function onDataChanged() {
            root.updateHighestPriority()
        }
        function onModelReset() {
            root.updateHighestPriority()
        }
    }
    
    // Timer to reset selection to highest priority after 10 seconds
    Timer {
        id: selectionResetTimer
        interval: 10000  // 10 seconds
        running: false
        repeat: false
        onTriggered: {
            console.log("[UI] Selection timeout - reverting to highest priority")
            manualSelection = false
            selectedTrackId = highestPriorityTrackId
        }
    }
    
    // Timer to periodically update highest priority (for dynamic threat changes)
    Timer {
        interval: 100  // Every 100ms - fast updates for immediate selection
        running: true
        repeat: true
        onTriggered: {
            root.updateHighestPriority()
        }
    }
    
    // Background grid pattern (subtle)
    Canvas {
        anchors.fill: parent
        z: -1
        
        onPaint: {
            var ctx = getContext("2d")
            ctx.strokeStyle = "#FFFFFF03"  // 3% white - very subtle
            ctx.lineWidth = 1
            
            // Vertical lines
            for (var x = 0; x < width; x += 50) {
                ctx.beginPath()
                ctx.moveTo(x, 0)
                ctx.lineTo(x, height)
                ctx.stroke()
            }
            
            // Horizontal lines
            for (var y = 0; y < height; y += 50) {
                ctx.beginPath()
                ctx.moveTo(0, y)
                ctx.lineTo(width, y)
                ctx.stroke()
            }
        }
    }
    
    // FPS and performance indicator (toggle with 'D' key)
    property bool devMode: false
    property int fps: 0
    
    Text {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 8
        z: 1000
        text: `${fps} FPS | ${tracksModel ? tracksModel.count : 0} tracks`
        font.family: Theme.fontFamilyMono
        font.pixelSize: 9
        color: Theme.textTertiary
        visible: devMode
    }
    
    Timer {
        interval: 1000
        running: true
        repeat: true
        property int frameCount: 0
        onTriggered: {
            fps = frameCount
            frameCount = 0
        }
        Component.onCompleted: {
            // Increment frame count
            var timer = this
            root.onFrameSwapped.connect(function() {
                timer.frameCount++
            })
        }
    }
    
    // Keyboard shortcuts overlay (toggle with '?' key)
    property bool showShortcuts: false
    
    Rectangle {
        anchors.centerIn: parent
        width: 400
        height: 300
        radius: Theme.radiusLarge
        color: Theme.base1
        border.width: 1
        border.color: Theme.borderSubtle
        visible: showShortcuts
        z: 2000
        
        layer.enabled: true
        layer.effect: DropShadow {
            horizontalOffset: 0
            verticalOffset: 8
            radius: 24
            samples: 17
            color: Qt.rgba(0, 0, 0, 0.6)
            transparentBorder: true
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 24
            spacing: 12
            
            Text {
                text: "KEYBOARD SHORTCUTS"
                font.family: Theme.fontFamilyDisplay
                font.pixelSize: 18
                font.weight: Theme.fontWeightBold
                color: Theme.textPrimary
            }
            
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: Theme.borderSubtle
            }
            
            GridLayout {
                columns: 2
                columnSpacing: 20
                rowSpacing: 8
                Layout.fillWidth: true
                
                Text { text: "?"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Show/Hide Shortcuts"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
                
                Text { text: "D"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Toggle Dev Mode (FPS)"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
                
                Text { text: "1-5"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Load Scenario"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
                
                Text { text: "Space"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Engage Selected Track"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
                
                Text { text: "Esc"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Clear Selection"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
                
                Text { text: "+/-"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Zoom In/Out"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
                
                Text { text: "R"; font.family: Theme.fontFamilyMono; font.pixelSize: 12; font.weight: Font.Bold; color: Theme.accentFocus }
                Text { text: "Reset Zoom"; font.family: Theme.fontFamily; font.pixelSize: 12; color: Theme.textSecondary }
            }
            
            Item { Layout.fillHeight: true }
            
            Text {
                text: "Press ? to close"
                font.family: Theme.fontFamily
                font.pixelSize: 10
                color: Theme.textTertiary
                Layout.alignment: Qt.AlignHCenter
            }
        }
    }
    
    // Global key handler wrapper
    Item {
        anchors.fill: parent
        focus: true
        z: -100
        
        Keys.onPressed: (event) => {
            if (event.key === Qt.Key_Question) {
                showShortcuts = !showShortcuts
                event.accepted = true
            } else if (event.key === Qt.Key_D) {
                devMode = !devMode
                event.accepted = true
            } else if (event.key === Qt.Key_Escape) {
                selectedTrackId = -1
                manualSelection = false
                event.accepted = true
            } else if (event.key === Qt.Key_Space && selectedTrackId >= 0) {
                // Engage selected track
                if (bridge) {
                    bridge.engage_track(selectedTrackId, "OPERATOR_1")
                }
                event.accepted = true
            } else if (event.key === Qt.Key_R) {
                // Reset zoom
                radarDisplay.zoomLevel = 1.0
                event.accepted = true
            }
        }
    }
    
    Rectangle {
        anchors.fill: parent
        color: Theme.base0  // Deep space black (#0A0E12)
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 24
            
            // Header
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: Theme.headerHeight
                color: Theme.base1
                radius: Theme.radiusLarge
                border.width: 1
                border.color: Qt.rgba(0, 0.9, 1, 0.3)  // Cyan border (matching Active Tracks)
                
                // Cyan glow effect (matching Active Tracks)
                layer.enabled: true
                layer.effect: DropShadow {
                    horizontalOffset: 0
                    verticalOffset: 0
                    radius: 16
                    samples: 17
                    color: Qt.rgba(0, 0.9, 1, 0.25)  // Cyan glow
                    transparentBorder: true
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10
                    
                    // Title row with GPS
                    RowLayout {
                        spacing: 20
                        Layout.fillWidth: true
                        
                        Text {
                            text: "TriAD C2"
                            font.family: Theme.fontFamilyDisplay
                            font.pixelSize: 22
                            font.weight: Theme.fontWeightBold
                            color: Theme.textPrimary
                            font.letterSpacing: 1
                        }
                        
                        Rectangle {
                            width: 1
                            height: 30
                            color: Theme.borderSubtle
                        }
                        
                        Text {
                            text: "Counter-UAS Command & Control"
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeBody
                            color: Theme.textSecondary
                        }
                        
                        Item { Layout.fillWidth: true }
                        
                        // GPS Position
                        RowLayout {
                            spacing: 8
                            
                            Rectangle {
                                width: 8
                                height: 8
                                radius: 4
                                color: "#00ff00"
                                
                                SequentialAnimation on opacity {
                                    running: true
                                    loops: Animation.Infinite
                                    NumberAnimation { to: 0.3; duration: 1000 }
                                    NumberAnimation { to: 1.0; duration: 1000 }
                                }
                            }
                            
                            ColumnLayout {
                                spacing: 0
                                
                                Text {
                                    text: ownship ? 
                                          ownship.lat.toFixed(6) + "° N" : 
                                          "NO GPS"
                                    font.family: "SF Mono"
                                    font.pixelSize: 10
                                    color: Theme.textPrimary
                                }
                                Text {
                                    text: ownship ? 
                                          ownship.lon.toFixed(6) + "° E" : 
                                          "—"
                                    font.family: "SF Mono"
                                    font.pixelSize: 10
                                    color: Theme.textPrimary
                                }
                            }
                        }
                        
                        Rectangle {
                            width: 1
                            height: 30
                            color: Theme.borderSubtle
                        }
                        
                        // Vehicle Heading
                        ColumnLayout {
                            spacing: 0
                            
                            Text {
                                text: "HEADING"
                                font.family: Theme.fontFamily
                                font.pixelSize: 8
                                color: Theme.textSecondary
                            }
                            Text {
                                text: "045°"
                                font.family: "SF Mono"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: Theme.accentCyan
                            }
                        }
                        
                        Rectangle {
                            width: 1
                            height: 30
                            color: Theme.borderSubtle
                        }
                        
                        Text {
                            text: new Date().toLocaleTimeString(Qt.locale(), "HH:mm:ss")
                            font.family: "SF Mono"
                            font.pixelSize: Theme.fontSizeMono
                            color: Theme.textSecondary
                            
                            Timer {
                                interval: 1000
                                running: true
                                repeat: true
                                onTriggered: parent.text = new Date().toLocaleTimeString(Qt.locale(), "HH:mm:ss")
                            }
                        }
                    }
                    
                    // Sensors - Minimal dots (Option B)
                    RowLayout {
                        spacing: 16
                        Layout.fillWidth: true
                        
                        // GPS
                        RowLayout {
                            spacing: 6
                            Rectangle {
                                width: 7
                                height: 7
                                radius: 3.5
                                color: "#64748B"  // Offline: darker slate
                            }
                            Text {
                                text: "GPS"
                                font.family: Theme.fontFamily
                                font.pixelSize: 10
                                font.weight: Theme.fontWeightMedium
                                color: "#64748B"  // Offline: darker slate
                            }
                        }
                        
                        // SkyView
                        RowLayout {
                            spacing: 6
                            Rectangle {
                                width: 7
                                height: 7
                                radius: 3.5
                                color: "#64748B"  // Offline: darker slate
                            }
                            Text {
                                text: "SKYVIEW"
                                font.family: Theme.fontFamily
                                font.pixelSize: 10
                                font.weight: Theme.fontWeightMedium
                                color: "#64748B"  // Offline: darker slate
                            }
                        }
                        
                        // Echoguard
                        RowLayout {
                            spacing: 6
                            Rectangle {
                                width: 7
                                height: 7
                                radius: 3.5
                                color: "#64748B"  // Offline: darker slate
                            }
                            Text {
                                text: "ECHOGUARD"
                                font.family: Theme.fontFamily
                                font.pixelSize: 10
                                font.weight: Theme.fontWeightMedium
                                color: "#64748B"  // Offline: darker slate
                            }
                        }
                        
                        // Gunner
                        RowLayout {
                            spacing: 6
                            Rectangle {
                                width: 7
                                height: 7
                                radius: 3.5
                                color: "#64748B"  // Offline: darker slate
                            }
                            Text {
                                text: "GUNNER"
                                font.family: Theme.fontFamily
                                font.pixelSize: 10
                                font.weight: Theme.fontWeightMedium
                                color: "#64748B"  // Offline: darker slate
                            }
                        }
                        
                        Item { Layout.fillWidth: true }
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
                    Layout.preferredWidth: 380
                    Layout.fillHeight: true
                    color: Theme.base1
                    radius: Theme.radiusLarge
                    border.width: 1
                    border.color: Qt.rgba(0, 0.9, 1, 0.3)  // Cyan border (consistent style)
                    
                    // Cyan glow effect (consistent style)
                    layer.enabled: true
                    layer.effect: DropShadow {
                        horizontalOffset: 0
                        verticalOffset: 0
                        radius: 16
                        samples: 17
                        color: Qt.rgba(0, 0.9, 1, 0.25)  // Cyan glow
                        transparentBorder: true
                    }
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.cardPadding
                        spacing: 16
                        
                        RowLayout {
                            spacing: 12
                            Layout.fillWidth: true
                            
                            Text {
                                text: "ACTIVE TRACKS"
                                font.family: Theme.fontFamily
                                font.pixelSize: Theme.fontSizeHeading
                                font.weight: Theme.fontWeightSemiBold
                                font.capitalization: Font.AllUppercase
                                font.letterSpacing: 0.8
                                color: Theme.textSecondary
                                Layout.fillWidth: true
                            }
                            
                            // Track count with glow
                            Text {
                                id: trackCountText
                                text: tracksModel ? tracksModel.count : 0
                                font.family: "SF Mono"
                                font.pixelSize: 18
                                font.weight: Font.Bold
                                color: Theme.accentFocus
                                
                                // Subtle glow effect
                                layer.enabled: true
                                layer.effect: DropShadow {
                                    horizontalOffset: 0
                                    verticalOffset: 0
                                    radius: 8
                                    samples: 17
                                    color: Qt.rgba(0, 0.9, 1, 0.4)
                                    transparentBorder: true
                                }
                                
                                // Scale animation when count changes
                                property int previousCount: 0
                                onTextChanged: {
                                    if (previousCount !== 0 && previousCount !== parseInt(text)) {
                                        scaleAnim.restart()
                                    }
                                    previousCount = parseInt(text)
                                }
                                
                                SequentialAnimation {
                                    id: scaleAnim
                                    NumberAnimation {
                                        target: trackCountText
                                        property: "scale"
                                        to: 1.3
                                        duration: 150
                                        easing.type: Easing.OutQuad
                                    }
                                    NumberAnimation {
                                        target: trackCountText
                                        property: "scale"
                                        to: 1.0
                                        duration: 200
                                        easing.type: Easing.OutQuad
                                    }
                                }
                            }
                        }
                        
                        // Column headers
                        Rectangle {
                            Layout.fillWidth: true
                            height: 28
                            color: Theme.base2
                            radius: 4
                            
                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 12
                                anchors.rightMargin: 12
                                spacing: 8
                                
                                Text {
                                    text: "ID"
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.fontWeightSemiBold
                                    font.capitalization: Font.AllUppercase
                                    color: Theme.textSecondary
                                    Layout.preferredWidth: 50
                                }
                                
                                Text {
                                    text: "TYPE"
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.fontWeightSemiBold
                                    font.capitalization: Font.AllUppercase
                                    color: Theme.textSecondary
                                    Layout.preferredWidth: 70
                                }
                                
                                Text {
                                    text: "SENSOR"
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.fontWeightSemiBold
                                    font.capitalization: Font.AllUppercase
                                    color: Theme.textSecondary
                                    Layout.preferredWidth: 60
                                }
                                
                                Text {
                                    text: "RANGE"
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.fontWeightSemiBold
                                    font.capitalization: Font.AllUppercase
                                    color: Theme.textSecondary
                                    Layout.preferredWidth: 70
                                }
                                
                                Text {
                                    text: "CONF"
                                    font.family: Theme.fontFamily
                                    font.pixelSize: 10
                                    font.weight: Theme.fontWeightSemiBold
                                    font.capitalization: Font.AllUppercase
                                    color: Theme.textSecondary
                                    Layout.fillWidth: true
                                }
                            }
                        }
                        
                        // Custom track list - eliminates Qt ListView crashes
                        CustomTrackList {
                            id: customTrackList
                            Layout.fillWidth: true
                            Layout.preferredHeight: 220
                            model: tracksModel  // Pass global tracksModel to component's model property
                            selectedTrackId: root.selectedTrackId
                            trackCardHeight: Theme.trackCardHeight
                            spacing: Theme.spacingSmall
                            
                            onTrackSelected: function(trackId) {
                                console.log("[UI] Manual selection from Active Tracks: Track", trackId)
                                root.selectedTrackId = trackId
                                root.manualSelection = true
                                selectionResetTimer.restart()
                            }
                        }
                        
                        // Selected Track Detail Panel
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Theme.base1
                            radius: Theme.radiusLarge
                            border.width: 0  // No borders
                            
                            // Subtle elevation
                            layer.enabled: true
                            layer.effect: DropShadow {
                                horizontalOffset: 0
                                verticalOffset: Theme.shadowOffset
                                radius: Theme.shadowBlur
                                samples: 17
                                color: Theme.shadowMedium
                                transparentBorder: true
                            }
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 16
                                spacing: 12
                                
                                // Header
                                Text {
                                    text: root.selectedTrackId >= 0 ? "Track " + root.selectedTrackId + " Details" : "No Track Selected"
                                    font.family: Theme.fontFamilyDisplay
                                    font.pixelSize: Theme.fontSizeLarge
                                    font.weight: Theme.fontWeightSemiBold
                                    font.letterSpacing: 0.5
                                    color: root.selectedTrackId >= 0 ? Theme.textPrimary : Theme.textSecondary
                                }
                                
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true
                                    
                                    ScrollBar.vertical.policy: ScrollBar.AsNeeded
                                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                                    
                                    ColumnLayout {
                                        id: trackDetailsLayout
                                        width: parent.width
                                        spacing: 10
                                        
                                        // Find selected track data
                                        property var selectedTrack: null
                                        
                                        function updateSelectedTrack() {
                                            if (root.selectedTrackId < 0 || !tracksModel) {
                                                selectedTrack = null
                                                return
                                            }
                                            for (var i = 0; i < tracksModel.rowCount(); i++) {
                                                var track = tracksModel.data(tracksModel.index(i, 0), 0x0101)  // Qt.UserRole + 1
                                                if (track && track.id === root.selectedTrackId) {
                                                    selectedTrack = track
                                                    return
                                                }
                                            }
                                            selectedTrack = null
                                        }
                                        
                                        Component.onCompleted: updateSelectedTrack()
                                        
                                        Connections {
                                            target: root
                                            function onSelectedTrackIdChanged() {
                                                trackDetailsLayout.updateSelectedTrack()
                                            }
                                        }
                                        
                                        Connections {
                                            target: tracksModel
                                            function onDataChanged() {
                                                trackDetailsLayout.updateSelectedTrack()
                                            }
                                        }
                                        
                                        // Position Information
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: Theme.spacingSmall
                                            visible: parent.selectedTrack !== null
                                            
                                            // Section header
                                            Text {
                                                text: "Position"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: Theme.fontSizeSmall
                                                font.weight: Theme.fontWeightSemiBold
                                                font.letterSpacing: 0.5
                                                color: Theme.textSecondary
                                                Layout.fillWidth: true
                                            }
                                            
                                            Rectangle {
                                                Layout.fillWidth: true
                                                height: 1
                                                color: Theme.borderSubtle
                                            }
                                            
                                            GridLayout {
                                                id: positionGrid
                                                Layout.fillWidth: true
                                                columns: 2
                                                columnSpacing: Theme.spacing
                                                rowSpacing: Theme.spacingSmall
                                                
                                                Text { text: "Range"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.range.toFixed(1) + " m" : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                                
                                                Text { text: "Azimuth"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.azimuth.toFixed(2) + "°" : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                                
                                                Text { text: "Elevation"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.elevation.toFixed(2) + "°" : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                            }
                                        }
                                        
                                        // Classification Information
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: Theme.spacingSmall
                                            visible: parent.selectedTrack !== null
                                            
                                            // Section header
                                            Text {
                                                text: "Classification"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: Theme.fontSizeSmall
                                                font.weight: Theme.fontWeightSemiBold
                                                font.letterSpacing: 0.5
                                                color: Theme.textSecondary
                                                Layout.fillWidth: true
                                            }
                                            
                                            Rectangle {
                                                Layout.fillWidth: true
                                                height: 1
                                                color: Theme.borderSubtle
                                            }
                                            
                                            GridLayout {
                                                id: classGrid
                                                Layout.fillWidth: true
                                                columns: 2
                                                columnSpacing: Theme.spacing
                                                rowSpacing: Theme.spacingSmall
                                                
                                                Text { text: "Type"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.type : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                                
                                                Text { text: "Confidence"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? (trackDetailsLayout.selectedTrack.confidence * 100).toFixed(0) + "%" : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                                
                                                Text { text: "Source"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.source : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                            }
                                        }
                                        
                                        // Velocity Information (Echoguard Radar)
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: Theme.spacingSmall
                                            visible: parent.selectedTrack !== null
                                            
                                            // Section header
                                            Text {
                                                text: "Velocity"
                                                font.family: Theme.fontFamily
                                                font.pixelSize: Theme.fontSizeSmall
                                                font.weight: Theme.fontWeightSemiBold
                                                font.letterSpacing: 0.5
                                                color: Theme.textSecondary
                                                Layout.fillWidth: true
                                            }
                                            
                                            Rectangle {
                                                Layout.fillWidth: true
                                                height: 1
                                                color: Theme.borderSubtle
                                            }
                                            
                                            GridLayout {
                                                id: velGrid
                                                Layout.fillWidth: true
                                                columns: 2
                                                columnSpacing: Theme.spacing
                                                rowSpacing: Theme.spacingSmall
                                                
                                                Text { text: "Speed"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? 
                                                          Math.sqrt(Math.pow(trackDetailsLayout.selectedTrack.velocity_x, 2) + 
                                                                   Math.pow(trackDetailsLayout.selectedTrack.velocity_y, 2)).toFixed(1) + " m/s" : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                                
                                                Text { text: "Heading"; font.family: Theme.fontFamily; font.pixelSize: Theme.fontSizeSmall; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? 
                                                          Math.atan2(trackDetailsLayout.selectedTrack.velocity_y, 
                                                                    trackDetailsLayout.selectedTrack.velocity_x) * 180 / Math.PI + "°" : "—"
                                                    font.family: Theme.fontFamilyMono; font.pixelSize: Theme.fontSizeBody; color: Theme.textPrimary; font.weight: Theme.fontWeightMedium
                                                }
                                                
                                                Text { text: "Vel X (fwd):"; font.family: Theme.fontFamily; font.pixelSize: 11; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.velocity_x.toFixed(2) + " m/s" : "—"
                                                    font.family: "SF Mono"; font.pixelSize: 11; color: Theme.textPrimary
                                                }
                                                
                                                Text { text: "Vel Y (side):"; font.family: Theme.fontFamily; font.pixelSize: 11; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack ? trackDetailsLayout.selectedTrack.velocity_y.toFixed(2) + " m/s" : "—"
                                                    font.family: "SF Mono"; font.pixelSize: 11; color: Theme.textPrimary
                                                }
                                            }
                                        }
                                        
                                        // RF Sensor Information (SkyView)
                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: rfGrid.implicitHeight + 20
                                            color: Qt.rgba(Theme.accentYellow.r, Theme.accentYellow.g, Theme.accentYellow.b, 0.05)
                                            radius: 4
                                            visible: parent.selectedTrack !== null && parent.selectedTrack.source !== "RADAR"
                                            
                                            GridLayout {
                                                id: rfGrid
                                                anchors.fill: parent
                                                anchors.margins: 10
                                                columns: 2
                                                columnSpacing: 16
                                                rowSpacing: 8
                                                
                                                Text {
                                                    text: "RF INTELLIGENCE (SKYVIEW)"
                                                    font.family: Theme.fontFamily
                                                    font.pixelSize: 10
                                                    font.weight: Theme.fontWeightSemiBold
                                                    font.letterSpacing: 1
                                                    color: Theme.accentYellow
                                                    Layout.columnSpan: 2
                                                }
                                                
                                                Text { text: "Aircraft Model:"; font.family: Theme.fontFamily; font.pixelSize: 11; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack && trackDetailsLayout.selectedTrack.aircraft_model ? 
                                                          trackDetailsLayout.selectedTrack.aircraft_model : "Unknown"
                                                    font.family: "SF Mono"; font.pixelSize: 11; color: Theme.accentYellow; font.weight: Font.Bold
                                                }
                                                
                                                Text { text: "Pilot Location:"; font.family: Theme.fontFamily; font.pixelSize: 11; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack && trackDetailsLayout.selectedTrack.pilot_lat ? 
                                                          trackDetailsLayout.selectedTrack.pilot_lat.toFixed(6) + ", " + 
                                                          trackDetailsLayout.selectedTrack.pilot_lon.toFixed(6) : "Unknown"
                                                    font.family: "SF Mono"; font.pixelSize: 10; color: Theme.textPrimary
                                                }
                                                
                                                Text { text: "Frequency:"; font.family: Theme.fontFamily; font.pixelSize: 11; color: Theme.textSecondary }
                                                Text { 
                                                    text: trackDetailsLayout.selectedTrack && trackDetailsLayout.selectedTrack.frequency ? 
                                                          trackDetailsLayout.selectedTrack.frequency + " MHz" : "—"
                                                    font.family: "SF Mono"; font.pixelSize: 11; color: Theme.textPrimary
                                                }
                                            }
                                        }
                                        
                                        Item { Layout.fillHeight: true }
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Center - Tactical Display
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Qt.darker(Theme.base1, 1.15)  // Medium-dark background - between base0 and base1
                    radius: Theme.radiusLarge
                    border.width: 1
                    border.color: Qt.rgba(0, 0.9, 1, 0.3)  // Cyan border (matching all panels)
                    
                    // Cyan glow effect (matching all panels)
                    layer.enabled: true
                    layer.effect: DropShadow {
                        horizontalOffset: 0
                        verticalOffset: 0
                        radius: 16
                        samples: 17
                        color: Qt.rgba(0, 0.9, 1, 0.25)  // Cyan glow
                        transparentBorder: true
                    }
                    
                    Item {
                        id: radarDisplay
                        anchors.centerIn: parent
                        width: Math.min(parent.width, parent.height) * 0.92
                        height: width
                        
                        property real vehicleHeading: 45  // degrees from north
                        property real radarPointing: 90   // degrees from north
                        property real maxRange: 3000      // meters - adjustable with zoom
                        property real zoomLevel: 1.0      // 1.0 = 3000m, 2.0 = 1500m, 0.5 = 6000m
                        
                        // Mouse wheel zoom
                        MouseArea {
                            anchors.fill: parent
                            acceptedButtons: Qt.NoButton
                            onWheel: (wheel) => {
                                var delta = wheel.angleDelta.y / 120
                                var newZoom = radarDisplay.zoomLevel * Math.pow(1.2, delta)
                                radarDisplay.zoomLevel = Math.max(0.25, Math.min(8.0, newZoom))
                                radarDisplay.maxRange = 3000 / radarDisplay.zoomLevel
                                wheel.accepted = true
                            }
                        }
                        
                        // Range rings (very subtle - minimal visual weight)
                        Repeater {
                            model: 5
                            Rectangle {
                                anchors.centerIn: parent
                                width: parent.width * (index + 1) / 5
                                height: width
                                radius: width / 2
                                color: "transparent"
                                border.width: index === 4 ? 0.5 : 1  // Outer ring extremely thin
                                border.color: Qt.rgba(1, 1, 1, 0.1)  // Very subtle, almost invisible
                                z: 100  // Ensure rings are visible on top
                            }
                        }
                        
                        // Range labels with semi-transparent pills
                        Repeater {
                            model: 5
                            Rectangle {
                                x: parent.width / 2 + (parent.width * (index + 1) / 10) - width / 2
                                y: parent.height / 2 - height / 2
                                width: rangeText.width + 12
                                height: rangeText.height + 6
                                radius: height / 2
                                color: Qt.rgba(0, 0, 0, 0.6)  // Semi-transparent black pill
                                border.width: 1
                                border.color: Qt.rgba(255, 255, 255, 0.1)
                                
                                Text {
                                    id: rangeText
                                    anchors.centerIn: parent
                                    text: {
                                        var rangePerRing = radarDisplay.maxRange / 5
                                        var range = (index + 1) * rangePerRing
                                        return range >= 1000 ? (range / 1000).toFixed(1) + "km" : range.toFixed(0) + "m"
                                    }
                                    font.family: "SF Mono"
                                    font.pixelSize: 11
                                    font.weight: Font.Bold
                                    color: Theme.textPrimary
                                }
                            }
                        }
                        
                        // Radar Field of View (120 degrees wedge)
                        Canvas {
                            id: fovCanvas
                            anchors.centerIn: parent
                            width: parent.width
                            height: parent.height
                            
                            property real radarPointingRad: (parent.radarPointing - 90) * Math.PI / 180
                            property real fovAngle: 120 * Math.PI / 180  // 120 degrees in radians
                            
                            // Very subtle glow effect for the FOV outline
                            layer.enabled: true
                            layer.effect: DropShadow {
                                horizontalOffset: 0
                                verticalOffset: 0
                                radius: 8
                                samples: 17
                                color: Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.15)
                                transparentBorder: true
                            }
                            
                            Component.onCompleted: requestPaint()
                            
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.reset()
                                
                                var centerX = width / 2
                                var centerY = height / 2
                                var radius = width / 2
                                
                                // Draw FoV wedge
                                ctx.beginPath()
                                ctx.moveTo(centerX, centerY)
                                ctx.arc(centerX, centerY, radius, 
                                       radarPointingRad - fovAngle/2, 
                                       radarPointingRad + fovAngle/2, false)
                                ctx.closePath()
                                
                                // Fill with very light transparent cyan
                                ctx.fillStyle = Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.03)
                                ctx.fill()
                                
                                // Ultra-thin, very light border
                                ctx.strokeStyle = Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.25)
                                ctx.lineWidth = 0.5  // Extremely thin
                                ctx.stroke()
                            }
                        }
                        
                        // FOV Sweep removed per user request
                        
                        // Center dot removed per user request - only heading arrow remains
                        
                        // Ownship position indicator - heading arrow only
                        Item {
                            anchors.centerIn: parent
                            width: parent.width
                            height: parent.height
                            rotation: parent.vehicleHeading
                            
                            Canvas {
                                id: ownshipCanvas
                                anchors.centerIn: parent
                                width: parent.width
                                height: parent.height
                                
                                // Pulsing animation disabled
                                // SequentialAnimation on scale {
                                //     running: true
                                //     loops: Animation.Infinite
                                //     NumberAnimation { to: 1.08; duration: 2000; easing.type: Easing.InOutQuad }
                                //     NumberAnimation { to: 1.0; duration: 2000; easing.type: Easing.InOutQuad }
                                // }
                                
                                // White glow removed per user request
                                layer.enabled: false
                                
                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.reset()
                                    
                                    var centerX = width / 2
                                    var centerY = height / 2
                                    
                                    // Draw vehicle heading arrow - twice as large
                                    ctx.beginPath()
                                    ctx.moveTo(centerX, centerY - 30)
                                    ctx.lineTo(centerX - 16, centerY + 10)
                                    ctx.lineTo(centerX, centerY)
                                    ctx.lineTo(centerX + 16, centerY + 10)
                                    ctx.closePath()
                                    
                                    ctx.fillStyle = "#FFFFFF"
                                    ctx.fill()
                                    ctx.strokeStyle = "#1E293B"
                                    ctx.lineWidth = 3
                                    ctx.stroke()
                                }
                            }
                        }
                        
                        // Radar pointing indicator - ultra-thin and twice as long
                        Item {
                            anchors.centerIn: parent
                            width: parent.width
                            height: parent.height
                            rotation: parent.radarPointing
                            
                            Rectangle {
                                anchors.horizontalCenter: parent.horizontalCenter
                                y: parent.height / 2 - 240
                                width: 1
                                height: 240
                                color: Theme.accentCyan
                                
                                Rectangle {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.top: parent.top
                                    width: 8
                                    height: 8
                                    rotation: 45
                                    color: Theme.accentCyan
                                }
                            }
                        }
                        
                        // Track tails layer (single Canvas for all tracks)
                        Canvas {
                            id: tailsCanvas
                            anchors.fill: parent
                            z: 5  // Below track dots (z: 10)
                            
                            // Trigger repaint when model changes
                            Connections {
                                target: tracksModel
                                function onCountChanged() {
                                    tailsCanvas.requestPaint()
                                }
                            }
                            
                            // Update tails frequently for smooth rendering
                            Timer {
                                interval: 200  // 5 Hz - balance between smoothness and performance
                                running: true
                                repeat: true
                                onTriggered: tailsCanvas.requestPaint()
                            }
                            
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.reset()
                                
                                var centerX = width / 2
                                var centerY = height / 2
                                var radarRadius = width / 2
                                var currentTime = Date.now() / 1000
                                
                                // Draw tails for all tracks
                                for (var t = 0; t < tracksModel.rowCount(); t++) {
                                    var trackData = tracksModel.data(tracksModel.index(t, 0), 0x0101)
                                    if (!trackData || !trackData.tail) continue
                                    
                                    var tailPositions = trackData.tail
                                    if (tailPositions.length < 2) continue
                                    
                                    // Draw tail segments for this track
                                    for (var i = 0; i < tailPositions.length - 1; i++) {
                                        var pos1 = tailPositions[i]
                                        var pos2 = tailPositions[i + 1]
                                        
                                        var range1 = Math.min(pos1.range / radarDisplay.maxRange, 1.0)
                                        var range2 = Math.min(pos2.range / radarDisplay.maxRange, 1.0)
                                        var angle1 = pos1.az * Math.PI / 180
                                        var angle2 = pos2.az * Math.PI / 180
                                        
                                        var x1 = centerX + Math.sin(angle1) * range1 * radarRadius
                                        var y1 = centerY - Math.cos(angle1) * range1 * radarRadius
                                        var x2 = centerX + Math.sin(angle2) * range2 * radarRadius
                                        var y2 = centerY - Math.cos(angle2) * range2 * radarRadius
                                        
                                        // Fade based on age
                                        var age = currentTime - pos1.time
                                        var fade = 1.0 - (age / 15.0)
                                        fade = Math.max(0.1, Math.min(1.0, fade))
                                        
                                        ctx.beginPath()
                                        ctx.moveTo(x1, y1)
                                        ctx.lineTo(x2, y2)
                                        
                                        var baseColor = trackData.type === "UAV" ? "#EF4444" :
                                                      trackData.type === "BIRD" ? "#475569" :
                                                      trackData.type === "UNKNOWN" ? "#00E5FF" : "#a0a0a0"
                                        
                                        ctx.strokeStyle = Qt.rgba(
                                            parseInt(baseColor.substring(1,3), 16) / 255,
                                            parseInt(baseColor.substring(3,5), 16) / 255,
                                            parseInt(baseColor.substring(5,7), 16) / 255,
                                            fade * 0.8
                                        )
                                        ctx.lineWidth = 3
                                        ctx.stroke()
                                    }
                                }
                            }
                        }
                        
                        // Tracks on radar
                        Repeater {
                            model: tracksModel
                            
                            Item {
                                property real radarRadius: parent.width / 2
                                property real normalizedRange: Math.min(modelData.range / radarDisplay.maxRange, 1.0)
                                property real angleRad: modelData.azimuth * Math.PI / 180
                                
                                property real targetX: parent.width / 2 + Math.sin(angleRad) * normalizedRange * radarRadius - width / 2
                                property real targetY: parent.height / 2 - Math.cos(angleRad) * normalizedRange * radarRadius - height / 2
                                
                                // Use root's single source of truth for highest priority
                                // (no local calculation to avoid race conditions)
                                
                                x: targetX
                                y: targetY
                                
                                // Smooth position transitions
                                Behavior on x { 
                                    NumberAnimation { 
                                        duration: 100
                                        easing.type: Easing.OutQuad
                                    }
                                }
                                Behavior on y { 
                                    NumberAnimation { 
                                        duration: 100
                                        easing.type: Easing.OutQuad
                                    }
                                }
                                
                                width: 60
                                height: 60
                                z: 10  // Above tails
                                
                                // Highest priority track ring (red) - CRITICAL THREAT INDICATOR
                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 32
                                    height: 32
                                    radius: width / 2
                                    color: "transparent"
                                    border.width: 3
                                    border.color: Theme.accentThreat  // Red for highest priority
                                    opacity: 1.0
                                    visible: modelData && modelData.id === root.highestPriorityTrackId
                                    
                                    // Pulsing animation for highest threat
                                    SequentialAnimation on scale {
                                        running: modelData && modelData.id === root.highestPriorityTrackId
                                        loops: Animation.Infinite
                                        NumberAnimation { from: 1.0; to: 1.15; duration: 800; easing.type: Easing.InOutQuad }
                                        NumberAnimation { from: 1.15; to: 1.0; duration: 800; easing.type: Easing.InOutQuad }
                                    }
                                    
                                    // Glow effect
                                    layer.enabled: true
                                    layer.effect: DropShadow {
                                        horizontalOffset: 0
                                        verticalOffset: 0
                                        radius: 16
                                        samples: 17
                                        color: Theme.accentThreat
                                        transparentBorder: true
                                    }
                                }
                                
                                // Selected track ring (white) - larger outer ring
                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 28
                                    height: 28
                                    radius: width / 2
                                    color: "transparent"
                                    border.width: 2
                                    border.color: "#ffffff"  // White for selected
                                    opacity: 0.8
                                    visible: modelData && root.selectedTrackId === modelData.id
                                }
                                
                                // Main track dot (fixed size to prevent clutter)
                                Rectangle {
                                    id: trackDot
                                    anchors.centerIn: parent
                                    width: 12  // Fixed size
                                    height: 12
                                    radius: 6
                                    
                                    // Color by type - Monochrome + Critical Red (Ultra-Minimal)
                                    color: {
                                        if (!modelData) return "#a0a0a0"
                                        if (modelData.type === "UAV") return "#EF4444"  // Clean modern red - confirmed threat
                                        if (modelData.type === "BIRD") return "#475569"  // Darker muted slate - subtle non-threat
                                        if (modelData.type === "UNKNOWN") return "#00E5FF"  // Cyan - uncertain
                                        return "#a0a0a0"  // Gray fallback
                                    }
                                    
                                    // No border - we use rings instead
                                    border.width: 0
                                    
                                    Behavior on width { NumberAnimation { duration: Theme.durationFast } }
                                    Behavior on color { ColorAnimation { duration: 300 } }
                                }
                                
                                // Track ID label above dot
                                Rectangle {
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.bottom: trackDot.top
                                    anchors.bottomMargin: 4
                                    width: idText.width + 6
                                    height: idText.height + 2
                                    radius: 2
                                    color: Qt.rgba(0, 0, 0, 0.8)
                                    border.width: 1
                                    border.color: Qt.rgba(255, 255, 255, 0.2)
                                    visible: modelData
                                    
                                    Text {
                                        id: idText
                                        anchors.centerIn: parent
                                        text: modelData ? modelData.id : ""
                                        font.family: Theme.fontFamilyMono
                                        font.pixelSize: 9
                                        font.weight: Font.Bold
                                        color: "#FFFFFF"
                                    }
                                }
                                
                                // Velocity arrows removed per user request
                                
                                // Clickable area for track selection - small area for precise clicking
                                MouseArea {
                                    anchors.centerIn: parent
                                    width: 24  // Small clickable area (just the dot)
                                    height: 24
                                    z: 20  // Ensure it's on top of everything
                                    hoverEnabled: true
                                    cursorShape: Qt.PointingHandCursor
                                    enabled: modelData !== null && modelData !== undefined
                                    
                                    onEntered: {
                                        // Mouse over track dot
                                    }
                                    onPressed: {
                                        if (!modelData) return
                                        console.log("[UI] Manual selection from Tactical Display: Track", modelData.id)
                                        root.selectedTrackId = modelData.id
                                        root.manualSelection = true
                                        selectionResetTimer.restart()
                                    }
                                    
                                    // Tooltip
                                    ToolTip {
                                        visible: modelData && parent.containsMouse
                                        text: modelData ? ("Track " + modelData.id + " - " + modelData.type + "\n" +
                                              "Range: " + modelData.range.toFixed(0) + "m\n" +
                                              "Azimuth: " + modelData.azimuth.toFixed(1) + "°") : ""
                                        delay: 500
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
                        text: "TACTICAL DISPLAY"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeHeading
                        font.weight: Theme.fontWeightSemiBold
                        font.capitalization: Font.AllUppercase
                        font.letterSpacing: 0.8
                        color: Theme.textSecondary
                    }
                    
                    // Zoom controls
                    Row {
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 20
                        spacing: 10
                        
                        // Zoom level indicator
                        Rectangle {
                            width: 100
                            height: 32
                            radius: 4
                            color: Qt.rgba(Theme.base2.r, Theme.base2.g, Theme.base2.b, 0.8)
                            border.width: 1
                            border.color: Theme.borderSubtle
                            
                            Text {
                                anchors.centerIn: parent
                                text: radarDisplay.maxRange >= 1000 ? 
                                      (radarDisplay.maxRange / 1000).toFixed(1) + " km" : 
                                      radarDisplay.maxRange.toFixed(0) + " m"
                                font.family: "SF Mono"
                                font.pixelSize: 12
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                        }
                        
                        // Zoom in button
                        Rectangle {
                            width: 32
                            height: 32
                            radius: 4
                            color: zoomInMouse.containsMouse ? Theme.accentCyan : Theme.base2
                            border.width: 1
                            border.color: Theme.borderSubtle
                            
                            Text {
                                anchors.centerIn: parent
                                text: "+"
                                font.pixelSize: 18
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            
                            MouseArea {
                                id: zoomInMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    radarDisplay.zoomLevel = Math.min(8.0, radarDisplay.zoomLevel * 1.5)
                                    radarDisplay.maxRange = 3000 / radarDisplay.zoomLevel
                                }
                            }
                        }
                        
                        // Zoom out button
                        Rectangle {
                            width: 32
                            height: 32
                            radius: 4
                            color: zoomOutMouse.containsMouse ? Theme.accentCyan : Theme.base2
                            border.width: 1
                            border.color: Theme.borderSubtle
                            
                            Text {
                                anchors.centerIn: parent
                                text: "−"
                                font.pixelSize: 18
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            
                            MouseArea {
                                id: zoomOutMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    radarDisplay.zoomLevel = Math.max(0.25, radarDisplay.zoomLevel / 1.5)
                                    radarDisplay.maxRange = 3000 / radarDisplay.zoomLevel
                                }
                            }
                        }
                        
                        // Reset zoom button
                        Rectangle {
                            width: 32
                            height: 32
                            radius: 4
                            color: resetMouse.containsMouse ? Theme.accentYellow : Theme.base2
                            border.width: 1
                            border.color: Theme.borderSubtle
                            
                            Text {
                                anchors.centerIn: parent
                                text: "⊙"
                                font.pixelSize: 16
                                font.weight: Font.Bold
                                color: Theme.textPrimary
                            }
                            
                            MouseArea {
                                id: resetMouse
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    radarDisplay.zoomLevel = 1.0
                                    radarDisplay.maxRange = 3000
                                }
                            }
                        }
                    }
                    
                    // Zoom percentage indicator - positioned better
                    Rectangle {
                        anchors.top: parent.top
                        anchors.right: parent.right
                        anchors.margins: 20
                        anchors.topMargin: 60
                        width: 55
                        height: 28
                        radius: 4
                        color: Qt.rgba(Theme.base2.r, Theme.base2.g, Theme.base2.b, 0.8)
                        border.width: 1
                        border.color: Theme.borderSubtle
                        
                        Text {
                            anchors.centerIn: parent
                            text: `${(radarDisplay.zoomLevel * 100).toFixed(0)}%`
                            font.family: Theme.fontFamilyMono
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                        }
                    }
                    
                    // Compass rose (bottom right)
                    Item {
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        anchors.margins: 24
                        width: 90
                        height: 90
                        
                        // Outer circle with background
                        Rectangle {
                            anchors.centerIn: parent
                            width: parent.width
                            height: parent.height
                            radius: width / 2
                            color: Qt.rgba(0, 0, 0, 0.7)
                            border.width: 2
                            border.color: Theme.borderSubtle
                            
                            // Subtle gradient effect
                            layer.enabled: true
                            layer.effect: DropShadow {
                                horizontalOffset: 0
                                verticalOffset: 2
                                radius: 8
                                samples: 17
                                color: Qt.rgba(0, 0, 0, 0.5)
                                transparentBorder: true
                            }
                        }
                        
                        // Cardinal direction markers
                        Canvas {
                            anchors.fill: parent
                            onPaint: {
                                var ctx = getContext("2d")
                                ctx.reset()
                                
                                var centerX = width / 2
                                var centerY = height / 2
                                var radius = width / 2 - 4
                                
                                // Draw tick marks
                                ctx.strokeStyle = Theme.textSecondary
                                ctx.lineWidth = 1
                                
                                for (var i = 0; i < 12; i++) {
                                    var angle = i * Math.PI / 6 - Math.PI / 2
                                    var isMajor = i % 3 === 0
                                    var startRadius = isMajor ? radius - 8 : radius - 4
                                    
                                    ctx.beginPath()
                                    ctx.moveTo(centerX + startRadius * Math.cos(angle),
                                              centerY + startRadius * Math.sin(angle))
                                    ctx.lineTo(centerX + radius * Math.cos(angle),
                                              centerY + radius * Math.sin(angle))
                                    ctx.stroke()
                                }
                            }
                        }
                        
                        // N (North)
                        Text {
                            anchors.top: parent.top
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.topMargin: 8
                            text: "N"
                            font.family: Theme.fontFamilyDisplay
                            font.pixelSize: 16
                            font.weight: Font.Bold
                            color: Theme.accentFocus
                        }
                        
                        // S (South)
                        Text {
                            anchors.bottom: parent.bottom
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottomMargin: 8
                            text: "S"
                            font.family: Theme.fontFamilyDisplay
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }
                        
                        // E (East)
                        Text {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.rightMargin: 8
                            text: "E"
                            font.family: Theme.fontFamilyDisplay
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }
                        
                        // W (West)
                        Text {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 8
                            text: "W"
                            font.family: Theme.fontFamilyDisplay
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                        }
                    }
                    
                    // Distance scale bar (bottom left)
                    Rectangle {
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom
                        anchors.margins: 24
                        width: 120
                        height: 40
                        radius: 6
                        color: Qt.rgba(0, 0, 0, 0.7)
                        border.width: 1
                        border.color: Theme.borderSubtle
                        
                        layer.enabled: true
                        layer.effect: DropShadow {
                            horizontalOffset: 0
                            verticalOffset: 2
                            radius: 8
                            samples: 17
                            color: Qt.rgba(0, 0, 0, 0.5)
                            transparentBorder: true
                        }
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4
                            
                            Text {
                                text: "SCALE"
                                font.family: Theme.fontFamily
                                font.pixelSize: 8
                                font.weight: Font.Bold
                                color: Theme.textSecondary
                                Layout.alignment: Qt.AlignHCenter
                            }
                            
                            RowLayout {
                                spacing: 8
                                Layout.fillWidth: true
                                
                                Rectangle {
                                    Layout.preferredWidth: 60
                                    height: 3
                                    color: Theme.textPrimary
                                    
                                    // Tick marks at ends
                                    Rectangle {
                                        anchors.left: parent.left
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 2
                                        height: 8
                                        color: Theme.textPrimary
                                    }
                                    
                                    Rectangle {
                                        anchors.right: parent.right
                                        anchors.verticalCenter: parent.verticalCenter
                                        width: 2
                                        height: 8
                                        color: Theme.textPrimary
                                    }
                                }
                                
                                Text {
                                    text: {
                                        var scaleDistance = radarDisplay.maxRange / 4
                                        return scaleDistance >= 1000 ? 
                                               (scaleDistance / 1000).toFixed(1) + " km" : 
                                               scaleDistance.toFixed(0) + " m"
                                    }
                                    font.family: Theme.fontFamilyMono
                                    font.pixelSize: 11
                                    font.weight: Font.Bold
                                    color: Theme.textPrimary
                                }
                            }
                        }
                    }
                }
                
                // Right Panel - Engagement Control
                EngagementPanel {
                    Layout.preferredWidth: 320
                    Layout.fillHeight: true
                    selectedTrackId: root.selectedTrackId
                    
                    onResetToHighestPriority: {
                        console.log("[UI] Reset to highest priority requested")
                        root.manualSelection = false
                        // Force update highest priority
                        var highestId = bridge.get_highest_priority_track_id()
                        root.highestPriorityTrackId = highestId
                        root.selectedTrackId = highestId
                        console.log("[UI] Reset complete - selected track:", highestId)
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
                border.color: Qt.rgba(0, 0.9, 1, 0.3)  // Cyan border (matching all panels)
                
                // Cyan glow effect (matching all panels)
                layer.enabled: true
                layer.effect: DropShadow {
                    horizontalOffset: 0
                    verticalOffset: 0
                    radius: 16
                    samples: 17
                    color: Qt.rgba(0, 0.9, 1, 0.25)  // Cyan glow
                    transparentBorder: true
                }
                
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 20
                    anchors.rightMargin: 20
                    spacing: 12
                    
                    Text {
                        text: "SYSTEM OPERATIONAL"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Theme.fontWeightSemiBold
                        font.capitalization: Font.AllUppercase
                        color: Theme.accentCyan
                    }
                    
                    Rectangle {
                        width: 1
                        height: 24
                        color: Theme.borderSubtle
                    }
                    
                    // ===== TEST SCENARIO CONTROLS (TEMPORARY - DELETE BEFORE PRODUCTION) =====
                    Text {
                        text: "TEST:"
                        font.family: Theme.fontFamily
                        font.pixelSize: 9
                        font.weight: Font.Bold
                        color: Theme.textSecondary
                    }
                    
                    Button {
                        text: "SCENARIO 2"
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 32
                        
                        background: Rectangle {
                            color: parent.hovered ? Qt.rgba(Theme.accentThreat.r, Theme.accentThreat.g, Theme.accentThreat.b, 0.2) : "transparent"
                            border.width: 0
                            radius: Theme.radiusSmall
                            
                            Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeTiny
                            font.weight: Theme.fontWeightSemiBold
                            color: Theme.accentThreat
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("[TEST] Loading Scenario 2: Single Track")
                            engine.load_test_scenario('scenario_2')
                        }
                        
                        ToolTip {
                            visible: parent.hovered
                            text: "Single Track Testing\n1 track at 1000m, 25 m/s"
                            delay: 500
                        }
                    }
                    
                    Button {
                        text: "SCENARIO 3"
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 32
                        
                        background: Rectangle {
                            color: parent.hovered ? Qt.rgba(Theme.accentThreat.r, Theme.accentThreat.g, Theme.accentThreat.b, 0.2) : "transparent"
                            border.width: 0
                            radius: Theme.radiusSmall
                            
                            Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeTiny
                            font.weight: Theme.fontWeightSemiBold
                            color: Theme.accentThreat
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("[TEST] Loading Scenario 3: Priority Algorithm")
                            engine.load_test_scenario('scenario_3')
                        }
                        
                        ToolTip {
                            visible: parent.hovered
                            text: "Priority Algorithm Testing\n5 tracks at various ranges, 10-50 m/s"
                            delay: 500
                        }
                    }
                    
                    Button {
                        text: "SCENARIO 4"
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 32
                        
                        background: Rectangle {
                            color: parent.hovered ? Qt.rgba(Theme.accentThreat.r, Theme.accentThreat.g, Theme.accentThreat.b, 0.2) : "transparent"
                            border.width: 0
                            radius: Theme.radiusSmall
                            
                            Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeTiny
                            font.weight: Theme.fontWeightSemiBold
                            color: Theme.accentThreat
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("[TEST] Loading Scenario 4: Sensor Fusion")
                            engine.load_test_scenario('scenario_4')
                        }
                        
                        ToolTip {
                            visible: parent.hovered
                            text: "Sensor Fusion Testing\n2 FUSED tracks with RF intelligence"
                            delay: 500
                        }
                    }
                    
                    Button {
                        text: "SCENARIO 5"
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 32
                        
                        background: Rectangle {
                            color: parent.hovered ? Qt.rgba(Theme.accentThreat.r, Theme.accentThreat.g, Theme.accentThreat.b, 0.2) : "transparent"
                            border.width: 0
                            radius: Theme.radiusSmall
                            
                            Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.family: Theme.fontFamily
                            font.pixelSize: Theme.fontSizeTiny
                            font.weight: Theme.fontWeightSemiBold
                            color: Theme.accentThreat
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("[TEST] Loading Scenario 5: Stress Test")
                            engine.load_test_scenario('scenario_5')
                        }
                        
                        ToolTip {
                            visible: parent.hovered
                            text: "Stress Testing\n25 tracks, all moving 10-50 m/s"
                            delay: 500
                        }
                    }
                    
                    Button {
                        text: "DISABLE"
                        Layout.preferredWidth: 70
                        Layout.preferredHeight: 28
                        
                        background: Rectangle {
                            color: parent.pressed ? Qt.darker(Theme.base2, 1.2) : Theme.base2
                            border.width: 1
                            border.color: Theme.textSecondary
                            radius: 3
                        }
                        
                        contentItem: Text {
                            text: parent.text
                            font.family: Theme.fontFamily
                            font.pixelSize: 9
                            font.weight: Font.Bold
                            color: Theme.textSecondary
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("[TEST] Disabling test scenarios - clearing all tracks")
                            engine.load_test_scenario('disable')
                        }
                        
                        ToolTip {
                            visible: parent.hovered
                            text: "Disable All Scenarios\nClear simulated tracks\nWait for real sensor inputs"
                            delay: 500
                        }
                    }
                    // ===== END TEST CONTROLS =====
                    
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
