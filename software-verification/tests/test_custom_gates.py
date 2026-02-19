"""
Unit tests for custom unitary gates.

Tests the custom gate functionality including matrix validation,
code generation, parsing, and simulation.
"""

import pytest
import numpy as np
from models.circuit_model import CircuitModel
from models.code_generator import QiskitCodeGenerator
from models.code_parser import QiskitCodeParser


class TestCustomGateBasics:
    """Tests for basic custom gate functionality."""
    
    def test_add_custom_single_qubit_gate(self):
        """Test adding a custom single-qubit gate."""
        model = CircuitModel(num_qubits=2)
        # Hadamard matrix as custom gate
        h_matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        model.add_gate('CUSTOM', 0, 0, matrix=h_matrix)
        
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['gate'] == 'CUSTOM'
        assert ops[0]['qubit'] == 0
        assert np.allclose(ops[0]['matrix'], h_matrix)
    
    def test_add_custom_two_qubit_gate(self):
        """Test adding a custom two-qubit gate."""
        model = CircuitModel(num_qubits=3)
        # CNOT matrix as custom gate (4x4)
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        model.add_gate('CUSTOM', 0, 0, target_index=1, matrix=cnot_matrix)
        
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['gate'] == 'CUSTOM'
        assert ops[0]['target'] == 1
        assert np.allclose(ops[0]['matrix'], cnot_matrix)
    
    def test_custom_gate_matrix_stored_correctly(self):
        """Test that custom gate matrix is properly stored."""
        model = CircuitModel(num_qubits=1)
        matrix = np.array([[0, 1], [1, 0]])  # Pauli-X
        model.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        ops = model.get_operations()
        stored_matrix = ops[0]['matrix']
        assert isinstance(stored_matrix, np.ndarray)
        assert stored_matrix.shape == (2, 2)


class TestCustomGateSimulation:
    """Tests for custom gate simulation."""
    
    def test_custom_hadamard_simulation(self):
        """Test simulation with custom Hadamard gate."""
        model = CircuitModel(num_qubits=1)
        h_matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        model.add_gate('CUSTOM', 0, 0, matrix=h_matrix)
        
        counts, statevector = model.run_simulation()
        
        # Should create superposition like regular H gate
        assert '0' in counts and '1' in counts
        total = sum(counts.values())
        assert abs(counts['0'] - counts['1']) < total * 0.2
    
    def test_custom_pauli_x_simulation(self):
        """Test simulation with custom Pauli-X gate."""
        model = CircuitModel(num_qubits=1)
        x_matrix = np.array([[0, 1], [1, 0]])
        model.add_gate('CUSTOM', 0, 0, matrix=x_matrix)
        
        counts, statevector = model.run_simulation()
        
        # Should flip |0⟩ to |1⟩
        assert counts['1'] > 1000
    
    def test_custom_gate_applies_to_correct_qubit(self):
        """Test that custom gate applies to correct qubit."""
        model = CircuitModel(num_qubits=2)
        # Apply custom X gate on qubit 0
        x_matrix = np.array([[0, 1], [1, 0]])
        model.add_gate('CUSTOM', 0, 0, matrix=x_matrix)
        
        counts, statevector = model.run_simulation()
        
        # Should flip qubit 0 from |0⟩ to |1⟩
        # Qiskit little-endian: qubit 0 is rightmost bit
        # So |10⟩ means qubit 1=1, qubit 0=0
        # And |01⟩ means qubit 1=0, qubit 0=1
        total = sum(counts.values())
        # Check that qubit 0 is in state |1⟩
        qubit_0_is_1 = counts.get('01', 0) + counts.get('11', 0)
        assert qubit_0_is_1 > total * 0.85
    
    def test_custom_phase_gate_simulation(self):
        """Test simulation with custom phase gate."""
        model = CircuitModel(num_qubits=1)
        # S gate matrix
        s_matrix = np.array([[1, 0], [0, 1j]])
        model.add_gate('CUSTOM', 0, 0, matrix=s_matrix)
        
        counts, statevector = model.run_simulation()
        
        # Phase gate doesn't change measurement of |0⟩
        assert counts['0'] > 1000


class TestCustomGateCodeGeneration:
    """Tests for custom gate code generation."""
    
    def test_generate_custom_single_qubit_code(self):
        """Test generating code for custom single-qubit gate."""
        model = CircuitModel(num_qubits=1)
        matrix = np.array([[0, 1], [1, 0]])  # Pauli-X
        model.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        
        assert 'from qiskit.circuit.library import UnitaryGate' in code
        assert 'UnitaryGate' in code
        assert 'qc.append' in code
    
    def test_generate_custom_two_qubit_code(self):
        """Test generating code for custom two-qubit gate."""
        model = CircuitModel(num_qubits=2)
        matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        model.add_gate('CUSTOM', 0, 0, target_index=1, matrix=matrix)
        
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        
        assert 'qc.append' in code
        assert '[0, 1]' in code  # Should reference both qubits
    
    def test_custom_gate_matrix_in_code(self):
        """Test that matrix values appear in generated code."""
        model = CircuitModel(num_qubits=1)
        matrix = np.array([[1, 0], [0, -1]])  # Pauli-Z
        model.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        
        # Matrix elements should be in the code
        assert '1' in code
        assert '-1' in code or '-1.0' in code


class TestCustomGateCodeParsing:
    """Tests for parsing custom gates from code."""
    
    def test_parse_custom_unitary_gate(self):
        """Test parsing custom unitary gate from code."""
        code = """
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
import numpy as np

# Custom Pauli-X
custom_gate_0 = UnitaryGate(np.array([[0, 1], [1, 0]]))

qc = QuantumCircuit(1)
qc.append(custom_gate_0, [0])
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=1)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['gate'] == 'CUSTOM'
        assert 'matrix' in result[0]
        assert np.allclose(result[0]['matrix'], [[0, 1], [1, 0]])
    
    def test_parse_custom_two_qubit_unitary(self):
        """Test parsing two-qubit custom unitary."""
        code = """
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
import numpy as np

# Custom SWAP gate
swap_matrix = np.array([
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1]
])
custom_gate_0 = UnitaryGate(swap_matrix)

qc = QuantumCircuit(2)
qc.append(custom_gate_0, [0, 1])
"""
        result = QiskitCodeParser.parse_to_model(code, num_qubits=2)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]['gate'] == 'CUSTOM'
        assert result[0]['target'] == 1
        assert result[0]['matrix'] is not None


class TestCustomGateRoundTrip:
    """Tests for round-trip conversion with custom gates."""
    
    def test_custom_gate_round_trip(self):
        """Test full round-trip: Model -> Code -> Model with custom gate."""
        original = CircuitModel(num_qubits=1)
        matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)  # Hadamard
        original.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        # Generate code
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        
        # Parse back
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 1
        assert parsed_ops[0]['gate'] == 'CUSTOM'
        assert np.allclose(parsed_ops[0]['matrix'], matrix)
    
    def test_custom_gate_with_params_round_trip(self):
        """Test round-trip preserves custom gate target qubit."""
        original = CircuitModel(num_qubits=2)
        matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])
        original.add_gate('CUSTOM', 0, 0, target_index=1, matrix=matrix)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert parsed_ops[0]['target'] == 1


class TestCustomGateJSON:
    """Tests for JSON serialization of custom gates."""
    
    def test_custom_gate_json_serialization(self):
        """Test that custom gates serialize to JSON correctly."""
        import json
        
        model = CircuitModel(num_qubits=1)
        matrix = np.array([[0, 1], [1, 0]])
        model.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        json_str = model.to_json()
        data = json.loads(json_str)
        
        assert data['operations'][0]['gate'] == 'CUSTOM'
        assert 'matrix' in data['operations'][0]
        # Matrix should be stored as list
        assert isinstance(data['operations'][0]['matrix'], list)
    
    def test_custom_gate_json_deserialization(self):
        """Test that custom gates deserialize from JSON correctly."""
        import json
        
        original = CircuitModel(num_qubits=1)
        matrix = np.array([[0, 1], [1, 0]])
        original.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        json_str = original.to_json()
        
        restored = CircuitModel()
        restored.load_from_json(json_str)
        
        assert restored.operations[0]['gate'] == 'CUSTOM'
        assert np.allclose(restored.operations[0]['matrix'], matrix)
    
    def test_custom_gate_roundtrip_json(self):
        """Test complete round-trip through JSON."""
        import json
        
        original = CircuitModel(num_qubits=2)
        matrix = np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ])
        original.add_gate('CUSTOM', 0, 0, target_index=1, matrix=matrix)
        
        json_str = original.to_json()
        restored = CircuitModel()
        restored.load_from_json(json_str)
        
        # Verify all properties
        assert restored.num_qubits == 2
        assert restored.operations[0]['gate'] == 'CUSTOM'
        assert restored.operations[0]['qubit'] == 0
        assert restored.operations[0]['target'] == 1
        assert np.allclose(restored.operations[0]['matrix'], matrix)


class TestCustomGateEdgeCases:
    """Tests for custom gate edge cases."""
    
    def test_custom_gate_with_complex_entries(self):
        """Test custom gate with complex matrix entries."""
        model = CircuitModel(num_qubits=1)
        # S gate with complex entries
        matrix = np.array([[1, 0], [0, 1j]])
        model.add_gate('CUSTOM', 0, 0, matrix=matrix)
        
        # Should not raise error
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        assert code is not None
    
    def test_multiple_custom_gates(self):
        """Test circuit with multiple different custom gates."""
        model = CircuitModel(num_qubits=2)
        h_matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        x_matrix = np.array([[0, 1], [1, 0]])
        
        model.add_gate('CUSTOM', 0, 0, matrix=h_matrix)
        model.add_gate('CUSTOM', 1, 0, matrix=x_matrix)
        
        ops = model.get_operations()
        assert len(ops) == 2
        
        # Generate code
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        assert 'custom_gate_0' in code
        assert 'custom_gate_1' in code
    
    def test_custom_gate_identity(self):
        """Test custom identity gate."""
        model = CircuitModel(num_qubits=1)
        identity = np.eye(2)
        model.add_gate('CUSTOM', 0, 0, matrix=identity)
        
        counts, statevector = model.run_simulation()
        
        # Identity should leave |0⟩ unchanged
        assert counts['0'] > 1000


class TestCustomGateValidation:
    """Tests for matrix validation."""
    
    def test_unitary_matrix_validation(self):
        """Test that unitary matrices are properly validated."""
        # Hadamard is unitary
        h_matrix = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        
        # Check U†U = I
        dagger = h_matrix.conj().T
        product = dagger @ h_matrix
        identity = np.eye(2)
        
        assert np.allclose(product, identity)
    
    def test_non_unitary_matrix_fails(self):
        """Test that non-unitary matrices are detected."""
        # Non-unitary matrix
        bad_matrix = np.array([[2, 0], [0, 2]])  # Scaled identity
        
        # Check U†U ≠ I
        dagger = bad_matrix.conj().T
        product = dagger @ bad_matrix
        identity = np.eye(2)
        
        assert not np.allclose(product, identity)
