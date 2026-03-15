# AGENTS.md - Quantum Composer Development Guide

## Project Overview

Quantum Composer is a PyQt6-based drag-and-drop quantum circuit designer that generates Qiskit code in real-time. The project uses a strict **Model-View-Controller (MVC)** architecture.

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
│   ├── visualization_view.py # Matplotlib charts
│   └── styles.py             # CSS themes
└── controllers/              # Business logic
    └── main_controller.py    # Event handling & simulation
```

---

## Build, Lint, and Test Commands

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run from source
python main.py
```

### Building Executables

```bash
# Install pyinstaller
pip install pyinstaller

# Build for current OS (example for Linux)
pyinstaller --noconsole --onefile --collect-all qiskit --collect-all qiskit_aer --hidden-import=matplotlib --name="QuantumComposer" main.py
```

### Running Tests

Tests are located in `software-verification/tests/`:

```bash
# Install pytest
pip install pytest

# Run all tests
pytest software-verification/tests/

# Run a specific test file
pytest software-verification/tests/test_circuit_model.py

# Run a specific test class
pytest software-verification/tests/test_circuit_model.py::TestCircuitModelInitialization

# Run a single test method (Recommended for debugging)
pytest software-verification/tests/test_circuit_model.py::TestCircuitModelInitialization::test_default_initialization

# Run with verbose output
pytest software-verification/tests/ -v
```

---

## Code Style Guidelines

### Imports

Order imports in the following groups (separate each group with a blank line):
1. Standard library modules
2. Third-party packages (PyQt6, qiskit, numpy, matplotlib)
3. Local application modules

```python
# Correct
import sys
import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np

from models.circuit_model import CircuitModel
from views.main_window import MainWindow
from controllers.main_controller import MainController

# Inside PyQt6, group by: QtCore -> QtGui -> QtWidgets
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `CircuitModel`, `MainWindow`, `QiskitCodeGenerator`)
- **Functions/variables**: snake_case (e.g., `add_gate`, `num_qubits`, `is_path_clear`)
- **Constants**: SCREAMING_SNAKE_CASE (e.g., `LIGHT_THEME`)
- **Private methods**: Prefix with underscore (e.g., `_internal_method`)

### Type Annotations

Currently the codebase does **not** use type hints. However, when adding new code, prefer adding type annotations:

```python
# Preferred for new code
def add_gate(self, gate_type: str, qubit_index: int, time_index: int, 
             target_index: int | None = None, params: float | None = None) -> None:
    ...

# Acceptable legacy style without types
def add_gate(self, gate_type, qubit_index, time_index, target_index=None, params=None):
    ...
```

### Error Handling

- Use **try/except** for operations that may fail (file I/O, parsing, simulation)
- Show user-friendly errors with **QMessageBox.warning()** for UI errors
- Return `None` or `False` for recoverable errors rather than raising exceptions
- Log errors with print statements for debugging

```python
# Example: File operations
try:
    with open(fname, 'w') as f:
        f.write(code)
    print(f"Code saved to {fname}")
except IOError as e:
    QMessageBox.warning(self.view, "Save Error", f"Could not save file: {e}")

# Example: User input validation
text, ok = QInputDialog.getText(self.view, "Rotation Angle", "Enter Angle (radians):", text="1.57")
if ok and text:
    try:
        params = float(text)
    except ValueError:
        return  # Invalid input, silently ignore
```

### Code Organization

- **Class methods**: Group by functionality with comment headers
- **Signal connections**: Place all signal connections in `__init__` or a dedicated `setup_signals()` method
- **Keep methods focused**: Each method should do one thing

```python
class MainController:
    def __init__(self, view):
        self.view = view
        self.model = CircuitModel(num_qubits=3)
        
        # --- View Signals ---
        self.view.circuit_view.gate_dropped.connect(self.on_gate_dropped)
        self.view.circuit_view.gate_deleted.connect(self.on_gate_deleted)
        
        # --- Initial Render ---
        self.update_full_ui()

    # --- 1. Gate Logic ---
    def on_gate_dropped(self, gate_type, qubit_index, time_index):
        ...

    # --- 2. Export Implementations ---
    def export_image(self):
        ...
```

### Qt/PyQt6 Patterns

- Use **signals and slots** for communication between views and controllers
- Define custom signals in classes inheriting from QObject
- Use `super().__init__()` in all QObject subclasses
- Access parent view through `self.view` in controllers

```python
# Custom signal in a view
from PyQt6.QtCore import pyqtSignal, QObject

class CircuitView(QWidget):
    gate_dropped = pyqtSignal(str, int, int)  # gate_type, qubit, time
    
    def some_method(self):
        self.gate_dropped.emit("H", 0, 1)
```

### File Paths

Always use absolute paths or relative to the project root. When accessing project files:

```python
# Correct
from models.circuit_model import CircuitModel
from views.main_window import MainWindow

# Avoid
import sys
sys.path.insert(0, '/path/to/project')
```

---

## Testing Guidelines

### Writing Tests

- Place tests in `software-verification/tests/`
- Use pytest framework
- Follow the naming convention: `test_<module_name>.py`
- Group tests in classes by functionality

```python
import pytest
from models.circuit_model import CircuitModel

class TestCircuitModelInitialization:
    """Tests for CircuitModel initialization."""
    
    def test_default_initialization(self):
        """Test that CircuitModel initializes with default values."""
        model = CircuitModel()
        assert model.num_qubits == 3
        assert model.operations == []
```

### Test Best Practices

- Each test should be independent and not rely on execution order
- Use descriptive test names that explain what is being tested
- Test both success and failure cases
- Use meaningful assertions with clear error messages

---

## Common Development Tasks

### Adding a New Gate

1. Add gate handling in `models/circuit_model.py` (`add_gate` method)
2. Add gate rendering in `views/circuit_view.py` (`paintEvent`)
3. Add gate icon in `views/palette_view.py`
4. Add gate mapping in `models/code_generator.py`
5. Add tests in `software-verification/tests/test_circuit_model.py`

### Adding a New View Tab

1. Create new view class in `views/`
2. Import and add to `MainWindow` in `views/main_window.py`
3. Connect signals to controller in `controllers/main_controller.py`

---

## Dependencies

```
PyQt6
qiskit
qiskit-aer
matplotlib
pytest (dev)
pyinstaller (build)
```

---

## Notes

- The project builds executables for Windows, macOS, and Linux using GitHub Actions (see `.github/workflows/build.yml`)
- Qiskit version should be compatible with Python 3.10+
- The application uses custom painting for the circuit grid - avoid modifying `paintEvent` unless necessary
