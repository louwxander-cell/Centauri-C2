import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects

Rectangle {
    id: engagementPanel
    
    color: Theme.base1
    border.width: 1
    border.color: Qt.rgba(0, 0.9, 1, 0.3)  // Cyan border (matching Active Tracks)
    radius: Theme.radiusLarge
    
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
    
    property var selectedTrack: null
    property int selectedTrackId: -1  // Passed from parent (Main.qml)
    property bool isEngaged: false
    property int engagedTrackId: -1
    
    // Signal to request highest priority selection
    signal resetToHighestPriority()
    
    // Track details as simple properties for reliable binding
    property string trackType: "—"
    property string trackRange: "—"
    property string trackConfidence: "—"
    
    // Debug property to force UI updates
    property int updateCounter: 0
    
    // Component initialization
    Component.onCompleted: {
        console.log("[EngagementPanel] Initialized")
        updateSelectedTrack()
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.cardPadding
        spacing: Theme.spacingLarge
        
        // Header
        Text {
            text: "ENGAGEMENT CONTROL"
            font.family: Theme.fontFamilyDisplay
            font.pixelSize: Theme.fontSizeLarge
            font.weight: Theme.fontWeightSemiBold
            font.letterSpacing: 1.5
            color: Theme.textPrimary
            Layout.fillWidth: true
        }
        
        // Highest Priority Threat Display
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 160
            color: Theme.base2
            border.width: 0  // No borders
            radius: Theme.radiusMedium
            
            // Subtle accent glow for critical tracks
            layer.enabled: selectedTrackId >= 0 && selectedTrack && selectedTrack.range < 300
            layer.effect: DropShadow {
                horizontalOffset: 0
                verticalOffset: 0
                radius: Theme.glowBlur
                samples: 17
                color: Theme.accentThreat
                transparentBorder: true
            }
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacing
                spacing: Theme.spacing
                
                // Priority indicator (removed - cleaner look)
                
                // Track ID with subtle red accent
                Text {
                    text: selectedTrackId >= 0 ? 
                          `Track ${selectedTrackId}` : 
                          "No Active Threat"
                    font.family: Theme.fontFamilyDisplay
                    font.pixelSize: 24
                    font.weight: Theme.fontWeightBold
                    color: selectedTrackId >= 0 ? Theme.textPrimary : Theme.textSecondary
                    Layout.fillWidth: true
                }
                
                // Thin red accent line for threats
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 2
                    color: selectedTrackId >= 0 ? Theme.accentThreat : "transparent"
                    radius: 1
                    visible: selectedTrackId >= 0
                }
                
                // Track info - Clean minimal design
                GridLayout {
                    columns: 2
                    columnSpacing: Theme.spacing
                    rowSpacing: Theme.spacingSmall
                    Layout.fillWidth: true
                    
                    Text {
                        text: "Type"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textSecondary
                    }
                    Text {
                        text: trackType
                        font.family: Theme.fontFamilyMono
                        font.pixelSize: Theme.fontSizeBody
                        font.weight: Theme.fontWeightMedium
                        color: Theme.textPrimary
                    }
                    
                    Text {
                        text: "Range"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textSecondary
                    }
                    Text {
                        text: trackRange
                        font.family: Theme.fontFamilyMono
                        font.pixelSize: Theme.fontSizeBody
                        font.weight: Theme.fontWeightMedium
                        color: Theme.textPrimary
                    }
                    
                    Text {
                        text: "Confidence"
                        font.family: Theme.fontFamily
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.textSecondary
                    }
                    Text {
                        text: trackConfidence
                        font.family: Theme.fontFamilyMono
                        font.pixelSize: Theme.fontSizeBody
                        font.weight: Theme.fontWeightMedium
                        color: Theme.textPrimary
                    }
                }
            }
        }
        
        // Reset to Highest Priority - Always available
        Text {
            text: "↻ Reset to Highest Priority"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.accentFocus
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            
            MouseArea {
                anchors.fill: parent
                enabled: true  // Always enabled
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    console.log("[ENGAGE] Reset to highest priority requested")
                    engagementPanel.resetToHighestPriority()
                }
            }
        }
        
        // ENGAGE Button - Minimal, refined
        Button {
            id: engageButton
            Layout.fillWidth: true
            Layout.preferredHeight: 48  // Reduced height
            
            enabled: !isEngaged && selectedTrackId >= 0
            
            background: Rectangle {
                color: {
                    if (!parent.enabled) return Qt.rgba(1, 1, 1, 0.05)
                    if (parent.pressed) return Qt.darker(Theme.accentThreat, 1.1)
                    if (parent.hovered) return Qt.lighter(Theme.accentThreat, 1.1)
                    return Theme.accentThreat
                }
                radius: 4  // Smaller radius
                border.width: parent.enabled ? 0 : 1
                border.color: Qt.rgba(1, 1, 1, 0.1)
                
                Behavior on color { ColorAnimation { duration: 150 } }
            }
            
            contentItem: Text {
                text: selectedTrackId >= 0 ? 
                      `ENGAGE ${selectedTrackId}` : 
                      "—"
                font.family: Theme.fontFamily
                font.pixelSize: 14
                font.weight: Font.Medium
                font.letterSpacing: 0.5
                color: engageButton.enabled ? "#FFFFFF" : Theme.textTertiary
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            
            onClicked: {
                console.log("[EngagementPanel] ========== ENGAGE CLICKED ==========")
                console.log("[EngagementPanel] BEFORE - isEngaged:", isEngaged, "Track:", selectedTrackId)
                
                var result = bridge.engage_track(selectedTrackId, "OPERATOR_1")
                console.log("[EngagementPanel] Bridge result:", JSON.stringify(result))
                
                if (result && result.success) {
                    // Force state update
                    engagementPanel.isEngaged = true
                    engagementPanel.engagedTrackId = selectedTrackId
                    
                    console.log("[EngagementPanel] AFTER - isEngaged:", isEngaged, "engagedTrackId:", engagedTrackId)
                    console.log("[EngagementPanel] ✓ ENGAGED - UI state set")
                } else {
                    console.log("[EngagementPanel] ✗ FAILED:", result ? result.message : "No result")
                }
            }
        }
        
        // Subtle divider
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: Theme.borderSubtle
            visible: isEngaged
        }
        
        // Engagement status - Minimal, clean
        ColumnLayout {
            Layout.fillWidth: true
            spacing: Theme.spacingSmall
            visible: isEngaged
            
            // Status indicator
            RowLayout {
                spacing: Theme.spacingSmall
                Layout.fillWidth: true
                
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: Theme.accentSafe
                    
                    SequentialAnimation on opacity {
                        running: isEngaged
                        loops: Animation.Infinite
                        NumberAnimation { to: 0.4; duration: 800 }
                        NumberAnimation { to: 1.0; duration: 800 }
                    }
                }
                
                Text {
                    text: "Engagement Active"
                    font.family: Theme.fontFamily
                    font.pixelSize: Theme.fontSizeSmall
                    font.weight: Theme.fontWeightMedium
                    color: Theme.accentSafe
                }
            }
            
            Text {
                text: `Streaming Track ${engagedTrackId} to gunner stations`
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeTiny
                color: Theme.textSecondary
                Layout.fillWidth: true
            }
            
            // DISENGAGE button - matching ENGAGE button style
            Button {
                id: disengageButton
                Layout.fillWidth: true
                Layout.preferredHeight: 48  // Same as engage button
                
                background: Rectangle {
                    color: {
                        if (parent.pressed) return Qt.darker(Theme.accentThreat, 1.1)
                        if (parent.hovered) return Qt.lighter(Theme.accentThreat, 1.1)
                        return Theme.accentThreat
                    }
                    radius: 4  // Same as engage button
                    border.width: 0
                    
                    Behavior on color { ColorAnimation { duration: 150 } }
                }
                
                contentItem: Text {
                    text: `CANCEL ${engagedTrackId}`
                    font.family: Theme.fontFamily
                    font.pixelSize: 14
                    font.weight: Font.Medium
                    font.letterSpacing: 0.5
                    color: "#FFFFFF"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: {
                    console.log("[EngagementPanel] ========== DISENGAGE CLICKED ==========")
                    console.log("[EngagementPanel] BEFORE - isEngaged:", isEngaged, "engagedTrackId:", engagedTrackId)
                    
                    var result = bridge.disengage_track()
                    console.log("[EngagementPanel] Bridge result:", JSON.stringify(result))
                    
                    if (result && result.success) {
                        // Force state update
                        engagementPanel.isEngaged = false
                        engagementPanel.engagedTrackId = -1
                        
                        console.log("[EngagementPanel] AFTER - isEngaged:", isEngaged, "engagedTrackId:", engagedTrackId)
                        console.log("[EngagementPanel] ✓ CANCELLED - UI state reset")
                    } else {
                        console.log("[EngagementPanel] ✗ FAILED:", result ? result.message : "null")
                    }
                }
            }
        }
        
        // Awaiting decision message when not engaged
        Text {
            text: "Awaiting operator decision"
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeTiny
            color: Theme.textTertiary
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            visible: !isEngaged
        }
    }
    
    // Function to update selected track from model
    function updateSelectedTrack() {
        console.log("[EngagementPanel] updateSelectedTrack called, selectedTrackId:", selectedTrackId)
        
        if (selectedTrackId >= 0 && typeof tracksModel !== 'undefined' && tracksModel) {
            console.log("[EngagementPanel] tracksModel count:", tracksModel.rowCount())
            var foundTrack = null
            
            for (var i = 0; i < tracksModel.rowCount(); i++) {
                var track = tracksModel.data(tracksModel.index(i, 0), 0x0101)  // Qt.UserRole + 1
                if (track) {
                    if (track.id === selectedTrackId) {
                        foundTrack = track
                        console.log("[EngagementPanel] ✓ Found track:", track.id, "Type:", track.type, "Range:", track.range.toFixed(1) + "m", "Confidence:", track.confidence)
                        
                        // Copy values to simple properties for reliable binding
                        trackType = track.type || "UNKNOWN"
                        trackRange = Math.round(track.range) + "m"
                        trackConfidence = (track.confidence * 100).toFixed(0) + "%"
                        
                        break
                    }
                } else {
                    console.log("[EngagementPanel] WARNING: track at index", i, "is null")
                }
            }
            
            // Force property update by setting to null first, then to new value
            selectedTrack = null
            selectedTrack = foundTrack
            
            if (!foundTrack) {
                console.log("[EngagementPanel] ✗ Track", selectedTrackId, "not found in", tracksModel.rowCount(), "tracks")
                trackType = "—"
                trackRange = "—"
                trackConfidence = "—"
            }
        } else {
            selectedTrack = null
            trackType = "—"
            trackRange = "—"
            trackConfidence = "—"
            console.log("[EngagementPanel] Cannot update: selectedTrackId =", selectedTrackId, "tracksModel =", typeof tracksModel)
        }
    }
    
    // Update when selection changes
    onSelectedTrackIdChanged: {
        updateSelectedTrack()
    }
    
    // Update when model changes
    Connections {
        target: tracksModel
        function onDataChanged() {
            updateSelectedTrack()
        }
    }
    
    // Monitor selected track for data changes
    Connections {
        target: selectedTrack
        function onDataChanged() {
            updateCounter++  // Force UI refresh
        }
    }
    
    // Update engagement status
    Timer {
        interval: 100
        running: true
        repeat: true
        onTriggered: {
            if (bridge) {
                var currentlyEngaged = bridge.is_track_engaged()
                if (currentlyEngaged !== isEngaged) {
                    isEngaged = currentlyEngaged
                    if (isEngaged) {
                        engagedTrackId = bridge.get_engaged_track_id()
                    }
                }
            }
        }
    }
}
