# AGENTS.md - Quantum Composer Development Guide

## Project Overview

Quantum Composer is a PyQt6-based drag-and-drop quantum circuit designer that generates Qiskit code in real-time. Uses strict **MVC** architecture.

```
quantum_composer/
├── main.py                   # Entry point
├── models/                   # Data layer
│   ├── circuit_model.py      # Circuit state & undo stack
│   ├── code_generator.py     # Grid -> Qiskit string
│   └── code_parser.py        # Qiskit string -> Grid
├── views/                    # UI layer
│   ├── main_window.py        # Main application window
│   ├── palette_view.py       # Draggable gate palette
│   ├── circuit_view.py       # Custom painting engine (grid)
│   └── visualization_view.py # Matplotlib charts
└── controllers/              # Business logic
    └── main_controller.py    # Event handling & simulation
```

## Build, Lint, and Test Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py

# Build executable (Linux example)
pip install pyinstaller
pyinstaller --noconsole --onefile --collect-all qiskit --collect-all qiskit_aer --hidden-import=matplotlib --name="QuantumComposer" main.py
```

### Running Tests

Tests in `software-verification/tests/`:

```bash
# Run all tests
pytest software-verification/tests/

# Run specific test file
pytest software-verification/tests/test_circuit_model.py

# Run specific test class
pytest software-verification/tests/test_circuit_model.py::TestCircuitModelInitialization

# Run single test method (recommended for debugging)
pytest software-verification/tests/test_circuit_model.py::TestCircuitModelInitialization::test_default_initialization

# Run with verbose output
pytest software-verification/tests/ -v
```

## Code Style Guidelines

### Imports

Order: 1) Standard library, 2) Third-party (PyQt6, qiskit, numpy, matplotlib), 3) Local modules. Inside PyQt6: QtCore -> QtGui -> QtWidgets.

```python
import sys
import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

from models.circuit_model import CircuitModel
from views.main_window import MainWindow

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
```

### Naming

- **Classes**: PascalCase (`CircuitModel`, `MainWindow`)
- **Functions/variables**: snake_case (`add_gate`, `num_qubits`)
- **Constants**: SCREAMING_SNAKE_CASE (`LIGHT_THEME`)
- **Private methods**: Prefix with underscore (`_internal_method`)

### Type Annotations

New code should use type hints. Legacy code without types is acceptable.

### Error Handling

- Use try/except for file I/O, parsing, simulation
- Show user-friendly errors with `QMessageBox.warning()`
- Return `None`/`False` for recoverable errors
- Log errors with print statements

### Code Organization

Group class methods by functionality. Place signal connections in `__init__` or `setup_signals()`.

```python
class MainController:
    def __init__(self, view):
        self.view = view
        self.model = CircuitModel(num_qubits=3)
        self.view.circuit_view.gate_dropped.connect(self.on_gate_dropped)

    # --- 1. Gate Logic ---
    def on_gate_dropped(self, gate_type, qubit_index, time_index):
        ...

    # --- 2. Export Implementations ---
    def export_image(self):
        ...
```

### Qt/PyQt6 Patterns

- Use signals/slots for view-controller communication
- Define custom signals in classes inheriting from QObject
- Use `super().__init__()` in QObject subclasses
- Access parent view through `self.view` in controllers

### File Paths

Use absolute paths or relative to project root:

```python
# Correct
from models.circuit_model import CircuitModel

# Avoid
import sys
sys.path.insert(0, '/path/to/project')
```

## Testing Guidelines

- Tests in `software-verification/tests/`
- Use pytest, follow `test_<module_name>.py` naming
- Group tests in classes by functionality
- Tests should be independent, use descriptive names

```python
class TestCircuitModelInitialization:
    def test_default_initialization(self):
        model = CircuitModel()
        assert model.num_qubits == 3
```

## Common Development Tasks

### Adding a New Gate
1. `models/circuit_model.py` - add_gate method
2. `views/circuit_view.py` - paintEvent rendering
3. `views/palette_view.py` - gate icon
4. `models/code_generator.py` - gate mapping
5. `software-verification/tests/` - add tests

### Adding a New View Tab
1. Create view class in `views/`
2. Import and add to MainWindow in `views/main_window.py`
3. Connect signals to controller in `controllers/main_controller.py`

## Dependencies

```
PyQt6, qiskit, qiskit-aer, matplotlib, pytest (dev), pyinstaller (build)
```

## Notes

- Builds executables for Windows/macOS/Linux via GitHub Actions (`.github/workflows/build.yml`)
- Python 3.10+ required
- Avoid modifying `paintEvent` in circuit_view unless necessary