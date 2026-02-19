#!/usr/bin/env python3
"""
Quick validation test runner.

Runs a subset of critical tests without requiring pytest.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.circuit_model import CircuitModel
from models.code_generator import QiskitCodeGenerator
from models.code_parser import QiskitCodeParser


def test_circuit_creation():
    """Test basic circuit creation."""
    model = CircuitModel(num_qubits=3)
    assert model.num_qubits == 3
    assert len(model.get_operations()) == 0
    print("✓ Circuit creation works")


def test_gate_addition():
    """Test adding gates."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('H', 0, 0)
    model.add_gate('CX', 0, 1, target_index=1)
    
    ops = model.get_operations()
    assert len(ops) == 2
    assert ops[0]['gate'] == 'H'
    assert ops[1]['gate'] == 'CX'
    print("✓ Gate addition works")


def test_gate_removal():
    """Test removing gates."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('H', 0, 0)
    model.remove_gate(0, 0)
    
    assert len(model.get_operations()) == 0
    print("✓ Gate removal works")


def test_gate_move():
    """Test moving gates."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('H', 0, 0)
    result = model.move_gate(0, 0, 1, 1)
    
    assert result is True
    ops = model.get_operations()
    assert ops[0]['qubit'] == 1
    assert ops[0]['index'] == 1
    print("✓ Gate movement works")


def test_code_generation():
    """Test code generation."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('H', 0, 0)
    model.add_gate('CX', 0, 1, target_index=1)
    
    code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
    
    assert 'from qiskit import QuantumCircuit' in code
    assert 'qc.h(0)' in code
    assert 'qc.cx(0, 1)' in code
    assert 'qc.measure_all()' in code
    print("✓ Code generation works")


def test_code_parsing():
    """Test code parsing."""
    code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
"""
    result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
    
    assert result is not None
    assert len(result) == 2
    assert result[0]['gate'] == 'H'
    assert result[1]['gate'] == 'CX'
    print("✓ Code parsing works")


def test_round_trip():
    """Test round-trip conversion."""
    original = CircuitModel(num_qubits=2)
    original.add_gate('H', 0, 0)
    original.add_gate('CX', 0, 1, target_index=1)
    
    # Generate code
    code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
    
    # Parse back
    parsed = QiskitCodeParser.parse_to_model(code, original.num_qubits)
    
    assert parsed is not None
    assert len(parsed) == 2
    assert parsed[0]['gate'] == 'H'
    assert parsed[1]['gate'] == 'CX'
    print("✓ Round-trip conversion works")


def test_simulation():
    """Test circuit simulation."""
    model = CircuitModel(num_qubits=1)
    model.add_gate('H', 0, 0)
    
    counts, statevector = model.run_simulation()
    
    # Check we got measurement results
    assert len(counts) > 0
    assert statevector is not None
    print("✓ Circuit simulation works")


def test_json_serialization():
    """Test JSON serialization."""
    import json
    
    original = CircuitModel(num_qubits=2)
    original.add_gate('H', 0, 0)
    
    # Serialize
    json_str = original.to_json()
    data = json.loads(json_str)
    
    assert data['num_qubits'] == 2
    assert len(data['operations']) == 1
    
    # Deserialize
    restored = CircuitModel()
    restored.load_from_json(json_str)
    
    assert restored.num_qubits == 2
    assert len(restored.get_operations()) == 1
    print("✓ JSON serialization works")


def main():
    print("Running quick validation tests...\n")
    
    tests = [
        test_circuit_creation,
        test_gate_addition,
        test_gate_removal,
        test_gate_move,
        test_code_generation,
        test_code_parsing,
        test_round_trip,
        test_simulation,
        test_json_serialization,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
