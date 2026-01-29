from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QApplication
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag, QPainter, QColor, QPixmap, QFont, QFontMetrics

class DraggableButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("GateButton")
        self.gate_type = text

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.gate_type)
            drag.setMimeData(mime)

            # Create a semi-transparent rounded pixmap for the drag (IBM-like shadow)
            w, h = 50, 50
            pixmap = QPixmap(w, h)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            rect = pixmap.rect().adjusted(4, 4, -4, -4)
            painter.setBrush(QColor(20, 40, 120, 160))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            font = QFont("Sans", 10, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255, 220))
            fm = QFontMetrics(font)
            tx = (w - fm.horizontalAdvance(self.gate_type)) // 2
            ty = (h + fm.ascent() - fm.descent()) // 2
            painter.drawText(tx, ty, self.gate_type)
            painter.end()

            drag.setPixmap(pixmap)
            drag.setHotSpot(pixmap.rect().center())

            # Cursor: show copy cursor while dragging from palette
            QApplication.setOverrideCursor(Qt.CursorShape.DragCopyCursor)
            try:
                drag.exec(Qt.DropAction.CopyAction)
            finally:
                QApplication.restoreOverrideCursor()

class PaletteView(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        header = QLabel("Gates")
        header.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        main_layout.addWidget(header)

        # Scroll Area for many gates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # --- EXPANDED GATE LIST ---
        # Grouped by type for logic (visually just a list here)
        # Updated List
        gates = [
            'H', 'X', 'Y', 'Z', 
            'RX', 'RY', 'RZ', 'P', # Rotations
            'CX', 'SWAP', 'CZ'

        ]
        for g in gates:
            btn = DraggableButton(g)
            layout.addWidget(btn)
        
        layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
