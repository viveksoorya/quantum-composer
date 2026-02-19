"""
Unit tests for the QiskitCodeParser class.

Tests parsing Qiskit code back to circuit operations.
"""

import pytest
from models.code_parser import QiskitCodeParser


class TestQiskitCodeParserBasics:
    """Tests for basic parser functionality."""
    
    def test_parser_initialization(self):
        """Test that parser can be instantiated."""
        parser = QiskitCodeParser()
        assert parser is not None
    
    def test_parse_empty_code(self):
        """Test parsing code without circuit definition."""
        code = "from qiskit import QuantumCircuit"
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is None
    
    def test_parse_invalid_code(self):
        """Test parsing syntactically invalid code."""
        code = "this is not valid python"
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is None
    
    def test_parse_non_circuit_variable(self):
        """Test parsing code without 'qc' variable."""
        code = """
from qiskit import QuantumCircuit
other = QuantumCircuit(1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is None


class TestSingleQubitGateParsing:
    """Tests for parsing single-qubit gates."""
    
    def test_parse_hadamard(self):
        """Test parsing Hadamard gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['gate'] == 'H'
        assert result[0]['qubit'] == 0
        assert result[0]['target'] is None
    
    def test_parse_pauli_x(self):
        """Test parsing Pauli-X gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.x(1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert result[0]['gate'] == 'X'
        assert result[0]['qubit'] == 1
    
    def test_parse_pauli_y(self):
        """Test parsing Pauli-Y gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.y(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'Y'
    
    def test_parse_pauli_z(self):
        """Test parsing Pauli-Z gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.z(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'Z'
    
    def test_parse_s_gate(self):
        """Test parsing S gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.s(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'S'
    
    def test_parse_t_gate(self):
        """Test parsing T gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.t(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'T'
    
    def test_parse_multiple_single_qubit_gates(self):
        """Test parsing multiple single-qubit gates."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(3)
qc.h(0)
qc.x(1)
qc.z(2)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=3)
        
        assert result is not None
        assert len(result) == 3
        gates = [op['gate'] for op in result]
        assert 'H' in gates
        assert 'X' in gates
        assert 'Z' in gates


class TestRotationGateParsing:
    """Tests for parsing rotation gates."""
    
    def test_parse_rx_gate(self):
        """Test parsing RX rotation gate."""
        code = """
from qiskit import QuantumCircuit
import numpy as np
qc = QuantumCircuit(1)
qc.rx(1.5708, 0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'RX'
        assert result[0]['params'] == 1.5708
        assert result[0]['qubit'] == 0
    
    def test_parse_ry_gate(self):
        """Test parsing RY rotation gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.ry(0.7854, 0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'RY'
        assert result[0]['params'] == 0.7854
    
    def test_parse_rz_gate(self):
        """Test parsing RZ rotation gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.rz(3.14159, 0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'RZ'
    
    def test_parse_phase_gate(self):
        """Test parsing Phase gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.p(1.0, 0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'P'


class TestMultiQubitGateParsing:
    """Tests for parsing multi-qubit gates."""
    
    def test_parse_cnot(self):
        """Test parsing CNOT gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.cx(0, 1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['gate'] == 'CX'
        assert result[0]['qubit'] == 0
        assert result[0]['target'] == 1
    
    def test_parse_cnot_reverse(self):
        """Test parsing CNOT with different control/target."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(3)
qc.cx(2, 0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=3)
        
        assert result is not None
        assert result[0]['gate'] == 'CX'
        assert result[0]['qubit'] == 2
        assert result[0]['target'] == 0
    
    def test_parse_swap(self):
        """Test parsing SWAP gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.swap(0, 1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert result[0]['gate'] == 'SWAP'
    
    def test_parse_cz(self):
        """Test parsing CZ gate."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.cz(0, 1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert result[0]['gate'] == 'CZ'


class TestTimingAndOrdering:
    """Tests for operation timing and ordering."""
    
    def test_sequential_gates_different_time(self):
        """Test that sequential gates get different time indices."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.h(0)
qc.x(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert len(result) == 2
        assert result[0]['index'] == 0
        assert result[1]['index'] == 1
    
    def test_parallel_gates_same_time(self):
        """Test that parallel gates on different qubits get same time index."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.h(1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert len(result) == 2
        # Both should be at time 0 since they don't interfere
        assert result[0]['index'] == 0
        assert result[1]['index'] == 0
    
    def test_multi_qubit_affects_timing(self):
        """Test that multi-qubit gates affect timing of qubits in range."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(3)
qc.h(0)
qc.cx(0, 2)  # Affects qubits 0, 1, 2
qc.x(1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=3)
        
        assert result is not None
        # The X gate on qubit 1 should be at time 2 because CX spans qubits 0-2
        x_gate = [op for op in result if op['gate'] == 'X'][0]
        assert x_gate['index'] == 2


class TestCompleteCircuitParsing:
    """Tests for parsing complete circuits."""
    
    def test_bell_state_circuit(self):
        """Test parsing Bell state circuit."""
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
    
    def test_complex_circuit(self):
        """Test parsing a complex circuit."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(3)
qc.h(0)
qc.rx(1.5708, 1)
qc.cx(0, 1)
qc.swap(1, 2)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=3)
        
        assert result is not None
        gates = [op['gate'] for op in result]
        assert 'H' in gates
        assert 'RX' in gates
        assert 'CX' in gates
        assert 'SWAP' in gates
    
    def test_unknown_gate_causes_failure(self):
        """Test that unknown gates cause parsing to fail."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.h(0)
qc.custom_gate(0)  # Unknown gate - causes exec to fail
qc.x(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        # Unknown gates cause the exec to fail, so parser returns None
        assert result is None


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_circuit(self):
        """Test parsing circuit with no operations."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert len(result) == 0
    
    def test_code_with_print_statements(self):
        """Test parsing code that includes print statements."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
print("Creating circuit")
qc.h(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['gate'] == 'H'
    
    def test_code_with_comments(self):
        """Test parsing code with comments."""
        code = """
from qiskit import QuantumCircuit
# Create a quantum circuit
qc = QuantumCircuit(1)
qc.h(0)  # Apply Hadamard
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'H'
    
    def test_missing_numpy_import(self):
        """Test parsing code without explicit numpy import."""
        code = """
from qiskit import QuantumCircuit
qc = QuantumCircuit(1)
qc.h(0)
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert result[0]['gate'] == 'H'
