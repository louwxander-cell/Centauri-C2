"""
Enhanced Modern Radar Scope
Features:
- Track tails with 10-second fade
- Threat prioritization with labels
- Selection indicators (red circle)
- Click-to-select functionality
- Detection type legend
- Clean, minimalist design
"""

import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt6.QtGui import QFont, QPen, QColor, QBrush, QPainterPath
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPathItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsPixmapItem, QPushButton
from PyQt6.QtGui import QPixmap
from ..core.datamodels import Track
from ..core.threat_assessment import ThreatAssessment
from .styles_modern import COLORS, FONTS, get_track_color
import numpy as np
import math
import time
from collections import deque
from typing import Dict, Optional, Tuple


class RadarScopeEnhanced(pg.PlotWidget):
    """
    Enhanced tactical radar scope with:
    - Track tails (10-second fade)
    - Threat prioritization
    - Selection indicators
    - Click-to-select
    - Legend
    - Clean, minimalist design
    """
    
    # Signal emitted when track is selected by clicking
    track_selected = pyqtSignal(int)  # track_id
    
    def __init__(self, max_range_m: float = 1500.0):
        super().__init__()
        
        self.max_range = max_range_m
        self.tracks = {}  # id -> Track
        self.track_plots = {}  # id -> scatter plot
        self.track_tails = {}  # id -> deque of (x, y, timestamp)
        self.track_tail_plots = {}  # id -> path item
        self.threat_labels = {}  # id -> text item
        self.selection_indicator = None  # Circle around selected track
        self.highest_threat_indicator = None  # Red circle around highest threat
        self.selected_track_id = None
        self.highest_threat_id = None
        self.radar_fov_item = None  # Radar field of view indicator
        self.radar_heading = 0.0  # Radar pointing direction (0 = North)
        
        # Tail settings
        self.tail_duration = 20.0  # seconds (increased from 10)
        self.tail_max_points = 100  # Maximum points in tail (increased for smoother trails)
        
        self._setup_plot()
        self._draw_static_elements()
        self._create_legend_overlay()
        self._create_zoom_controls()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)
        self.timer.start(100)  # 10 Hz
        
        # Enable mouse interaction
        self.scene().sigMouseClicked.connect(self._on_mouse_clicked)
    
    def _setup_plot(self):
        """Setup the plot widget"""
        # Set background
        self.setBackground(COLORS['bg_panel'])
        
        # Configure plot
        plot_item = self.getPlotItem()
        plot_item.setAspectLocked(True)
        plot_item.showGrid(False, False)
        plot_item.hideAxis('left')
        plot_item.hideAxis('bottom')
        
        # Set range
        plot_item.setXRange(-self.max_range, self.max_range)
        plot_item.setYRange(-self.max_range, self.max_range)
        
        # Disable auto-range
        plot_item.enableAutoRange(False)
    
    def _draw_static_elements(self):
        """Draw static elements (range rings, bearing lines)"""
        plot_item = self.getPlotItem()
        
        # Range rings - more pronounced
        ranges = [250, 500, 750, 1000, 1250, 1500, 2000, 2500, 3000]
        for r in ranges:
            if r <= self.max_range:
                circle = pg.QtWidgets.QGraphicsEllipseItem(-r, -r, 2*r, 2*r)
                circle.setPen(pg.mkPen(
                    color=COLORS['border_primary'],  # More visible color
                    width=2,  # Thicker lines
                    style=Qt.PenStyle.DashLine
                ))
                plot_item.addItem(circle)
                
                # Range label - 50% larger
                label = pg.TextItem(
                    text=f"{r}m",
                    color=COLORS['text_primary'],  # Brighter text
                    anchor=(0.5, 0.5)
                )
                label.setFont(QFont(FONTS['mono'], 12))  # Increased from 8 to 12
                label.setPos(0, r)
                plot_item.addItem(label)
        
        # Bearing lines (every 30 degrees)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x = self.max_range * math.sin(rad)
            y = self.max_range * math.cos(rad)
            
            line = pg.PlotDataItem(
                [0, x], [0, y],
                pen=pg.mkPen(
                    color=COLORS['border_dim'], 
                    width=1, 
                    style=Qt.PenStyle.DotLine
                )
            )
            plot_item.addItem(line)
            
            # Bearing label
            if angle % 90 == 0:  # Only cardinal directions
                label_dist = self.max_range * 0.92
                label_x = label_dist * math.sin(rad)
                label_y = label_dist * math.cos(rad)
                
                direction = ['N', 'E', 'S', 'W'][angle // 90]
                label = pg.TextItem(
                    text=direction,
                    color=COLORS['accent_cyan'],
                    anchor=(0.5, 0.5)
                )
                label.setFont(QFont(FONTS['caps'], 12, QFont.Weight.Bold))
                label.setPos(label_x, label_y)
                plot_item.addItem(label)
        
        # Center marker (ownship)
        center = pg.ScatterPlotItem(
            [0], [0],
            size=20,
            brush=pg.mkBrush(COLORS['accent_cyan']),
            pen=pg.mkPen(color=COLORS['accent_cyan'], width=3),
            symbol='+'
        )
        plot_item.addItem(center)
        
        # Forward indicator
        forward_arrow = pg.ArrowItem(
            angle=0,
            tipAngle=30,
            baseAngle=20,
            headLen=40,
            tailLen=60,
            tailWidth=10,
            pen=pg.mkPen(color=COLORS['accent_cyan'], width=2),
            brush=pg.mkBrush(COLORS['accent_cyan'])
        )
        forward_arrow.setPos(0, 0)
        plot_item.addItem(forward_arrow)
        
        # Radar FOV indicator (80 degree azimuth)
        self._draw_radar_fov()
    
    def _draw_radar_fov(self):
        """Draw radar field of view (80 degree azimuth)"""
        plot_item = self.getPlotItem()
        
        # Radar FOV: 80 degrees centered on heading
        fov_angle = 80.0  # degrees
        half_fov = fov_angle / 2.0
        
        # Calculate FOV boundaries (assuming North = 0 degrees)
        left_angle = self.radar_heading - half_fov
        right_angle = self.radar_heading + half_fov
        
        # Create FOV wedge
        num_points = 50
        angles = np.linspace(math.radians(left_angle), math.radians(right_angle), num_points)
        
        # FOV extends to max range
        fov_range = self.max_range * 0.95
        
        x_points = [0]  # Start at origin
        y_points = [0]
        
        for angle in angles:
            x = fov_range * math.sin(angle)
            y = fov_range * math.cos(angle)
            x_points.append(x)
            y_points.append(y)
        
        x_points.append(0)  # Close the wedge
        y_points.append(0)
        
        # Draw FOV boundary
        fov_boundary = pg.PlotDataItem(
            x_points, y_points,
            pen=pg.mkPen(color=COLORS['accent_cyan'], width=2, style=Qt.PenStyle.DashLine),
            fillLevel=0,
            fillBrush=pg.mkBrush(color=(*QColor(COLORS['accent_cyan']).getRgb()[:3], 20))  # Very transparent fill
        )
        plot_item.addItem(fov_boundary)
        self.radar_fov_item = fov_boundary
        
        # Add FOV angle labels
        for side, angle in [("L", left_angle), ("R", right_angle)]:
            rad = math.radians(angle)
            label_dist = self.max_range * 0.85
            label_x = label_dist * math.sin(rad)
            label_y = label_dist * math.cos(rad)
            
            label = pg.TextItem(
                text=f"{angle:.0f}°",
                color=COLORS['accent_cyan'],
                anchor=(0.5, 0.5)
            )
            label.setFont(QFont(FONTS['mono'], 8))
            label.setPos(label_x, label_y)
            plot_item.addItem(label)
    
    def _create_legend_overlay(self):
        """Create fixed legend overlay in upper right corner"""
        # Create legend widget
        self.legend_widget = QWidget(self)
        self.legend_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(17, 24, 39, 0.9);
                border: 1px solid {COLORS['border_primary']};
                border-radius: 4px;
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(self.legend_widget)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title = QLabel("TYPES")
        title.setFont(QFont(FONTS['caps'], 9, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        layout.addWidget(title)
        
        # Legend items with visible symbols
        items = [
            ("UAV", COLORS['track_uav'], "▲"),
            ("BIRD", COLORS['track_bird'], "▲"),
            ("UNKNOWN", COLORS['track_unknown'], "▲"),
            ("SELECT", "#ffffff", "○"),
            ("THREAT", "#ef4444", "○"),
        ]
        
        for label, color, symbol in items:
            item_layout = QHBoxLayout()
            item_layout.setSpacing(6)
            item_layout.setContentsMargins(0, 0, 0, 0)
            
            # Symbol with explicit rendering
            symbol_label = QLabel(symbol)
            symbol_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            symbol_label.setStyleSheet(f"color: {color}; background: transparent;")
            symbol_label.setFixedWidth(15)
            symbol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item_layout.addWidget(symbol_label)
            
            # Label
            text_label = QLabel(label)
            text_label.setFont(QFont(FONTS['normal'], 8))
            text_label.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
            item_layout.addWidget(text_label)
            item_layout.addStretch()
            
            layout.addLayout(item_layout)
        
        # Set fixed size and position in upper right corner
        self.legend_widget.setFixedWidth(110)
        self.legend_widget.adjustSize()
        self.legend_widget.move(self.width() - self.legend_widget.width() - 15, 15)
        self.legend_widget.show()
    
    def _create_zoom_controls(self):
        """Create zoom control buttons in bottom right corner"""
        # Zoom controls container
        self.zoom_widget = QWidget(self)
        self.zoom_widget.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(17, 24, 39, 0.9);
                border: 1px solid {COLORS['border_primary']};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {COLORS['bg_panel']};
                border: 1px solid {COLORS['border_primary']};
                color: {COLORS['text_primary']};
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border_primary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['border_dim']};
            }}
        """)
        
        layout = QVBoxLayout(self.zoom_widget)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Zoom in button (+)
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(40, 40)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        layout.addWidget(self.zoom_in_btn)
        
        # Zoom out button (-)
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedSize(40, 40)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        layout.addWidget(self.zoom_out_btn)
        
        # Position in bottom right corner
        self.zoom_widget.adjustSize()
        self.zoom_widget.move(self.width() - self.zoom_widget.width() - 15, 
                             self.height() - self.zoom_widget.height() - 15)
        self.zoom_widget.show()
    
    def resizeEvent(self, event):
        """Handle resize to keep legend and zoom controls positioned"""
        super().resizeEvent(event)
        if hasattr(self, 'legend_widget'):
            self.legend_widget.move(self.width() - self.legend_widget.width() - 15, 15)
        if hasattr(self, 'zoom_widget'):
            self.zoom_widget.move(self.width() - self.zoom_widget.width() - 15,
                                 self.height() - self.zoom_widget.height() - 15)
    
    def update_track(self, track: Track):
        """Update or add a track"""
        self.tracks[track.id] = track
        
        # Convert polar to Cartesian
        x, y = self._polar_to_cartesian(track.azimuth, track.range_m)
        
        # Update track tail
        if track.id not in self.track_tails:
            self.track_tails[track.id] = deque(maxlen=self.tail_max_points)
        
        tail = self.track_tails[track.id]
        tail.append((x, y, time.time()))
        
        # Remove old tail points (> 10 seconds)
        current_time = time.time()
        while tail and (current_time - tail[0][2]) > self.tail_duration:
            tail.popleft()
        
        # Get track color
        color = get_track_color(track.type)
        
        # Update or create track plot
        if track.id in self.track_plots:
            # Update existing
            self.track_plots[track.id].setData([x], [y])
        else:
            # Create new
            scatter = pg.ScatterPlotItem(
                [x], [y],
                size=14,
                brush=pg.mkBrush(color),
                pen=pg.mkPen(color=color, width=2),
                symbol='t'  # Triangle
            )
            self.getPlotItem().addItem(scatter)
            self.track_plots[track.id] = scatter
    
    def remove_track(self, track_id: int):
        """Remove a track from display"""
        if track_id in self.tracks:
            del self.tracks[track_id]
        
        if track_id in self.track_plots:
            self.getPlotItem().removeItem(self.track_plots[track_id])
            del self.track_plots[track_id]
        
        if track_id in self.track_tails:
            del self.track_tails[track_id]
        
        if track_id in self.track_tail_plots:
            self.getPlotItem().removeItem(self.track_tail_plots[track_id])
            del self.track_tail_plots[track_id]
        
        if track_id in self.threat_labels:
            self.getPlotItem().removeItem(self.threat_labels[track_id])
            del self.threat_labels[track_id]
    
    def set_selected_track(self, track_id: Optional[int]):
        """Set the selected track"""
        self.selected_track_id = track_id
        self._update_selection_indicator()
    
    def set_highest_threat(self, track_id: Optional[int]):
        """Set the highest threat track (draws red circle)"""
        self.highest_threat_id = track_id
    
    def _zoom_in(self):
        """Zoom in (decrease range)"""
        zoom_levels = [750, 1000, 1500, 2000, 3000]
        current_idx = zoom_levels.index(self.max_range) if self.max_range in zoom_levels else 2
        if current_idx > 0:
            self.set_max_range(zoom_levels[current_idx - 1])
    
    def _zoom_out(self):
        """Zoom out (increase range)"""
        zoom_levels = [750, 1000, 1500, 2000, 3000]
        current_idx = zoom_levels.index(self.max_range) if self.max_range in zoom_levels else 2
        if current_idx < len(zoom_levels) - 1:
            self.set_max_range(zoom_levels[current_idx + 1])
    
    def set_max_range(self, new_range: float):
        """Change the maximum range of the radar scope"""
        self.max_range = new_range
        
        # Update plot ranges
        plot_item = self.getPlotItem()
        plot_item.setXRange(-self.max_range, self.max_range)
        plot_item.setYRange(-self.max_range, self.max_range)
        
        # Store current tracks and indicators
        stored_tracks = dict(self.tracks)
        stored_selected = self.selected_track_id
        stored_highest = self.highest_threat_id
        
        # Clear and redraw static elements
        plot_item.clear()
        self.track_plots.clear()
        self.track_tail_plots.clear()
        self.threat_labels.clear()
        
        self._draw_static_elements()
        
        # Restore tracks
        self.tracks = {}
        for track_id, track in stored_tracks.items():
            self.update_track(track)
        
        # Restore indicators
        self.selected_track_id = stored_selected
        self.highest_threat_id = stored_highest
        self._update_selection_indicator()
        self._update_highest_threat_indicator()
    
    def _polar_to_cartesian(self, azimuth: float, range_m: float) -> tuple:
        """Convert polar coordinates to Cartesian (vehicle-relative)"""
        rad = math.radians(azimuth)
        x = range_m * math.sin(rad)
        y = range_m * math.cos(rad)
        return (x, y)
    
    def _update_display(self):
        """Update display (called by timer)"""
        self._draw_track_tails()
        self._draw_threat_labels()
        self._update_selection_indicator()
    
    def _draw_track_tails(self):
        """Draw track tails with fading"""
        current_time = time.time()
        
        for track_id, tail in self.track_tails.items():
            if len(tail) < 2:
                continue
            
            # Remove old tail plot
            if track_id in self.track_tail_plots:
                self.getPlotItem().removeItem(self.track_tail_plots[track_id])
            
            # Create path for tail
            path = QPainterPath()
            
            # Get track color
            if track_id in self.tracks:
                color = QColor(get_track_color(self.tracks[track_id].type))
            else:
                color = QColor(COLORS['text_secondary'])
            
            # Draw tail segments with gradual fading
            points = list(tail)
            for i in range(len(points) - 1):
                x1, y1, t1 = points[i]
                x2, y2, t2 = points[i + 1]
                
                # Calculate fade based on age (gradual fade over 20 seconds)
                age = current_time - t1
                alpha = max(0.2, 1.0 - (age / self.tail_duration))  # Min alpha 0.2, max 1.0
                
                # Create segment
                if i == 0:
                    path.moveTo(x1, y1)
                path.lineTo(x2, y2)
            
            # Create path item with more visible settings
            color.setAlphaF(0.85)  # More opaque (was 0.6)
            pen = QPen(color, 4, Qt.PenStyle.SolidLine)  # Thicker line (was 2)
            
            path_item = QGraphicsPathItem(path)
            path_item.setPen(pen)
            
            self.getPlotItem().addItem(path_item)
            self.track_tail_plots[track_id] = path_item
    
    def _draw_threat_labels(self):
        """Draw threat level labels"""
        # Calculate threat scores
        tracks_list = list(self.tracks.values())
        if not tracks_list:
            return
        
        prioritized = ThreatAssessment.prioritize_tracks(tracks_list)
        
        # Update highest threat
        if prioritized:
            self.highest_threat_id = prioritized[0][0].id
        
        # Draw labels for high threats
        for track, threat_score in prioritized:
            if threat_score < 0.4:  # Only show medium+ threats
                continue
            
            x, y = self._polar_to_cartesian(track.azimuth, track.range_m)
            
            # Threat level and color
            threat_level = ThreatAssessment.get_threat_level(threat_score)
            threat_color = ThreatAssessment.get_threat_color(threat_score)
            
            # Create or update label
            label_text = f"ID:{track.id}\n{threat_level}"
            
            if track.id in self.threat_labels:
                label = self.threat_labels[track.id]
                label.setText(label_text)
                label.setPos(x + 80, y + 40)
            else:
                label = pg.TextItem(
                    text=label_text,
                    color=threat_color,
                    anchor=(0, 0.5)
                )
                label.setFont(QFont(FONTS['caps'], 9, QFont.Weight.Bold))
                label.setPos(x + 80, y + 40)
                self.getPlotItem().addItem(label)
                self.threat_labels[track.id] = label
            
            # Update color
            label.setColor(threat_color)
    
    def _update_selection_indicator(self):
        """Update selection indicator (white circle)"""
        # Remove old indicator
        if self.selection_indicator:
            self.getPlotItem().removeItem(self.selection_indicator)
            self.selection_indicator = None
        
        # Draw new indicator if track selected
        if self.selected_track_id and self.selected_track_id in self.tracks:
            track = self.tracks[self.selected_track_id]
            x, y = self._polar_to_cartesian(track.azimuth, track.range_m)
            
            # Create white circle for selection
            radius = 100
            circle = QGraphicsEllipseItem(
                x - radius, y - radius,
                2 * radius, 2 * radius
            )
            circle.setPen(QPen(QColor("#ffffff"), 3, Qt.PenStyle.SolidLine))
            circle.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            
            self.getPlotItem().addItem(circle)
            self.selection_indicator = circle
        
        # Update highest threat indicator (red circle)
        if self.highest_threat_indicator:
            self.getPlotItem().removeItem(self.highest_threat_indicator)
            self.highest_threat_indicator = None
        
        if self.highest_threat_id and self.highest_threat_id in self.tracks:
            track = self.tracks[self.highest_threat_id]
            x, y = self._polar_to_cartesian(track.azimuth, track.range_m)
            
            # Create red circle for highest threat
            radius = 120  # Slightly larger than selection
            circle = QGraphicsEllipseItem(
                x - radius, y - radius,
                2 * radius, 2 * radius
            )
            circle.setPen(QPen(QColor("#ef4444"), 4, Qt.PenStyle.DashLine))  # Red dashed
            circle.setBrush(QBrush(Qt.BrushStyle.NoBrush))
            
            self.getPlotItem().addItem(circle)
            self.highest_threat_indicator = circle
    
    def _on_mouse_clicked(self, event):
        """Handle mouse click for track selection"""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        
        # Get click position in data coordinates
        pos = self.getPlotItem().vb.mapSceneToView(event.scenePos())
        click_x = pos.x()
        click_y = pos.y()
        
        # Find nearest track
        min_dist = 150  # Maximum click distance
        nearest_id = None
        
        for track_id, track in self.tracks.items():
            x, y = self._polar_to_cartesian(track.azimuth, track.range_m)
            dist = math.sqrt((x - click_x)**2 + (y - click_y)**2)
            
            if dist < min_dist:
                min_dist = dist
                nearest_id = track_id
        
        # Select track
        if nearest_id is not None:
            self.set_selected_track(nearest_id)
            self.track_selected.emit(nearest_id)
