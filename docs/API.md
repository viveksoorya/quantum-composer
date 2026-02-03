# Quantum Composer API Documentation

This document provides a comprehensive API reference for the Quantum Composer codebase, covering models, views, controllers, and the main entry point.

---

## Models

### `circuit_model.py`
- **`CircuitModel`**: Manages the quantum circuit's state, including gates, qubits, and undo/redo functionality.
  - `add_gate(gate: str, qubit: int, position: int)`: Adds a gate to the circuit.
  - `remove_gate(qubit: int, position: int)`: Removes a gate from the circuit.
  - `move_gate(old_qubit: int, old_position: int, new_qubit: int, new_position: int)`: Moves a gate within the circuit.
  - `get_circuit() -> List[Dict]`: Returns the current circuit state as a list of dictionaries.

### `code_generator.py`
- **`CodeGenerator`**: Converts the circuit model into Qiskit code.
  - `generate_code(circuit: List[Dict]) -> str`: Generates Qiskit code from the circuit.

### `code_parser.py`
- **`CodeParser`**: Parses Qiskit code into the circuit model.
  - `parse_code(code: str) -> List[Dict]`: Parses Qiskit code and returns the circuit structure.

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
    - `populate_palette()`

### `visualization_view.py`
- **`VisualizationView`**: Displays simulation results, including histograms and Bloch sphere visualizations.
  - Methods:
    - `update_histogram(data: Dict)`
    - `update_bloch_sphere(state: List[float])`

---

## Controllers

### `main_controller.py`
- **`MainController`**: Handles user interactions and updates the model and views.
  - Methods:
    - `on_gate_added(gate: str, qubit: int, position: int)`
    - `on_gate_removed(qubit: int, position: int)`
    - `on_gate_moved(old_qubit: int, old_position: int, new_qubit: int, new_position: int)`
    - `run_simulation()`

---

## Main Entry Point

### `main.py`
- Initializes the application and sets up the main window.
  - Methods:
    - `main()`: Entry point for the application.

---

This API documentation provides an overview of the key components and their methods, signals, and responsibilities. For detailed usage examples, refer to the README or the source code.