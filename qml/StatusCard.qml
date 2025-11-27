// StatusCard.qml
// Reusable status information card
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    implicitHeight: contentColumn.height + Theme.cardPadding * 2
    color: cardColor
    radius: Theme.radiusMedium
    border.width: 1
    border.color: Theme.borderCard
    
    property string title: ""
    property color cardColor: Theme.base1
    default property alias content: contentArea.children
    
    Column {
        id: contentColumn
        anchors.fill: parent
        anchors.margins: Theme.cardPadding
        spacing: Theme.itemSpacing
        
        // Title
        Text {
            text: root.title
            font.family: Theme.fontFamily
            font.pixelSize: Theme.fontSizeBody
            font.weight: Theme.fontWeightSemiBold
            font.capitalization: Font.AllUppercase
            font.letterSpacing: 0.8
            color: Theme.textSecondary
        }
        
        // Content area
        Item {
            id: contentArea
            width: parent.width
            implicitHeight: childrenRect.height
        }
    }
    
    // Subtle hover effect
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: root.border.color = Qt.rgba(1, 1, 1, 0.15)
        onExited: root.border.color = Theme.borderCard
    }
    
    Behavior on border.color { ColorAnimation { duration: Theme.durationFast } }
}
