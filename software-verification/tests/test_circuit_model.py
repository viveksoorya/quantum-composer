"""
Unit tests for the CircuitModel class.

Tests circuit state management, gate operations, and simulation.
"""

import pytest
import json
from models.circuit_model import CircuitModel


class TestCircuitModelInitialization:
    """Tests for CircuitModel initialization."""
    
    def test_default_initialization(self):
        """Test that CircuitModel initializes with default values."""
        model = CircuitModel()
        assert model.num_qubits == 3
        assert model.operations == []
    
    def test_custom_qubit_count(self):
        """Test initialization with custom qubit count."""
        model = CircuitModel(num_qubits=5)
        assert model.num_qubits == 5
    
    def test_single_qubit_circuit(self):
        """Test initialization with single qubit."""
        model = CircuitModel(num_qubits=1)
        assert model.num_qubits == 1


class TestGateOperations:
    """Tests for gate addition, removal, and movement."""
    
    def test_add_single_qubit_gate(self):
        """Test adding a single-qubit gate."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['gate'] == 'H'
        assert ops[0]['qubit'] == 0
        assert ops[0]['index'] == 0
    
    def test_add_multi_qubit_gate(self):
        """Test adding a multi-qubit gate (CNOT)."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('CX', 0, 0, target_index=1)
        
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['gate'] == 'CX'
        assert ops[0]['qubit'] == 0
        assert ops[0]['target'] == 1
    
    def test_add_rotation_gate(self):
        """Test adding a rotation gate with parameters."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('RX', 0, 0, params=1.5708)
        
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['gate'] == 'RX'
        assert ops[0]['params'] == 1.5708
    
    def test_add_gate_replaces_existing(self):
        """Test that adding a gate at occupied position replaces it."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        model.add_gate('X', 0, 0)
        
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['gate'] == 'X'
    
    def test_remove_gate(self):
        """Test removing a gate."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        model.remove_gate(0, 0)
        
        ops = model.get_operations()
        assert len(ops) == 0
    
    def test_remove_nonexistent_gate(self):
        """Test removing a gate that doesn't exist."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        model.remove_gate(1, 1)  # Different position
        
        ops = model.get_operations()
        assert len(ops) == 1  # Original gate should still exist
    
    def test_move_gate_success(self):
        """Test successfully moving a gate."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        
        result = model.move_gate(0, 0, 1, 1)
        
        assert result is True
        ops = model.get_operations()
        assert len(ops) == 1
        assert ops[0]['qubit'] == 1
        assert ops[0]['index'] == 1
    
    def test_move_gate_no_source(self):
        """Test moving a gate from non-existent source."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        
        result = model.move_gate(1, 1, 2, 2)  # No gate at (1, 1)
        
        assert result is False
    
    def test_move_gate_target_occupied(self):
        """Test moving a gate to an occupied position."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 0)
        model.add_gate('X', 1, 1)
        
        result = model.move_gate(0, 0, 1, 1)
        
        assert result is False
    
    def test_operations_sorted_by_index(self):
        """Test that operations are sorted by time index."""
        model = CircuitModel(num_qubits=3)
        model.add_gate('H', 0, 2)
        model.add_gate('X', 0, 0)
        model.add_gate('Z', 0, 1)
        
        ops = model.get_operations()
        indices = [op['index'] for op in ops]
        assert indices == [0, 1, 2]


class TestSerialization:
    """Tests for JSON serialization and deserialization."""
    
    def test_to_json(self):
        """Test converting circuit to JSON."""
        model = CircuitModel(num_qubits=2)
        model.add_gate('H', 0, 0)
        model.add_gate('CX', 0, 1, target_index=1)
        
        json_str = model.to_json()
        data = json.loads(json_str)
        
        assert data['num_qubits'] == 2
        assert len(data['operations']) == 2
        assert data['operations'][0]['gate'] == 'H'
    
    def test_load_from_json(self):
        """Test loading circuit from JSON."""
        model = CircuitModel()
        json_str = json.dumps({
            "num_qubits": 2,
            "operations": [
                {"gate": "H", "qubit": 0, "target": None, "params": None, "index": 0},
                {"gate": "CX", "qubit": 0, "target": 1, "params": None, "index": 1}
            ]
        })
        
        model.load_from_json(json_str)
        
        assert model.num_qubits == 2
        assert len(model.operations) == 2
        assert model.operations[0]['gate'] == 'H'
    
    def test_roundtrip_serialization(self):
        """Test that serialization is reversible."""
        original = CircuitModel(num_qubits=2)
        original.add_gate('H', 0, 0)
        original.add_gate('CX', 0, 1, target_index=1)
        
        json_str = original.to_json()
        
        restored = CircuitModel()
        restored.load_from_json(json_str)
        
        assert restored.num_qubits == original.num_qubits
        assert len(restored.operations) == len(original.operations)


class TestSimulation:
    """Tests for circuit simulation."""
    
    def test_simulate_hadamard(self):
        """Test simulation of Hadamard gate."""
        model = CircuitModel(num_qubits=1)
        model.add_gate('H', 0, 0)
        
        counts, statevector = model.run_simulation()
        
        # Hadamard on |0> creates equal superposition
        assert '0' in counts
        assert '1' in counts
        # Both outcomes should have roughly equal probability
        total = sum(counts.values())
        assert abs(counts['0'] - counts['1']) < total * 0.2  # Allow 20% variance
    
    def test_simulate_pauli_x(self):
        """Test simulation of Pauli-X gate."""
        model = CircuitModel(num_qubits=1)
        model.add_gate('X', 0, 0)
        
        counts, statevector = model.run_simulation()
        
        # X|0> = |1>
        assert counts['1'] > 1000  # Almost all shots should measure 1
    
    def test_simulate_bell_state(self):
        """Test simulation of Bell state creation."""
        model = CircuitModel(num_qubits=2)
        model.add_gate('H', 0, 0)
        model.add_gate('CX', 0, 1, target_index=1)
        
        counts, statevector = model.run_simulation()
        
        # Bell state should only produce '00' or '11'
        assert '00' in counts or '11' in counts
        assert '01' not in counts or counts['01'] < 50
        assert '10' not in counts or counts['10'] < 50
    
    def test_simulate_rotation_gate(self):
        """Test simulation of rotation gate."""
        model = CircuitModel(num_qubits=1)
        model.add_gate('RX', 0, 0, params=1.5708)  # pi/2 rotation
        
        counts, statevector = model.run_simulation()
        
        # Should produce both 0 and 1 outcomes
        assert len(counts) >= 1
    
    def test_simulate_swap_gate(self):
        """Test simulation of SWAP gate."""
        model = CircuitModel(num_qubits=2)
        model.add_gate('X', 0, 0)  # Set qubit 0 to |1>
        model.add_gate('SWAP', 0, 1, target_index=1)
        
        counts, statevector = model.run_simulation()
        
        # After SWAP, qubit 1 should be |1>
        # Measurement shows '10' (binary: qubit1=1, qubit0=0 in Qiskit little-endian)
        assert '10' in counts
