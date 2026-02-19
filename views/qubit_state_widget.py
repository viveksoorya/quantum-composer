from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
import numpy as np


class QubitStateWidget(QWidget):
    """Inline visualization of a single qubit's state as a simplified Bloch sphere."""
    
    def __init__(self, qubit_idx, parent=None):
        super().__init__(parent)
        self.qubit_idx = qubit_idx
        self.bloch_x = 0.0
        self.bloch_y = 0.0
        self.bloch_z = 1.0
        self.setFixedSize(80, 80)
        self.setToolTip(f"Qubit {qubit_idx} state visualization - color shows phase, position shows state")
    
    def set_state(self, bloch_vector):
        """Update the Bloch sphere visualization with new state.
        
        Args:
            bloch_vector: Tuple (x, y, z) representing the Bloch vector
        """
        self.bloch_x, self.bloch_y, self.bloch_z = bloch_vector
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Widget dimensions
        w, h = self.width(), self.height()
        center_x, center_y = w // 2, h // 2
        radius = min(w, h) // 2 - 8
        
        # Draw sphere outline (circle) - don't fill since stylesheet handles background
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Draw axes
        painter.setPen(QPen(QColor(80, 80, 80), 1, Qt.PenStyle.DashLine))
        # Z-axis (vertical)
        painter.drawLine(center_x, center_y - radius, center_x, center_y + radius)
        # X-axis (horizontal)
        painter.drawLine(center_x - radius, center_y, center_x + radius, center_y)
        
        # Calculate projection of Bloch vector
        # Map 3D Bloch vector to 2D circle with perspective
        # x maps to horizontal, z affects vertical with perspective
        scale = radius * 0.85
        proj_x = center_x + self.bloch_x * scale
        proj_y = center_y - self.bloch_z * scale  # Negative because Y grows downward
        
        # Adjust for y-component (into/out of screen) by scaling the marker
        marker_size = max(4, 8 + int(self.bloch_y * 3))
        
        # Draw the state vector as a point
        # Calculate phase from x and y components
        phase = np.arctan2(self.bloch_y, self.bloch_x)  # Range: -π to π
        if phase < 0:
            phase += 2 * np.pi  # Convert to 0 to 2π range
        
        # Map phase to hue (0 to 360 degrees)
        # 0 = red, π/2 = yellow/green, π = cyan, 3π/2 = blue, 2π = red
        hue = int((phase / (2 * np.pi)) * 360)
        
        # Saturation based on how far from the poles (|Z| close to 1 means low saturation)
        # Maximum saturation at equator (Z=0), minimum at poles
        xy_magnitude = np.sqrt(self.bloch_x**2 + self.bloch_y**2)
        saturation = int(155 + 100 * xy_magnitude)  # 155-255 range
        
        color = QColor.fromHsv(hue % 360, saturation, 255)
        
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(int(proj_x - marker_size//2), int(proj_y - marker_size//2), 
                          marker_size, marker_size)
        
        # Draw a small indicator of the phase angle value
        phase_deg = int(np.degrees(phase))
        painter.setPen(QPen(QColor(150, 150, 150)))
        font_small = QFont("Sans", 6)
        painter.setFont(font_small)
        painter.drawText(2, h - 4, f"{phase_deg}°")
        
        # Draw label
        painter.setPen(QPen(QColor(200, 200, 200)))
        font = QFont("Sans", 7)
        painter.setFont(font)
        painter.drawText(2, 12, f"q[{self.qubit_idx}]")
        
        painter.end()
