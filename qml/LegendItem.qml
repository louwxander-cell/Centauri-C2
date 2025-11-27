// LegendItem.qml
// Legend entry for track types
import QtQuick
import QtQuick.Layouts

Row {
    spacing: 8
    
    property string label: ""
    property color color: Theme.accentCyan
    property string symbol: "▲"
    
    Text {
        text: symbol
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSmall
        color: parent.color
        verticalAlignment: Text.AlignVCenter
    }
    
    Text {
        text: label
        font.family: Theme.fontFamily
        font.pixelSize: Theme.fontSizeSmall
        color: Theme.textPrimary
        verticalAlignment: Text.AlignVCenter
    }
}
