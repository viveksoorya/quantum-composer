"""
Unit tests for the QiskitCodeGenerator class.

Tests code generation from circuit operations.
"""

import pytest
from models.code_generator import QiskitCodeGenerator


class TestQiskitCodeGeneratorBasics:
    """Tests for basic code generation functionality."""
    
    def test_generator_initialization(self):
        """Test that generator can be instantiated."""
        generator = QiskitCodeGenerator()
        assert generator is not None
    
    def test_empty_circuit_generation(self):
        """Test generating code for empty circuit."""
        code = QiskitCodeGenerator.generate(num_qubits=3, operations=[])
        
        assert 'from qiskit import QuantumCircuit' in code
        assert 'qc = QuantumCircuit(3)' in code
        assert 'qc.measure_all()' in code
    
    def test_import_statements(self):
        """Test that required imports are included."""
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=[])
        
        assert 'import numpy as np' in code
        assert 'from qiskit import QuantumCircuit' in code


class TestSingleQubitGates:
    """Tests for single-qubit gate code generation."""
    
    def test_hadamard_gate(self):
        """Test generating Hadamard gate code."""
        operations = [{'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.h(0)' in code
    
    def test_pauli_x_gate(self):
        """Test generating Pauli-X gate code."""
        operations = [{'gate': 'X', 'qubit': 1, 'target': None, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        assert 'qc.x(1)' in code
    
    def test_pauli_y_gate(self):
        """Test generating Pauli-Y gate code."""
        operations = [{'gate': 'Y', 'qubit': 0, 'target': None, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.y(0)' in code
    
    def test_pauli_z_gate(self):
        """Test generating Pauli-Z gate code."""
        operations = [{'gate': 'Z', 'qubit': 0, 'target': None, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.z(0)' in code
    
    def test_s_gate(self):
        """Test generating S gate code."""
        operations = [{'gate': 'S', 'qubit': 0, 'target': None, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.s(0)' in code
    
    def test_t_gate(self):
        """Test generating T gate code."""
        operations = [{'gate': 'T', 'qubit': 0, 'target': None, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.t(0)' in code
    
    def test_multiple_single_qubit_gates(self):
        """Test generating multiple single-qubit gates."""
        operations = [
            {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
            {'gate': 'X', 'qubit': 1, 'target': None, 'params': None, 'index': 0},
            {'gate': 'Z', 'qubit': 2, 'target': None, 'params': None, 'index': 0},
        ]
        code = QiskitCodeGenerator.generate(num_qubits=3, operations=operations)
        
        assert 'qc.h(0)' in code
        assert 'qc.x(1)' in code
        assert 'qc.z(2)' in code


class TestRotationGates:
    """Tests for rotation gate code generation."""
    
    def test_rx_gate(self):
        """Test generating RX rotation gate code."""
        operations = [{'gate': 'RX', 'qubit': 0, 'target': None, 'params': 1.5708, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.rx(1.5708, 0)' in code
    
    def test_ry_gate(self):
        """Test generating RY rotation gate code."""
        operations = [{'gate': 'RY', 'qubit': 1, 'target': None, 'params': 0.7854, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        assert 'qc.ry(0.7854, 1)' in code
    
    def test_rz_gate(self):
        """Test generating RZ rotation gate code."""
        operations = [{'gate': 'RZ', 'qubit': 0, 'target': None, 'params': 3.14159, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.rz(3.14159, 0)' in code
    
    def test_phase_gate(self):
        """Test generating Phase gate code."""
        operations = [{'gate': 'P', 'qubit': 0, 'target': None, 'params': 1.0, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.p(1.0, 0)' in code
    
    def test_rotation_gate_negative_params(self):
        """Test rotation gate with negative parameters."""
        operations = [{'gate': 'RX', 'qubit': 0, 'target': None, 'params': -1.5708, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.rx(-1.5708, 0)' in code
    
    def test_rotation_gate_zero_params(self):
        """Test rotation gate with zero parameter."""
        operations = [{'gate': 'RY', 'qubit': 0, 'target': None, 'params': 0.0, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        assert 'qc.ry(0.0, 0)' in code


class TestMultiQubitGates:
    """Tests for multi-qubit gate code generation."""
    
    def test_cnot_gate(self):
        """Test generating CNOT gate code."""
        operations = [{'gate': 'CX', 'qubit': 0, 'target': 1, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        assert 'qc.cx(0, 1)' in code
    
    def test_cnot_different_qubits(self):
        """Test CNOT with different control and target qubits."""
        operations = [{'gate': 'CX', 'qubit': 2, 'target': 0, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=3, operations=operations)
        
        assert 'qc.cx(2, 0)' in code
    
    def test_swap_gate(self):
        """Test generating SWAP gate code."""
        operations = [{'gate': 'SWAP', 'qubit': 0, 'target': 1, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        assert 'qc.swap(0, 1)' in code
    
    def test_cz_gate(self):
        """Test generating CZ gate code."""
        operations = [{'gate': 'CZ', 'qubit': 0, 'target': 1, 'params': None, 'index': 0}]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        assert 'qc.cz(0, 1)' in code


class TestCodeOrdering:
    """Tests for operation ordering in generated code."""
    
    def test_operations_sorted_by_index(self):
        """Test that operations are sorted by time index."""
        operations = [
            {'gate': 'X', 'qubit': 0, 'target': None, 'params': None, 'index': 2},
            {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
            {'gate': 'Z', 'qubit': 0, 'target': None, 'params': None, 'index': 1},
        ]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        lines = [line for line in code.split('\n') if line.startswith('qc.') and 'measure' not in line]
        assert lines[0] == 'qc.h(0)'
        assert lines[1] == 'qc.z(0)'
        assert lines[2] == 'qc.x(0)'
    
    def test_same_index_operations(self):
        """Test operations with same time index."""
        operations = [
            {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
            {'gate': 'X', 'qubit': 1, 'target': None, 'params': None, 'index': 0},
        ]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        # Both gates should be present
        assert 'qc.h(0)' in code
        assert 'qc.x(1)' in code


class TestCompleteCircuits:
    """Tests for complete circuit generation."""
    
    def test_bell_state_circuit(self):
        """Test generating Bell state circuit code."""
        operations = [
            {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
            {'gate': 'CX', 'qubit': 0, 'target': 1, 'params': None, 'index': 1},
        ]
        code = QiskitCodeGenerator.generate(num_qubits=2, operations=operations)
        
        assert 'qc = QuantumCircuit(2)' in code
        assert 'qc.h(0)' in code
        assert 'qc.cx(0, 1)' in code
        assert 'qc.measure_all()' in code
    
    def test_complex_circuit(self):
        """Test generating a complex circuit with multiple gate types."""
        operations = [
            {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
            {'gate': 'RX', 'qubit': 1, 'target': None, 'params': 1.5708, 'index': 0},
            {'gate': 'CX', 'qubit': 0, 'target': 1, 'params': None, 'index': 1},
            {'gate': 'SWAP', 'qubit': 1, 'target': 2, 'params': None, 'index': 2},
        ]
        code = QiskitCodeGenerator.generate(num_qubits=3, operations=operations)
        
        assert 'qc = QuantumCircuit(3)' in code
        assert 'qc.h(0)' in code
        assert 'qc.rx(1.5708, 1)' in code
        assert 'qc.cx(0, 1)' in code
        assert 'qc.swap(1, 2)' in code
        assert 'qc.measure_all()' in code
    
    def test_executable_code_structure(self):
        """Test that generated code has valid Python structure."""
        operations = [
            {'gate': 'H', 'qubit': 0, 'target': None, 'params': None, 'index': 0},
        ]
        code = QiskitCodeGenerator.generate(num_qubits=1, operations=operations)
        
        lines = code.strip().split('\n')
        assert 'from qiskit import QuantumCircuit' in lines
        assert 'import numpy as np' in lines
        assert 'qc = QuantumCircuit(1)' in code
        assert 'qc.measure_all()' in code
