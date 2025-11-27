// EngageButton.qml
// Engage button with long-press safety and confirmation dialog
import QtQuick
import QtQuick.Controls
import QtQuick.Effects

Rectangle {
    id: root
    implicitHeight: 60
    radius: Theme.radiusPill
    color: enabled ? Theme.accentRed : Theme.base2
    border.width: 2
    border.color: {
        if (!enabled) return Theme.borderCard
        if (mouseArea.pressed) return Theme.accentRedPressed
        if (mouseArea.containsMouse) return Theme.accentRedHover
        if (isArming) return Theme.accentCyan
        return "transparent"
    }
    
    enabled: trackId >= 0
    
    property int trackId: -1
    property bool isArming: false
    property real armProgress: 0
    
    signal engageClicked(int trackId)
    
    Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
    Behavior on border.color { ColorAnimation { duration: Theme.durationFast } }
    Behavior on scale { NumberAnimation { duration: Theme.durationFast; easing.type: Easing.OutBack } }
    
    // Button text
    Text {
        anchors.centerIn: parent
        text: root.enabled ? ("ENGAGE ID:" + root.trackId) : "ENGAGE TARGET"
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeHeading
        font.weight: Theme.fontWeightBold
        color: root.enabled ? Theme.textPrimary : Theme.textTertiary
        
        Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
    }
    
    // Arming progress indicator
    Rectangle {
        visible: root.isArming
        anchors.fill: parent
        radius: parent.radius
        color: "transparent"
        border.width: 3
        border.color: Theme.accentCyan
        opacity: root.armProgress
        
        Behavior on opacity { NumberAnimation { duration: 100 } }
    }
    
    // Glow effect when armed
    layer.enabled: root.isArming
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowColor: Theme.accentCyan
        shadowOpacity: 0.5 * root.armProgress
        shadowBlur: 1.0
    }
    
    // Long-press timer
    Timer {
        id: longPressTimer
        interval: 900
        repeat: false
        onTriggered: {
            root.isArming = true
            armAnimation.start()
        }
    }
    
    // Arm animation
    SequentialAnimation {
        id: armAnimation
        NumberAnimation {
            target: root
            property: "armProgress"
            to: 1.0
            duration: 2000
            easing.type: Easing.Linear
        }
        ScriptAction {
            script: {
                confirmDialog.open()
                root.isArming = false
                root.armProgress = 0
            }
        }
    }
    
    // Mouse interaction
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ForbiddenCursor
        
        onPressed: {
            root.scale = 0.97
            if (root.enabled) {
                longPressTimer.start()
            }
        }
        
        onReleased: {
            root.scale = 1.0
            if (longPressTimer.running) {
                // Short press - open confirmation immediately
                longPressTimer.stop()
                if (root.enabled) {
                    confirmDialog.open()
                }
            }
            // Stop arming if released during arm sequence
            if (root.isArming) {
                armAnimation.stop()
                root.isArming = false
                root.armProgress = 0
            }
        }
        
        onCanceled: {
            root.scale = 1.0
            longPressTimer.stop()
            if (root.isArming) {
                armAnimation.stop()
                root.isArming = false
                root.armProgress = 0
            }
        }
    }
    
    // Confirmation Dialog
    Dialog {
        id: confirmDialog
        anchors.centerIn: Overlay.overlay
        width: 400
        modal: true
        title: "Confirm Engagement"
        
        background: Rectangle {
            color: Theme.base1
            radius: Theme.radiusMedium
            border.width: 1
            border.color: Theme.accentRed
            
            layer.enabled: true
            layer.effect: MultiEffect {
                shadowEnabled: true
                shadowColor: Theme.accentRed
                shadowOpacity: 0.3
                shadowBlur: 1.0
            }
        }
        
        contentItem: Column {
            spacing: Theme.itemSpacing
            
            Text {
                width: parent.width
                text: "<b>Confirm ENGAGE Track ID:" + root.trackId + "</b>"
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeHeading
                color: Theme.textPrimary
                wrapMode: Text.WordWrap
                textFormat: Text.RichText
            }
            
            Text {
                width: parent.width
                text: "This action will command the Remote Weapon Station to fire.\n\nAre you sure you want to proceed?"
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                color: Theme.textSecondary
                wrapMode: Text.WordWrap
                lineHeight: 1.4
            }
        }
        
        footer: Row {
            spacing: Theme.itemSpacing
            padding: Theme.itemSpacing
            
            Button {
                text: "✗ Cancel"
                implicitWidth: 150
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                
                background: Rectangle {
                    color: parent.pressed ? Theme.base2 : Theme.base1
                    border.width: 1
                    border.color: Theme.borderCard
                    radius: Theme.radiusMedium
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: confirmDialog.close()
            }
            
            Button {
                text: "✓ CONFIRM ENGAGE"
                implicitWidth: 200
                font.family: Theme.fontFamily
                font.pixelSize: Theme.fontSizeBody
                font.weight: Theme.fontWeightBold
                
                background: Rectangle {
                    color: parent.pressed ? Theme.accentRedPressed : 
                           (parent.hovered ? Theme.accentRedHover : Theme.accentRed)
                    radius: Theme.radiusMedium
                    
                    Behavior on color { ColorAnimation { duration: Theme.durationFast } }
                }
                
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: Theme.textPrimary
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: {
                    confirmDialog.close()
                    root.engageClicked(root.trackId)
                }
            }
        }
    }
}
