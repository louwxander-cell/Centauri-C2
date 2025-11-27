"""
Enhanced Radar Widget with Advanced Visualizations
- Halo glow around markers
- Velocity vectors
- Pulsing ring for selected target
- Smooth animations
- Vignette background
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QPainterPath, QFont
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
import math


class RadarWidgetEnhanced(QWidget):
    """
    Enhanced radar display with threat halos, velocity vectors, and pulsing selection
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracks = {}  # dict: id -> dict(range_m, az_deg, speed_mps, heading_deg, status)
        self.selected_id = None
        self.max_range = 3000  # meters
        self.pulse_phase = 0.0
        
        # Pulse animation timer (~25Hz for smooth animation)
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._on_pulse)
        self.pulse_timer.start(40)
        
        # Set minimum size
        self.setMinimumSize(400, 400)
        
        # Status color map
        self.color_map = {
            'CRITICAL': QColor(255, 59, 59),    # #FF3B3B
            'HIGH': QColor(244, 140, 6),        # #F48C06
            'MED': QColor(242, 180, 110),       # #F2B46E
            'LOW': QColor(56, 230, 224),        # #38E6E0
            'FRIENDLY': QColor(46, 224, 138),   # #2CE08A
        }
    
    def _on_pulse(self):
        """Update pulse animation phase"""
        self.pulse_phase = (self.pulse_phase + 0.04) % (2 * math.pi)
        self.update()
    
    def set_tracks(self, tracks):
        """Update track data"""
        self.tracks = tracks
        self.update()
    
    def set_selected(self, track_id):
        """Set selected track for pulsing ring"""
        self.selected_id = track_id
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event with advanced rendering"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        cx, cy = w // 2, h // 2
        radius = min(cx, cy) - 40
        
        # Background with vignette (subtle)
        grad = QRadialGradient(cx, cy, radius)
        grad.setColorAt(0.0, QColor(15, 17, 19, 255))
        grad.setColorAt(1.0, QColor(15, 17, 19, 220))
        painter.fillRect(0, 0, w, h, grad)
        
        # Draw range rings (solid, progressive opacity)
        self._draw_range_rings(painter, cx, cy, radius)
        
        # Draw bearing lines
        self._draw_bearing_lines(painter, cx, cy, radius)
        
        # Draw tracks with halos and velocity vectors
        self._draw_tracks(painter, cx, cy, radius)
        
        # Draw pulsing ring for selected target
        if self.selected_id and self.selected_id in self.tracks:
            self._draw_selected_ring(painter, cx, cy, radius)
        
        painter.end()
    
    def _draw_range_rings(self, painter, cx, cy, radius):
        """Draw concentric range rings with progressive opacity"""
        ring_steps = 6
        for i in range(1, ring_steps + 1):
            r = radius * i / ring_steps
            # Inner rings slightly brighter
            alpha = 40 if i > (ring_steps - 2) else 26
            pen = QPen(QColor(255, 255, 255, alpha))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), r, r)
            
            # Draw range label
            if i % 2 == 0:  # Every other ring
                range_m = int(self.max_range * i / ring_steps)
                painter.setPen(QColor(255, 255, 255, 60))
                font = QFont("SF Mono", 8)
                painter.setFont(font)
                painter.drawText(int(cx + 5), int(cy - r + 15), f"{range_m}m")
    
    def _draw_bearing_lines(self, painter, cx, cy, radius):
        """Draw cardinal direction lines"""
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1, Qt.PenStyle.DotLine))
        
        # Draw main cardinal lines
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            x = radius * math.cos(rad)
            y = radius * math.sin(rad)
            painter.drawLine(int(cx), int(cy), int(cx + x), int(cy - y))
            
            # Draw direction label
            if angle == 0:
                label = "N"
            elif angle == 90:
                label = "E"
            elif angle == 180:
                label = "S"
            else:
                label = "W"
            
            label_dist = radius * 0.92
            lx = cx + label_dist * math.cos(rad)
            ly = cy - label_dist * math.sin(rad)
            
            painter.setPen(QColor(61, 218, 215, 180))
            font = QFont("Inter", 10, QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(int(lx - 10), int(ly + 5), label)
    
    def _draw_tracks(self, painter, cx, cy, radius):
        """Draw all tracks with halos, markers, and velocity vectors"""
        for tid, track in self.tracks.items():
            range_m = track.get('range_m', 0)
            az_deg = track.get('az_deg', 0)
            status = track.get('status', 'MED')
            speed_mps = track.get('speed_mps', 0)
            heading_deg = track.get('heading_deg', 0)
            
            # Convert polar to cartesian
            r_pix = (range_m / self.max_range) * radius
            az_rad = math.radians(-az_deg + 90)  # Convert to screen coords
            x = cx + r_pix * math.cos(az_rad)
            y = cy - r_pix * math.sin(az_rad)
            
            # Get color for status
            color = self.color_map.get(status, QColor(56, 230, 224))
            
            # Draw halo glow (larger for higher threats)
            halo_r = 16 if status == 'CRITICAL' else (12 if status == 'HIGH' else 8)
            halo_color = QColor(color.red(), color.green(), color.blue(), 80)
            painter.setBrush(halo_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(x, y), halo_r, halo_r)
            
            # Draw triangle marker (rotated by heading)
            self._draw_triangle_marker(painter, x, y, heading_deg, color)
            
            # Draw velocity vector
            if speed_mps > 0.1:
                self._draw_velocity_vector(painter, x, y, az_rad, speed_mps, color)
            
            # Draw label capsule
            self._draw_label_capsule(painter, x, y, tid, status)
    
    def _draw_triangle_marker(self, painter, x, y, heading_deg, color):
        """Draw rotated triangle marker"""
        painter.save()
        painter.translate(x, y)
        
        heading_rad = math.radians(-heading_deg + 90)
        painter.rotate(-math.degrees(heading_rad))
        
        # Triangle path
        tri = QPainterPath()
        w_tri = 12
        h_tri = 14
        tri.moveTo(0, -h_tri / 2)
        tri.lineTo(w_tri / 2, h_tri / 2)
        tri.lineTo(-w_tri / 2, h_tri / 2)
        tri.closeSubpath()
        
        painter.setBrush(color)
        painter.setPen(QPen(QColor(0, 0, 0, 120), 1))
        painter.drawPath(tri)
        
        painter.restore()
    
    def _draw_velocity_vector(self, painter, x, y, az_rad, speed_mps, color):
        """Draw velocity vector line"""
        vec_len = min(40, speed_mps * 2.0)
        proj_x = x + vec_len * math.cos(az_rad)
        proj_y = y - vec_len * math.sin(az_rad)
        
        pen = QPen(QColor(color.red(), color.green(), color.blue(), 200), 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(x, y), QPointF(proj_x, proj_y))
    
    def _draw_label_capsule(self, painter, x, y, tid, status):
        """Draw translucent label capsule"""
        label_text = f"ID:{tid}  {status}"
        font = QFont("Inter", 9)
        painter.setFont(font)
        fm = painter.fontMetrics()
        label_w = fm.horizontalAdvance(label_text) + 14
        label_h = fm.height() + 6
        
        # Position offset from marker
        lx = x + 16
        ly = y - label_h / 2
        
        # Draw capsule background
        painter.setBrush(QColor(21, 24, 26, 210))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.drawRoundedRect(QRectF(lx, ly, label_w, label_h), 6, 6)
        
        # Draw text
        painter.setPen(QPen(QColor(255, 255, 255, 220)))
        painter.drawText(QRectF(lx + 6, ly + 3, label_w, label_h), label_text)
    
    def _draw_selected_ring(self, painter, cx, cy, radius):
        """Draw pulsing ring around selected target"""
        sel = self.tracks[self.selected_id]
        range_m = sel.get('range_m', 0)
        az_deg = sel.get('az_deg', 0)
        
        # Convert to screen coordinates
        r_pix = (range_m / self.max_range) * radius
        az_rad = math.radians(-az_deg + 90)
        sx = cx + r_pix * math.cos(az_rad)
        sy = cy - r_pix * math.sin(az_rad)
        
        # Pulsing animation (0..1)
        phase = 0.5 + 0.5 * math.sin(self.pulse_phase)
        ring_r = 20 + 18 * phase
        alpha = int(140 * (1.0 - 0.5 * phase))
        
        # Draw pulsing ring
        pen = QPen(QColor(255, 59, 59, alpha), 2)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(sx, sy), ring_r, ring_r)
