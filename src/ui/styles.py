"""Tactical Dark Mode styling for TriAD C2"""


TACTICAL_DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 11pt;
}

/* Panels and Frames */
QFrame {
    background-color: #252525;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
}

QGroupBox {
    background-color: #252525;
    border: 2px solid #3a3a3a;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: bold;
    color: #00ff00;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    color: #00ff00;
}

/* Tables */
QTableWidget {
    background-color: #1a1a1a;
    alternate-background-color: #252525;
    gridline-color: #3a3a3a;
    border: 1px solid #3a3a3a;
    selection-background-color: #0d47a1;
    selection-color: #ffffff;
}

QTableWidget::item {
    padding: 4px;
    color: #e0e0e0;
}

QTableWidget::item:selected {
    background-color: #0d47a1;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #2d2d2d;
    color: #00ff00;
    padding: 6px;
    border: 1px solid #3a3a3a;
    font-weight: bold;
}

/* Buttons */
QPushButton {
    background-color: #2d2d2d;
    color: #e0e0e0;
    border: 2px solid #4a4a4a;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #3a3a3a;
    border-color: #5a5a5a;
}

QPushButton:pressed {
    background-color: #1a1a1a;
}

QPushButton:disabled {
    background-color: #1a1a1a;
    color: #5a5a5a;
    border-color: #2a2a2a;
}

/* Engage Button - Special Red Styling */
QPushButton#engageButton {
    background-color: #8b0000;
    color: #ffffff;
    border: 3px solid #ff0000;
    font-size: 14pt;
    font-weight: bold;
    min-height: 50px;
}

QPushButton#engageButton:hover {
    background-color: #a00000;
    border-color: #ff3333;
}

QPushButton#engageButton:pressed {
    background-color: #600000;
}

QPushButton#engageButton:disabled {
    background-color: #3a1a1a;
    color: #5a3a3a;
    border-color: #4a2a2a;
}

/* Labels */
QLabel {
    color: #e0e0e0;
    background-color: transparent;
    border: none;
}

QLabel#statusLabel {
    font-weight: bold;
    padding: 4px;
}

QLabel#headerLabel {
    color: #00ff00;
    font-size: 12pt;
    font-weight: bold;
}

/* Status Indicators */
QLabel#statusOnline {
    color: #00ff00;
    font-weight: bold;
}

QLabel#statusOffline {
    color: #ff0000;
    font-weight: bold;
}

QLabel#statusStandby {
    color: #ffaa00;
    font-weight: bold;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #1a1a1a;
    width: 12px;
    border: 1px solid #3a3a3a;
}

QScrollBar::handle:vertical {
    background-color: #4a4a4a;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5a5a5a;
}

QScrollBar:horizontal {
    background-color: #1a1a1a;
    height: 12px;
    border: 1px solid #3a3a3a;
}

QScrollBar::handle:horizontal {
    background-color: #4a4a4a;
    min-width: 20px;
    border-radius: 4px;
}

/* Text Edit / Input */
QTextEdit, QLineEdit {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 4px;
    selection-background-color: #0d47a1;
}

/* Splitter */
QSplitter::handle {
    background-color: #3a3a3a;
}

QSplitter::handle:hover {
    background-color: #4a4a4a;
}

/* Status Bar */
QStatusBar {
    background-color: #1a1a1a;
    color: #00ff00;
    border-top: 1px solid #3a3a3a;
}
"""


def get_status_color(online: bool) -> str:
    """Get color for status indicator"""
    return "#00ff00" if online else "#ff0000"


def format_status_text(name: str, online: bool) -> str:
    """Format status text with color"""
    status = "ONLINE" if online else "OFFLINE"
    color = get_status_color(online)
    return f'<span style="color: {color}; font-weight: bold;">{name}: {status}</span>'
