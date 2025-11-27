"""
Confidence Bar Delegate for Track Table
Renders confidence as a horizontal gradient bar with percentage text
"""

from PyQt6.QtWidgets import QStyledItemDelegate
from PyQt6.QtGui import QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRect, QRectF, QPointF


class ConfidenceDelegate(QStyledItemDelegate):
    """Custom delegate to render confidence as a gradient bar + percentage"""
    
    def paint(self, painter, option, index):
        """Paint confidence bar and percentage text"""
        value = index.data(Qt.ItemDataRole.DisplayRole)
        
        # Convert to float (0.0 to 1.0)
        try:
            val = float(value)
        except (ValueError, TypeError):
            val = 0.0
        
        pct = max(0.0, min(1.0, val))
        
        # Calculate bar dimensions
        r = option.rect.adjusted(6, 10, -6, -10)
        bar_h = 8
        bar_w = max(40, r.width() - 60)
        bar_rect = QRect(r.left(), r.center().y() - bar_h//2, bar_w, bar_h)
        
        # Draw background bar
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 8))
        painter.drawRoundedRect(bar_rect, 4, 4)
        
        # Draw filled portion with gradient
        fill_w = int(bar_w * pct)
        if fill_w > 0:
            # Create gradient with QPointF (not QPoint)
            grad = QLinearGradient(QPointF(bar_rect.topLeft()), QPointF(bar_rect.topRight()))
            grad.setColorAt(0.0, QColor(242, 180, 110))  # Amber
            grad.setColorAt(0.5, QColor(56, 230, 224))   # Cyan
            grad.setColorAt(1.0, QColor(46, 224, 138))   # Green
            
            fill_rect = QRect(bar_rect.left(), bar_rect.top(), fill_w, bar_h)
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(fill_rect, 4, 4)
        
        # Draw percentage text
        pct_text = f"{int(pct*100)}%"
        painter.setPen(QColor(255, 255, 255, 210))
        painter.setFont(option.font)
        text_rect = QRect(r.right()-48, r.top()+bar_h+6, 48, 16)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, pct_text)
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """Return recommended size for confidence cell"""
        from PyQt6.QtCore import QSize
        return QSize(120, 36)
