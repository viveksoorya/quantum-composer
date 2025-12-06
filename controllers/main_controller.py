from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QVBoxLayout
from models.circuit_model import CircuitModel
from models.code_generator import QiskitCodeGenerator
from models.code_parser import QiskitCodeParser

class MainController:
    def __init__(self, view):
        self.view = view
        self.model = CircuitModel(num_qubits=3)
        self.code_gen = QiskitCodeGenerator()
        self.parser = QiskitCodeParser()
        self.is_internal_update = False

        # --- SIGNALS ---
        self.view.circuit_view.gate_dropped.connect(self.on_gate_dropped)
        self.view.circuit_view.gate_deleted.connect(self.on_gate_deleted)
        self.view.circuit_view.gate_moved.connect(self.on_gate_moved)
        
        self.view.run_action.triggered.connect(self.run_simulation_manually)
        self.view.undo_action.triggered.connect(self.undo)
        self.view.redo_action.triggered.connect(self.redo)
        
        self.view.save_action.triggered.connect(self.save_project)
        self.view.load_action.triggered.connect(self.load_project)
        self.view.export_image_action.triggered.connect(self.export_image)
        self.view.export_code_action.triggered.connect(self.export_code)

        # Tab Switching Logic
        self.view.right_tabs.currentChanged.connect(self.on_tab_changed)

        # Editor Debounce
        self.debounce_timer = QTimer()
        self.debounce_timer.setInterval(600)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_code_parsed)
        self.view.code_view.editor.textChanged.connect(self.on_text_edited)

        # Ensure layouts exist for tabs (Robustness)
        self._ensure_tab_layouts()

        # Initial Render
        self.update_full_ui()

    def _ensure_tab_layouts(self):
        """Ensures Tab 1 and Tab 2 have layouts to hold the VizView."""
        # Tab 1: Histogram
        tab1 = self.view.right_tabs.widget(1)
        if not tab1.layout():
            tab1.setLayout(QVBoxLayout())
            
        # Tab 2: Bloch Sphere
        # (This might fail if user didn't update main_window.py, so we try/except)
        if self.view.right_tabs.count() > 2:
            tab2 = self.view.right_tabs.widget(2)
            if not tab2.layout():
                tab2.setLayout(QVBoxLayout())

    def update_full_ui(self):
        """Refreshes the entire application state."""
        self.update_code_from_model()
        self.redraw_circuit_from_model()

    # --- UNDO / REDO ---
    def undo(self):
        if self.model.undo():
            self.update_full_ui()
            self.on_tab_changed(self.view.right_tabs.currentIndex())

    def redo(self):
        if self.model.redo():
            self.update_full_ui()
            self.on_tab_changed(self.view.right_tabs.currentIndex())

    # --- TAB SWITCHING (The Magic Swap) ---
    def on_tab_changed(self, index):
        """Moves the VizView to the active tab and runs the specific sim."""
        viz_widget = self.view.viz_view
        
        try:
            # Tab 0: Code (Do nothing)
            if index == 0:
                pass

            # Tab 1: Histogram
            elif index == 1:
                # Move widget to Tab 1
                target_tab = self.view.right_tabs.widget(1)
                if viz_widget.parent() != target_tab:
                    target_tab.layout().addWidget(viz_widget)
                
                # Run Simulation
                counts = self.model.run_simulation()
                viz_widget.plot_histogram(counts)

            # Tab 2: Bloch Sphere
            elif index == 2:
                # Move widget to Tab 2
                target_tab = self.view.right_tabs.widget(2)
                if viz_widget.parent() != target_tab:
                    target_tab.layout().addWidget(viz_widget)
                
                # Run Simulation
                statevector = self.model.get_statevector()
                viz_widget.plot_bloch_multivector(statevector, self.model.num_qubits)

        except Exception as e:
            print(f"Visualization Error: {e}")

    # --- SIMULATION ---
    def run_simulation_manually(self):
        # Force refresh current tab
        self.on_tab_changed(self.view.right_tabs.currentIndex())

    # --- GATE LOGIC ---
    def on_gate_dropped(self, gate_type, qubit_index, time_index):
        target_index = None
        params = None

        if gate_type in ["CX", "CY", "CZ", "CH", "SWAP"]:
            target_index = self.view.show_input_dialog(f"{gate_type} Gate", "Select Target:")
            if target_index is None or target_index == qubit_index:
                self.view.circuit_view.drop_zones[(qubit_index, time_index)].clear_visual()
                return

        if gate_type in ["RX", "RY", "RZ", "P"]:
            text, ok = QInputDialog.getText(self.view, "Rotation", "Angle (radians):", text="1.57")
            if ok and text:
                try: params = float(text)
                except ValueError: return
            else: 
                self.view.circuit_view.drop_zones[(qubit_index, time_index)].clear_visual()
                return

        # SNAPSHOT & UPDATE
        self.model.save_snapshot()
        self.model.add_gate(gate_type, qubit_index, time_index, target_index, params)
        self.update_full_ui()
        
        # Auto-refresh visualization if visible
        if self.view.right_tabs.currentIndex() > 0:
            self.on_tab_changed(self.view.right_tabs.currentIndex())

    def on_gate_deleted(self, q, t):
        self.model.save_snapshot()
        self.model.remove_gate(q, t)
        self.update_full_ui()
        if self.view.right_tabs.currentIndex() > 0:
            self.on_tab_changed(self.view.right_tabs.currentIndex())

    def on_gate_moved(self, oq, ot, nq, nt):
        ops = self.model.get_operations()
        op = next((o for o in ops if o['qubit'] == oq and o['index'] == ot), None)
        if op:
            self.model.save_snapshot()
            self.model.remove_gate(oq, ot)
            self.model.add_gate(op['gate'], nq, nt, op.get('target'), op.get('params'))
            self.update_full_ui()
            if self.view.right_tabs.currentIndex() > 0:
                self.on_tab_changed(self.view.right_tabs.currentIndex())

    # --- HELPERS ---
    def on_text_edited(self):
        if not self.is_internal_update: self.debounce_timer.start()

    def on_code_parsed(self):
        self.model.save_snapshot()
        code = self.view.code_view.get_code()
        new_ops = self.parser.parse_to_model(code, self.model.num_qubits)
        if new_ops is not None:
            self.model.operations = new_ops
            self.redraw_circuit_from_model()

    def update_code_from_model(self):
        self.is_internal_update = True
        ops = self.model.get_operations()
        code = self.code_gen.generate(self.model.num_qubits, ops)
        self.view.code_view.update_code(code)
        self.is_internal_update = False

    def redraw_circuit_from_model(self):
        self.view.circuit_view.clear_grid()
        for op in self.model.get_operations():
            self.view.circuit_view.place_gate_visual(
                op['gate'], op['qubit'], op['index'], op.get('target'), op.get('params')
            )

    def save_project(self):
        fname = self.view.show_save_dialog("Save", "JSON (*.json)")
        if fname:
            with open(fname, 'w') as f: f.write(self.model.to_json())

    def load_project(self):
        fname = self.view.show_load_dialog()
        if fname:
            with open(fname, 'r') as f: self.model.load_from_json(f.read())
            self.update_full_ui()
    
    def export_image(self):
        fname = self.view.show_save_dialog("Export", "PNG (*.png)")
        if fname: self.view.circuit_view.grab().save(fname)

    def export_code(self):
        fname = self.view.show_save_dialog("Export", "Python (*.py)")
        if fname:
            with open(fname, 'w') as f: f.write(self.view.code_view.get_code())
