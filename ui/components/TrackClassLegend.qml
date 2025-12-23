// TrackClassLegend.qml - Track classification legend
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".."

Rectangle {
    id: root
    
    width: 180
    height: collapsed ? 32 : 240
    color: Qt.rgba(Theme.base2.r, Theme.base2.g, Theme.base2.b, 0.95)
    border.color: Theme.borderSubtle
    border.width: 1
    radius: 6
    
    property bool collapsed: true  // Default to collapsed
    property var classColors: ({
        "UAV": "#DC143C",              // Crimson red
        "UAV Multi-Rotor": "#8B0000",  // Dark red
        "UAV Fixed-Wing": "#FF6600",   // Bright orange
        "Walker": "#4169E1",           // Royal blue
        "Plane": "#FFD700",            // Gold
        "Bird": "#00CED1",             // Dark turquoise
        "Vehicle": "#9370DB",          // Medium purple
        "Clutter": "#808080",          // Gray
        "Undeclared": "#D3D3D3"        // Light gray
    })
    
    Behavior on height {
        NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 8
        anchors.topMargin: 6
        anchors.bottomMargin: 6
        spacing: 5
        
        // Header with collapse button
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            
            Text {
                text: "TRACK CLASS LEGEND"
                font.family: Theme.fontFamily
                font.pixelSize: 10
                font.weight: Font.Bold
                color: Theme.textSecondary
                Layout.fillWidth: true
            }
            
            // Collapse/Expand button
            Rectangle {
                width: 18
                height: 18
                radius: 3
                color: collapseMouseArea.containsMouse ? Theme.base3 : "transparent"
                border.color: Theme.borderSubtle
                border.width: 1
                
                Text {
                    anchors.centerIn: parent
                    text: root.collapsed ? "▼" : "▲"
                    font.pixelSize: 8
                    color: Theme.textSecondary
                }
                
                MouseArea {
                    id: collapseMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.collapsed = !root.collapsed
                }
            }
        }
        
        // Separator
        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: Theme.borderSubtle
            visible: !root.collapsed
            Layout.topMargin: 0
            Layout.bottomMargin: 0
        }
        
        // Legend items
        ColumnLayout {
            Layout.fillWidth: true
            Layout.topMargin: 2
            Layout.bottomMargin: 2
            spacing: 6
            visible: !root.collapsed
            
            // UAV
            LegendItem {
                color: root.classColors["UAV"]
                label: "UAV"
            }
            
            // UAV Multi-Rotor
            LegendItem {
                color: root.classColors["UAV Multi-Rotor"]
                label: "UAV Multi-Rotor"
            }
            
            // UAV Fixed-Wing
            LegendItem {
                color: root.classColors["UAV Fixed-Wing"]
                label: "UAV Fixed-Wing"
            }
            
            // Walker
            LegendItem {
                color: root.classColors["Walker"]
                label: "Walker"
            }
            
            // Plane
            LegendItem {
                color: root.classColors["Plane"]
                label: "Plane"
            }
            
            // Bird
            LegendItem {
                color: root.classColors["Bird"]
                label: "Bird"
            }
            
            // Vehicle
            LegendItem {
                color: root.classColors["Vehicle"]
                label: "Vehicle"
            }
            
            // Clutter
            LegendItem {
                color: root.classColors["Clutter"]
                label: "Clutter"
            }
            
            // Undeclared
            LegendItem {
                color: root.classColors["Undeclared"]
                label: "Undeclared"
                hasBorder: true
            }
        }
    }
    
    // Legend item component
    component LegendItem: RowLayout {
        property color color: "#FFFFFF"
        property string label: ""
        property bool hasBorder: false
        
        Layout.fillWidth: true
        spacing: 8
        
        Rectangle {
            width: 12
            height: 12
            radius: 2
            color: parent.color
            border.color: parent.hasBorder ? Theme.textSecondary : "transparent"
            border.width: parent.hasBorder ? 1 : 0
        }
        
        Text {
            text: parent.label
            font.family: Theme.fontFamily
            font.pixelSize: 9
            color: Theme.textPrimary
            Layout.fillWidth: true
        }
    }
}
