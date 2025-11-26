"""
Modern Tactical Radar Scope with RF Overlay
Displays tracks, pilot positions, and range rings
"""

import pyqtgraph as pg
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPen, QColor
from ..core.datamodels import Track
from .styles_modern import COLORS, FONTS, get_track_color, get_sensor_color
import numpy as np
import math


class RadarScopeModern(pg.PlotWidget):
    """
    Modern tactical radar scope with:
    - Polar plot (range/bearing)
    - Track display (radar + RF)
    - Pilot position markers
    - Range rings
    - Bearing lines
    - Track trails
    """
    
    def __init__(self, max_range_m: float = 5000.0):
        super().__init__()
        
        self.max_range = max_range_m
        self.tracks = {}  # id -> Track
        self.track_plots = {}  # id -> scatter plot
        self.pilot_plots = {}  # id -> scatter plot
        self.track_trails = {}  # id -> list of positions
        self.trail_length = 20  # Number of points in trail
        
        self._setup_plot()
        self._draw_static_elements()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_display)
        self.timer.start(100)  # 10 Hz
    
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
        
        # Title
        title_style = f"color: {COLORS['accent_cyan']}; font-family: '{FONTS['caps']}'; font-size: 16pt; font-weight: bold;"
        plot_item.setTitle("TACTICAL RADAR SCOPE", **{'color': COLORS['accent_cyan'], 'size': '16pt'})
    
    def _draw_static_elements(self):
        """Draw static elements (range rings, bearing lines)"""
        plot_item = self.getPlotItem()
        
        # Range rings
        ranges = [1000, 2000, 3000, 4000, 5000]
        for r in ranges:
            if r <= self.max_range:
                circle = pg.QtWidgets.QGraphicsEllipseItem(-r, -r, 2*r, 2*r)
                circle.setPen(pg.mkPen(color=COLORS['border_primary'], width=1, style=Qt.PenStyle.DashLine))
                plot_item.addItem(circle)
                
                # Range label
                label = pg.TextItem(
                    text=f"{r/1000:.0f}km",
                    color=COLORS['text_tertiary'],
                    anchor=(0.5, 0.5)
                )
                label.setFont(QFont(FONTS['mono'], 8))
                label.setPos(0, r)
                plot_item.addItem(label)
        
        # Bearing lines (every 30 degrees)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            x = self.max_range * math.sin(rad)
            y = self.max_range * math.cos(rad)
            
            line = pg.PlotDataItem(
                [0, x], [0, y],
                pen=pg.mkPen(color=COLORS['border_dim'], width=1, style=Qt.PenStyle.DotLine)
            )
            plot_item.addItem(line)
            
            # Bearing label
            label_dist = self.max_range * 1.05
            label_x = label_dist * math.sin(rad)
            label_y = label_dist * math.cos(rad)
            
            label = pg.TextItem(
                text=f"{angle}°",
                color=COLORS['text_tertiary'],
                anchor=(0.5, 0.5)
            )
            label.setFont(QFont(FONTS['caps'], 9))
            label.setPos(label_x, label_y)
            plot_item.addItem(label)
        
        # Center marker (ownship)
        center = pg.ScatterPlotItem(
            [0], [0],
            size=15,
            brush=pg.mkBrush(COLORS['accent_cyan']),
            pen=pg.mkPen(color=COLORS['accent_cyan'], width=2),
            symbol='+'
        )
        plot_item.addItem(center)
        
        # Forward indicator
        forward_line = pg.PlotDataItem(
            [0, 0], [0, self.max_range * 0.15],
            pen=pg.mkPen(color=COLORS['accent_cyan'], width=3)
        )
        plot_item.addItem(forward_line)
        
        forward_label = pg.TextItem(
            text="FWD",
            color=COLORS['accent_cyan'],
            anchor=(0.5, 1.5)
        )
        forward_label.setFont(QFont(FONTS['caps'], 10, QFont.Weight.Bold))
        forward_label.setPos(0, self.max_range * 0.15)
        plot_item.addItem(forward_label)
    
    def update_track(self, track: Track):
        """Update or add a track"""
        self.tracks[track.id] = track
        
        # Convert polar to Cartesian
        x, y = self._polar_to_cartesian(track.azimuth, track.range_m)
        
        # Update track trail
        if track.id not in self.track_trails:
            self.track_trails[track.id] = []
        
        trail = self.track_trails[track.id]
        trail.append((x, y))
        if len(trail) > self.trail_length:
            trail.pop(0)
        
        # Get track color
        color = get_track_color(track.type)
        
        # Update or create track plot
        if track.id in self.track_plots:
            # Update existing
            self.track_plots[track.id].setData([x], [y])
        else:
            # Create new
            symbol = self._get_track_symbol(track)
            scatter = pg.ScatterPlotItem(
                [x], [y],
                size=12,
                brush=pg.mkBrush(color),
                pen=pg.mkPen(color=color, width=2),
                symbol=symbol
            )
            self.getPlotItem().addItem(scatter)
            self.track_plots[track.id] = scatter
        
        # Update pilot position if available
        if track.pilot_latitude and track.pilot_longitude and track.source == "RF":
            # For now, just mark pilot position relative to drone
            # In production, convert lat/lon to vehicle-relative coordinates
            pilot_x = x + 50  # Placeholder offset
            pilot_y = y + 50
            
            if track.id in self.pilot_plots:
                self.pilot_plots[track.id].setData([pilot_x], [pilot_y])
            else:
                pilot_scatter = pg.ScatterPlotItem(
                    [pilot_x], [pilot_y],
                    size=10,
                    brush=pg.mkBrush(COLORS['accent_yellow']),
                    pen=pg.mkPen(color=COLORS['accent_yellow'], width=2),
                    symbol='star'
                )
                self.getPlotItem().addItem(pilot_scatter)
                self.pilot_plots[track.id] = pilot_scatter
    
    def remove_track(self, track_id: int):
        """Remove a track from display"""
        if track_id in self.tracks:
            del self.tracks[track_id]
        
        if track_id in self.track_plots:
            self.getPlotItem().removeItem(self.track_plots[track_id])
            del self.track_plots[track_id]
        
        if track_id in self.pilot_plots:
            self.getPlotItem().removeItem(self.pilot_plots[track_id])
            del self.pilot_plots[track_id]
        
        if track_id in self.track_trails:
            del self.track_trails[track_id]
    
    def _polar_to_cartesian(self, azimuth: float, range_m: float) -> tuple:
        """Convert polar coordinates to Cartesian (vehicle-relative)"""
        # Azimuth 0° = forward (North on plot)
        # Convert to radians
        rad = math.radians(azimuth)
        
        # Calculate x, y (rotate 90° so 0° points up)
        x = range_m * math.sin(rad)
        y = range_m * math.cos(rad)
        
        return (x, y)
    
    def _get_track_symbol(self, track: Track) -> str:
        """Get symbol for track based on type and source"""
        if track.source == "RF":
            return 'o'  # Circle for RF
        elif track.source == "RADAR":
            return 't'  # Triangle for radar
        elif track.source == "FUSED":
            return 's'  # Square for fused
        else:
            return 'd'  # Diamond for unknown
    
    def _update_display(self):
        """Update display (called by timer)"""
        # Draw track trails
        plot_item = self.getPlotItem()
        
        for track_id, trail in self.track_trails.items():
            if len(trail) > 1 and track_id in self.tracks:
                track = self.tracks[track_id]
                color = get_track_color(track.type)
                
                # Extract x, y arrays
                x_arr = [p[0] for p in trail]
                y_arr = [p[1] for p in trail]
                
                # Create trail line (fading)
                # TODO: Implement fading trail effect
