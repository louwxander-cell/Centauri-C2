// DetailValue.qml
// Value for detail fields (monospace)
import QtQuick

Text {
    font.family: Theme.fontFamilyMono
    font.pixelSize: Theme.fontSizeMono
    font.weight: Theme.fontWeightSemiBold
    color: Theme.textPrimary
    verticalAlignment: Text.AlignVCenter
    
    // Smooth value changes
    Behavior on text {
        SequentialAnimation {
            NumberAnimation { target: parent; property: "opacity"; to: 0.5; duration: 80 }
            PropertyAction { target: parent; property: "text" }
            NumberAnimation { target: parent; property: "opacity"; to: 1.0; duration: 80 }
        }
    }
}
