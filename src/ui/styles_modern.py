"""
Ultra-Modern Tactical UI Design System for TriAD C2
Design Philosophy: Tesla/Anduril-inspired - Sculpted deep charcoal, soft elevation, restrained animations
Typography: SF Pro Display / Inter for UI, Roboto Mono for telemetry
Color: Ultra-minimal desaturated accents, high-contrast data clarity
Spacing: 12px baseline grid, generous whitespace
"""

# ===== DESIGN TOKENS =====

# Color Tokens - Stealthy tactical aesthetic (Anduril/Tesla refined)
COLORS = {
    # Backgrounds - Deeper separation for visual hierarchy
    'bg_primary': '#0F1113',      # Main background (deeper black)
    'bg_secondary': '#15181A',    # Card surface (subtle lift)
    'bg_tertiary': '#1B1F22',     # Elevated cards (clear separation)
    'bg_panel': '#15181A',        # Panel background
    'bg_hover': 'rgba(56,230,224,0.06)',  # Subtle cyan hover (6% opacity)
    'bg_selected': 'rgba(56,230,224,0.10)', # Subtle cyan selection (10% opacity)
    
    # Accent Colors - Toned down for stealth (20% darker, less glow)
    'accent_cyan': '#3DDAD7',     # Toned-down cyan (was too bright)
    'accent_cyan_dim': '#2AB8B3', # Dimmed cyan
    'accent_cyan_glow': 'rgba(61,218,215,0.20)', # Soft cyan glow
    'accent_cyan_text': 'rgba(61,218,215,0.70)', # Cyan for text/labels (reduced saturation)
    
    # Status Colors - Clear semantic meaning
    'accent_green': '#2CE08A',    # Success/online (Anduril green)
    'accent_green_dim': '#23B370', # Dimmed green
    'accent_green_glow': 'rgba(44,224,138,0.16)', # Soft green glow
    
    # Alert/Threat - Refined red with depth
    'accent_red': '#E84855',      # Refined red (less saturated, more depth)
    'accent_red_hover': '#FF6B6F', # Brighter on hover
    'accent_red_dim': '#CC484C',  # Dimmed red
    'accent_red_glow': 'rgba(232,72,85,0.20)', # Soft red glow for depth
    
    # Warning - Warm amber
    'accent_amber': '#F2B46E',    # Warning (warm amber)
    'accent_amber_dim': '#C29058', # Dimmed amber
    
    # Track colors - Semantic and clear
    'track_uav': '#FF5A5F',       # Alert red - hostile UAV
    'track_bird': '#2CE08A',      # Success green - neutral bird
    'track_unknown': '#F2B46E',   # Amber - unknown
    'track_fused': '#9D4EDD',     # Purple - fused track
    
    # Sensor colors - Matched to accents
    'sensor_radar': '#38E6E0',    # Cyan
    'sensor_rf': '#2CE08A',       # Green
    'sensor_gps': '#F2B46E',      # Amber
    'sensor_rws': '#FF5A5F',      # Red
    
    # Text colors - High contrast with opacity hierarchy
    'text_high_emphasis': 'rgba(255,255,255,0.92)',  # 92% white - primary data
    'text_medium_emphasis': 'rgba(255,255,255,0.54)', # 54% white - secondary labels
    'text_low_emphasis': 'rgba(255,255,255,0.30)',   # 30% white - muted/disabled
    'text_primary': '#EBEBEB',    # Near-white for high contrast
    'text_secondary': '#8A8A8A',  # Medium gray
    'text_tertiary': '#4D4D4D',   # Subtle gray
    'text_highlight': '#FFFFFF',  # Pure white
    
    # Status colors - Matched to semantic accents
    'status_online': '#2CE08A',   # Green
    'status_offline': '#4D4D4D',  # Muted gray
    'status_warning': '#F2B46E',  # Amber
    'status_error': '#FF5A5F',    # Red
    'status_ready': '#38E6E0',    # Cyan
    
    # Border colors - Subtle, minimal (no bright cyan outlines)
    'border_subtle': 'rgba(255,255,255,0.08)',   # Very subtle separator
    'border_card': 'rgba(61,218,215,0.15)',      # Subtle cyan tint (not bright outline)
    'border_card_hex': '#252A2E',  # Hex version for PyQtGraph (subtle gray)
    'border_card_alt': 'rgba(255,255,255,0.05)', # Alternative subtle border
    'border_focus': '#3DDAD7',    # Toned-down cyan focus
    'border_accent_bar': '#3DDAD7', # Left accent bar for selected rows
    'border_dim': 'rgba(255,255,255,0.03)',      # Very subtle border
    'border_dim_hex': '#1A1D20',  # Hex version for PyQtGraph
}

# Typography Tokens - Inter font family (modern, screen-optimized)
FONTS = {
    'title': 'Inter, -apple-system, Helvetica Neue, sans-serif',  # Inter for clean modern UI
    'heading': 'Inter, -apple-system, Helvetica Neue, sans-serif',  # Inter headings
    'body': 'Inter, -apple-system, Helvetica Neue, sans-serif',  # Inter body text
    'mono': 'JetBrains Mono, SF Mono, Menlo, Monaco, monospace',  # JetBrains Mono for data
    'primary': 'Inter, -apple-system, Helvetica Neue, sans-serif',  # Primary UI
    'data': 'JetBrains Mono, SF Mono, Menlo, Monaco, monospace',  # Monospace telemetry
}

# Font sizes - INCREASED for better legibility at 2-3ft viewing distance
FONT_SIZES = {
    'title': 26,      # Headline/title (larger for impact)
    'heading': 18,    # Headings (increased from 16)
    'body': 13,       # Body text (increased from 12)
    'mono': 14,       # Monospace telemetry (increased from 13)
    'small': 11,      # Small labels (increased from 10)
    'tiny': 10,       # Minimal text (increased from 9)
}

# Spacing Tokens - Precise layout measurements for 1600×960 window
SPACING = {
    'baseline': 12,        # Base unit
    'window_padding': 24,  # Outer margin around all content
    'panel_gutter': 18,    # Horizontal gutters between panels
    'card_padding': 20,    # Inside cards
    'item_spacing': 12,    # Between items
    'tight': 8,            # Tight spacing
}

# Border radius - Rounded, modern
BORDER_RADIUS = {
    'small': '8px',   # Small elements
    'medium': '12px', # Cards, buttons, panels
    'large': '16px',  # Large containers
    'pill': '999px',  # Pill-shaped buttons
}

# Layout Tokens - Wide desktop layout for 1800×960 reference window
LAYOUT = {
    'window_width': 1800,      # Wide reference window (16.5:9 aspect ratio)
    'window_height': 960,      # Reference window height
    'min_width': 1440,         # Minimum window width (wide panoramic minimum)
    'min_height': 850,         # Minimum window height
    'left_panel_width': 460,   # Active tracks table (fixed width)
    'right_panel_width': 360,  # System status/engage (fixed width)
    'header_height': 80,       # Top bar height
    'footer_height': 40,       # Bottom bar height
    'table_row_height': 50,    # Table rows (generous touch targets)
}

# Animation Tokens - Restrained, purposeful
ANIMATIONS = {
    'hover_duration': 120,     # ms - hover transitions
    'focus_duration': 180,     # ms - focus transitions
    'threat_pulse_min': 1200,  # ms - threat pulse (min)
    'threat_pulse_max': 1600,  # ms - threat pulse (max)
}


def load_triad_theme():
    """Load the external Triad Theme QSS file"""
    import os
    qss_path = os.path.join(os.path.dirname(__file__), 'triad_theme.qss')
    try:
        with open(qss_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"[WARNING] triad_theme.qss not found at {qss_path}, using fallback")
        return get_main_stylesheet()


def get_main_stylesheet():
    """Tesla/Apple-inspired ultra-minimalist stylesheet (fallback)"""
    return f"""
    /* ===== GLOBAL STYLES - Monochromatic depth ===== */
    QMainWindow {{
        background-color: {COLORS['bg_primary']};
        color: {COLORS['text_high_emphasis']};
        font-family: {FONTS['primary']};
        font-size: {FONT_SIZES['body']}pt;
    }}
    
    /* ===== PANELS - Subtle depth hierarchy (no bright outlines) ===== */
    QWidget#panel {{
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_card']};
        border-radius: {BORDER_RADIUS['medium']};
        padding: 20px;
        margin: 0px;
    }}
    
    QWidget#panel_elevated {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border_card_alt']};
        border-radius: {BORDER_RADIUS['medium']};
        padding: 20px;
        margin: 0px;
    }}
    
    QWidget#panel_accent {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border_card']};
        border-radius: {BORDER_RADIUS['medium']};
        padding: 20px;
        margin: 0px;
    }}
    
    /* ===== LABELS - Clean typography with opacity hierarchy ===== */
    QLabel {{
        color: {COLORS['text_high_emphasis']};
        background-color: transparent;
        font-family: {FONTS['primary']};
    }}
    
    QLabel#title {{
        font-family: {FONTS['title']};
        font-size: {FONT_SIZES['title']}pt;
        font-weight: 600;
        color: {COLORS['text_high_emphasis']};
        letter-spacing: 0.2px;
    }}
    
    QLabel#heading {{
        font-family: {FONTS['heading']};
        font-size: {FONT_SIZES['heading']}pt;
        font-weight: 600;
        color: {COLORS['text_high_emphasis']};
        letter-spacing: 0.5px;
    }}
    
    QLabel#subheading {{
        font-family: {FONTS['heading']};
        font-size: 12pt;
        font-weight: 600;
        color: {COLORS['text_medium_emphasis']};
        letter-spacing: 1.0px;
        text-transform: uppercase;
    }}
    
    QLabel#value {{
        font-family: {FONTS['data']};
        font-size: 13pt;
        color: {COLORS['text_primary']};
        font-weight: 500;
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
    
    /* ===== BUTTONS - Pill-shaped, minimal, with soft glows ===== */
    QPushButton {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_high_emphasis']};
        border: 1px solid {COLORS['border_card']};
        border-radius: {BORDER_RADIUS['medium']};
        padding: 12px 24px;
        font-family: {FONTS['heading']};
        font-size: {FONT_SIZES['body']}pt;
        font-weight: 400;
        letter-spacing: 0.3px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['bg_hover']};
        border: 2px solid {COLORS['border_focus']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['bg_selected']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['bg_secondary']};
        color: {COLORS['text_low_emphasis']};
        border-color: {COLORS['border_dim']};
    }}
    
    QPushButton:focus {{
        border: 2px solid {COLORS['border_focus']};
        outline: none;
    }}
    
    /* Engage button - Pill-shaped with refined red and hover effects */
    QPushButton#engage {{
        background-color: {COLORS['accent_red']};
        border: none;
        border-radius: {BORDER_RADIUS['pill']};
        color: {COLORS['text_highlight']};
        font-size: {FONT_SIZES['heading']}pt;
        font-weight: 600;
        padding: 16px 40px;
        transition: all 120ms ease-out;
    }}
    
    QPushButton#engage:hover {{
        background-color: {COLORS['accent_red_hover']};
    }}
    
    QPushButton#engage:pressed {{
        background-color: {COLORS['accent_red_dim']};
    }}
    
    QPushButton#engage:disabled {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border_dim']};
        color: {COLORS['text_low_emphasis']};
    }}
    
    /* Secondary button - Neutral with cyan hover */
    QPushButton#button_secondary {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border_card_alt']};
        border-radius: {BORDER_RADIUS['medium']};
        color: {COLORS['text_high_emphasis']};
        font-family: {FONTS['heading']};
        font-size: {FONT_SIZES['body']}pt;
        font-weight: 500;
        padding: 10px 20px;
    }}
    
    QPushButton#button_secondary:hover {{
        background-color: {COLORS['bg_hover']};
        border: 1px solid {COLORS['border_focus']};
    }}
    
    QPushButton#button_secondary:pressed {{
        background-color: {COLORS['bg_selected']};
    }}
    
    /* ===== TABLES - 50px rows, clearer styling ===== */
    QTableWidget {{
        background-color: transparent;
        gridline-color: transparent;
        border: none;
        selection-background-color: {COLORS['bg_selected']};
        alternate-background-color: transparent;
        font-size: {FONT_SIZES['body']}pt;
    }}
    
    QTableWidget::item {{
        padding: 16px 12px;
        border: none;
        border-bottom: 1px solid {COLORS['border_subtle']};
        color: {COLORS['text_high_emphasis']};
        font-size: {FONT_SIZES['body']}pt;
    }}
    
    QTableWidget::item:hover {{
        background-color: {COLORS['bg_hover']};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLORS['bg_selected']};
        color: {COLORS['text_high_emphasis']};
    }}
    
    QTableWidget::item:selected:!active {{
        background-color: {COLORS['bg_hover']};
        color: {COLORS['text_high_emphasis']};
    }}
    
    QHeaderView::section {{
        background-color: transparent;
        color: {COLORS['text_medium_emphasis']};
        padding: 16px 12px;
        border: none;
        border-bottom: 1px solid {COLORS['border_subtle']};
        font-family: {FONTS['heading']};
        font-weight: 600;
        font-size: 12pt;
        letter-spacing: 1.0px;
        text-transform: uppercase;
    }}
    
    /* ===== PROGRESS BARS ===== */
    QProgressBar {{
        border: 1px solid {COLORS['border_card']};
        border-radius: {BORDER_RADIUS['small']};
        background-color: {COLORS['bg_secondary']};
        text-align: center;
        color: {COLORS['text_high_emphasis']};
        font-family: {FONTS['mono']};
        font-weight: 400;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS['accent_cyan']};
        border-radius: {BORDER_RADIUS['small']};
    }}
    
    /* ===== SCROLL BARS - Subtle and transparent ===== */
    QScrollBar:vertical {{
        background-color: transparent;
        width: 8px;
        border-radius: 4px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: rgba(255,255,255,0.08);
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: rgba(255,255,255,0.15);
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* ===== STATUS INDICATORS ===== */
    QWidget#status_indicator {{
        border-radius: 6px;
        padding: 4px 12px;
        font-family: {FONTS['heading']};
        font-size: {FONT_SIZES['small']}pt;
        font-weight: 600;
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
    
    /* ===== GROUPBOX - Data cards with alternating depths ===== */
    QGroupBox {{
        background-color: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border_card_alt']};
        border-radius: {BORDER_RADIUS['medium']};
        padding: 20px;
        margin-top: 12px;
        font-family: {FONTS['heading']};
        font-size: 12pt;
        font-weight: 600;
        color: {COLORS['text_medium_emphasis']};
        letter-spacing: 1.0px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0px 8px;
        color: {COLORS['text_medium_emphasis']};
        background-color: transparent;
        text-transform: uppercase;
    }}
    
    /* Alternate GroupBox styling for visual hierarchy */
    QGroupBox#panel_accent {{
        background-color: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border_card']};
    }}
    
    /* ===== TOOLTIPS - Floating cards ===== */
    QToolTip {{
        background-color: {COLORS['bg_tertiary']};
        color: {COLORS['text_high_emphasis']};
        border: 1px solid {COLORS['border_card']};
        border-radius: {BORDER_RADIUS['medium']};
        padding: 8px 12px;
        font-family: {FONTS['primary']};
    }}
    
    /* ===== SPLITTERS - Minimal dividers ===== */
    QSplitter::handle {{
        background-color: {COLORS['border_dim']};
        width: 1px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {COLORS['border_focus']};
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
