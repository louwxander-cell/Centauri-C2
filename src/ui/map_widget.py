"""
Offline Map Widget
Displays cached map tiles with track overlays
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QRect, QTimer, pyqtSlot
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QFont, QPolygon
from pathlib import Path
import math
from typing import Dict, Optional
from ..core.datamodels import Track, GeoPosition
from .styles_modern import COLORS, FONTS, get_track_color


class OfflineMapWidget(QWidget):
    """
    Offline map widget using cached tiles.
    
    Features:
    - Displays cached OSM tiles
    - Shows ownship position
    - Displays tracks (drone + pilot positions)
    - Pan and zoom
    - Vehicle-relative overlay
    """
    
    def __init__(self, cache_dir: str = "map_cache", 
                 center_lat: float = -25.841105, 
                 center_lon: float = 28.180340):
        super().__init__()
        
        self.cache_dir = Path(cache_dir)
        
        # Map state
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.zoom = 13  # Default zoom level
        self.tile_size = 256  # OSM tile size in pixels
        
        # Ownship
        self.ownship_lat = center_lat
        self.ownship_lon = center_lon
        self.ownship_heading = 0.0
        
        # Tracks
        self.tracks: Dict[int, Track] = {}
        
        # Tile cache
        self.tile_cache: Dict[tuple, QPixmap] = {}
        
        # Pan offset
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        
        # Mouse drag
        self.last_mouse_pos = None
        
        # Setup
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # 10 Hz
    
    def set_center(self, lat: float, lon: float):
        """Set map center"""
        self.center_lat = lat
        self.center_lon = lon
        self.update()
    
    def set_ownship(self, lat: float, lon: float, heading: float = 0.0):
        """Set ownship position"""
        self.ownship_lat = lat
        self.ownship_lon = lon
        self.ownship_heading = heading
        
        # Center map on ownship
        self.center_lat = lat
        self.center_lon = lon
        self.update()
    
    def update_track(self, track: Track):
        """Update or add a track"""
        self.tracks[track.id] = track
    
    def remove_track(self, track_id: int):
        """Remove a track"""
        if track_id in self.tracks:
            del self.tracks[track_id]
    
    def lat_lon_to_tile(self, lat: float, lon: float) -> tuple:
        """Convert lat/lon to tile coordinates"""
        lat_rad = math.radians(lat)
        n = 2.0 ** self.zoom
        
        tile_x = (lon + 180.0) / 360.0 * n
        tile_y = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n
        
        return (tile_x, tile_y)
    
    def tile_to_lat_lon(self, tile_x: float, tile_y: float) -> tuple:
        """Convert tile coordinates to lat/lon"""
        n = 2.0 ** self.zoom
        
        lon = tile_x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
        lat = math.degrees(lat_rad)
        
        return (lat, lon)
    
    def lat_lon_to_screen(self, lat: float, lon: float) -> QPoint:
        """Convert lat/lon to screen coordinates"""
        # Convert to tile coordinates
        tile_x, tile_y = self.lat_lon_to_tile(lat, lon)
        
        # Get center tile coordinates
        center_tile_x, center_tile_y = self.lat_lon_to_tile(self.center_lat, self.center_lon)
        
        # Calculate pixel offset from center
        pixel_x = (tile_x - center_tile_x) * self.tile_size
        pixel_y = (tile_y - center_tile_y) * self.tile_size
        
        # Add widget center and pan offset
        screen_x = self.width() / 2 + pixel_x + self.pan_offset_x
        screen_y = self.height() / 2 + pixel_y + self.pan_offset_y
        
        return QPoint(int(screen_x), int(screen_y))
    
    def load_tile(self, zoom: int, tile_x: int, tile_y: int) -> Optional[QPixmap]:
        """Load a tile from cache"""
        key = (zoom, tile_x, tile_y)
        
        # Check cache
        if key in self.tile_cache:
            return self.tile_cache[key]
        
        # Load from disk
        tile_path = self.cache_dir / str(zoom) / str(tile_x) / f"{tile_y}.png"
        
        if tile_path.exists():
            pixmap = QPixmap(str(tile_path))
            self.tile_cache[key] = pixmap
            return pixmap
        
        return None
    
    def paintEvent(self, event):
        """Paint the map"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor(COLORS['bg_panel']))
        
        # Draw tiles
        self._draw_tiles(painter)
        
        # Draw tracks
        self._draw_tracks(painter)
        
        # Draw ownship
        self._draw_ownship(painter)
        
        # Draw info overlay
        self._draw_info(painter)
    
    def _draw_tiles(self, painter: QPainter):
        """Draw map tiles"""
        # Get center tile
        center_tile_x, center_tile_y = self.lat_lon_to_tile(self.center_lat, self.center_lon)
        center_tile_x_int = int(center_tile_x)
        center_tile_y_int = int(center_tile_y)
        
        # Calculate how many tiles we need to cover the widget
        tiles_x = math.ceil(self.width() / self.tile_size) + 2
        tiles_y = math.ceil(self.height() / self.tile_size) + 2
        
        # Draw tiles
        for dx in range(-tiles_x // 2, tiles_x // 2 + 1):
            for dy in range(-tiles_y // 2, tiles_y // 2 + 1):
                tile_x = center_tile_x_int + dx
                tile_y = center_tile_y_int + dy
                
                # Load tile
                pixmap = self.load_tile(self.zoom, tile_x, tile_y)
                
                if pixmap:
                    # Calculate screen position
                    pixel_offset_x = (tile_x - center_tile_x) * self.tile_size
                    pixel_offset_y = (tile_y - center_tile_y) * self.tile_size
                    
                    screen_x = self.width() / 2 + pixel_offset_x + self.pan_offset_x
                    screen_y = self.height() / 2 + pixel_offset_y + self.pan_offset_y
                    
                    painter.drawPixmap(int(screen_x), int(screen_y), pixmap)
                else:
                    # Draw placeholder for missing tile
                    screen_x = self.width() / 2 + (tile_x - center_tile_x) * self.tile_size + self.pan_offset_x
                    screen_y = self.height() / 2 + (tile_y - center_tile_y) * self.tile_size + self.pan_offset_y
                    
                    painter.fillRect(
                        int(screen_x), int(screen_y), 
                        self.tile_size, self.tile_size,
                        QColor(COLORS['bg_secondary'])
                    )
                    painter.setPen(QPen(QColor(COLORS['border_dim']), 1))
                    painter.drawRect(
                        int(screen_x), int(screen_y),
                        self.tile_size, self.tile_size
                    )
    
    def _draw_ownship(self, painter: QPainter):
        """Draw ownship position"""
        pos = self.lat_lon_to_screen(self.ownship_lat, self.ownship_lon)
        
        # Draw circle
        painter.setPen(QPen(QColor(COLORS['accent_cyan']), 3))
        painter.setBrush(QBrush(QColor(COLORS['accent_cyan'])))
        painter.drawEllipse(pos, 8, 8)
        
        # Draw heading indicator
        heading_rad = math.radians(self.ownship_heading)
        end_x = pos.x() + 30 * math.sin(heading_rad)
        end_y = pos.y() - 30 * math.cos(heading_rad)
        
        painter.setPen(QPen(QColor(COLORS['accent_cyan']), 3))
        painter.drawLine(pos, QPoint(int(end_x), int(end_y)))
        
        # Draw label
        painter.setPen(QPen(QColor(COLORS['text_primary']), 1))
        painter.setFont(QFont(FONTS['caps'], 10))
        painter.drawText(pos.x() + 15, pos.y() - 10, "OWNSHIP")
    
    def _draw_tracks(self, painter: QPainter):
        """Draw tracks on map"""
        for track_id, track in self.tracks.items():
            # For now, we need to convert vehicle-relative Az/El/Range to lat/lon
            # This requires ownship position
            # Simplified: just show tracks near ownship for demonstration
            
            # Calculate approximate lat/lon from Az/Range
            # This is a simplified calculation
            bearing_rad = math.radians(track.azimuth + self.ownship_heading)
            range_km = track.range_m / 1000.0
            
            # Approximate offset (1 degree ≈ 111 km)
            lat_offset = (range_km / 111.0) * math.cos(bearing_rad)
            lon_offset = (range_km / (111.0 * math.cos(math.radians(self.ownship_lat)))) * math.sin(bearing_rad)
            
            track_lat = self.ownship_lat + lat_offset
            track_lon = self.ownship_lon + lon_offset
            
            # Draw track
            pos = self.lat_lon_to_screen(track_lat, track_lon)
            
            color = get_track_color(track.type)
            painter.setPen(QPen(QColor(color), 2))
            painter.setBrush(QBrush(QColor(color)))
            
            # Draw triangle for drone
            size = 10
            points = QPolygon([
                QPoint(pos.x(), pos.y() - size),
                QPoint(pos.x() - size, pos.y() + size),
                QPoint(pos.x() + size, pos.y() + size)
            ])
            painter.drawPolygon(points)
            
            # Draw label
            painter.setPen(QPen(QColor(COLORS['text_primary']), 1))
            painter.setFont(QFont(FONTS['mono'], 8))
            painter.drawText(pos.x() + 15, pos.y(), f"ID:{track.id}")
            
            # Draw pilot position if available
            if track.pilot_latitude and track.pilot_longitude:
                pilot_pos = self.lat_lon_to_screen(track.pilot_latitude, track.pilot_longitude)
                
                # Draw star for pilot
                painter.setPen(QPen(QColor(COLORS['accent_yellow']), 2))
                painter.setBrush(QBrush(QColor(COLORS['accent_yellow'])))
                painter.drawEllipse(pilot_pos, 6, 6)
                
                # Draw line from drone to pilot
                painter.setPen(QPen(QColor(COLORS['accent_yellow']), 1, Qt.PenStyle.DashLine))
                painter.drawLine(pos, pilot_pos)
                
                # Label
                painter.setPen(QPen(QColor(COLORS['text_primary']), 1))
                painter.setFont(QFont(FONTS['mono'], 8))
                painter.drawText(pilot_pos.x() + 10, pilot_pos.y(), "PILOT")
    
    def _draw_info(self, painter: QPainter):
        """Draw info overlay"""
        # Draw zoom level
        painter.setPen(QPen(QColor(COLORS['text_secondary']), 1))
        painter.setFont(QFont(FONTS['mono'], 10))
        painter.drawText(10, 20, f"Zoom: {self.zoom}")
        
        # Draw coordinates
        painter.drawText(10, 40, f"Center: {self.center_lat:.6f}, {self.center_lon:.6f}")
        
        # Draw scale bar (approximate)
        scale_km = (156543.03392 * math.cos(math.radians(self.center_lat)) / (2 ** self.zoom)) / 1000
        painter.drawText(10, 60, f"Scale: ~{scale_km:.1f} km/tile")
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        
        if delta > 0 and self.zoom < 18:
            self.zoom += 1
        elif delta < 0 and self.zoom > 1:
            self.zoom -= 1
        
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press for panning"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for panning"""
        if self.last_mouse_pos and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.pos() - self.last_mouse_pos
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = None
