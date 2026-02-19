"""
Integration tests for the Quantum Circuit Composer.

Tests the interaction between models, code generation, and parsing.
"""

import pytest
from models.circuit_model import CircuitModel
from models.code_generator import QiskitCodeGenerator
from models.code_parser import QiskitCodeParser


class TestRoundTripConversion:
    """Tests for round-trip conversion: Model -> Code -> Model."""
    
    def test_single_gate_roundtrip(self):
        """Test round-trip conversion of a single gate."""
        # Create original circuit
        original = CircuitModel(num_qubits=1)
        original.add_gate('H', 0, 0)
        
        # Generate code
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        
        # Parse back
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        # Verify
        assert parsed_ops is not None
        assert len(parsed_ops) == 1
        assert parsed_ops[0]['gate'] == 'H'
        assert parsed_ops[0]['qubit'] == 0
    
    def test_multiple_gates_roundtrip(self):
        """Test round-trip conversion of multiple gates."""
        original = CircuitModel(num_qubits=2)
        original.add_gate('H', 0, 0)
        original.add_gate('X', 1, 0)
        original.add_gate('CX', 0, 1, target_index=1)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 3
        gates = [op['gate'] for op in parsed_ops]
        assert 'H' in gates
        assert 'X' in gates
        assert 'CX' in gates
    
    def test_rotation_gates_roundtrip(self):
        """Test round-trip conversion of rotation gates."""
        original = CircuitModel(num_qubits=2)
        original.add_gate('RX', 0, 0, params=1.5708)
        original.add_gate('RY', 1, 0, params=0.7854)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 2
        
        # Find RX gate and verify its parameter
        rx_gate = [op for op in parsed_ops if op['gate'] == 'RX'][0]
        assert rx_gate['params'] == 1.5708
    
    def test_bell_state_roundtrip(self):
        """Test round-trip conversion of Bell state circuit."""
        original = CircuitModel(num_qubits=2)
        original.add_gate('H', 0, 0)
        original.add_gate('CX', 0, 1, target_index=1)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 2
        
        # Verify order is preserved
        assert parsed_ops[0]['gate'] == 'H'
        assert parsed_ops[1]['gate'] == 'CX'
    
    def test_complex_circuit_roundtrip(self):
        """Test round-trip conversion of a complex circuit."""
        original = CircuitModel(num_qubits=3)
        original.add_gate('H', 0, 0)
        original.add_gate('RX', 1, 0, params=1.5708)
        original.add_gate('CX', 0, 1, target_index=1)
        original.add_gate('SWAP', 1, 2, target_index=2)
        original.add_gate('Z', 2, 3)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 5
        
        # Verify all gate types are preserved
        gates = set(op['gate'] for op in parsed_ops)
        assert gates == {'H', 'RX', 'CX', 'SWAP', 'Z'}


class TestSimulationAccuracy:
    """Tests that verify simulation results are accurate."""
    
    def test_hadamard_simulation_result(self):
        """Test that Hadamard gate produces correct simulation results."""
        model = CircuitModel(num_qubits=1)
        model.add_gate('H', 0, 0)
        
        counts, statevector = model.run_simulation()
        
        # Check measurement distribution
        total_shots = sum(counts.values())
        assert total_shots == 1024  # Default number of shots
        
        # Hadamard should create roughly equal superposition
        for outcome in ['0', '1']:
            assert outcome in counts
            # Allow 15% deviation for statistical variance
            assert 400 < counts[outcome] < 624
    
    def test_x_gate_flips_qubit(self):
        """Test that X gate correctly flips qubit from |0> to |1>."""
        model = CircuitModel(num_qubits=1)
        model.add_gate('X', 0, 0)
        
        counts, statevector = model.run_simulation()
        
        # X|0> = |1>, so we should measure '1' almost always
        assert '1' in counts
        assert counts['1'] > 1000  # > 97% should be '1'
    
    def test_bell_state_correlations(self):
        """Test that Bell state shows quantum correlations."""
        model = CircuitModel(num_qubits=2)
        model.add_gate('H', 0, 0)
        model.add_gate('CX', 0, 1, target_index=1)
        
        counts, statevector = model.run_simulation()
        
        # Bell state should only produce '00' or '11'
        assert '00' in counts or '11' in counts
        
        # Should have almost no '01' or '10'
        unexpected = counts.get('01', 0) + counts.get('10', 0)
        assert unexpected < 50  # Less than 5% unexpected outcomes
    
    def test_identity_operation(self):
        """Test that identity (no gates) leaves qubit in |0>."""
        model = CircuitModel(num_qubits=1)
        # No gates added
        
        counts, statevector = model.run_simulation()
        
        # Should measure '0' with high probability
        assert '0' in counts
        assert counts['0'] > 1000
    
    def test_cascade_of_gates(self):
        """Test multiple gates applied in sequence."""
        model = CircuitModel(num_qubits=1)
        model.add_gate('X', 0, 0)
        model.add_gate('X', 0, 1)  # X followed by X = Identity
        
        counts, statevector = model.run_simulation()
        
        # Two X gates should return to |0>
        assert '0' in counts
        assert counts['0'] > 1000


class TestCodeExecution:
    """Tests that verify generated code can be executed."""
    
    def test_generated_code_runs(self):
        """Test that generated code can be executed without errors."""
        model = CircuitModel(num_qubits=2)
        model.add_gate('H', 0, 0)
        model.add_gate('CX', 0, 1, target_index=1)
        
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        
        # Execute the generated code
        local_scope = {}
        exec(code, {}, local_scope)
        
        # Verify 'qc' variable was created
        assert 'qc' in local_scope
    
    def test_generated_code_creates_valid_circuit(self):
        """Test that generated code creates a valid QuantumCircuit."""
        from qiskit import QuantumCircuit
        
        model = CircuitModel(num_qubits=2)
        model.add_gate('H', 0, 0)
        
        code = QiskitCodeGenerator.generate(model.num_qubits, model.get_operations())
        
        local_scope = {}
        exec(code, {}, local_scope)
        
        qc = local_scope['qc']
        assert isinstance(qc, QuantumCircuit)
        assert qc.num_qubits == 2
    
    def test_parsed_code_runs(self):
        """Test that code from parsed operations can be executed."""
        original = CircuitModel(num_qubits=1)
        original.add_gate('H', 0, 0)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        # Generate code from parsed operations
        new_code = QiskitCodeGenerator.generate(original.num_qubits, parsed_ops)
        
        # Execute the new code
        local_scope = {}
        exec(new_code, {}, local_scope)
        
        assert 'qc' in local_scope


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_circuit_roundtrip(self):
        """Test round-trip of empty circuit."""
        original = CircuitModel(num_qubits=2)
        # No gates
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 0
    
    def test_single_qubit_circuit(self):
        """Test circuits with minimum qubits."""
        original = CircuitModel(num_qubits=1)
        original.add_gate('H', 0, 0)
        original.add_gate('X', 0, 1)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 2
    
    def test_many_qubits(self):
        """Test circuits with many qubits."""
        original = CircuitModel(num_qubits=10)
        for i in range(10):
            original.add_gate('H', i, 0)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert len(parsed_ops) == 10
    
    def test_zero_parameter_rotation(self):
        """Test rotation gates with zero angle."""
        original = CircuitModel(num_qubits=1)
        original.add_gate('RX', 0, 0, params=0.0)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert parsed_ops[0]['params'] == 0.0
    
    def test_negative_parameter_rotation(self):
        """Test rotation gates with negative angle."""
        original = CircuitModel(num_qubits=1)
        original.add_gate('RY', 0, 0, params=-1.5708)
        
        code = QiskitCodeGenerator.generate(original.num_qubits, original.get_operations())
        parsed_ops = QiskitCodeParser.parse_to_model(code, original.num_qubits)
        
        assert parsed_ops is not None
        assert parsed_ops[0]['params'] == -1.5708


class TestSerializationIntegration:
    """Tests for JSON serialization integration."""
    
    def test_json_serialization_roundtrip(self):
        """Test that JSON serialization preserves circuit state."""
        original = CircuitModel(num_qubits=2)
        original.add_gate('H', 0, 0)
        original.add_gate('CX', 0, 1, target_index=1)
        original.add_gate('RX', 1, 2, params=0.5)
        
        # Serialize
        json_str = original.to_json()
        
        # Deserialize
        restored = CircuitModel()
        restored.load_from_json(json_str)
        
        # Verify
        assert restored.num_qubits == original.num_qubits
        assert len(restored.operations) == len(original.operations)
        
        # Check each operation
        for orig_op, rest_op in zip(original.operations, restored.operations):
            assert orig_op['gate'] == rest_op['gate']
            assert orig_op['qubit'] == rest_op['qubit']
            assert orig_op['index'] == rest_op['index']
            assert orig_op.get('target') == rest_op.get('target')
            assert orig_op.get('params') == rest_op.get('params')
    
    def test_json_then_code_generation(self):
        """Test that JSON-serialized circuit can generate correct code."""
        original = CircuitModel(num_qubits=2)
        original.add_gate('H', 0, 0)
        
        # Save and load
        json_str = original.to_json()
        loaded = CircuitModel()
        loaded.load_from_json(json_str)
        
        # Generate code from loaded circuit
        code = QiskitCodeGenerator.generate(loaded.num_qubits, loaded.get_operations())
        
        assert 'qc.h(0)' in code
    
    def test_simulation_after_deserialization(self):
        """Test that deserialized circuit can be simulated."""
        original = CircuitModel(num_qubits=1)
        original.add_gate('H', 0, 0)
        
        # Serialize and deserialize
        json_str = original.to_json()
        restored = CircuitModel()
        restored.load_from_json(json_str)
        
        # Simulate
        counts, statevector = restored.run_simulation()
        
        # Should produce both 0 and 1
        assert '0' in counts and '1' in counts
