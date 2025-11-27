// ZoomButton.qml
// Circular zoom control button
import QtQuick
import QtQuick.Effects

Rectangle {
    id: root
    width: 40
    height: 40
    radius: 20
    color: Qt.rgba(1, 1, 1, 0.02)
    border.width: 1
    border.color: mouseArea.containsMouse ? Theme.accentCyan : Theme.borderCard
    
    property string text: "+"
    signal clicked()
    
    Behavior on border.color { ColorAnimation { duration: Theme.durationFast } }
    Behavior on scale { NumberAnimation { duration: Theme.durationFast; easing.type: Easing.OutBack } }
    
    Text {
        anchors.centerIn: parent
        text: root.text
        font.family: Theme.fontFamily
        font.pixelSize: 18
        font.weight: Theme.fontWeightBold
        color: Theme.textPrimary
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
        onPressed: root.scale = 0.9
        onReleased: root.scale = 1.0
        onCanceled: root.scale = 1.0
    }
    
    // Glow on hover
    layer.enabled: mouseArea.containsMouse
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowColor: Theme.accentCyan
        shadowOpacity: 0.3
        shadowBlur: 0.6
    }
}
