"""
Modern Tactical UI Styling for TriAD C2 System
Ultra-modern dark theme with tactical colors
Fonts: Nex Sphere (caps), Bahnschrift (normal text)
"""

# Color palette - Tactical dark theme
COLORS = {
    # Backgrounds
    'bg_primary': '#0a0e14',      # Very dark blue-black
    'bg_secondary': '#151a21',    # Dark charcoal
    'bg_tertiary': '#1f2937',     # Medium dark gray
    'bg_panel': '#111827',        # Panel background
    'bg_hover': '#1f2937',        # Hover state
    
    # Text
    'text_primary': '#ffffff',    # White
    'text_secondary': '#9ca3af',  # Medium gray
    'text_tertiary': '#6b7280',   # Dim gray
    'text_disabled': '#4b5563',   # Very dim gray
    
    # Accents
    'accent_cyan': '#ffffff',     # White
    'accent_green': '#10b981',    # Green (success)
    'accent_yellow': '#fbbf24',   # Yellow (warning)
    'accent_red': '#ef4444',      # Red (danger/critical)
    'accent_orange': '#f97316',   # Alert orange
    'accent_purple': '#a855f7',   # Fused tracks
    
    # Track colors
    'track_uav': '#ef4444',       # Red - hostile (UAV)
    'track_bird': '#60a5fa',      # Light blue - neutral
    'track_unknown': '#fbbf24',   # Yellow - unknown
    'track_fused': '#a855f7',     # Purple - fused
    
    # Sensor colors
    'sensor_radar': '#ffffff',    # White (was cyan)
    'sensor_rf': '#10b981',       # Green
    'sensor_gps': '#fbbf24',      # Yellow
    'sensor_rws': '#f97316',      # Orange
    
    # Status colors
    'status_online': '#10b981',   # Green
    'status_offline': '#6b7280',  # Gray
    'status_warning': '#fbbf24',  # Yellow
    'status_error': '#ef4444',    # Red
    
    # Text colors
    'text_primary': '#f9fafb',    # Almost white
    'text_secondary': '#9ca3af',  # Light gray
    'text_tertiary': '#6b7280',   # Medium gray
    'text_disabled': '#4b5563',   # Dark gray
    
    # Border colors
    'border_primary': '#374151',  # Medium border
    'border_accent': '#ffffff',   # White border (was cyan)
    'border_dim': '#1f2937',      # Dim border
    
    # Glow effects
    'glow_cyan': 'rgba(0, 217, 255, 0.3)',
    'glow_green': 'rgba(16, 185, 129, 0.3)',
    'glow_red': 'rgba(239, 68, 68, 0.3)',
}

# Font settings
# Note: Using bold, impactful fonts for tactical appearance
FONTS = {
    'caps': 'Arial Black, Impact, sans-serif',  # For headings, labels (ALL CAPS) - Bold, wide font
    'normal': 'Arial, Helvetica, sans-serif',  # For body text, values
    'mono': 'Courier New, Monaco, monospace',   # For coordinates, numbers
}

# Font sizes
FONT_SIZES = {
    'title': 24,
    'heading': 18,
    'subheading': 14,
    'body': 12,
    'small': 10,
    'tiny': 8,
}


def get_main_stylesheet():
    """Get the main application stylesheet"""
    return f"""
    /* ===== GLOBAL STYLES ===== */
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_primary']};
        font-family: '{FONTS['normal']}';
        font-size: {FONT_SIZES['body']}pt;
    }}
    
    /* ===== PANELS ===== */
    QWidget#panel {{
        background-color: {COLORS['bg_panel']};
        border: 1px solid {COLORS['border_primary']};
        border-radius: 8px;
    }}
    
    QWidget#panel_accent {{
        background-color: {COLORS['bg_panel']};
        border: 2px solid {COLORS['border_accent']};
        border-radius: 8px;
    }}
    
    /* ===== LABELS ===== */
    QLabel {{
        color: {COLORS['text_primary']};
        background-color: transparent;
        font-family: '{FONTS['normal']}';
    }}
    
    QLabel#heading {{
        font-family: '{FONTS['caps']}';
        font-size: {FONT_SIZES['heading']}pt;
        font-weight: bold;
        color: {COLORS['accent_cyan']};
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    
    QLabel#subheading {{
        font-family: '{FONTS['caps']}';
        font-size: {FONT_SIZES['subheading']}pt;
        font-weight: bold;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    QLabel#value {{
        font-family: '{FONTS['mono']}';
        font-size: {FONT_SIZES['body']}pt;
        color: {COLORS['text_primary']};
        font-weight: bold;
    }}
    
    QLabel#status_online {{
        color: {COLORS['status_online']};
        font-weight: bold;
    }}
    
    QLabel#status_offline {{
        color: {COLORS['status_offline']};
    }}
    
    QLabel#status_warning {{
        color: {COLORS['status_warning']};
        font-weight: bold;
    }}
    
    /* ===== BUTTONS ===== */
    QPushButton {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_primary']};
        border: 2px solid {COLORS['border_primary']};
        border-radius: 6px;
        padding: 10px 20px;
        font-family: '{FONTS['caps']}';
        font-size: {FONT_SIZES['body']}pt;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['bg_hover']};
        border-color: {COLORS['accent_cyan']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['bg_secondary']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_disabled']};
        border-color: {COLORS['border_dim']};
    }}
    
    QPushButton#engage {{
        background-color: {COLORS['accent_red']};
        border-color: {COLORS['accent_red']};
        color: white;
        font-size: {FONT_SIZES['heading']}pt;
        padding: 15px 30px;
    }}
    
    QPushButton#engage:hover {{
        background-color: #dc2626;
        box-shadow: 0 0 20px {COLORS['glow_red']};
    }}
    
    QPushButton#engage:disabled {{
        background-color: {COLORS['bg_tertiary']};
        border-color: {COLORS['border_primary']};
        color: {COLORS['text_disabled']};
    }}
    
    QPushButton#button_secondary {{
        background-color: {COLORS['bg_secondary']};
        border: 2px solid {COLORS['accent_cyan']};
        color: {COLORS['accent_cyan']};
        font-family: '{FONTS['caps']}';
        font-size: {FONT_SIZES['body']}px;
        font-weight: bold;
        padding: 10px;
        border-radius: 4px;
    }}
    
    QPushButton#button_secondary:hover {{
        background-color: {COLORS['bg_tertiary']};
        border-color: {COLORS['accent_cyan']};
    }}
    
    QPushButton#button_secondary:pressed {{
        background-color: {COLORS['accent_cyan']};
        color: {COLORS['bg_primary']};
    }}
    
    /* ===== TABLES ===== */
    QTableWidget {{
        background-color: {COLORS['bg_panel']};
        gridline-color: {COLORS['border_dim']};
        border: 1px solid {COLORS['border_dim']};
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {COLORS['border_dim']};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['bg_panel']};
        border: 2px solid #ffffff;
    }}
    
    QTableWidget::item:selected:!active {{
        background-color: {COLORS['bg_panel']};
    }}
    
    QHeaderView::section {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['accent_cyan']};
        padding: 10px;
        border: none;
        border-bottom: 2px solid {COLORS['border_accent']};
        font-family: '{FONTS['caps']}';
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* ===== PROGRESS BARS ===== */
    QProgressBar {{
        border: 2px solid {COLORS['border_primary']};
        border-radius: 6px;
        background-color: {COLORS['bg_secondary']};
        text-align: center;
        color: {COLORS['text_primary']};
        font-family: '{FONTS['mono']}';
        font-weight: bold;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS['accent_cyan']};
        border-radius: 4px;
    }}
    
    /* ===== SCROLL BARS ===== */
    QScrollBar:vertical {{
        background-color: {COLORS['bg_secondary']};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {COLORS['border_primary']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['accent_cyan']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* ===== STATUS INDICATORS ===== */
    QWidget#status_indicator {{
        border-radius: 6px;
        padding: 4px 12px;
        font-family: '{FONTS['caps']}';
        font-size: {FONT_SIZES['small']}pt;
        font-weight: bold;
        text-transform: uppercase;
    }}
    
    QWidget#status_online {{
        background-color: {COLORS['status_online']};
        color: white;
    }}
    
    QWidget#status_offline {{
        background-color: {COLORS['status_offline']};
        color: white;
    }}
    
    QWidget#status_warning {{
        background-color: {COLORS['status_warning']};
        color: {COLORS['bg_primary']};
    }}
    
    QWidget#status_error {{
        background-color: {COLORS['status_error']};
        color: white;
    }}
    
    /* ===== TOOLTIPS ===== */
    QToolTip {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border_accent']};
        border-radius: 4px;
        padding: 6px;
        font-family: '{FONTS['normal']}';
    }}
    
    /* ===== SPLITTERS ===== */
    QSplitter::handle {{
        background-color: {COLORS['border_primary']};
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['accent_cyan']};
    }}
    """


def get_status_color(online: bool, warning: bool = False) -> str:
    """Get status color based on state"""
    if warning:
        return COLORS['status_warning']
    return COLORS['status_online'] if online else COLORS['status_offline']


def get_track_color(track_type: str) -> str:
    """Get color for track type"""
    colors = {
        'UAV': COLORS['track_uav'],
        'BIRD': COLORS['track_bird'],
        'UNKNOWN': COLORS['track_unknown'],
        'FUSED': COLORS['track_fused']
    }
    return colors.get(track_type, COLORS['track_unknown'])


def get_sensor_color(sensor: str) -> str:
    """Get color for sensor type"""
    colors = {
        'RADAR': COLORS['sensor_radar'],
        'RF': COLORS['sensor_rf'],
        'GPS': COLORS['sensor_gps'],
        'RWS': COLORS['sensor_rws'],
    }
    return colors.get(sensor, COLORS['text_secondary'])
