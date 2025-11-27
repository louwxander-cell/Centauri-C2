// Theme.qml - Design tokens (Anduril/Tesla-inspired)
pragma Singleton
import QtQuick

QtObject {
    // Background Colors (Deep Space Black)
    readonly property color base0: "#0A0E12"  // Deep background
    readonly property color base1: "#151B23"  // Elevated panels
    readonly property color base2: "#1E2631"  // Cards, containers
    readonly property color base3: "#2D3748"  // Hover states
    
    // Accent Colors (Minimal, Purpose-Driven)
    readonly property color accentThreat: "#FF3B3B"    // Critical threats only
    readonly property color accentWarning: "#FF8C42"   // Mid-level alerts
    readonly property color accentSafe: "#00D9A3"      // Confirmed safe/friendly
    readonly property color accentInfo: "#4A9EFF"      // Information
    readonly property color accentFocus: "#00E5FF"     // Selected/focused elements
    readonly property color accentCyan: "#00E5FF"      // Legacy compatibility
    readonly property color accentRed: "#FF3B3B"       // Legacy compatibility
    readonly property color accentYellow: "#FF8C42"    // Legacy compatibility
    
    // Text Colors (High Contrast)
    readonly property color textPrimary: "#FFFFFF"     // 100% white - critical info
    readonly property color textSecondary: "#9BA3AF"   // 60% gray - labels
    readonly property color textTertiary: "#5B6471"    // 35% gray - subtle text
    readonly property color textDisabled: "#3C4350"    // Disabled state
    
    // Border Colors (Minimal Tesla-Style)
    readonly property color borderStrong: "#2D3748"    // Major separations only
    readonly property color borderSubtle: "#1A202C"    // Minimal presence
    readonly property color borderNone: "#00000000"    // Transparent
    
    // Glow/Shadow Effects
    readonly property color glowFocus: "#00E5FF40"     // 25% opacity cyan glow
    readonly property color shadowLight: "#00000040"   // 25% opacity shadow
    readonly property color shadowMedium: "#00000060"  // 40% opacity shadow
    readonly property color shadowStrong: "#00000080"  // 50% opacity shadow
    
    // Typography (Inter + JetBrains Mono)
    readonly property string fontFamily: "Inter"           // Primary UI font
    readonly property string fontFamilyDisplay: "Inter"    // Headers
    readonly property string fontFamilyMono: "JetBrains Mono"  // Technical data
    
    // Font Sizes (Slightly larger for readability)
    readonly property int fontSizeHeading: 14          // Increased from 12
    readonly property int fontSizeLarge: 16            // New large size
    readonly property int fontSizeBody: 13             // Same
    readonly property int fontSizeSmall: 11            // Same
    readonly property int fontSizeTiny: 10             // New tiny size
    readonly property int fontSizeMono: 12             // Same
    
    // Font Weights
    readonly property int fontWeightLight: Font.Light
    readonly property int fontWeightRegular: Font.Normal
    readonly property int fontWeightMedium: Font.Medium
    readonly property int fontWeightSemiBold: Font.DemiBold
    readonly property int fontWeightBold: Font.Bold
    
    // Spacing (Increased for breathing room)
    readonly property int spacingTiny: 4
    readonly property int spacingSmall: 8
    readonly property int spacing: 16                  // Increased from 12
    readonly property int spacingMedium: 20
    readonly property int spacingLarge: 24             // New
    readonly property int spacingXLarge: 32            // New
    readonly property int cardPadding: 24              // Increased from 20
    
    // Border Radius (Modern, not too round)
    readonly property int radiusSmall: 4
    readonly property int radiusMedium: 6              // Reduced from 12
    readonly property int radiusLarge: 8               // Reduced from 16
    readonly property int radiusXLarge: 12             // New
    
    // Animation (Smooth Tesla-style)
    readonly property int durationFast: 200            // Quick interactions
    readonly property int durationNormal: 300          // Standard transitions
    readonly property int durationSlow: 500            // Smooth animations
    readonly property int durationSweep: 3000          // Radar sweep
    readonly property string easingOut: "OutQuad"      // Smooth deceleration
    readonly property string easingInOut: "InOutQuad"  // Smooth both ways
    
    // Component Sizes
    readonly property int buttonHeight: 44             // Touch-friendly
    readonly property int buttonHeightLarge: 56        // Primary actions
    readonly property int inputHeight: 40              // Text inputs
    readonly property int trackCardHeight: 56          // Track list cards
    readonly property int headerHeight: 80             // Top bar
    
    // Shadows (Subtle elevation)
    readonly property int shadowBlur: 8                // Soft shadows
    readonly property int shadowOffset: 2              // Slight offset
    readonly property int glowBlur: 12                 // Focus glow
}
