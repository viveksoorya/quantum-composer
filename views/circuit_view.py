from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QMenu, QApplication, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPoint
from PyQt6.QtGui import QDrag, QAction, QPainter, QPen, QColor, QPixmap, QFont, QFontMetrics
from .styles import GATE_CSS
from .qubit_state_widget import QubitStateWidget
from .phase_legend_widget import PhaseLegendWidget
from .custom_gate_analyzer import CustomGateAnalyzer
import numpy as np

class DropLabel(QLabel):
    gate_placed = pyqtSignal(str, int, int)
    gate_removed = pyqtSignal(int, int)
    gate_repositioned = pyqtSignal(int, int, int, int)

    def __init__(self, qubit_idx, time_idx):
        super().__init__("")
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qubit_idx = qubit_idx
        self.time_idx = time_idx
        
        self.current_gate = None
        self.target_idx = None
        self.custom_matrix = None  # For custom gates

    # --- Interaction Logic ---
    def contextMenuEvent(self, event):
        if not self.current_gate or self.current_gate == "CONNECTOR": return
        menu = QMenu(self)
        delete_action = QAction("Delete", self)
        menu.addAction(delete_action)
        if menu.exec(event.globalPos()) == delete_action:
            self.clear_visual()
            self.gate_removed.emit(self.qubit_idx, self.time_idx)

    def mouseMoveEvent(self, e):
        if self.current_gate in ["CONNECTOR", "TARGET"]: return
        if e.buttons() == Qt.MouseButton.LeftButton and self.current_gate:
            drag = QDrag(self)
            mime = QMimeData()
            payload = f"MOVE:{self.current_gate}:{self.qubit_idx}:{self.time_idx}"
            mime.setText(payload)
            drag.setMimeData(mime)

            # Create a styled, semi-transparent pixmap for the drag (shadow-like)
            pixmap = QPixmap(self.width(), self.height())
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            rect = pixmap.rect().adjusted(4, 4, -4, -4)
            painter.setBrush(QColor(20, 40, 120, 160))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect, 8, 8)
            # Text
            font = QFont("Sans", 10, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255, 220))
            fm = QFontMetrics(font)
            tx = (pixmap.width() - fm.horizontalAdvance(self.current_gate)) // 2
            ty = (pixmap.height() + fm.ascent() - fm.descent()) // 2
            painter.drawText(tx, ty, self.current_gate)
            painter.end()

            drag.setPixmap(pixmap)
            drag.setHotSpot(self.rect().center())

            # Change cursor to indicate move
            QApplication.setOverrideCursor(Qt.CursorShape.ClosedHandCursor)
            try:
                drag.exec(Qt.DropAction.MoveAction)
            finally:
                QApplication.restoreOverrideCursor()

    def dragEnterEvent(self, event):
        if self.current_gate == "CONNECTOR": event.ignore(); return
        # Show a lightweight shadow/preview when dragging over this zone
        if event.mimeData().hasText():
            text = event.mimeData().text()
            # Parse MOVE payloads: "MOVE:NAME:old_q:old_t"
            if text.startswith("MOVE:"):
                _, gate_name, _, _ = text.split(":")
            else:
                gate_name = text
            self.show_shadow(gate_name)
            # change cursor based on action
            if text.startswith("MOVE:"):
                QApplication.setOverrideCursor(Qt.CursorShape.ClosedHandCursor)
            else:
                QApplication.setOverrideCursor(Qt.CursorShape.DragCopyCursor)
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if self.current_gate == "CONNECTOR": event.ignore(); return
        if event.mimeData().hasText():
            # keep the shadow updated (in case different gate types show different sizes)
            text = event.mimeData().text()
            if text.startswith("MOVE:"):
                _, gate_name, _, _ = text.split(":")
            else:
                gate_name = text
            self.show_shadow(gate_name)
            event.acceptProposedAction()

    def dropEvent(self, event):
        if self.current_gate == "CONNECTOR": event.ignore(); return
        data = event.mimeData().text()
        # Clear any preview and restore cursor
        self.clear_shadow()
        QApplication.restoreOverrideCursor()

        if data.startswith("MOVE:"):
            _, gate_name, old_q, old_t = data.split(":")
            old_q, old_t = int(old_q), int(old_t)
            # if moving within same position, ignore
            if old_q == self.qubit_idx and old_t == self.time_idx:
                event.ignore(); return

            # Emit reposition without aligning left
            self.gate_repositioned.emit(old_q, old_t, self.qubit_idx, self.time_idx)
        else:
            self.gate_placed.emit(data, self.qubit_idx, self.time_idx)
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        # Clear preview when drag leaves
        self.clear_shadow()
        QApplication.restoreOverrideCursor()
        event.accept()

    # --- Visual Logic ---
    
    def set_visual_gate(self, text, params=None, matrix=None):
        self.current_gate = text
        self.target_idx = None
        self.custom_matrix = matrix
        display_text = text
        style = GATE_CSS
        
        # Handle custom gates with meaningful icons
        if text == "U" and matrix is not None:
            properties = CustomGateAnalyzer.analyze_matrix(matrix)
            display_text = properties['icon']
            
            # Color-coded background based on gate type
            color = properties['color']
            style = f"""
                background-color: {color};
                color: white;
                border: 2px solid {color};
                border-radius: 6px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                font-size: 18px;
                min-width: 46px;
                min-height: 46px;
            """
            
            # Set tooltip with gate information
            tooltip = CustomGateAnalyzer.get_tooltip(properties)
            self.setToolTip(tooltip)
        elif params is not None:
            short_param = f"{float(params):.2f}"
            display_text = f"{text}\n{short_param}"
            style += "font-size: 11px;"
            
        self.setText(display_text)
        self.setStyleSheet(style)

    def set_visual_source(self, gate_type, target_idx, matrix=None):
        self.current_gate = gate_type
        self.target_idx = target_idx
        self.custom_matrix = matrix
        
        # Handle custom gate source (control qubit for 2-qubit custom gates)
        if gate_type == "U" and matrix is not None:
            properties = CustomGateAnalyzer.analyze_matrix(matrix)
            color = properties['color']
            
            # For custom gates, use a colored control dot
            style = f"""
                background-color: {color}; 
                border-radius: 8px; 
                min-width: 16px; min-height: 16px; 
                max-width: 16px; max-height: 16px;
                margin: 17px;
                border: 2px solid white;
            """
            
            tooltip = f"Custom {properties['qubit_count']}-qubit gate (control)\n{CustomGateAnalyzer.get_tooltip(properties)}"
            self.setToolTip(tooltip)
            self.setText("")
            self.setStyleSheet(style)
            return
        
        # Default: Control Dot (●)
        # Small, solid black circle centered in the box
        symbol = ""
        style = """
            background-color: #000000; 
            border-radius: 8px; 
            min-width: 16px; min-height: 16px; 
            max-width: 16px; max-height: 16px;
            margin: 17px; /* Centers the 16px dot in 50px box */
        """
        
        if gate_type == "SWAP":
            symbol = "✖"
            style = "background-color: transparent; color: #000000; font-size: 24px; font-weight: bold;"
            
        self.setText(symbol)
        self.setStyleSheet(style)

    def set_visual_target(self, gate_type, matrix=None):
        self.current_gate = "TARGET"
        self.target_idx = None
        self.custom_matrix = matrix
        
        # Handle custom gate target (for 2-qubit custom gates)
        if gate_type == "U" and matrix is not None:
            properties = CustomGateAnalyzer.analyze_matrix(matrix)
            color = properties['color']
            
            # For custom gates, use a colored circle with the gate icon
            symbol = properties['icon']
            style = f"""
                background-color: {color}; 
                border: 2px solid white;
                border-radius: 15px;
                color: white; 
                font-size: 18px; 
                font-weight: bold;
                min-width: 30px; min-height: 30px;
                max-width: 30px; max-height: 30px;
            """
            
            tooltip = f"Custom {properties['qubit_count']}-qubit gate (target)\n{CustomGateAnalyzer.get_tooltip(properties)}"
            self.setToolTip(tooltip)
            self.setText(symbol)
            self.setStyleSheet(style)
            return
        
        # Default: CNOT Target (⊕)
        # Open circle with Cross. 
        # We achieve this with a Border (Circle) and Text (+)
        symbol = "+"
        style = """
            background-color: #FFFFFF; 
            border: 2px solid #000000; 
            border-radius: 15px; /* Makes it a 30px circle */
            color: #000000; 
            font-size: 24px; 
            font-weight: bold;
            min-width: 30px; min-height: 30px;
            max-width: 30px; max-height: 30px;
        """
        
        if gate_type == "CZ":
            # CZ Target is also a Dot (●)
            symbol = ""
            style = """
                background-color: #000000; 
                border-radius: 8px; 
                min-width: 16px; min-height: 16px; 
                max-width: 16px; max-height: 16px;
                margin: 17px;
            """
        elif gate_type == "SWAP":
            symbol = "✖"
            style = "background-color: transparent; color: #000000; font-size: 24px; font-weight: bold;"

        self.setText(symbol)
        self.setStyleSheet(style)

    def set_visual_connector(self):
        self.current_gate = "CONNECTOR"
        self.target_idx = None
        self.setText("")
        self.setStyleSheet("background-color: transparent; border: none;")

    def clear_visual(self):
        self.current_gate = None
        self.target_idx = None
        self.custom_matrix = None
        self.setText("")
        self.setStyleSheet("border: none; background-color: transparent;")
        self.setToolTip("") 

    # --- Preview / Shadow helpers ---
    def show_shadow(self, gate_text):
        # Don't overwrite an actual gate visual; show a lightweight translucent preview instead
        if self.current_gate is not None: return
        style = f"background-color: rgba(20,40,120,0.45); color: white; border-radius: 8px; font-weight: bold;"
        self.setText(gate_text)
        self.setStyleSheet(style)

    def clear_shadow(self):
        # Only clear if it is a preview (i.e., current_gate is None)
        if self.current_gate is None:
            self.setText("")
            self.setStyleSheet("border: none; background-color: transparent;")


class CircuitView(QWidget):
    gate_dropped = pyqtSignal(str, int, int)
    gate_deleted = pyqtSignal(int, int)
    gate_moved = pyqtSignal(int, int, int, int)

    def __init__(self, num_qubits=3, num_steps=10):
        super().__init__()
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.grid.setSpacing(0)
        self.num_qubits = num_qubits
        self.num_steps = num_steps
        self.drop_zones = {}
        self.qubit_state_widgets = {}  # Store inline visualization widgets
        self.setup_grid()

        # Add a button to display the circuit array
        self.display_button = QPushButton("Show Circuit Array", self)
        self.display_button.clicked.connect(self.show_circuit_array)
        self.grid.addWidget(self.display_button, num_qubits, 0, 1, num_steps + 1)

        # Add a button to display the visual state of the circuit (drop_zones)
        self.display_visual_button = QPushButton("Show Visual State", self)
        self.display_visual_button.clicked.connect(self.show_visual_state)
        self.grid.addWidget(self.display_visual_button, num_qubits + 1, 0, 1, num_steps + 1)

        # Add phase color scheme legend at the bottom
        self.phase_legend = PhaseLegendWidget(self)
        self.grid.addWidget(self.phase_legend, num_qubits + 2, 0, 1, num_steps + 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def setup_grid(self):
        for q in range(self.num_qubits):
            lbl = QLabel(f"q[{q}]")
            lbl.setStyleSheet("color: #555; font-weight: bold; margin-right: 10px;")
            self.grid.addWidget(lbl, q, 0)
            
            wire = QFrame()
            wire.setObjectName("CircuitLine")
            self.grid.addWidget(wire, q, 1, 1, self.num_steps, Qt.AlignmentFlag.AlignVCenter)

            for t in range(self.num_steps):
                zone = DropLabel(q, t)
                zone.setFixedSize(50, 50)
                zone.gate_placed.connect(self.gate_dropped)
                zone.gate_removed.connect(self.gate_deleted)
                zone.gate_repositioned.connect(self.gate_moved)
                self.grid.addWidget(zone, q, t+1, Qt.AlignmentFlag.AlignCenter)
                self.drop_zones[(q, t)] = zone
            
            # Add inline qubit state visualization at the end of the line
            state_widget = QubitStateWidget(q)
            self.grid.addWidget(state_widget, q, self.num_steps + 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.qubit_state_widgets[q] = state_widget

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Black/Dark Gray line for CNOT connector
        pen = QPen(QColor("#333333"))
        pen.setWidth(2)
        painter.setPen(pen)

        for (q, t), zone in self.drop_zones.items():
            if zone.target_idx is not None:
                target_zone = self.drop_zones.get((zone.target_idx, t))
                if target_zone:
                    p1 = zone.mapTo(self, zone.rect().center())
                    p2 = target_zone.mapTo(self, target_zone.rect().center())
                    painter.drawLine(p1, p2)

    def clear_grid(self):
        for zone in self.drop_zones.values():
            zone.clear_visual()
        self.update()

    def place_gate_visual(self, gate_text, q, t, target_index=None, params=None, matrix=None):
        if (q, t) not in self.drop_zones: return
        zone = self.drop_zones[(q, t)]
        if target_index is not None:
            zone.set_visual_source(gate_text, target_index, matrix)
            if (target_index, t) in self.drop_zones:
                self.drop_zones[(target_index, t)].set_visual_target(gate_text, matrix)
        else:
            zone.set_visual_gate(gate_text, params, matrix)
        self.update()

    def place_connector_visual(self, q, t):
        if (q, t) in self.drop_zones:
            self.drop_zones[(q, t)].set_visual_connector()

    def show_circuit_array(self):
        circuit_array = []
        for (q, t), zone in self.drop_zones.items():
            if zone.current_gate:
                circuit_array.append({
                    'gate': zone.current_gate,
                    'qubit': q,
                    'position': t
                })
        # Display the circuit array in a QMessageBox
        QMessageBox.information(self, "Circuit Array", str(circuit_array))

    def show_visual_state(self):
        visual_state = []
        for (q, t), zone in self.drop_zones.items():
            if zone.current_gate:
                visual_state.append({
                    'gate': zone.current_gate,
                    'qubit': q,
                    'position': t
                })
        QMessageBox.information(self, "Visual State", str(visual_state))
