"""Radar scope widget using PyQtGraph for polar plot visualization"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from typing import Dict
from ..core.datamodels import Track


class RadarScope(QWidget):
    """
    Polar plot radar scope display.
    Shows tracks in range/bearing format with color coding by type.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracks: Dict[int, Track] = {}
        self.max_range = 2000  # meters
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Initialize the radar scope UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create PyQtGraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#1a1a1a')
        self.plot_widget.setAspectLocked(True)
        
        # Configure plot
        self.plot_widget.setLabel('left', 'North (m)')
        self.plot_widget.setLabel('bottom', 'East (m)')
        self.plot_widget.setTitle('Radar Scope', color='#00ff00', size='14pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set range limits
        self.plot_widget.setXRange(-self.max_range, self.max_range)
        self.plot_widget.setYRange(-self.max_range, self.max_range)
        
        # Add range rings
        self._add_range_rings()
        
        # Dictionary to store scatter plot items for each track
        self.track_plots: Dict[int, pg.ScatterPlotItem] = {}
        
        layout.addWidget(self.plot_widget)
        
    def _add_range_rings(self):
        """Add circular range rings to the display"""
        pen = pg.mkPen(color='#3a3a3a', width=1, style=Qt.PenStyle.DashLine)
        
        for range_m in [500, 1000, 1500, 2000]:
            circle = pg.QtWidgets.QGraphicsEllipseItem(
                -range_m, -range_m, 2*range_m, 2*range_m
            )
            circle.setPen(pen)
            self.plot_widget.addItem(circle)
            
            # Add range label
            text = pg.TextItem(f'{range_m}m', color='#5a5a5a', anchor=(0.5, 0.5))
            text.setPos(0, range_m)
            self.plot_widget.addItem(text)
    
    def update_track(self, track: Track):
        """Update or add a track to the display"""
        self.tracks[track.id] = track
        self._redraw_tracks()
    
    def remove_track(self, track_id: int):
        """Remove a track from the display"""
        if track_id in self.tracks:
            del self.tracks[track_id]
            if track_id in self.track_plots:
                self.plot_widget.removeItem(self.track_plots[track_id])
                del self.track_plots[track_id]
    
    def _redraw_tracks(self):
        """Redraw all tracks on the scope"""
        # Clear old plots
        for plot_item in self.track_plots.values():
            self.plot_widget.removeItem(plot_item)
        self.track_plots.clear()
        
        # Draw each track
        for track_id, track in self.tracks.items():
            # Convert polar to Cartesian (azimuth is clockwise from North)
            azimuth_rad = np.radians(track.azimuth)
            x = track.range_m * np.sin(azimuth_rad)  # East
            y = track.range_m * np.cos(azimuth_rad)  # North
            
            # Color based on target type
            color = self._get_track_color(track)
            size = 12 if track.source.value == "FUSED" else 8
            
            # Create scatter plot for this track
            scatter = pg.ScatterPlotItem(
                [x], [y],
                size=size,
                pen=pg.mkPen(color=color, width=2),
                brush=pg.mkBrush(color=color),
                symbol='o'
            )
            
            self.plot_widget.addItem(scatter)
            self.track_plots[track_id] = scatter
            
            # Add track ID label
            text = pg.TextItem(
                f'T{track_id}',
                color=color,
                anchor=(0.5, 1.5)
            )
            text.setPos(x, y)
            self.plot_widget.addItem(text)
    
    def _get_track_color(self, track: Track) -> str:
        """Get color for track based on type and source"""
        # Handle both enum and string values (due to use_enum_values=True)
        track_type = track.type if isinstance(track.type, str) else track.type.value
        track_source = track.source if isinstance(track.source, str) else track.source.value
        
        if track_type == "DRONE":
            return '#ff0000'  # Red for drones
        elif track_type == "BIRD":
            return '#00aaff'  # Blue for birds
        elif track_source == "FUSED":
            return '#ff00ff'  # Magenta for fused tracks
        else:
            return '#ffaa00'  # Orange for unknown
    
    def clear(self):
        """Clear all tracks from display"""
        self.tracks.clear()
        for plot_item in self.track_plots.values():
            self.plot_widget.removeItem(plot_item)
        self.track_plots.clear()
