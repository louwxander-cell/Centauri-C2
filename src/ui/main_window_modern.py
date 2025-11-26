"""
Modern Tactical Main Window for TriAD C2 System
Ultra-modern interface with all sensor capabilities
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QGridLayout,
    QFrame, QProgressBar, QGroupBox, QStyledItemDelegate, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QPen
from PyQt6.QtWidgets import QStyle
from ..core.bus import SignalBus
from ..core.datamodels import Track, GeoPosition
from .styles_modern import (
    get_main_stylesheet, COLORS, FONTS, FONT_SIZES,
    get_status_color, get_track_color, get_sensor_color
)
from .radar_scope_enhanced import RadarScopeEnhanced
from .map_widget import OfflineMapWidget
from ..core.threat_assessment import ThreatAssessment
import time


class ColorPreservingDelegate(QStyledItemDelegate):
    """Custom delegate to preserve text color when item is selected"""
    
    def paint(self, painter, option, index):
        # Get the original foreground color stored in UserRole
        original_color = index.data(Qt.ItemDataRole.UserRole)
        
        if original_color and (option.state & QStyle.StateFlag.State_Selected):
            # Item is selected - preserve the original color
            painter.save()
            
            # Draw selection border (white outline)
            pen = QPen(QColor("#ffffff"), 2)
            painter.setPen(pen)
            painter.drawRect(option.rect.adjusted(1, 1, -1, -1))
            
            # Draw text with original color
            painter.setPen(original_color)
            painter.drawText(option.rect, Qt.AlignmentFlag.AlignCenter, index.data())
            
            painter.restore()
        else:
            # Not selected - use default painting
            super().paint(painter, option, index)


class ModernMainWindow(QMainWindow):
    """
    Ultra-modern tactical main window for TriAD C2 system.
    
    Features:
    - Modern dark tactical theme
    - Real-time sensor status
    - Track table with all details
    - Radar scope with RF overlay
    - Pilot position display
    - Command chain status
    - RF-silent mode indicator
    - Optical lock status
    """
    
    def __init__(self):
        super().__init__()
        self.signal_bus = SignalBus.instance()
        
        # Track storage
        self.tracks = {}  # id -> Track
        # System status
        self.radar_online = False
        self.rf_online = False
        self.gps_online = False
        self.rws_online = False
        self.rf_silent_mode = False
        self.optical_lock = False
        
        # Tracks
        self.tracks: Dict[int, Track] = {}
        self.selected_track: Optional[Track] = None
        
        # Ownship
        self.ownship_lat = None
        self.ownship_lon = None
        self.ownship_heading = 0.0
        
        # View mode
        self.current_view = "radar"  # "radar" or "map"
        
        # Auto-reset timer for manual selections
        self.manual_selection_timer = QTimer()
        self.manual_selection_timer.setSingleShot(True)
        self.manual_selection_timer.timeout.connect(self._auto_reset_to_highest_threat)
        self.manual_selection_timeout = 10000  # 10 seconds
        self.manual_selection_active = False  # Track if user made manual selection
        
        self._init_ui()
        self._connect_signals()
        self._start_timers()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TriAD C2 - Counter-UAS Command & Control")
        self.setGeometry(100, 100, 1920, 1080)
        
        # Apply modern stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top bar - System status
        main_layout.addWidget(self._create_top_bar())
        
        # Content area - 3 columns
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Track list and details
        content_splitter.addWidget(self._create_left_panel())
        
        # Center panel - Radar scope
        content_splitter.addWidget(self._create_center_panel())
        
        # Right panel - System info and controls
        content_splitter.addWidget(self._create_right_panel())
        
        # Set splitter sizes (25% - 50% - 25%)
        content_splitter.setSizes([480, 960, 480])
        
        main_layout.addWidget(content_splitter)
        
        # Bottom bar - Command chain status
        main_layout.addWidget(self._create_bottom_bar())
    
    def _create_top_bar(self) -> QWidget:
        """Create top status bar"""
        bar = QWidget()
        bar.setObjectName("panel")
        bar.setFixedHeight(80)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # System title
        title = QLabel("TRIAD C2 SYSTEM")
        title.setObjectName("heading")
        title_font = QFont(FONTS['caps'], FONT_SIZES['title'], QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Sensor status indicators
        self.radar_status = self._create_status_indicator("RADAR", False)
        self.rf_status = self._create_status_indicator("RF SENSOR", False)
        self.gps_status = self._create_status_indicator("GPS", False)
        self.rws_status = self._create_status_indicator("RWS", False)
        
        layout.addWidget(self.radar_status)
        layout.addWidget(self.rf_status)
        layout.addWidget(self.gps_status)
        layout.addWidget(self.rws_status)
        
        return bar
    
    def _create_status_indicator(self, label: str, online: bool) -> QWidget:
        """Create a status indicator widget"""
        widget = QWidget()
        widget_layout = QHBoxLayout(widget)
        widget_layout.setContentsMargins(10, 5, 10, 5)
        widget_layout.setSpacing(8)
        
        # Status dot
        dot = QLabel("●")
        dot.setObjectName("status_offline" if not online else "status_online")
        dot_font = QFont(FONTS['normal'], 16)
        dot.setFont(dot_font)
        widget_layout.addWidget(dot)
        
        # Label
        text = QLabel(label)
        text.setObjectName("subheading")
        text_font = QFont(FONTS['caps'], FONT_SIZES['small'], QFont.Weight.Bold)
        text.setFont(text_font)
        widget_layout.addWidget(text)
        
        # Store references for updates
        widget.dot = dot
        widget.label = text
        
        return widget
    
    def _create_left_panel(self) -> QWidget:
        """Create left panel with track list and details"""
        panel = QWidget()
        panel.setObjectName("panel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Track list heading
        heading = QLabel("ACTIVE TRACKS")
        heading.setObjectName("heading")
        layout.addWidget(heading)
        
        # Track table
        self.track_table = QTableWidget()
        self.track_table.setColumnCount(6)
        self.track_table.setHorizontalHeaderLabels(["ID", "Type", "Source", "Range", "Az", "Conf"])
        self.track_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.track_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.track_table.setAlternatingRowColors(False)  # Disable alternating colors
        self.track_table.itemSelectionChanged.connect(self._on_track_selected)
        self.track_table.verticalHeader().setVisible(False)
        
        # Apply custom delegate to preserve text colors when selected
        self.color_delegate = ColorPreservingDelegate()
        self.track_table.setItemDelegate(self.color_delegate)
        
        # Set column widths for better visibility
        self.track_table.setColumnWidth(0, 30)   # ID
        self.track_table.setColumnWidth(1, 70)   # Type
        self.track_table.setColumnWidth(2, 70)   # Source
        self.track_table.setColumnWidth(3, 75)   # Range
        self.track_table.setColumnWidth(4, 70)   # Azimuth
        self.track_table.setColumnWidth(5, 60)   # Confidence
        
        layout.addWidget(self.track_table, stretch=2)
        
        # Track details heading
        details_heading = QLabel("TRACK DETAILS")
        details_heading.setObjectName("heading")
        layout.addWidget(details_heading)
        
        # Track details panel
        self.details_panel = self._create_track_details_panel()
        layout.addWidget(self.details_panel, stretch=1)
        
        return panel
    
    def _create_track_details_panel(self) -> QWidget:
        """Create track details panel"""
        panel = QWidget()
        panel.setObjectName("panel_accent")
        
        layout = QGridLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Create detail fields
        row = 0
        
        # Basic info
        self._add_detail_row(layout, row, "TRACK ID:", "track_id"); row += 1
        self._add_detail_row(layout, row, "Type:", "track_type"); row += 1
        self._add_detail_row(layout, row, "Source:", "track_source"); row += 1
        
        # Position
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "Range:", "track_range"); row += 1
        self._add_detail_row(layout, row, "Azimuth:", "track_azimuth"); row += 1
        self._add_detail_row(layout, row, "Elevation:", "track_elevation"); row += 1
        
        # RF-specific
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "Drone Model:", "drone_model"); row += 1
        self._add_detail_row(layout, row, "Serial Number:", "drone_serial"); row += 1
        self._add_detail_row(layout, row, "RF Frequency:", "rf_frequency"); row += 1
        self._add_detail_row(layout, row, "RF Power:", "rf_power"); row += 1
        
        # Pilot position
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "Pilot Lat:", "pilot_lat"); row += 1
        self._add_detail_row(layout, row, "Pilot Lon:", "pilot_lon"); row += 1
        
        # Radar-specific
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "RCS:", "track_rcs"); row += 1
        self._add_detail_row(layout, row, "UAV Probability:", "uav_prob"); row += 1
        
        # Velocity
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "Velocity:", "track_velocity"); row += 1
        self._add_detail_row(layout, row, "Heading:", "track_heading"); row += 1
        
        layout.setRowStretch(row, 1)
        
        return panel
    
    def _add_detail_row(self, layout: QGridLayout, row: int, label: str, value_name: str):
        """Add a detail row to the grid"""
        # Label
        lbl = QLabel(label)
        if label.isupper():
            lbl.setObjectName("subheading")
            lbl_font = QFont(FONTS['caps'], FONT_SIZES['small'], QFont.Weight.Bold)
        else:
            lbl_font = QFont(FONTS['normal'], FONT_SIZES['small'])
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        lbl.setFont(lbl_font)
        layout.addWidget(lbl, row, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Value
        val = QLabel("—")
        val.setObjectName("value")
        val_font = QFont(FONTS['mono'], FONT_SIZES['small'])
        val.setFont(val_font)
        layout.addWidget(val, row, 1, Qt.AlignmentFlag.AlignRight)
        
        # Store reference
        setattr(self, f"detail_{value_name}", val)
    
    def _create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {COLORS['border_dim']};")
        line.setFixedHeight(1)
        return line
    
    def _create_center_panel(self) -> QWidget:
        """Create center panel with radar scope and map view"""
        panel = QWidget()
        panel.setObjectName("panel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header with heading and view toggle
        header_layout = QHBoxLayout()
        
        # Heading
        heading = QLabel("TACTICAL DISPLAY")
        heading.setObjectName("heading")
        header_layout.addWidget(heading)
        
        header_layout.addStretch()
        
        # View toggle button
        self.view_toggle_btn = QPushButton("SWITCH TO MAP VIEW")
        self.view_toggle_btn.setObjectName("button_secondary")
        self.view_toggle_btn.setFixedHeight(35)
        self.view_toggle_btn.clicked.connect(self._toggle_view_mode)
        header_layout.addWidget(self.view_toggle_btn)
        
        layout.addLayout(header_layout)
        
        # Radar scope (enhanced)
        self.radar_scope = RadarScopeEnhanced()
        self.radar_scope.track_selected.connect(self._on_radar_track_selected)
        layout.addWidget(self.radar_scope)
        
        # Map widget (hidden initially)
        self.map_widget = OfflineMapWidget(
            cache_dir="map_cache",
            center_lat=-25.841105,
            center_lon=28.180340
        )
        # Set initial ownship position for map
        self.map_widget.set_ownship(-25.841105, 28.180340, 0.0)
        self.map_widget.hide()
        layout.addWidget(self.map_widget)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Create right panel with system info and controls"""
        panel = QWidget()
        panel.setObjectName("panel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Ownship position
        layout.addWidget(self._create_ownship_panel())
        
        # System mode indicators
        layout.addWidget(self._create_mode_panel())
        
        # RWS position
        layout.addWidget(self._create_rws_panel())
        
        layout.addStretch()
        
        # Reset to highest threat button
        self.reset_btn = QPushButton("RESET TO HIGHEST THREAT")
        self.reset_btn.setObjectName("button_secondary")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.clicked.connect(self._on_reset_to_highest_threat)
        layout.addWidget(self.reset_btn)
        
        # Engage button
        self.engage_btn = QPushButton("ENGAGE TARGET")
        self.engage_btn.setObjectName("engage")
        self.engage_btn.setEnabled(False)
        self.engage_btn.setFixedHeight(60)
        self.engage_btn.clicked.connect(self._on_engage_clicked)
        layout.addWidget(self.engage_btn)
        
        # Threat info label
        self.threat_info_label = QLabel("No threats detected")
        self.threat_info_label.setObjectName("value")
        self.threat_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.threat_info_label)
        
        return panel
    
    def _create_ownship_panel(self) -> QWidget:
        """Create ownship position panel"""
        group = QGroupBox()
        group.setObjectName("panel_accent")
        
        layout = QGridLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("OWNSHIP POSITION")
        title.setObjectName("heading")
        layout.addWidget(title, 0, 0, 1, 2)
        
        # Fields
        self._add_detail_row(layout, 1, "Latitude:", "own_lat")
        self._add_detail_row(layout, 2, "Longitude:", "own_lon")
        self._add_detail_row(layout, 3, "Heading:", "own_heading")
        
        return group
    
    def _create_mode_panel(self) -> QWidget:
        """Create system mode panel"""
        group = QGroupBox()
        group.setObjectName("panel_accent")
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("SYSTEM MODE")
        title.setObjectName("heading")
        layout.addWidget(title)
        
        # RF-Silent mode indicator
        self.rf_silent_indicator = self._create_mode_indicator(
            "RF-SILENT MODE", False, COLORS['status_warning']
        )
        layout.addWidget(self.rf_silent_indicator)
        
        # Optical lock indicator
        self.optical_lock_indicator = self._create_mode_indicator(
            "OPTICAL LOCK", False, COLORS['status_online']
        )
        layout.addWidget(self.optical_lock_indicator)
        
        return group
    
    def _create_mode_indicator(self, label: str, active: bool, color: str) -> QWidget:
        """Create a mode indicator"""
        widget = QWidget()
        widget_layout = QHBoxLayout(widget)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(10)
        
        # Icon
        icon = QLabel("●")
        icon_font = QFont(FONTS['normal'], 14)
        icon.setFont(icon_font)
        icon.setStyleSheet(f"color: {COLORS['status_offline']};")
        widget_layout.addWidget(icon)
        
        # Label
        text = QLabel(label)
        text.setObjectName("subheading")
        text_font = QFont(FONTS['caps'], FONT_SIZES['small'], QFont.Weight.Bold)
        text.setFont(text_font)
        widget_layout.addWidget(text)
        
        widget_layout.addStretch()
        
        # Store references
        widget.icon = icon
        widget.color = color
        widget.active = active
        
        return widget
    
    def _create_rws_panel(self) -> QWidget:
        """Create RWS position panel"""
        group = QGroupBox()
        group.setObjectName("panel_accent")
        
        layout = QGridLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("RWS POSITION")
        title.setObjectName("heading")
        layout.addWidget(title, 0, 0, 1, 2)
        
        # Radar position
        row = 1
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        lbl = QLabel("RADAR")
        lbl.setObjectName("subheading")
        layout.addWidget(lbl, row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "Azimuth:", "radar_az"); row += 1
        self._add_detail_row(layout, row, "Elevation:", "radar_el"); row += 1
        
        # Optics position
        layout.addWidget(self._create_separator(), row, 0, 1, 2); row += 1
        lbl = QLabel("OPTICS")
        lbl.setObjectName("subheading")
        layout.addWidget(lbl, row, 0, 1, 2); row += 1
        self._add_detail_row(layout, row, "Azimuth:", "optics_az"); row += 1
        self._add_detail_row(layout, row, "Elevation:", "optics_el"); row += 1
        
        return group
    
    def _create_bottom_bar(self) -> QWidget:
        """Create bottom command chain status bar"""
        bar = QWidget()
        bar.setObjectName("panel")
        bar.setFixedHeight(60)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(20)
        
        # Command chain status
        title = QLabel("COMMAND CHAIN:")
        title.setObjectName("subheading")
        layout.addWidget(title)
        
        # Chain steps
        self.chain_rf = self._create_chain_step("RF DETECT", COLORS['sensor_rf'])
        self.chain_radar_slew = self._create_chain_step("RADAR SLEW", COLORS['sensor_rws'])
        self.chain_radar_track = self._create_chain_step("RADAR TRACK", COLORS['sensor_radar'])
        self.chain_optics_slew = self._create_chain_step("OPTICS SLEW", COLORS['sensor_rws'])
        self.chain_optical_lock = self._create_chain_step("OPTICAL LOCK", COLORS['status_online'])
        
        layout.addWidget(self.chain_rf)
        layout.addWidget(QLabel("→"))
        layout.addWidget(self.chain_radar_slew)
        layout.addWidget(QLabel("→"))
        layout.addWidget(self.chain_radar_track)
        layout.addWidget(QLabel("→"))
        layout.addWidget(self.chain_optics_slew)
        layout.addWidget(QLabel("→"))
        layout.addWidget(self.chain_optical_lock)
        
        layout.addStretch()
        
        # System time
        self.time_label = QLabel()
        self.time_label.setObjectName("value")
        layout.addWidget(self.time_label)
        
        return bar
    
    def _create_chain_step(self, label: str, color: str) -> QLabel:
        """Create a command chain step indicator"""
        lbl = QLabel(label)
        lbl.setObjectName("subheading")
        lbl_font = QFont(FONTS['caps'], FONT_SIZES['tiny'], QFont.Weight.Bold)
        lbl.setFont(lbl_font)
        lbl.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            color: {COLORS['text_disabled']};
            border: 2px solid {COLORS['border_dim']};
            border-radius: 4px;
            padding: 6px 12px;
        """)
        lbl.active_color = color
        lbl.is_active = False
        return lbl
    
    def _connect_signals(self):
        """Connect signal bus signals"""
        self.signal_bus.sig_track_updated.connect(self._on_track_updated)
        self.signal_bus.sig_ownship_updated.connect(self._on_ownship_updated)
        # TODO: Connect sensor status signals
    
    def _start_timers(self):
        """Start update timers"""
        # UI update timer (10 Hz)
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_ui)
        self.ui_timer.start(100)
        
        # Time display timer (1 Hz)
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)
    
    @pyqtSlot(Track)
    def _on_track_updated(self, track: Track):
        """Handle track update from signal bus"""
        self.tracks[track.id] = track
        
        # Update both views
        self.radar_scope.update_track(track)
        if self.current_view == "map":
            self.map_widget.update_track(track)
    
    @pyqtSlot(GeoPosition)
    def _on_ownship_updated(self, position: GeoPosition):
        """Handle ownship position update"""
        self.ownship_lat = position.lat
        self.ownship_lon = position.lon
        if position.heading is not None:
            self.ownship_heading = position.heading
        
        # Update map widget with ownship position
        self.map_widget.set_ownship(self.ownship_lat, self.ownship_lon, self.ownship_heading)
    
    def _on_track_selected(self):
        """Handle track selection from table"""
        selected_rows = self.track_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            track_id = int(self.track_table.item(row, 0).text())
            self.selected_track = self.tracks.get(track_id)
            self._update_track_details()
            self.engage_btn.setEnabled(True)
            
            # Update radar scope selection
            self.radar_scope.set_selected_track(track_id)
            
            # Mark as manual selection and start timer
            self.manual_selection_active = True
            self.manual_selection_timer.start(self.manual_selection_timeout)
            
            # Update engage button text
            self.engage_btn.setText(f"ENGAGE ID:{track_id}")
        else:
            self.selected_track = None
            self.engage_btn.setEnabled(False)
            self.engage_btn.setText("ENGAGE TARGET")
            self.radar_scope.set_selected_track(None)

    def _on_radar_track_selected(self, track_id: int):
        """Handle track selection from radar scope click"""
        if track_id in self.tracks:
            self.selected_track = self.tracks[track_id]
            self._update_track_details()
            self.engage_btn.setEnabled(True)
            self.engage_btn.setText(f"ENGAGE ID:{track_id}")
            
            # Update table selection
            for row in range(self.track_table.rowCount()):
                if int(self.track_table.item(row, 0).text()) == track_id:
                    self.track_table.selectRow(row)
                    break
            
            # Mark as manual selection and start timer
            self.manual_selection_active = True
            self.manual_selection_timer.start(self.manual_selection_timeout)

    def _on_reset_to_highest_threat(self):
        """Reset selection to highest threat (manual button click)"""
        # Stop auto-reset timer and clear manual mode
        self.manual_selection_timer.stop()
        self.manual_selection_active = False
        
        # Clear manual selection
        self.selected_track = None
        self.track_table.clearSelection()
        self.radar_scope.set_selected_track(None)
        
        # Force update to re-select highest threat
        self._update_threat_prioritization()
        
        # Update track details to show highest threat
        self._update_track_details()
    
    def _auto_reset_to_highest_threat(self):
        """Auto-reset selection to highest threat after timeout"""
        # Exit manual selection mode - return to auto mode
        self.manual_selection_active = False
        
        # Clear manual selection
        self.selected_track = None
        self.track_table.clearSelection()
        self.radar_scope.set_selected_track(None)
        
        # Force update to re-select highest threat
        self._update_threat_prioritization()
        
        # Update track details to show highest threat
        self._update_track_details()
    
    def _toggle_view_mode(self):
        """Toggle between radar and map view"""
        if self.current_view == "radar":
            # Switch to map view
            self.radar_scope.hide()
            self.map_widget.show()
            self.view_toggle_btn.setText("SWITCH TO RADAR VIEW")
            self.current_view = "map"
            
            # Update map with current ownship position
            if self.ownship_lat and self.ownship_lon:
                self.map_widget.set_ownship(self.ownship_lat, self.ownship_lon, self.ownship_heading)
            
            # Update map with all tracks
            for track in self.tracks.values():
                self.map_widget.update_track(track)
        else:
            # Switch to radar view
            self.map_widget.hide()
            self.radar_scope.show()
            self.view_toggle_btn.setText("SWITCH TO MAP VIEW")
            self.current_view = "radar"
    
    def _on_engage_clicked(self):
        """Handle engage button click"""
        if self.selected_track:
            print(f"[UI] ENGAGE command for track {self.selected_track.id}")
            self.signal_bus.sig_slew_command.emit(
                self.selected_track.azimuth,
                self.selected_track.elevation
            )
    
    def _update_ui(self):
        """Update UI elements"""
        self._update_track_table()
        self._update_sensor_status()
        self._update_ownship_display()
        self._update_threat_prioritization()
        self._remove_stale_tracks()
    
    def _update_track_table(self):
        """Update track table"""
        # Temporarily block signals to prevent selection changes during update
        self.track_table.blockSignals(True)
        self.track_table.setRowCount(len(self.tracks))
        
        for row, (track_id, track) in enumerate(sorted(self.tracks.items())):
            # ID - use same color as Type column
            id_item = QTableWidgetItem(str(track.id))
            id_color = QColor(get_track_color(track.type))
            id_item.setForeground(id_color)
            id_item.setData(Qt.ItemDataRole.UserRole, id_color)  # Store original color
            self.track_table.setItem(row, 0, id_item)
            
            # Type
            type_item = QTableWidgetItem(track.type)
            type_color = QColor(get_track_color(track.type))
            type_item.setForeground(type_color)
            type_item.setData(Qt.ItemDataRole.UserRole, type_color)
            self.track_table.setItem(row, 1, type_item)
            
            # Source
            source_item = QTableWidgetItem(track.source)
            source_color = QColor(get_sensor_color(track.source))
            source_item.setForeground(source_color)
            source_item.setData(Qt.ItemDataRole.UserRole, source_color)
            self.track_table.setItem(row, 2, source_item)
            
            # Range
            range_item = QTableWidgetItem(f"{track.range_m:.0f}m")
            range_color = QColor(COLORS['text_primary'])
            range_item.setForeground(range_color)
            range_item.setData(Qt.ItemDataRole.UserRole, range_color)
            self.track_table.setItem(row, 3, range_item)
            
            # Azimuth
            az_item = QTableWidgetItem(f"{track.azimuth:.1f}°")
            az_color = QColor(COLORS['text_primary'])
            az_item.setForeground(az_color)
            az_item.setData(Qt.ItemDataRole.UserRole, az_color)
            self.track_table.setItem(row, 4, az_item)
            
            # Confidence
            conf_item = QTableWidgetItem(f"{track.confidence:.2f}")
            if track.confidence > 0.7:
                conf_color = QColor(COLORS['status_online'])
            elif track.confidence < 0.4:
                conf_color = QColor(COLORS['status_warning'])
            else:
                conf_color = QColor(COLORS['text_primary'])
            conf_item.setForeground(conf_color)
            conf_item.setData(Qt.ItemDataRole.UserRole, conf_color)
            self.track_table.setItem(row, 5, conf_item)
        
        self.track_table.blockSignals(False)
    
    def _update_track_details(self):
        """Update track details panel - defaults to highest threat"""
        # Use selected track if available, otherwise use highest threat
        display_track = self.selected_track
        
        if not display_track and self.tracks:
            # No manual selection - show highest threat
            from ..core.threat_assessment import ThreatAssessment
            tracks_list = list(self.tracks.values())
            display_track = ThreatAssessment.get_highest_threat(tracks_list)
        
        if not display_track:
            return
        
        t = display_track
        
        # Basic info
        self.detail_track_id.setText(str(t.id))
        self.detail_track_type.setText(t.type)
        self.detail_track_source.setText(t.source)
        
        # Position
        self.detail_track_range.setText(f"{t.range_m:.0f} m")
        self.detail_track_azimuth.setText(f"{t.azimuth:.1f}°")
        self.detail_track_elevation.setText(f"{t.elevation:.1f}°")
        
        # RF-specific
        self.detail_drone_model.setText(t.aircraft_model or "—")
        self.detail_drone_serial.setText(t.serial_number or "—")
        self.detail_rf_frequency.setText(
            f"{t.rf_frequency/1e9:.2f} GHz" if t.rf_frequency else "—"
        )
        self.detail_rf_power.setText(
            f"{t.rf_power:.1f} dBm" if t.rf_power else "—"
        )
        
        # Pilot position
        self.detail_pilot_lat.setText(
            f"{t.pilot_latitude:.6f}" if t.pilot_latitude else "—"
        )
        self.detail_pilot_lon.setText(
            f"{t.pilot_longitude:.6f}" if t.pilot_longitude else "—"
        )
        
        # Radar-specific
        self.detail_track_rcs.setText(
            f"{t.rcs:.2f} m²" if t.rcs else "—"
        )
        self.detail_uav_prob.setText(
            f"{t.probability_uav:.2%}" if t.probability_uav else "—"
        )
        
        # Velocity
        self.detail_track_velocity.setText(
            f"{t.velocity_mps:.1f} m/s" if t.velocity_mps else "—"
        )
        self.detail_track_heading.setText(
            f"{t.heading:.1f}°" if t.heading else "—"
        )
    
    def _update_threat_prioritization(self):
        """Update threat prioritization and auto-select highest threat"""
        if not self.tracks:
            self.threat_info_label.setText("No threats detected")
            self.radar_scope.set_highest_threat(None)
            self.engage_btn.setEnabled(False)
            self.engage_btn.setText("ENGAGE TARGET")
            return
        
        # Get highest threat
        tracks_list = list(self.tracks.values())
        highest_threat = ThreatAssessment.get_highest_threat(tracks_list)
        
        if highest_threat:
            # Calculate threat score
            threat_score = ThreatAssessment.calculate_threat_score(highest_threat)
            threat_level = ThreatAssessment.get_threat_level(threat_score)
            
            # Update radar scope with highest threat
            self.radar_scope.set_highest_threat(highest_threat.id)
            
            # Update threat info
            self.threat_info_label.setText(
                f"Highest Threat: ID:{highest_threat.id} - {threat_level} "
                f"({threat_score:.0%})"
            )
            
            # Auto-select if no manual selection OR if in auto mode
            if not self.manual_selection_active:
                # Auto mode - always track highest threat
                self.selected_track = highest_threat
                self.radar_scope.set_selected_track(highest_threat.id)
                self.engage_btn.setEnabled(True)
                self.engage_btn.setText(f"ENGAGE ID:{highest_threat.id}")
                self._update_track_details()
                
                # Select in table (block signals to prevent recursion)
                self.track_table.blockSignals(True)
                for row in range(self.track_table.rowCount()):
                    if self.track_table.item(row, 0) and int(self.track_table.item(row, 0).text()) == highest_threat.id:
                        self.track_table.selectRow(row)
                        break
                self.track_table.blockSignals(False)
            else:
                # Manual selection mode - keep manual selection
                if self.selected_track and self.selected_track.id in self.tracks:
                    # Selected track still exists
                    self.engage_btn.setEnabled(True)
                    self.engage_btn.setText(f"ENGAGE ID:{self.selected_track.id}")
                else:
                    # Selected track no longer exists - exit manual mode
                    self.manual_selection_active = False
                    self.manual_selection_timer.stop()
                    self.selected_track = None
                    self.track_table.clearSelection()
    
    def _update_sensor_status(self):
        """Update sensor status indicators"""
        # TODO: Get actual status from drivers
        pass
    
    def _update_ownship_display(self):
        """Update ownship position display"""
        if self.ownship_lat and self.ownship_lon:
            self.detail_own_lat.setText(f"{self.ownship_lat:.6f}")
            self.detail_own_lon.setText(f"{self.ownship_lon:.6f}")
            self.detail_own_heading.setText(f"{self.ownship_heading:.1f}°")
    
    def _update_time(self):
        """Update time display"""
        from datetime import datetime
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S UTC"))
    
    def _remove_stale_tracks(self):
        """Remove stale tracks"""
        stale_ids = [
            track_id for track_id, track in self.tracks.items()
            if track.is_stale(timeout_sec=5.0)
        ]
        for track_id in stale_ids:
            del self.tracks[track_id]
            self.radar_scope.remove_track(track_id)
    
    def set_mode_indicator(self, indicator: QWidget, active: bool):
        """Set mode indicator state"""
        if active:
            indicator.icon.setStyleSheet(f"color: {indicator.color};")
        else:
            indicator.icon.setStyleSheet(f"color: {COLORS['status_offline']};")
        indicator.active = active
    
    def set_chain_step(self, step: QLabel, active: bool):
        """Set command chain step state"""
        if active:
            step.setStyleSheet(f"""
                background-color: {step.active_color};
                color: white;
                border: 2px solid {step.active_color};
                border-radius: 4px;
                padding: 6px 12px;
            """)
        else:
            step.setStyleSheet(f"""
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_disabled']};
                border: 2px solid {COLORS['border_dim']};
                border-radius: 4px;
                padding: 6px 12px;
            """)
        step.is_active = active
