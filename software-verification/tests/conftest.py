"""
Test fixtures and utilities for quantum circuit verification.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.circuit_model import CircuitModel
from models.code_generator import QiskitCodeGenerator
from models.code_parser import QiskitCodeParser


@pytest.fixture
def empty_circuit():
    """Returns an empty CircuitModel with 3 qubits."""
    return CircuitModel(num_qubits=3)


@pytest.fixture
def single_qubit_circuit():
    """Returns a circuit with a single Hadamard gate on qubit 0."""
    model = CircuitModel(num_qubits=3)
    model.add_gate('H', 0, 0)
    return model


@pytest.fixture
def bell_state_circuit():
    """Returns a circuit that creates a Bell state (|00> + |11>)/sqrt(2)."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('H', 0, 0)
    model.add_gate('CX', 0, 1, target_index=1)
    return model


@pytest.fixture
def rotation_circuit():
    """Returns a circuit with rotation gates."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('RX', 0, 0, params=1.5708)  # pi/2
    model.add_gate('RY', 1, 0, params=0.7854)  # pi/4
    return model


@pytest.fixture
def sample_operations():
    """Returns a list of sample operations for testing code generation."""
    return [
        {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
        {'gate': 'X', 'qubit': 1, 'target': None, 'params': None, 'index': 0},
        {'gate': 'CX', 'qubit': 0, 'target': 1, 'params': None, 'index': 1},
        {'gate': 'RX', 'qubit': 0, 'target': None, 'params': 1.5708, 'index': 2},
    ]


@pytest.fixture
def code_generator():
    """Returns a QiskitCodeGenerator instance."""
    return QiskitCodeGenerator()


@pytest.fixture
def code_parser():
    """Returns a QiskitCodeParser instance."""
    return QiskitCodeParser()


class CircuitTestHelper:
    """Helper class for common test operations."""
    
    @staticmethod
    def count_gates(circuit_model, gate_type=None):
        """Count gates in a circuit, optionally filtered by type."""
        ops = circuit_model.get_operations()
        if gate_type:
            return len([op for op in ops if op['gate'].upper() == gate_type.upper()])
        return len(ops)
    
    @staticmethod
    def gate_exists_at(circuit_model, qubit, time_index):
        """Check if a gate exists at a specific position."""
        ops = circuit_model.get_operations()
        return any(op['qubit'] == qubit and op['index'] == time_index for op in ops)
    
    @staticmethod
    def assert_valid_qiskit_code(code_str):
        """Verify that generated code is valid Python/Qiskit code."""
        assert 'from qiskit import QuantumCircuit' in code_str
        assert 'qc = QuantumCircuit' in code_str
        assert 'qc.measure_all()' in code_str
