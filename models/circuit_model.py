import json
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np # Needed for 'pi' evaluation if we wanted to get fancy

class CircuitModel:
    def __init__(self, num_qubits=3):
        self.num_qubits = num_qubits
        self.operations = []

    def add_gate(self, gate_type, qubit_index, time_index, target_index=None, params=None, matrix=None):
        self.remove_gate(qubit_index, time_index)
        self.operations.append({
            'gate': gate_type,
            'qubit': qubit_index,
            'target': target_index,
            'params': params, # NEW: Store rotation angle
            'matrix': matrix, # NEW: Store custom gate matrix
            'index': time_index
        })
        self.operations.sort(key=lambda x: x['index'])

    def move_gate(self, old_q, old_t, new_q, new_t):
        """Atomically move a gate from (old_q, old_t) to (new_q, new_t).
        Returns True on success, False if the source doesn't exist or target occupied by a different gate.
        """
        op = next((o for o in self.operations if o['qubit'] == old_q and o['index'] == old_t), None)
        if not op:
            return False

        # If target already has a gate (different from the moving one), reject
        conflict = next((o for o in self.operations if o['qubit'] == new_q and o['index'] == new_t), None)
        if conflict and not (conflict is op):
            return False

        # Perform move
        self.remove_gate(old_q, old_t)
        self.operations.append({
            'gate': op['gate'],
            'qubit': new_q,
            'target': op.get('target'),
            'params': op.get('params'),
            'matrix': op.get('matrix'),  # Preserve custom gate matrix
            'index': new_t
        })
        self.operations.sort(key=lambda x: x['index'])
        return True

    def remove_gate(self, qubit_index, time_index):
        self.operations = [op for op in self.operations 
                           if not (op['qubit'] == qubit_index and op['index'] == time_index)]

    def get_operations(self):
        return self.operations

    def run_simulation(self):
        from qiskit.circuit.library import UnitaryGate
        
        qc = QuantumCircuit(self.num_qubits)
        
        for op in self.operations:
            g = op['gate'].lower()
            q = op['qubit']
            t = op.get('target')
            p = op.get('params') # Get parameters
            m = op.get('matrix') # Get custom gate matrix
           
            # --- Custom Gates ---
            if g == 'custom' and m is not None:
                # Convert stored matrix (list) back to numpy array
                matrix = np.array(m)
                # Create unitary gate
                unitary = UnitaryGate(matrix)
                # Apply to qubit(s)
                if t is not None:
                    # Two-qubit custom gate
                    qc.append(unitary, [q, t])
                else:
                    # Single-qubit custom gate
                    qc.append(unitary, [q])
            
            # --- Rotation Gates ---
            # We explicitly cast to float to ensure Qiskit accepts it
            elif g == 'rx': qc.rx(float(p), q)
            elif g == 'ry': qc.ry(float(p), q)
            elif g == 'rz': qc.rz(float(p), q)
            elif g == 'p':  qc.p(float(p), q) # Phase Gate
            
            # --- Standard Gates ---
            elif g == 'h': qc.h(q)
            elif g == 'x': qc.x(q)
            elif g == 'y': qc.y(q)
            elif g == 'z': qc.z(q)
            
            # --- Multi Qubit ---
            elif t is not None:
                if g == 'cx': qc.cx(q, t)
                elif g == 'swap': qc.swap(q, t)
                elif g == 'cz': qc.cz(q, t)

        # Save a copy of the circuit before measurement for statevector simulation
        qc_no_measure = qc.copy()
        
        # Run measurement simulation for histogram
        qc.measure_all()
        simulator = AerSimulator()
        compiled_circuit = transpile(qc, simulator)
        result = simulator.run(compiled_circuit, shots=1024).result()
        counts = result.get_counts()
        
        # Run statevector simulation for Bloch sphere visualization
        from qiskit.quantum_info import Statevector
        statevector = Statevector.from_instruction(qc_no_measure)
        
        return counts, statevector

    def to_json(self):
        """Serialize circuit to JSON, converting numpy arrays to lists."""
        # Convert operations to JSON-serializable format
        serializable_ops = []
        for op in self.operations:
            op_copy = op.copy()
            # Convert numpy arrays to lists for JSON serialization
            if 'matrix' in op_copy and op_copy['matrix'] is not None:
                if isinstance(op_copy['matrix'], np.ndarray):
                    op_copy['matrix'] = op_copy['matrix'].tolist()
            serializable_ops.append(op_copy)
        
        return json.dumps({"num_qubits": self.num_qubits, "operations": serializable_ops})

    def load_from_json(self, json_str):
        data = json.loads(json_str)
        self.num_qubits = data["num_qubits"]
        self.operations = data["operations"]
        # Convert matrix lists back to numpy arrays if needed
        for op in self.operations:
            if 'matrix' in op and op['matrix'] is not None:
                if isinstance(op['matrix'], list):
                    op['matrix'] = np.array(op['matrix'])
