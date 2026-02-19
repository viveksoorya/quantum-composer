from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QPixmap
import numpy as np


class PhaseLegendWidget(QWidget):
    """Fixed legend showing phase angle color scheme."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 80)
        self.setToolTip("Phase angle color scheme: hue represents phase from 0 to 2π")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # Background
        painter.fillRect(0, 0, w, h, QColor(30, 30, 30))
        
        # Title
        painter.setPen(QPen(QColor(200, 200, 200)))
        font = QFont("Sans", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(10, 15, "Phase Angle (radians)")
        
        # Draw color gradient bar
        bar_x = 10
        bar_y = 25
        bar_width = w - 20
        bar_height = 25
        
        # Create gradient with HSV colors (phase coloring)
        for i in range(bar_width):
            # Map position to phase angle 0 to 2π
            phase = (i / bar_width) * 2 * np.pi
            # Convert phase to hue (0 to 360 degrees)
            hue = int((phase / (2 * np.pi)) * 360)
            color = QColor.fromHsv(hue, 255, 255)
            painter.setPen(QPen(color, 1))
            painter.drawLine(bar_x + i, bar_y, bar_x + i, bar_y + bar_height)
        
        # Draw border around bar
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.setBrush(QBrush())  # No fill
        painter.drawRect(bar_x, bar_y, bar_width, bar_height)
        
        # Draw tick marks and labels
        painter.setPen(QPen(QColor(200, 200, 200)))
        font = QFont("Sans", 7)
        painter.setFont(font)
        
        tick_positions = [
            (0, "0"),
            (bar_width * 0.25, "π/2"),
            (bar_width * 0.5, "π"),
            (bar_width * 0.75, "3π/2"),
            (bar_width, "2π")
        ]
        
        for pos, label in tick_positions:
            x = bar_x + int(pos)
            # Tick mark
            painter.drawLine(x, bar_y + bar_height, x, bar_y + bar_height + 5)
            # Label
            text_width = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(x - text_width // 2, bar_y + bar_height + 18, label)
        
        painter.end()
