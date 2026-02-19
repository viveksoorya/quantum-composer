# Software Verification

This folder contains comprehensive tests and validation scripts for the Quantum Circuit Composer application.

## 📁 Folder Structure

```
software-verification/
├── tests/                    # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures and utilities
│   ├── test_circuit_model.py    # Tests for CircuitModel
│   ├── test_code_generator.py   # Tests for QiskitCodeGenerator
│   ├── test_code_parser.py      # Tests for QiskitCodeParser
│   └── test_integration.py      # Integration tests
├── validation/              # Validation scripts
│   ├── validate_circuits.py     # Quantum correctness validation
│   └── run_quick_tests.py       # Quick validation runner
├── __init__.py
└── README.md               # This file
```

## 🚀 Quick Start

### Option 1: Quick Validation (No pytest required)

Run basic validation without installing pytest:

```bash
python software-verification/validation/run_quick_tests.py
```

### Option 2: Quantum Correctness Validation

Validate quantum mechanical behavior:

```bash
python software-verification/validation/validate_circuits.py
```

With verbose output:

```bash
python software-verification/validation/validate_circuits.py --verbose
```

### Option 3: Full Test Suite (requires pytest)

Install pytest:

```bash
pip install pytest pytest-cov
```

Run all tests:

```bash
python -m pytest software-verification/tests/ -v
```

Run with coverage report:

```bash
python -m pytest software-verification/tests/ --cov=models --cov-report=html
```

Run specific test file:

```bash
python -m pytest software-verification/tests/test_circuit_model.py -v
```

Run specific test class:

```bash
python -m pytest software-verification/tests/test_circuit_model.py::TestGateOperations -v
```

## 🧪 Test Coverage

### Unit Tests

**test_circuit_model.py**
- Circuit initialization
- Gate operations (add, remove, move)
- Single-qubit gates (H, X, Y, Z, S, T)
- Multi-qubit gates (CX, SWAP, CZ)
- Rotation gates (RX, RY, RZ, P)
- JSON serialization/deserialization
- Circuit simulation

**test_code_generator.py**
- Code structure validation
- Single-qubit gate generation
- Rotation gate generation with parameters
- Multi-qubit gate generation
- Operation ordering
- Complete circuit generation

**test_code_parser.py**
- Parser initialization and error handling
- Single-qubit gate parsing
- Rotation gate parsing with parameters
- Multi-qubit gate parsing
- Timing and operation ordering
- Edge cases and error handling

### Integration Tests

**test_integration.py**
- Round-trip conversion (Model → Code → Model)
- Simulation accuracy validation
- Code execution verification
- JSON serialization integration
- Edge cases and boundary conditions

### Validation Scripts

**validate_circuits.py**
- Superposition validation
- Pauli gate behavior
- Bell state creation
- CNOT operations
- SWAP gate functionality
- Quantum identity operations

## 📊 Test Reports

Generate HTML coverage report:

```bash
python -m pytest software-verification/tests/ --cov=models --cov-report=html --cov-report=term
```

View the report at `htmlcov/index.html`.

## 🔧 Writing New Tests

### Adding Unit Tests

Create test classes that inherit from the base test structure:

```python
class TestNewFeature:
    def test_something(self):
        model = CircuitModel(num_qubits=2)
        # Your test code here
        assert condition
```

### Using Fixtures

Available fixtures in `conftest.py`:
- `empty_circuit` - Empty 3-qubit circuit
- `single_qubit_circuit` - Circuit with H gate on qubit 0
- `bell_state_circuit` - Bell state preparation circuit
- `rotation_circuit` - Circuit with rotation gates
- `code_generator` - QiskitCodeGenerator instance
- `code_parser` - QiskitCodeParser instance

Example usage:

```python
def test_with_fixture(empty_circuit):
    empty_circuit.add_gate('X', 0, 0)
    assert len(empty_circuit.get_operations()) == 1
```

### Adding Validation Tests

Add new validation functions to `validation/validate_circuits.py`:

```python
def validate_new_feature():
    model = CircuitModel(num_qubits=2)
    # Set up circuit
    # Run simulation
    # Return (passed: bool, details: str)
    return passed, "details"
```

Then add to the tests list in `main()`:

```python
tests = [
    # ... existing tests ...
    ("New Feature", validate_new_feature),
]
```

## 🐛 Debugging Failed Tests

Run a single test with maximum verbosity:

```bash
python -m pytest software-verification/tests/test_circuit_model.py::TestGateOperations::test_add_single_qubit_gate -vvs
```

Enable Python warnings:

```bash
python -m pytest software-verification/tests/ -v -W error
```

## 📝 Continuous Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/test.yml example
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Install dependencies
      run: pip install -r requirements.txt pytest pytest-cov
    - name: Run tests
      run: python -m pytest software-verification/tests/ -v
    - name: Run validation
      run: python software-verification/validation/validate_circuits.py
```

## 📚 Additional Resources

- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Quantum Computing Concepts](https://qiskit.org/textbook/preface.html)

## 🤝 Contributing

When adding new features:

1. Write unit tests in the appropriate test file
2. Add integration tests if the feature interacts with multiple components
3. Add validation tests if the feature affects quantum correctness
4. Ensure all tests pass before submitting
5. Maintain test coverage above 80%

## 📄 License

These tests are part of the Quantum Circuit Composer project and follow the same license.
