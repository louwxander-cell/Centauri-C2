// CommandChain.qml
// Command execution chain status footer
import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    color: Theme.base1
    radius: Theme.radiusMedium
    
    property int currentStep: 0  // 0=RF DETECT, 1=RADAR SLEW, 2=RADAR TRACK, 3=OPTICS SLEW, 4=OPTICAL LOCK
    property var chainSteps: [
        "RF DETECT",
        "RADAR SLEW",
        "RADAR TRACK",
        "OPTICS SLEW",
        "OPTICAL LOCK"
    ]
    
    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.tightSpacing
        spacing: Theme.tightSpacing
        
        // Command chain steps
        Repeater {
            model: root.chainSteps.length
            
            Row {
                Layout.fillWidth: true
                spacing: 4
                
                // Step capsule
                Rectangle {
                    width: parent.width - (index < root.chainSteps.length - 1 ? 16 : 0)
                    height: 32
                    radius: 10
                    color: {
                        if (index < root.currentStep) return Qt.rgba(1, 1, 1, 0.03)  // Completed
                        if (index === root.currentStep) return Qt.rgba(Theme.accentCyan.r, Theme.accentCyan.g, Theme.accentCyan.b, 0.10)  // Active
                        return "transparent"  // Future
                    }
                    border.width: 1
                    border.color: {
                        if (index === root.currentStep) return Theme.accentCyan
                        return Theme.borderSubtle
                    }
                    
                    Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
                    Behavior on border.color { ColorAnimation { duration: Theme.durationMedium } }
                    
                    // Step text
                    Text {
                        anchors.centerIn: parent
                        text: root.chainSteps[index]
                        font.family: Theme.fontFamilyMono
                        font.pixelSize: Theme.fontSizeTiny
                        font.weight: index === root.currentStep ? Theme.fontWeightSemiBold : Theme.fontWeightNormal
                        color: {
                            if (index < root.currentStep) return Theme.textTertiary
                            if (index === root.currentStep) return Theme.accentCyan
                            return Theme.textSecondary
                        }
                        
                        Behavior on color { ColorAnimation { duration: Theme.durationMedium } }
                    }
                    
                    // Active glow
                    layer.enabled: index === root.currentStep
                    layer.effect: MultiEffect {
                        shadowEnabled: true
                        shadowColor: Theme.accentCyan
                        shadowOpacity: 0.2
                        shadowBlur: 0.5
                    }
                }
                
                // Chevron arrow (except after last step)
                Text {
                    visible: index < root.chainSteps.length - 1
                    anchors.verticalCenter: parent.verticalCenter
                    text: "›"
                    font.family: Theme.fontFamily
                    font.pixelSize: 16
                    color: Theme.borderSubtle
                }
            }
        }
        
        // Spacer
        Item { Layout.fillWidth: true }
        
        // UTC Time
        Text {
            text: Qt.formatDateTime(new Date(), "hh:mm:ss UTC")
            font.family: Theme.fontFamilyMono
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.textSecondary
            verticalAlignment: Text.AlignVCenter
            
            Timer {
                interval: 1000
                running: true
                repeat: true
                onTriggered: parent.text = Qt.formatDateTime(new Date(), "hh:mm:ss UTC")
            }
        }
    }
}
