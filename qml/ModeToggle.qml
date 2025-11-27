// ModeToggle.qml
// System mode toggle with icon indicator
import QtQuick
import QtQuick.Layouts

Row {
    spacing: 12
    
    property string text: ""
    property bool checked: false
    
    // Icon indicator (filled when checked)
    Rectangle {
        width: 12
        height: 12
        radius: 6
        anchors.verticalCenter: parent.verticalCenter
        color: parent.checked ? Theme.accentCyan : Theme.textTertiary
        border.width: parent.checked ? 0 : 1
        border.color: Theme.borderSubtle
        
        Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
        
        // Inner glow when checked
        Rectangle {
            anchors.centerIn: parent
            width: 6
            height: 6
            radius: 3
            color: Theme.accentCyan
            visible: parent.parent.checked
            opacity: 0.5
        }
    }
    
    // Label text
    Text {
        anchors.verticalCenter: parent.verticalCenter
        text: parent.text
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeBody
        color: parent.checked ? Theme.textPrimary : Theme.textSecondary
        
        Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
    }
}
