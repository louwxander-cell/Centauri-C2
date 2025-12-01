import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQml.Models 2.15
import Qt5Compat.GraphicalEffects
import ".."  // Import parent module to get Theme singleton

// Custom track list with manual rendering for military-grade reliability
// Eliminates Qt ListView crashes by using Repeater with position animations
Item {
    id: trackListRoot
    
    // Properties
    property var model  // Renamed from tracksModel to avoid collision with global context property
    property int selectedTrackId: -1  // Track ID (int type to match Main.qml)
    property int trackCardHeight: 36  // Reduced for minimal look
    property int spacing: 3  // Tighter spacing
    
    // Signals
    signal trackSelected(int trackId)
    
    // ListModel for proper move animations
    ListModel {
        id: sortedTracksModel
    }
    
    Component.onCompleted: {
        // Delay to allow property binding to complete
        Qt.callLater(function() {
            updateSort()
        })
    }
    
    // Throttle timer to prevent excessive updates
    Timer {
        id: updateThrottle
        interval: 50  // 50ms throttle - fast but prevents spam
        repeat: false
        onTriggered: performSort()
    }
    
    // Request sort update (throttled)
    function updateSort() {
        if (!updateThrottle.running) {
            updateThrottle.start()
        }
    }
    
    // Perform actual sort with proper move operations for animations
    function performSort() {
        if (!model || model.count === 0) {
            sortedTracksModel.clear()
            return
        }
        
        // Build array of {index, priority, id, range}
        let trackData = []
        for (let i = 0; i < model.count; i++) {
            let track = model.data(model.index(i, 0), 257)
            if (track) {
                let priority = track.threat_priority !== undefined ? track.threat_priority : 0.0
                trackData.push({
                    modelIndex: i,
                    priority: priority,
                    id: track.id,
                    range: track.range
                })
            }
        }
        
        // Sort by priority (highest first)
        trackData.sort((a, b) => b.priority - a.priority)
        
        // Sync with ListModel using move operations
        // First pass: ensure all tracks exist
        for (let i = 0; i < trackData.length; i++) {
            let found = false
            for (let j = 0; j < sortedTracksModel.count; j++) {
                if (sortedTracksModel.get(j).id === trackData[i].id) {
                    found = true
                    break
                }
            }
            if (!found) {
                sortedTracksModel.append(trackData[i])
            }
        }
        
        // Second pass: remove tracks that no longer exist
        for (let i = sortedTracksModel.count - 1; i >= 0; i--) {
            let found = false
            for (let j = 0; j < trackData.length; j++) {
                if (sortedTracksModel.get(i).id === trackData[j].id) {
                    found = true
                    break
                }
            }
            if (!found) {
                sortedTracksModel.remove(i)
            }
        }
        
        // Third pass: reorder using move operations (this triggers animations!)
        for (let targetPos = 0; targetPos < trackData.length; targetPos++) {
            let targetId = trackData[targetPos].id
            
            // Find current position of this track
            for (let currentPos = targetPos; currentPos < sortedTracksModel.count; currentPos++) {
                if (sortedTracksModel.get(currentPos).id === targetId) {
                    if (currentPos !== targetPos) {
                        // Move it to correct position - this triggers animation!
                        sortedTracksModel.move(currentPos, targetPos, 1)
                    }
                    // Update the data
                    sortedTracksModel.set(targetPos, trackData[targetPos])
                    break
                }
            }
        }
    }
    
    onModelChanged: {
        updateSort()
    }
    
    Connections {
        target: model
        function onCountChanged() {
            updateSort()
        }
        function onDataChanged() {
            // Update immediately when data changes (syncs with selection)
            updateSort()
        }
        function onRowsInserted() {
            updateSort()
        }
        function onRowsRemoved() {
            updateSort()
        }
        function onModelReset() {
            updateSort()
        }
    }
    
    // Periodic update as fallback (in case signals don't fire for property changes)
    Timer {
        id: periodicUpdate
        interval: 200  // 200ms = 5 Hz
        running: model !== undefined && model !== null
        repeat: true
        onTriggered: {
            updateSort()
        }
    }
    
    // ListView with conservative animations (no ListView transitions - manual only)
    ListView {
        id: listView
        anchors.fill: parent
        clip: true
        
        model: sortedTracksModel
        spacing: trackListRoot.spacing
        
        boundsBehavior: Flickable.StopAtBounds
        flickDeceleration: 1500
        maximumFlickVelocity: 2500
        
        // Smooth reordering animations with scale effect
        move: Transition {
            SequentialAnimation {
                ParallelAnimation {
                    NumberAnimation {
                        properties: "y"
                        duration: 250
                        easing.type: Easing.InOutQuad
                    }
                    NumberAnimation {
                        property: "scale"
                        to: 1.05
                        duration: 125
                        easing.type: Easing.OutQuad
                    }
                }
                NumberAnimation {
                    property: "scale"
                    to: 1.0
                    duration: 125
                    easing.type: Easing.InQuad
                }
            }
        }
        
        moveDisplaced: Transition {
            NumberAnimation {
                properties: "y"
                duration: 250
                easing.type: Easing.InOutQuad
            }
        }
        
        displaced: Transition {
            NumberAnimation {
                properties: "y"
                duration: 250
                easing.type: Easing.InOutQuad
            }
        }
        
        // No add/remove animations - instant only
        add: null
        remove: null
        
        delegate: Item {
            id: trackContainer
            width: listView.width
            height: trackListRoot.trackCardHeight
            
            // Scale transform for smooth animation
            transformOrigin: Item.Center
            
            property int modelIndex: model.modelIndex  // The actual model index from ListModel
            property var trackData: trackListRoot.model ? 
                                   trackListRoot.model.data(trackListRoot.model.index(modelIndex, 0), 257) : null
            
            // ListView handles positioning - no manual y needed
                    
            Rectangle {
                id: trackCard
                anchors.fill: parent
                radius: 4  // Smaller radius for minimal look
                visible: trackContainer.trackData !== null && trackContainer.trackData !== undefined
                
                // Hover effect
                property bool hovered: false
                
                // Colors - highlight selected track
                color: (trackContainer.trackData && trackListRoot.selectedTrackId === trackContainer.trackData.id) ? 
                       Theme.base3 : 
                       Theme.base2
                border.width: (trackContainer.trackData && trackListRoot.selectedTrackId === trackContainer.trackData.id) ? 1 : 0
                border.color: Theme.accentFocus
                
                // Smooth border animation
                Behavior on border.width { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                
                transform: Scale {
                    origin.x: width / 2
                    origin.y: height / 2
                    xScale: (trackCard.hovered && trackContainer.trackData && trackListRoot.selectedTrackId !== trackContainer.trackData.id) ? 1.02 : 1.0
                    yScale: (trackCard.hovered && trackContainer.trackData && trackListRoot.selectedTrackId !== trackContainer.trackData.id) ? 1.02 : 1.0
                    
                    Behavior on xScale { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                    Behavior on yScale { NumberAnimation { duration: 150; easing.type: Easing.OutQuad } }
                }
                    
                    // Threat level indicator (left accent)
                    Rectangle {
                        width: 2
                        height: parent.height - 12
                        anchors.left: parent.left
                        anchors.leftMargin: 6
                        anchors.verticalCenter: parent.verticalCenter
                        radius: 1
                        color: {
                            if (!trackContainer.trackData) return "transparent"
                            if (trackContainer.trackData.range < 300) return Theme.accentThreat  // Red
                            if (trackContainer.trackData.range < 600) return Theme.accentWarning  // Orange
                            if (trackContainer.trackData.range < 1000) return Theme.accentYellow  // Yellow
                            return Qt.rgba(1, 1, 1, 0.3)  // Subtle white for > 1000m
                        }
                        
                        Behavior on color { ColorAnimation { duration: 150 } }
                    }
                    
                    // Subtle glow for selected
                    layer.enabled: trackContainer.trackData && trackListRoot.selectedTrackId === trackContainer.trackData.id
                    layer.effect: DropShadow {
                        horizontalOffset: 0
                        verticalOffset: 0
                        radius: 8
                        samples: 17
                        color: Qt.rgba(0, 0.9, 1, 0.2)  // Very subtle cyan glow
                        transparentBorder: true
                    }
                    
                    // Smooth color transition
                    Behavior on color { ColorAnimation { duration: 150; easing.type: Easing.OutQuad } }
                    
                    // Content - Minimalist layout
                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 8  // Match header spacing exactly
                        
                        // Track ID
                        Text {
                            text: trackContainer.trackData ? trackContainer.trackData.id : ""
                            font.family: Theme.fontFamilyMono
                            font.pixelSize: 13
                            font.weight: Font.Bold
                            color: Theme.textPrimary
                            Layout.preferredWidth: 50
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Type badge - minimal (matches tactical display colors)
                        Text {
                            text: trackContainer.trackData ? trackContainer.trackData.type : ""
                            font.family: Theme.fontFamily
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            color: {
                                if (!trackContainer.trackData) return Theme.textTertiary
                                if (trackContainer.trackData.type === "UAV") return "#EF4444"  // Clean modern red (Monochrome)
                                if (trackContainer.trackData.type === "BIRD") return "#475569"  // Darker muted slate
                                if (trackContainer.trackData.type === "UNKNOWN") return "#00E5FF"  // Cyan
                                return Theme.textSecondary
                            }
                            Layout.preferredWidth: 70
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Sensor icon - modern symbols
                        Text {
                            text: {
                                if (!trackContainer.trackData) return ""
                                if (trackContainer.trackData.source === "RADAR") return "◉"  // Radio waves
                                if (trackContainer.trackData.source === "RF") return "≋"     // Wave pattern
                                if (trackContainer.trackData.source === "FUSED") return "◈"  // Diamond (combined)
                                return "·"
                            }
                            font.family: Theme.fontFamily
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: {
                                if (!trackContainer.trackData) return Theme.textTertiary
                                if (trackContainer.trackData.source === "RADAR") return Theme.accentCyan
                                if (trackContainer.trackData.source === "RF") return Theme.accentYellow
                                if (trackContainer.trackData.source === "FUSED") return Theme.accentFocus
                                return Theme.textTertiary
                            }
                            Layout.preferredWidth: 60
                            horizontalAlignment: Text.AlignLeft
                        }
                        
                        // Range - prominent
                        Text {
                            text: trackContainer.trackData ? trackContainer.trackData.range.toFixed(0) + "m" : "-"
                            font.family: Theme.fontFamilyMono
                            font.pixelSize: 13
                            font.weight: Font.Medium
                            color: Theme.textPrimary
                            horizontalAlignment: Text.AlignLeft
                            Layout.preferredWidth: 70
                        }
                        
                        // Confidence indicator - minimal dot (monochrome palette)
                        Rectangle {
                            width: 6
                            height: 6
                            radius: 3
                            color: {
                                if (!trackContainer.trackData) return Theme.textTertiary
                                if (trackContainer.trackData.confidence > 0.8) return "#FFFFFF"  // White - high confidence
                                if (trackContainer.trackData.confidence > 0.5) return "#00E5FF"  // Cyan - medium confidence
                                return "#EF4444"  // Bright red - low confidence (warning)
                            }
                            Layout.fillWidth: true  // Match header layout
                            Layout.alignment: Qt.AlignVCenter
                            
                            Behavior on color { ColorAnimation { duration: 150 } }
                        }
                    }
                    
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: trackCard.hovered = true
                        onExited: trackCard.hovered = false
                        onClicked: {
                            if (trackContainer.trackData) {
                                console.log("[TrackList] Track clicked:", trackContainer.trackData.id)
                                trackListRoot.trackSelected(trackContainer.trackData.id)
                            }
                        }
                    }
            }  // End Rectangle (trackCard)
        }  // End Item (trackContainer / delegate)
    }  // End ListView
}
