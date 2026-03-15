# Open Quantum Composer Pro - Context Documentation

## Overview

**Open Quantum Composer Pro** is a professional, drag-and-drop Quantum Circuit Composer built with Python. It enables users to visually design quantum circuits using an intuitive graphical interface, visualize the corresponding Qiskit code in real-time, simulate results locally using Qiskit Aer, and verify quantum states on the Bloch Sphere.

## Purpose and Use Case

This software serves as an educational and prototyping tool for:

- **Learning Quantum Computing**: Users can visually build quantum circuits without writing code, making it ideal for students and beginners.
- **Rapid Prototyping**: Researchers and developers can quickly prototype quantum algorithms visually and then export the Qiskit code for further development.
- **Two-Way Synchronization**: The bidirectional sync between visual circuit design and Qiskit code allows seamless switching between visual and code-based editing.
- **Simulation and Visualization**: Built-in simulation with histogram results and inline Bloch sphere state visualization for each qubit.

## Technology Stack

- **GUI Framework**: PyQt6
- **Quantum Computing**: Qiskit, Qiskit Aer
- **Visualization**: Matplotlib
- **Language**: Python 3.13

## Architecture

The application follows a strict **Model-View-Controller (MVC)** architecture:

```
quantum_composer/
├── main.py                      # Entry point
├── models/                      # Data and business logic
│   ├── circuit_model.py         # Circuit state, operations, simulation
│   ├── code_generator.py        # Grid -> Qiskit code string
│   └── code_parser.py           # Qiskit code string -> Grid operations
├── views/                       # UI components
│   ├── main_window.py           # Main application window, menu, toolbar
│   ├── palette_view.py          # Draggable gate buttons
│   ├── circuit_view.py          # Quantum circuit grid with drop zones
│   ├── code_editor_view.py      # Qiskit code text editor
│   ├── visualization_view.py     # Matplotlib histogram display
│   ├── custom_gate_dialog.py    # Dialog for creating custom unitary gates
│   ├── custom_gate_analyzer.py  # Analyzes custom gate matrices
│   ├── qubit_state_widget.py    # Inline Bloch sphere visualization
│   ├── phase_legend_widget.py   # Phase color legend
│   └── styles.py                # CSS themes and styling
├── controllers/
│   └── main_controller.py       # Event handling, coordination between MVC
└── requirements.txt             # Python dependencies
```

## Key Features

### 1. Drag-and-Drop Circuit Design
- **Gate Palette**: Left sidebar with draggable quantum gates (H, X, Y, Z, RX, RY, RZ, P, CX, SWAP, CZ, CUSTOM)
- **Visual Grid**: Quantum circuit representation with qubits as rows and time steps as columns
- **Gate Placement**: Drag gates from palette onto the grid
- **Gate Movement**: Click and drag existing gates to reposition them
- **Gate Deletion**: Right-click on any gate to delete it

### 2. Gate Types Supported
- **Single-Qubit Gates**: H (Hadamard), X, Y, Z, S, T
- **Rotation Gates**: RX, RY, RZ, P (Phase) - with parameter input dialog
- **Multi-Qubit Gates**: CX (CNOT), SWAP, CZ - with target qubit selection
- **Custom Gates**: User-defined unitary matrices (1-qubit or 2-qubit)

### 3. Two-Way Code Synchronization
- **Visual to Code**: As gates are placed/moved, Qiskit code updates in real-time
- **Code to Visual**: Editing the Qiskit code directly updates the visual circuit grid
- **Debounced Parsing**: 600ms debounce on code editor to prevent excessive parsing

### 4. Simulation and Results
- **Local Simulation**: Uses Qiskit Aer simulator
- **Histogram View**: Displays measurement outcome probabilities
- **Bloch Sphere Visualization**: Inline widget showing each qubit's state vector after simulation
- **Run Action**: Toolbar button triggers simulation and switches to Results tab

### 5. File Operations
- **Save Project**: Save circuit as JSON (.json)
- **Load Project**: Load previously saved JSON circuit
- **Export Image**: Export circuit as PNG image
- **Export Code**: Export Qiskit code as Python file (.py)

## Components Detail

### Models

#### CircuitModel (`models/circuit_model.py`)
- **State**: num_qubits, operations list
- **Operations**: List of dictionaries with keys: gate, qubit, target, params, matrix, index
- **Methods**:
  - `add_gate()`: Add gate to circuit
  - `remove_gate()`: Remove gate from circuit
  - `move_gate()`: Reposition gate with conflict detection
  - `run_simulation()`: Execute circuit with Qiskit Aer, return counts and statevector
  - `to_json()` / `load_from_json()`: Serialization

#### QiskitCodeGenerator (`models/code_generator.py`)
- Converts circuit operations to Qiskit Python code string
- Handles custom gate definitions with UnitaryGate
- Generates executable Qiskit code

#### QiskitCodeParser (`models/code_parser.py`)
- Parses Qiskit code by executing it in a safe scope
- Reverse-engineers circuit layout from QuantumCircuit object
- Handles multi-qubit gate spanning correctly

### Views

#### MainWindow (`views/main_window.py`)
- PyQt6 QMainWindow
- Menu bar: File (Save/Load), Export (Image/Code)
- Toolbar: Run Simulation action
- Layout: Horizontal splitter with Palette | Circuit | Right Tabs (Code/Results)

#### PaletteView (`views/palette_view.py`)
- Scrollable list of DraggableButton widgets
- Gates: H, X, Y, Z, RX, RY, RZ, P, CX, SWAP, CZ, CUSTOM
- Uses QDrag with QMimeData for drag-and-drop

#### CircuitView (`views/circuit_view.py`)
- QGridLayout with DropLabel widgets as drop zones
- **DropLabel**: Individual grid cell that accepts drops
  - `gate_placed` signal: (gate_type, qubit_index, time_index)
  - `gate_deleted` signal: (qubit_index, time_index)
  - `gate_moved` signal: (old_qubit, old_time, new_qubit, new_time)
- Visual representations: Gate box, control dot (●), target cross (+), connectors
- Inline QubitStateWidget at end of each qubit line
- PhaseLegendWidget at bottom

#### CodeEditorView (`views/code_editor_view.py`)
- QPlainTextEdit for Qiskit code
- Syntax highlighting support
- Text change signal for sync

#### VisualizationView (`views/visualization_view.py`)
- Matplotlib FigureCanvas
- Dark theme histogram display
- `plot_histogram(counts)` method

#### CustomGateDialog (`views/custom_gate_dialog.py`)
- Modal dialog for creating custom unitary gates
- Gate name input
- Qubit count selector (1 or 2)
- Matrix input grid with complex number support
- Preset gates: Identity, Pauli-X/Y/Z, Hadamard, Phase, T, RX/RY/RZ
- Unitary matrix validation

#### QubitStateWidget (`views/qubit_state_widget.py`)
- Small inline visualization showing qubit state on Bloch sphere
- Updates after simulation with (x, y, z) Bloch vector

#### PhaseLegendWidget (`views/phase_legend_widget.py`)
- Displays color mapping for quantum phase

#### CustomGateAnalyzer (`views/custom_gate_analyzer.py`)
- Analyzes custom gate matrices
- Determines gate properties (icon, color, qubit count)
- Generates tooltips

### Controller

#### MainController (`controllers/main_controller.py`)
- Coordinates between Model and View
- Handles all signals from views
- Manages debounced code parsing
- Implements gate placement logic with path collision detection
- Runs simulation and updates visualizations
- File save/load implementation

## Gate Placement Logic

When placing multi-qubit gates (CX, SWAP, CZ, CUSTOM 2-qubit):
1. User drops gate on control qubit
2. Dialog prompts for target qubit index
3. Controller checks `is_path_clear()` - ensures no gates block the vertical span between control and target
4. If path is clear, gate is added to model; otherwise warning dialog shown

## Dependencies

```
PyQt6
qiskit
qiskit-aer
matplotlib
numpy
```

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py
```

## User Workflow

1. **Launch**: Application opens with 3 qubits, 12 time steps
2. **Design**: Drag gates from palette onto circuit grid
3. **Configure**: For rotation gates, enter angle in radians; for multi-qubit gates, select target
4. **Code View**: Switch to "Qiskit Code" tab to see generated code, or edit code directly
5. **Simulate**: Click "▶ Run Simulation" in toolbar
6. **Analyze**: View histogram in Results tab, observe inline Bloch states
7. **Export**: Save project, export image, or export code for IBM Quantum

## Important Implementation Notes

- **MVC Separation**: Views should not directly modify model; emit signals handled by controller
- **Internal Update Flag**: Controller uses `is_internal_update` flag to prevent circular updates when regenerating code
- **Collision Detection**: `is_path_clear()` ensures multi-qubit gates don't overlap with existing gates in their span
- **Custom Gate Matrices**: Stored as numpy arrays in model, converted to lists for JSON serialization
- **Statevector Simulation**: Runs separately from measurement simulation to get Bloch vector data
- **Debouncing**: 600ms timer on code editor prevents excessive parsing during typing
