// Theme.qml
// TriAD C2 Design System - Colors, Typography, Effects
pragma Singleton
import QtQuick

QtObject {
    // ===== COLOR PALETTE =====
    // Backgrounds - Monochromatic depth
    readonly property color base0: "#0F1113"  // Deepest background
    readonly property color base1: "#15181A"  // Card surface
    readonly property color base2: "#1B1F22"  // Elevated surface
    
    // Accent Colors - Desaturated for dark backgrounds
    readonly property color accentCyan: "#38E6E0"
    readonly property color accentCyanDim: "#2AB8B3"
    readonly property color accentCyanGlow: "#4D38E6E0"  // 30% opacity
    
    readonly property color accentRed: "#FF5A5F"
    readonly property color accentRedHover: "#FF6B6F"
    readonly property color accentRedPressed: "#E84855"
    readonly property color accentRedGlow: "#40FF5A5F"  // 25% opacity
    
    readonly property color accentAmber: "#F2B46E"
    readonly property color accentGreen: "#2CE08A"
    
    // Status Colors
    readonly property color statusCritical: "#FF3B3B"
    readonly property color statusHigh: "#F48C06"
    readonly property color statusMed: "#F2B46E"
    readonly property color statusFriendly: "#2CE08A"
    
    // Text Colors - Opacity-based hierarchy
    readonly property color textPrimary: "#EAEBEB"  // rgba(255,255,255,0.92)
    readonly property color textSecondary: "#99999999"  // rgba(255,255,255,0.60)
    readonly property color textTertiary: "#61FFFFFF"  // rgba(255,255,255,0.38)
    
    // Borders & Separators
    readonly property color borderSubtle: "#14FFFFFF"  // rgba(255,255,255,0.08)
    readonly property color borderCard: "#0FFFFFFF"  // rgba(255,255,255,0.06)
    readonly property color borderFocus: accentCyan
    
    // ===== TYPOGRAPHY =====
    readonly property string fontFamily: "Inter"
    readonly property string fontFamilyMono: "Roboto Mono"
    
    readonly property int fontSizeTitle: 18
    readonly property int fontSizeHeading: 14
    readonly property int fontSizeBody: 12
    readonly property int fontSizeMono: 12
    readonly property int fontSizeSmall: 10
    readonly property int fontSizeTiny: 9
    
    readonly property int fontWeightLight: Font.Light
    readonly property int fontWeightNormal: Font.Normal
    readonly property int fontWeightMedium: Font.Medium
    readonly property int fontWeightSemiBold: Font.DemiBold
    readonly property int fontWeightBold: Font.Bold
    
    // ===== SPACING & SIZING =====
    readonly property int baseline: 12  // Base grid unit
    readonly property int windowPadding: 32
    readonly property int panelGutter: 24
    readonly property int cardPadding: 20
    readonly property int itemSpacing: 16
    readonly property int tightSpacing: 8
    
    // Layout dimensions
    readonly property int leftPanelWidth: 460
    readonly property int rightPanelWidth: 360
    readonly property int headerHeight: 80
    readonly property int footerHeight: 44
    readonly property int tableRowHeight: 44
    
    // ===== BORDER RADIUS =====
    readonly property int radiusSmall: 6
    readonly property int radiusMedium: 12
    readonly property int radiusLarge: 16
    readonly property int radiusPill: 999
    
    // ===== ANIMATION DURATIONS =====
    readonly property int durationFast: 120
    readonly property int durationMedium: 180
    readonly property int durationSlow: 300
    readonly property int durationPulse: 1200
    readonly property int durationSweep: 3000
    
    // ===== EASING CURVES =====
    readonly property var easingStandard: Easing.OutCubic
    readonly property var easingEnter: Easing.OutBack
    readonly property var easingExit: Easing.InCubic
    
    // ===== EFFECTS =====
    function createDropShadow() {
        return {
            "radius": 10,
            "samples": 20,
            "color": "#AA000000",
            "horizontalOffset": 0,
            "verticalOffset": 4
        }
    }
    
    function createGlow(color, radius) {
        return {
            "radius": radius || 12,
            "samples": 24,
            "color": color,
            "spread": 0.3
        }
    }
    
    // ===== HELPER FUNCTIONS =====
    function getStatusColor(status) {
        switch(status) {
            case "CRITICAL": return statusCritical
            case "HIGH": return statusHigh
            case "MED": return statusMed
            case "FRIENDLY": return statusFriendly
            default: return accentCyan
        }
    }
    
    function getThreatGlow(status) {
        switch(status) {
            case "CRITICAL": return 16
            case "HIGH": return 12
            case "MED": return 8
            default: return 6
        }
    }
}
