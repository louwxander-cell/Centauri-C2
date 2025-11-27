// TableHeaderCell.qml
// Table header cell component
import QtQuick

Rectangle {
    id: root
    height: 36
    color: "transparent"
    
    property string text: ""
    
    // Bottom border
    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 1
        color: Theme.borderSubtle
    }
    
    Text {
        anchors.centerIn: parent
        anchors.horizontalCenterOffset: -parent.width * 0.1
        text: root.text
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSmall
        font.weight: Theme.fontWeightSemiBold
        font.capitalization: Font.AllUppercase
        font.letterSpacing: 1.0
        color: Theme.textSecondary
        horizontalAlignment: Text.AlignLeft
    }
}
