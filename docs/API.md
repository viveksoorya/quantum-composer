# Quantum Composer API Documentation

This document provides a comprehensive API reference for the Quantum Composer codebase, covering models, views, controllers, and the main entry point.

---

## Models

### `circuit_model.py`
- **`CircuitModel`**: Manages the quantum circuit's state, including gates, qubits, and undo/redo functionality.
  - Attributes:
    - `num_qubits`: Number of qubits in the circuit
    - `operations`: List of gate operations
  - Methods:
    - `__init__(num_qubits: int = 3)`
    - `add_gate(gate_type: str, qubit_index: int, time_index: int, target_index: int = None, params: float = None, matrix: np.ndarray = None)`: Adds a gate to the circuit.
    - `remove_gate(qubit_index: int, time_index: int)`: Removes a gate from the circuit.
    - `move_gate(old_q: int, old_t: int, new_q: int, new_t: int) -> bool`: Moves a gate within the circuit. Returns True on success.
    - `get_operations() -> List[Dict]`: Returns the current circuit operations.
    - `run_simulation() -> Tuple[Dict, Statevector]`: Runs Qiskit Aer simulation, returns counts and statevector.
    - `to_json() -> str`: Serializes circuit to JSON string.
    - `load_from_json(json_str: str)`: Loads circuit from JSON string.

### `code_generator.py`
- **`QiskitCodeGenerator`**: Converts the circuit model into Qiskit code.
  - `generate(num_qubits: int, operations: List[Dict]) -> str`: Generates Qiskit code from the circuit. (Static method)

### `code_parser.py`
- **`QiskitCodeParser`**: Parses Qiskit code into the circuit model.
  - `parse_to_model(code_str: str, num_qubits: int) -> List[Dict]`: Parses Qiskit code and returns the circuit structure. (Static method)

---

## Views

### `circuit_view.py`
- **`CircuitView`**: Represents the main visual interface for the quantum circuit.
  - Signals:
    - `gate_dropped(str, int, int)`
    - `gate_deleted(int, int)`
    - `gate_moved(int, int, int, int)`
  - Methods:
    - `__init__(num_qubits: int = 3, num_steps: int = 10)`
    - `setup_grid()`
    - `paintEvent(event)`
    - `clear_grid()`
    - `place_gate_visual(...)`
    - `place_connector_visual(...)`
    - `show_circuit_array()`

### `palette_view.py`
- **`PaletteView`**: Displays draggable quantum gates for the user to place on the circuit.
  - Methods:
    - `__init__()`
    - `populate_palette()`: Populates the palette with gate buttons
  - Gates Available: H, X, Y, Z, RX, RY, RZ, P, CX, SWAP, CZ, CUSTOM

### `code_editor_view.py`
- **`CodeEditorView`**: Qiskit code text editor with syntax highlighting.
  - Methods:
    - `update_code(code: str)`: Updates the editor content
    - `get_code() -> str`: Returns the current code

### `visualization_view.py`
- **`VisualizationView`**: Displays simulation results, including histograms.
  - Methods:
    - `plot_histogram(counts: Dict)`: Plots measurement outcome histogram

### `custom_gate_dialog.py`
- **`CustomGateDialog`**: Modal dialog for creating custom unitary gates.
  - Methods:
    - `get_result() -> Dict`: Returns the gate definition (name, matrix, num_qubits)

---

## Controllers

### `main_controller.py`
- **`MainController`**: Handles user interactions and updates the model and views.
  - Attributes:
    - `view`: Reference to the main window view
    - `model`: CircuitModel instance
    - `code_gen`: QiskitCodeGenerator instance
    - `parser`: QiskitCodeParser instance
    - `is_internal_update`: Flag to prevent circular updates during code regeneration
  - Methods:
    - `__init__(view: MainWindow)`
    - `on_gate_dropped(gate_type: str, qubit_index: int, time_index: int)`
    - `on_gate_deleted(qubit_index: int, time_index: int)`
    - `on_gate_moved(old_qubit: int, old_time: int, new_qubit: int, new_time: int)`
    - `run_simulation()`: Executes circuit and updates visualizations
    - `save_project()`: Saves circuit to JSON file
    - `load_project()`: Loads circuit from JSON file
    - `export_image()`: Exports circuit as PNG image
    - `export_code()`: Exports Qiskit code as Python file
    - `update_code_from_model()`: Generates code from model and updates editor
    - `redraw_circuit_from_model()`: Redraws circuit grid from model state
    - `update_full_ui()`: Full UI sync
    - `is_path_clear(q1: int, q2: int, time_index: int) -> bool`: Checks if path between qubits is clear for multi-qubit gates

---

### `main_window.py`
- **`MainWindow`**: Main application window with menu, toolbar, and layout.
  - Methods:
    - `show_save_dialog(title: str, ext: str) -> str`: Shows save file dialog
    - `show_load_dialog() -> str`: Shows open file dialog
    - `show_input_dialog(title: str, label: str) -> int`: Shows input dialog for qubit selection

---

## Main Entry Point

### `main.py`
- Initializes the application and sets up the main window.
  - `main()`: Entry point for the application.

---

This API documentation provides an overview of the key components and their methods, signals, and responsibilities. For detailed usage examples, refer to the README or the source code.