from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QInputDialog, QPushButton, QMessageBox
from models.circuit_model import CircuitModel
from models.code_generator import QiskitCodeGenerator
from models.code_parser import QiskitCodeParser
import numpy as np

class MainController:
    def __init__(self, view):
        self.view = view
        self.model = CircuitModel(num_qubits=3)
        self.code_gen = QiskitCodeGenerator()
        self.parser = QiskitCodeParser()
        self.is_internal_update = False

        # Add a button to display the logical state of the circuit
        self.view.circuit_view.display_model_button = QPushButton("Show Logical State", self.view.circuit_view)
        self.view.circuit_view.display_model_button.clicked.connect(self.show_logical_state)
        self.view.circuit_view.grid.addWidget(self.view.circuit_view.display_model_button, self.model.num_qubits + 1, 0, 1, self.view.circuit_view.num_steps + 1)

        # --- View Signals ---
        self.view.circuit_view.gate_dropped.connect(self.on_gate_dropped)
        self.view.circuit_view.gate_deleted.connect(self.on_gate_deleted)
        self.view.circuit_view.gate_moved.connect(self.on_gate_moved)
        
        # --- Toolbar Signals ---
        self.view.run_action.triggered.connect(self.run_simulation)
        
        # --- File Menu Signals ---
        self.view.save_action.triggered.connect(self.save_project)
        self.view.load_action.triggered.connect(self.load_project)
        
        # --- Export Signals ---
        self.view.export_image_action.triggered.connect(self.export_image)
        self.view.export_code_action.triggered.connect(self.export_code)

        # --- Editor Signals (Debounced) ---
        self.debounce_timer = QTimer()
        self.debounce_timer.setInterval(600)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_code_parsed)
        
        self.view.code_view.editor.textChanged.connect(self.on_text_edited)

        # Initial Render
        self.update_full_ui()

    # --- 1. Export Implementations ---
    def export_image(self):
        """Saves the visual grid as a PNG file."""
        fname = self.view.show_save_dialog("Export Image", "PNG Files (*.png)")
        if fname:
            # Grab the CircuitView specifically
            pixmap = self.view.circuit_view.grab()
            pixmap.save(fname)
            print(f"Image saved to {fname}")

    def export_code(self):
        """Saves the current Qiskit code as a .py file."""
        fname = self.view.show_save_dialog("Export Python Code", "Python Files (*.py)")
        if fname:
            code = self.view.code_view.get_code()
            with open(fname, 'w') as f:
                f.write(code)
            print(f"Code saved to {fname}")

    # --- 2. Gate Logic ---

    # Helper to check if the path between q_start and q_end is clear at time t
    def is_path_clear(self, q1, q2, time_index):
        start = min(q1, q2)
        end = max(q1, q2)
        
        # Check existing operations in the model
        ops = self.model.get_operations()
        for op in ops:
            # If an operation exists at this time index
            if op['index'] == time_index:
                # If it's on any qubit between (start, end) OR on the start/end qubits themselves
                # Note: We allow replacing the exact gate if we are dropping ON it, 
                # but we shouldn't allow dropping if there is something "in the way"
                q = op['qubit']
                t = op.get('target')
                
                # Check simple collision (gate already exists on intermediate wire)
                if start < q < end:
                    return False
                
                # Check crossing lines collision (e.g., trying to place CNOT(0,2) when CNOT(1,3) exists)
                # This is complex, but for now, just checking qubit occupancy is enough for "blocking"
        return True

    def on_gate_dropped(self, gate_type, qubit_index, time_index):
        target_index = None
        params = None
        
        # Handle Multi-Qubit Targets
        if gate_type in ["CX", "CY", "CZ", "CH", "SWAP"]:
            target_index = self.view.show_input_dialog(f"{gate_type} Gate", "Select Target Qubit:")
            if target_index is None or target_index == qubit_index:
                # Invalid selection; keep model unchanged and force a redraw from model
                self.redraw_circuit_from_model()
                return
            
            # --- NEW CHECK: IS PATH CLEAR? ---
            if not self.is_path_clear(qubit_index, target_index, time_index):
                QMessageBox.warning(self.view, "Invalid Placement", 
                                    "Cannot place gate here: Intermediate wires are blocked by other gates.")
                # Re-draw from model to ensure view matches model (don't manipulate view state directly)
                self.redraw_circuit_from_model()
                return

        # Handle Parameters
        if gate_type in ["RX", "RY", "RZ", "P"]:
            text, ok = QInputDialog.getText(self.view, "Rotation Angle", "Enter Angle (radians):", text="1.57")
            if ok and text:
                try: params = float(text)
                except ValueError: return
            else: return

        # Add gate to model (model enforces uniqueness) then redraw
        self.model.add_gate(gate_type, qubit_index, time_index, target_index, params)
        self.update_code_from_model()
        self.redraw_circuit_from_model()


    def on_gate_deleted(self, q, t):
        self.model.remove_gate(q, t)
        self.update_code_from_model()

    def on_gate_moved(self, oq, ot, nq, nt):
        # Use an atomic model operation for move; if it fails, redraw to restore view
        success = self.model.move_gate(oq, ot, nq, nt)
        if not success:
            # Move failed (source missing or target occupied) — re-sync the view
            self.redraw_circuit_from_model()
            return

        # Move succeeded — update code and redraw from authoritative model
        self.update_code_from_model()
        self.redraw_circuit_from_model()

    # --- 3. Code Editor Logic ---
    def on_text_edited(self):
        """Called whenever user types in the editor."""
        if self.is_internal_update:
            return 
        self.debounce_timer.start()

    def on_code_parsed(self):
        """Called after user stops typing."""
        code = self.view.code_view.get_code()
        new_ops = self.parser.parse_to_model(code, self.model.num_qubits)
        
        if new_ops is not None:
            self.model.operations = new_ops
            self.redraw_circuit_from_model()

    # --- 4. Helpers ---
    def update_code_from_model(self):
        """Generates code from grid and puts it in editor."""
        self.is_internal_update = True
        ops = self.model.get_operations()
        code = self.code_gen.generate(self.model.num_qubits, ops)
        self.view.code_view.update_code(code)
        self.is_internal_update = False

    # ... Update redraw to pass params ...
    def redraw_circuit_from_model(self):
        self.view.circuit_view.clear_grid()
        for op in self.model.get_operations():
            gate = op['gate']
            q = op['qubit']
            idx = op['index']
            target = op.get('target')
            params = op.get('params')

            self.view.circuit_view.place_gate_visual(gate, q, idx, target, params)

            # --- NEW: Draw Connectors for Multi-Qubit Gates ---
            if target is not None:
                start, end = min(q, target), max(q, target)
                # Fill in every qubit strictly between start and end
                for intermediate_q in range(start + 1, end):
                    self.view.circuit_view.place_connector_visual(intermediate_q, idx)



    def update_full_ui(self):
        """Syncs everything."""
        self.update_code_from_model()

    # --- 5. Simulation & File IO ---
    def run_simulation(self):
        # We simulate whatever is currently in the model 
        counts, statevector = self.model.run_simulation()
        self.view.viz_view.plot_histogram(counts)
        
        # Update inline qubit state visualizations
        self._update_qubit_visualizations(statevector)
        
        self.view.right_tabs.setCurrentIndex(1)
    
    def _update_qubit_visualizations(self, statevector):
        """Extract individual qubit Bloch vectors and update inline visualizations."""
        from qiskit.quantum_info import partial_trace, DensityMatrix
        
        for qubit_idx in range(self.model.num_qubits):
            # Calculate reduced density matrix for this qubit
            traced_out = [i for i in range(self.model.num_qubits) if i != qubit_idx]
            reduced_dm = partial_trace(statevector, traced_out)
            
            # Calculate Bloch vector components
            dm_array = reduced_dm.data
            
            # Pauli matrices
            sx = np.array([[0, 1], [1, 0]], dtype=complex)
            sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
            sz = np.array([[1, 0], [0, -1]], dtype=complex)
            
            # Calculate expectation values
            x = np.real(np.trace(dm_array @ sx))
            y = np.real(np.trace(dm_array @ sy))
            z = np.real(np.trace(dm_array @ sz))
            
            # Update the visualization widget
            if qubit_idx in self.view.circuit_view.qubit_state_widgets:
                widget = self.view.circuit_view.qubit_state_widgets[qubit_idx]
                widget.set_state((x, y, z))

    def save_project(self):
        fname = self.view.show_save_dialog("Save Project", "JSON Files (*.json)")
        if fname:
            with open(fname, 'w') as f:
                f.write(self.model.to_json())

    def load_project(self):
        fname = self.view.show_load_dialog()
        if fname:
            with open(fname, 'r') as f:
                self.model.load_from_json(f.read())
            self.redraw_circuit_from_model()
            self.update_full_ui()

    def show_logical_state(self):
        logical_state = self.model.get_operations()
        QMessageBox.information(self.view.circuit_view, "Logical State", str(logical_state))
