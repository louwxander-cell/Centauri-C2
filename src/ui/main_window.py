"""Main application window for TriAD C2 system"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QGroupBox, QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from typing import Dict, Optional
import time

from ..core.bus import SignalBus
from ..core.datamodels import Track, GeoPosition, SystemStatus
from .radar_scope import RadarScope
from .styles import TACTICAL_DARK_THEME, format_status_text


class MainWindow(QMainWindow):
    """
    Main C2 application window with 3-pane layout:
    - Left: Track list table
    - Center: Radar scope display
    - Right: System status panel
    - Bottom: Engage/Slew control
    """
    
    def __init__(self):
        super().__init__()
        self.signal_bus = SignalBus.instance()
        
        # Track data
        self.tracks: Dict[int, Track] = {}
        self.selected_track_id: Optional[int] = None
        self.ownship_position: Optional[GeoPosition] = None
        
        # System status
        self.system_status = SystemStatus()
        
        self._setup_ui()
        self._connect_signals()
        self._start_update_timer()
        
    def _setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("TriAD Counter-UAS C2 System")
        self.setGeometry(100, 100, 1600, 900)
        
        # Apply tactical dark theme
        self.setStyleSheet(TACTICAL_DARK_THEME)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Top section: 3-pane splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Track list
        left_panel = self._create_track_list_panel()
        splitter.addWidget(left_panel)
        
        # Center panel: Radar scope
        center_panel = self._create_radar_scope_panel()
        splitter.addWidget(center_panel)
        
        # Right panel: System status
        right_panel = self._create_status_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800, 400])
        
        main_layout.addWidget(splitter)
        
        # Bottom section: Engage button
        engage_panel = self._create_engage_panel()
        main_layout.addWidget(engage_panel)
        
        # Status bar
        self.statusBar().showMessage("System Initializing...")
        
    def _create_track_list_panel(self) -> QGroupBox:
        """Create left panel with track list table"""
        group = QGroupBox("Active Tracks")
        layout = QVBoxLayout(group)
        
        # Track table
        self.track_table = QTableWidget()
        self.track_table.setColumnCount(6)
        self.track_table.setHorizontalHeaderLabels([
            "ID", "Range (m)", "Azimuth (°)", "Type", "Source", "Conf"
        ])
        
        # Configure table
        self.track_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.track_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.track_table.setAlternatingRowColors(True)
        self.track_table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.track_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 50)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 80)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 70)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(5, 60)
        
        # Connect selection signal
        self.track_table.itemSelectionChanged.connect(self._on_track_selected)
        
        layout.addWidget(self.track_table)
        
        # Track count label
        self.track_count_label = QLabel("Tracks: 0")
        self.track_count_label.setObjectName("headerLabel")
        layout.addWidget(self.track_count_label)
        
        return group
    
    def _create_radar_scope_panel(self) -> QGroupBox:
        """Create center panel with radar scope"""
        group = QGroupBox("Tactical Display")
        layout = QVBoxLayout(group)
        
        # Radar scope widget
        self.radar_scope = RadarScope()
        layout.addWidget(self.radar_scope)
        
        return group
    
    def _create_status_panel(self) -> QGroupBox:
        """Create right panel with system status"""
        group = QGroupBox("System Status")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Sensor status labels
        self.radar_status_label = QLabel()
        self.rf_status_label = QLabel()
        self.gps_status_label = QLabel()
        self.rws_status_label = QLabel()
        
        for label in [self.radar_status_label, self.rf_status_label,
                      self.gps_status_label, self.rws_status_label]:
            label.setObjectName("statusLabel")
            layout.addWidget(label)
        
        layout.addSpacing(20)
        
        # Ownship position
        ownship_group = QGroupBox("Ownship Position")
        ownship_layout = QVBoxLayout(ownship_group)
        
        self.lat_label = QLabel("Lat: --")
        self.lon_label = QLabel("Lon: --")
        self.heading_label = QLabel("Heading: --")
        
        ownship_layout.addWidget(self.lat_label)
        ownship_layout.addWidget(self.lon_label)
        ownship_layout.addWidget(self.heading_label)
        
        layout.addWidget(ownship_group)
        
        layout.addStretch()
        
        # Update status display
        self._update_status_display()
        
        return group
    
    def _create_engage_panel(self) -> QWidget:
        """Create bottom panel with engage button"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Selected track info
        self.selected_track_label = QLabel("No track selected")
        self.selected_track_label.setObjectName("headerLabel")
        layout.addWidget(self.selected_track_label)
        
        layout.addStretch()
        
        # Engage button
        self.engage_button = QPushButton("🎯 ENGAGE / SLEW")
        self.engage_button.setObjectName("engageButton")
        self.engage_button.setEnabled(False)
        self.engage_button.clicked.connect(self._on_engage_clicked)
        self.engage_button.setMinimumWidth(300)
        
        layout.addWidget(self.engage_button)
        
        return widget
    
    def _connect_signals(self):
        """Connect signal bus signals to handlers"""
        self.signal_bus.sig_track_updated.connect(self._on_track_updated)
        self.signal_bus.sig_track_removed.connect(self._on_track_removed)
        self.signal_bus.sig_ownship_updated.connect(self._on_ownship_updated)
        self.signal_bus.sig_radar_status.connect(lambda online: self._on_sensor_status("Radar", online))
        self.signal_bus.sig_rf_status.connect(lambda online: self._on_sensor_status("RF", online))
        self.signal_bus.sig_gps_status.connect(lambda online: self._on_sensor_status("GPS", online))
        self.signal_bus.sig_rws_status.connect(lambda online: self._on_sensor_status("RWS", online))
    
    def _start_update_timer(self):
        """Start timer for periodic UI updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._periodic_update)
        self.update_timer.start(100)  # 10 Hz update rate
    
    def _on_track_updated(self, track: Track):
        """Handle track update from signal bus"""
        self.tracks[track.id] = track
        self.radar_scope.update_track(track)
        self._update_track_table()
    
    def _on_track_removed(self, track_id: int):
        """Handle track removal"""
        if track_id in self.tracks:
            del self.tracks[track_id]
            self.radar_scope.remove_track(track_id)
            self._update_track_table()
    
    def _on_ownship_updated(self, position: GeoPosition):
        """Handle ownship position update"""
        self.ownship_position = position
        self.lat_label.setText(f"Lat: {position.lat:.6f}°")
        self.lon_label.setText(f"Lon: {position.lon:.6f}°")
        self.heading_label.setText(f"Heading: {position.heading:.1f}°")
    
    def _on_sensor_status(self, sensor_name: str, online: bool):
        """Handle sensor status update"""
        if sensor_name == "Radar":
            self.system_status.radar_online = online
        elif sensor_name == "RF":
            self.system_status.rf_online = online
        elif sensor_name == "GPS":
            self.system_status.gps_online = online
        elif sensor_name == "RWS":
            self.system_status.rws_online = online
        
        self._update_status_display()
    
    def _update_status_display(self):
        """Update status panel display"""
        self.radar_status_label.setText(format_status_text("Radar", self.system_status.radar_online))
        self.rf_status_label.setText(format_status_text("RF Sensor", self.system_status.rf_online))
        self.gps_status_label.setText(format_status_text("GPS", self.system_status.gps_online))
        
        rws_status = "STANDBY" if self.system_status.rws_online else "OFFLINE"
        color = "#ffaa00" if self.system_status.rws_online else "#ff0000"
        self.rws_status_label.setText(
            f'<span style="color: {color}; font-weight: bold;">RWS: {rws_status}</span>'
        )
    
    def _update_track_table(self):
        """Update track list table"""
        self.track_table.setRowCount(len(self.tracks))
        
        for row, (track_id, track) in enumerate(sorted(self.tracks.items())):
            # ID
            self.track_table.setItem(row, 0, QTableWidgetItem(str(track.id)))
            
            # Range
            self.track_table.setItem(row, 1, QTableWidgetItem(f"{track.range_m:.0f}"))
            
            # Azimuth
            self.track_table.setItem(row, 2, QTableWidgetItem(f"{track.azimuth:.1f}"))
            
            # Type
            self.track_table.setItem(row, 3, QTableWidgetItem(track.type.value))
            
            # Source
            self.track_table.setItem(row, 4, QTableWidgetItem(track.source.value))
            
            # Confidence
            self.track_table.setItem(row, 5, QTableWidgetItem(f"{track.confidence:.2f}"))
        
        self.track_count_label.setText(f"Tracks: {len(self.tracks)}")
    
    def _on_track_selected(self):
        """Handle track selection in table"""
        selected_rows = self.track_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            track_id_item = self.track_table.item(row, 0)
            if track_id_item:
                self.selected_track_id = int(track_id_item.text())
                track = self.tracks.get(self.selected_track_id)
                if track:
                    self.selected_track_label.setText(
                        f"Selected: Track {track.id} | {track.type.value} | "
                        f"Range: {track.range_m:.0f}m | Az: {track.azimuth:.1f}°"
                    )
                    self.engage_button.setEnabled(True)
                    self.signal_bus.sig_track_selected.emit(self.selected_track_id)
        else:
            self.selected_track_id = None
            self.selected_track_label.setText("No track selected")
            self.engage_button.setEnabled(False)
    
    def _on_engage_clicked(self):
        """Handle engage button click"""
        if self.selected_track_id and self.selected_track_id in self.tracks:
            track = self.tracks[self.selected_track_id]
            
            # Emit slew command
            self.signal_bus.emit_slew(track.azimuth, track.elevation)
            
            # Update status
            self.statusBar().showMessage(
                f"SLEW COMMAND: Track {track.id} | Az: {track.azimuth:.1f}° | El: {track.elevation:.1f}°",
                3000
            )
            
            print(f"[MainWindow] Engage command issued for Track {track.id}")
    
    def _periodic_update(self):
        """Periodic update for stale track removal"""
        current_time = time.time()
        stale_tracks = [
            track_id for track_id, track in self.tracks.items()
            if track.is_stale(timeout_sec=5.0)
        ]
        
        for track_id in stale_tracks:
            self._on_track_removed(track_id)
        
        # Update system status
        self.system_status.active_tracks = len(self.tracks)
        self.system_status.last_update = current_time
    
    def closeEvent(self, event):
        """Handle window close event"""
        print("[MainWindow] Shutting down...")
        self.signal_bus.sig_shutdown.emit()
        event.accept()
