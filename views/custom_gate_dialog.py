from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QGridLayout, QMessageBox,
                             QComboBox, QGroupBox, QScrollArea, QWidget)
from PyQt6.QtCore import Qt
import numpy as np


class CustomGateDialog(QDialog):
    """Dialog for entering custom unitary gate matrices."""
    
    def __init__(self, parent=None, num_qubits=1):
        super().__init__(parent)
        self.num_qubits = num_qubits
        self.matrix = None
        self.gate_name = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Create Custom Unitary Gate")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Gate name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Gate Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., U1, MyGate")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Number of qubits selector
        qubit_layout = QHBoxLayout()
        qubit_layout.addWidget(QLabel("Number of Qubits:"))
        self.qubit_selector = QComboBox()
        self.qubit_selector.addItems(["1 (Single Qubit)", "2 (Two Qubit)"])
        self.qubit_selector.setCurrentIndex(self.num_qubits - 1)
        self.qubit_selector.currentIndexChanged.connect(self.on_qubit_count_changed)
        qubit_layout.addWidget(self.qubit_selector)
        layout.addLayout(qubit_layout)
        
        # Scroll area for matrix entries
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        self.matrix_widget = QWidget()
        self.matrix_layout = QVBoxLayout(self.matrix_widget)
        scroll.setWidget(self.matrix_widget)
        layout.addWidget(scroll)
        
        # Preset buttons
        preset_group = QGroupBox("Common Presets")
        preset_layout = QHBoxLayout()
        
        self.preset_1qubit = QComboBox()
        self.preset_1qubit.addItem("Select 1-Qubit Preset...")
        self.preset_1qubit.addItem("Identity", "identity")
        self.preset_1qubit.addItem("Pauli-X (NOT)", "pauli_x")
        self.preset_1qubit.addItem("Pauli-Y", "pauli_y")
        self.preset_1qubit.addItem("Pauli-Z", "pauli_z")
        self.preset_1qubit.addItem("Hadamard", "hadamard")
        self.preset_1qubit.addItem("Phase (S)", "phase")
        self.preset_1qubit.addItem("π/8 (T)", "t_gate")
        self.preset_1qubit.addItem("RX(π/2)", "rx_90")
        self.preset_1qubit.addItem("RY(π/2)", "ry_90")
        self.preset_1qubit.addItem("RZ(π/2)", "rz_90")
        self.preset_1qubit.currentIndexChanged.connect(self.apply_preset)
        preset_layout.addWidget(self.preset_1qubit)
        
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group)
        
        # Validation info
        info_label = QLabel(
            "Enter complex numbers in format: a+bj or a-bj\n"
            "Examples: 1, 0, 1+0j, 0.707-0.707j, 1j\n"
            "Matrix must be unitary (U†U = I)"
        )
        info_label.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        validate_btn = QPushButton("Validate Matrix")
        validate_btn.clicked.connect(self.validate_matrix)
        button_layout.addWidget(validate_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Create Gate")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.create_gate)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Create initial matrix inputs
        self.create_matrix_inputs()
    
    def on_qubit_count_changed(self, index):
        """Handle qubit count change."""
        self.num_qubits = index + 1
        self.create_matrix_inputs()
    
    def create_matrix_inputs(self):
        """Create input fields for matrix entries."""
        # Clear existing inputs
        while self.matrix_layout.count():
            item = self.matrix_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        dim = 2 ** self.num_qubits
        self.matrix_inputs = []
        
        # Title
        title = QLabel(f"Unitary Matrix ({dim}×{dim})")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.matrix_layout.addWidget(title)
        
        # Computational basis label
        basis_label = QLabel("Computational basis order: " + 
                            " → ".join([format(i, f'0{self.num_qubits}b') 
                                      for i in range(dim)]))
        basis_label.setStyleSheet("color: gray; font-size: 11px;")
        self.matrix_layout.addWidget(basis_label)
        
        # Matrix grid
        grid = QGridLayout()
        grid.setSpacing(5)
        
        # Column headers (output states)
        for j in range(dim):
            header = QLabel(format(j, f'0{self.num_qubits}b'))
            header.setStyleSheet("font-weight: bold; color: blue;")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(header, 0, j + 1)
        
        # Row headers (input states) and inputs
        for i in range(dim):
            # Row header
            header = QLabel(format(i, f'0{self.num_qubits}b'))
            header.setStyleSheet("font-weight: bold; color: blue;")
            header.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(header, i + 1, 0)
            
            row_inputs = []
            for j in range(dim):
                entry = QLineEdit()
                entry.setPlaceholderText("0")
                entry.setFixedWidth(100)
                entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Set default values for identity
                if i == j:
                    entry.setText("1")
                else:
                    entry.setText("0")
                
                grid.addWidget(entry, i + 1, j + 1)
                row_inputs.append(entry)
            
            self.matrix_inputs.append(row_inputs)
        
        self.matrix_layout.addLayout(grid)
        self.matrix_layout.addStretch()
    
    def apply_preset(self, index):
        """Apply a preset gate matrix."""
        if index == 0:
            return
        
        preset_id = self.preset_1qubit.itemData(index)
        
        presets = {
            "identity": np.eye(2),
            "pauli_x": np.array([[0, 1], [1, 0]]),
            "pauli_y": np.array([[0, -1j], [1j, 0]]),
            "pauli_z": np.array([[1, 0], [0, -1]]),
            "hadamard": np.array([[1, 1], [1, -1]]) / np.sqrt(2),
            "phase": np.array([[1, 0], [0, 1j]]),
            "t_gate": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]]),
            "rx_90": np.array([[1, -1j], [-1j, 1]]) / np.sqrt(2),
            "ry_90": np.array([[1, -1], [1, 1]]) / np.sqrt(2),
            "rz_90": np.array([[np.exp(-1j * np.pi / 4), 0], 
                               [0, np.exp(1j * np.pi / 4)]]),
        }
        
        if preset_id in presets:
            matrix = presets[preset_id]
            self.fill_matrix(matrix)
            # Reset preset selector
            self.preset_1qubit.setCurrentIndex(0)
    
    def fill_matrix(self, matrix):
        """Fill matrix input fields with values."""
        dim = matrix.shape[0]
        required_qubits = int(np.log2(dim))
        
        if required_qubits != self.num_qubits:
            # Switch to correct qubit count
            self.qubit_selector.setCurrentIndex(required_qubits - 1)
            self.num_qubits = required_qubits
            self.create_matrix_inputs()
        
        for i in range(dim):
            for j in range(dim):
                val = matrix[i, j]
                # Format complex number nicely
                if np.isreal(val):
                    text = f"{val.real:.6g}"
                elif np.isreal(val * 1j):  # Pure imaginary
                    text = f"{val.imag:.6g}j"
                else:
                    real_part = f"{val.real:.6g}" if val.real != 0 else ""
                    imag_part = f"{val.imag:+.6g}j" if val.imag != 0 else ""
                    text = real_part + imag_part
                
                self.matrix_inputs[i][j].setText(text)
    
    def get_matrix_from_inputs(self):
        """Parse matrix from input fields."""
        dim = 2 ** self.num_qubits
        matrix = np.zeros((dim, dim), dtype=complex)
        
        for i in range(dim):
            for j in range(dim):
                text = self.matrix_inputs[i][j].text().strip()
                try:
                    # Handle various complex number formats
                    text = text.replace('i', 'j')  # Allow 'i' for imaginary
                    if text == '':
                        matrix[i, j] = 0
                    elif 'j' in text or '+' in text or '-' in text[1:]:
                        matrix[i, j] = complex(text)
                    else:
                        matrix[i, j] = complex(float(text), 0)
                except ValueError as e:
                    QMessageBox.warning(self, "Invalid Input", 
                                       f"Invalid value at [{i},{j}]: {text}\n"
                                       f"Use format: a+bj or a-bj")
                    return None
        
        return matrix
    
    def validate_matrix(self):
        """Check if matrix is unitary."""
        matrix = self.get_matrix_from_inputs()
        if matrix is None:
            return False
        
        dim = matrix.shape[0]
        
        # Check if unitary: U†U = I
        dagger_u = matrix.conj().T
        product = dagger_u @ matrix
        identity = np.eye(dim)
        
        # Check if product is close to identity
        is_unitary = np.allclose(product, identity)
        
        if is_unitary:
            # Show matrix properties
            det = np.linalg.det(matrix)
            msg = f"✓ Matrix is unitary!\n\n"
            msg += f"Determinant: {det:.6f}\n"
            msg += f"Dimension: {dim}×{dim}\n"
            msg += f"\nMatrix:\n"
            for i in range(dim):
                row_str = " ".join([f"{matrix[i,j]:10.4f}" for j in range(dim)])
                msg += f"|{row_str}|\n"
            
            QMessageBox.information(self, "Matrix Validation", msg)
            return True
        else:
            # Show error details
            deviation = np.max(np.abs(product - identity))
            msg = f"✗ Matrix is NOT unitary!\n\n"
            msg += f"Max deviation from identity: {deviation:.6f}\n"
            msg += f"U†U should equal I, but it doesn't.\n"
            msg += f"\nMake sure columns are orthonormal."
            
            QMessageBox.warning(self, "Matrix Validation", msg)
            return False
    
    def create_gate(self):
        """Create the custom gate."""
        # Validate name
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a gate name.")
            return
        
        # Validate matrix
        if not self.validate_matrix():
            return
        
        self.gate_name = name
        self.matrix = self.get_matrix_from_inputs()
        self.accept()
    
    def get_result(self):
        """Get the created gate information."""
        return {
            'name': self.gate_name,
            'matrix': self.matrix,
            'num_qubits': self.num_qubits
        }
