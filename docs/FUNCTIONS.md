# Quantum Composer - Function Directory

Comprehensive list of functions organized by file for Models, Views, and Controllers.

---

## Models

### `models/circuit_model.py` - CircuitModel

**Class Methods:**
- `__init__(num_qubits=3)` - Initialize the circuit model with number of qubits
- `add_gate(gate_type, qubit_index, time_index, target_index=None, params=None, matrix=None)` - Add a gate to the circuit at specified position
- `move_gate(old_q, old_t, new_q, new_t)` - Atomically move a gate from one position to another
- `remove_gate(qubit_index, time_index)` - Remove a gate from the circuit
- `get_operations()` - Retrieve all current operations in the circuit
- `run_simulation()` - Execute circuit simulation and return counts histogram and statevector
- `to_json()` - Serialize circuit state to JSON string
- `load_from_json(json_str)` - Deserialize and load circuit state from JSON string

---

### `models/code_generator.py` - QiskitCodeGenerator

**Static Methods:**
- `generate(num_qubits, operations)` - Generate Qiskit Python code from circuit operations

---

### `models/code_parser.py` - QiskitCodeParser

**Static Methods:**
- `parse_to_model(code_str, num_qubits)` - Parse Qiskit Python code and convert to circuit model operations

---

## Views

### `views/main_window.py` - MainWindow

**Class Methods:**
- `__init__()` - Initialize the main application window with menu bar, toolbar, and layout
- `show_save_dialog(title, ext)` - Display file save dialog and return selected filename
- `show_load_dialog()` - Display file load dialog and return selected filename
- `show_input_dialog(title, label)` - Display input dialog for integer value and return result

---

### `views/circuit_view.py` - CircuitView

**Class Methods:**
- `__init__(num_qubits=3, num_steps=10)` - Initialize the visual circuit grid
- `setup_grid()` - Create grid layout with drop zones, qubit labels, and wires
- `paintEvent(event)` - Render connector lines for multi-qubit gates
- `clear_grid()` - Clear all gates from visual display
- `place_gate_visual(gate_text, q, t, target_index=None, params=None, matrix=None)` - Place gate visual in specific position
- `place_connector_visual(q, t)` - Place connector visual for multi-qubit gates
- `show_circuit_array()` - Display circuit array in message box (debug)
- `show_visual_state()` - Display visual state in message box (debug)
- `update_circuit(operations)` - Update circuit view from operations list

---

### `views/circuit_view.py` - DropLabel

**Class Methods:**
- `__init__(qubit_idx, time_idx)` - Initialize a drop zone for a specific qubit and time step
- `contextMenuEvent(event)` - Handle right-click context menu for gate deletion
- `mouseMoveEvent(e)` - Handle mouse movement for drag-and-drop
- `dragEnterEvent(event)` - Handle drag enter with visual preview
- `dragMoveEvent(event)` - Handle drag move event
- `dropEvent(event)` - Handle drop event for placing or moving gates
- `dragLeaveEvent(event)` - Handle drag leave event
- `set_visual_gate(text, params=None, matrix=None)` - Set visual appearance of gate
- `set_visual_source(gate_type, target_idx, matrix=None)` - Set visual for multi-qubit gate source (control)
- `set_visual_target(gate_type, matrix=None)` - Set visual for multi-qubit gate target
- `set_visual_connector()` - Set visual for connector between qubits
- `clear_visual()` - Reset visual and logical state
- `show_shadow(gate_text)` - Show drag preview shadow
- `clear_shadow()` - Clear drag preview shadow

---

### `views/palette_view.py` - PaletteView

**Class Methods:**
- `__init__()` - Initialize the gate palette with draggable buttons

---

### `views/palette_view.py` - DraggableButton

**Class Methods:**
- `__init__(text, parent=None)` - Initialize a draggable gate button
- `mouseMoveEvent(e)` - Handle mouse movement for drag initiation

---

### `views/code_editor_view.py` - CodeEditorView

**Class Methods:**
- `__init__()` - Initialize code editor view with syntax highlighting
- `update_code(code)` - Update code display with new code string
- `get_code()` - Retrieve current code from editor

---

### `views/visualization_view.py` - VisualizationView

**Class Methods:**
- `__init__()` - Initialize matplotlib canvas for visualization
- `plot_histogram(counts)` - Plot measurement results histogram

---

### `views/qubit_state_widget.py` - QubitStateWidget

**Class Methods:**
- `__init__(qubit_idx, parent=None)` - Initialize Bloch sphere visualization for single qubit
- `set_state(bloch_vector)` - Update Bloch sphere visualization with new state vector
- `paintEvent(event)` - Render Bloch sphere with state vector as point

---

### `views/phase_legend_widget.py` - PhaseLegendWidget

**Class Methods:**
- `__init__(parent=None)` - Initialize phase color scheme legend widget
- `paintEvent(event)` - Render color gradient bar showing phase angle mapping

---

### `views/custom_gate_analyzer.py` - CustomGateAnalyzer

**Static Methods:**
- `analyze_matrix(matrix)` - Analyze unitary matrix and return visual properties (type, color, icon)
- `get_css_style(properties)` - Generate CSS stylesheet based on gate properties
- `get_tooltip(properties)` - Generate tooltip text describing gate properties
- `_is_diagonal(matrix, tol=1e-10)` - Check if matrix is diagonal
- `_is_real(matrix, tol=1e-10)` - Check if matrix contains only real values
- `_is_hermitian(matrix, tol=1e-10)` - Check if matrix is Hermitian (U† = U)
- `_is_hadamard_like(matrix, tol=1e-10)` - Check if matrix has Hadamard structure
- `_is_identity(matrix, tol=1e-10)` - Check if matrix is identity matrix
- `_is_rotation_gate(matrix, qubit_count, tol=1e-10)` - Check if matrix is rotation gate

---

### `views/custom_gate_dialog.py` - CustomGateDialog

**Class Methods:**
- `__init__(parent=None, num_qubits=1)` - Initialize custom gate creation dialog
- `setup_ui()` - Create dialog UI components (matrix inputs, presets, validation)
- `on_qubit_count_changed(index)` - Handle qubit count selector change
- `create_matrix_inputs()` - Create input fields for matrix entries
- `apply_preset(index)` - Apply preset unitary matrix
- `fill_matrix(matrix)` - Populate matrix input fields with values
- `get_matrix_from_inputs()` - Parse and return matrix from input fields
- `validate_matrix()` - Check if entered matrix is unitary
- `create_gate()` - Create and return custom gate (final step)

---

## Controllers

### `controllers/main_controller.py` - MainController

**Class Methods:**

**Initialization & UI Setup:**
- `__init__(view)` - Initialize controller with view and model, connect signals

**Export Functions:**
- `export_image()` - Save circuit visual as PNG image file
- `export_code()` - Save generated Qiskit code as Python file

**Gate Logic:**
- `on_gate_dropped(gate_type, qubit_index, time_index)` - Handle gate placement from palette
- `on_gate_deleted(q, t)` - Handle gate deletion
- `on_gate_moved(oq, ot, nq, nt)` - Handle gate repositioning
- `is_path_clear(q1, q2, time_index)` - Check if path between qubits is clear at time index

**Code Editor Logic:**
- `on_text_edited()` - Handle code editor text changes (with debouncing)
- `on_code_parsed()` - Parse edited code and update circuit model

**Helper Functions:**
- `update_code_from_model()` - Generate and update code view from circuit model
- `redraw_circuit_from_model()` - Redraw circuit visuals from authoritative model
- `update_full_ui()` - Synchronize entire UI with model state

**Simulation & Visualization:**
- `run_simulation()` - Execute circuit simulation and display results
- `_update_qubit_visualizations(statevector)` - Update inline Bloch sphere visualizations

**File I/O:**
- `save_project()` - Save circuit to JSON file
- `load_project()` - Load circuit from JSON file
- `show_logical_state()` - Display circuit operations in message box (debug)

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Model Classes | 3 |
| Model Methods | 8 |
| View Classes | 9 |
| View Methods | 47 |
| Controller Classes | 1 |
| Controller Methods | 20 |
| **Total Classes** | **13** |
| **Total Methods** | **75** |

---

## Architecture Notes

- **MVC Pattern**: Models handle data/logic, Views handle UI rendering, Controllers handle events
- **Signals/Slots**: PyQt6 signals connect view events to controller methods
- **Code Generation**: Circuit operations are bidirectionally converted between visual grid and Qiskit code
- **Custom Gates**: Support for 1 and 2-qubit custom unitary gates with visual analysis
- **Real-time Simulation**: Circuit can be executed and results visualized immediately
