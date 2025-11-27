// Theme.qml - Design tokens
pragma Singleton
import QtQuick

QtObject {
    // Colors
    readonly property color base0: "#0F1113"
    readonly property color base1: "#15181A"
    readonly property color base2: "#1B1F22"
    readonly property color accentCyan: "#38E6E0"
    readonly property color accentRed: "#E84855"
    readonly property color accentYellow: "#F2B46E"
    readonly property color textPrimary: "#EBEBEB"
    readonly property color textSecondary: "#999999"
    readonly property color borderSubtle: "#FFFFFF10"
    
    // Typography
    readonly property string fontFamily: "SF Pro Display"
    readonly property int fontSizeHeading: 12
    readonly property int fontSizeBody: 13
    readonly property int fontSizeSmall: 11
    readonly property int fontSizeMono: 12
    readonly property int fontWeightRegular: Font.Normal
    readonly property int fontWeightSemiBold: Font.DemiBold
    
    // Spacing
    readonly property int spacing: 12
    readonly property int cardPadding: 20
    readonly property int radiusMedium: 12
    readonly property int radiusLarge: 16
    
    // Animation
    readonly property int durationFast: 200
    readonly property int durationNormal: 400
    readonly property int durationSlow: 600
    readonly property int durationSweep: 3000
}
