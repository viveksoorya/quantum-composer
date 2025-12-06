import json
import copy
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

class CircuitModel:
    def __init__(self, num_qubits=3):
        self.num_qubits = num_qubits
        self.operations = []
        
        self.undo_stack = []
        self.redo_stack = []

    # --- Undo/Redo Logic ---
    def save_snapshot(self):
        """Saves a deep copy of current operations to undo stack."""
        # We create a full independent copy of the list of dicts
        snapshot = copy.deepcopy(self.operations)
        self.undo_stack.append(snapshot)
        
        # Limit stack size to prevent memory issues (optional, e.g., 50 steps)
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
            
        self.redo_stack.clear() 

    def undo(self):
        if not self.undo_stack: return False
        
        # Save current state to redo
        self.redo_stack.append(copy.deepcopy(self.operations))
        
        # Pop previous state
        self.operations = self.undo_stack.pop()
        return True

    def redo(self):
        if not self.redo_stack: return False
        
        # Save current state to undo
        self.undo_stack.append(copy.deepcopy(self.operations))
        
        # Pop future state
        self.operations = self.redo_stack.pop()
        return True

    # --- Operations ---
    def add_gate(self, gate_type, qubit_index, time_index, target_index=None, params=None):
        # NOTE: Snapshot must be called by Controller BEFORE this function
        self.remove_gate(qubit_index, time_index)
        self.operations.append({
            'gate': gate_type,
            'qubit': qubit_index,
            'target': target_index,
            'params': params,
            'index': time_index
        })
        self.operations.sort(key=lambda x: x['index'])

    def remove_gate(self, qubit_index, time_index):
        self.operations = [op for op in self.operations 
                           if not (op['qubit'] == qubit_index and op['index'] == time_index)]

    def get_operations(self):
        return self.operations

    # --- Simulation Helpers ---
    def _build_circuit(self):
        qc = QuantumCircuit(self.num_qubits)
        for op in self.operations:
            g = op['gate'].lower()
            q = op['qubit']
            t = op.get('target')
            p = op.get('params')
            
            if g == 'rx': qc.rx(float(p), q)
            elif g == 'ry': qc.ry(float(p), q)
            elif g == 'rz': qc.rz(float(p), q)
            elif g == 'p':  qc.p(float(p), q)
            elif g == 'h': qc.h(q)
            elif g == 'x': qc.x(q)
            elif g == 'y': qc.y(q)
            elif g == 'z': qc.z(q)
            elif g == 's': qc.s(q)
            elif g == 'sdg': qc.sdg(q)
            elif g == 't': qc.t(q)
            elif g == 'tdg': qc.tdg(q)
            elif g == 'sx': qc.sx(q)
            elif t is not None:
                if g == 'cx': qc.cx(q, t)
                elif g == 'cy': qc.cy(q, t)
                elif g == 'cz': qc.cz(q, t)
                elif g == 'ch': qc.ch(q, t)
                elif g == 'swap': qc.swap(q, t)
        return qc

    def run_simulation(self):
        """Counts (Histogram)"""
        qc = self._build_circuit()
        qc.measure_all()
        simulator = AerSimulator()
        compiled_circuit = transpile(qc, simulator)
        result = simulator.run(compiled_circuit, shots=1024).result()
        return result.get_counts()

    def get_statevector(self):
        """Bloch Sphere (Complex Vector)"""
        qc = self._build_circuit()
        # Important: Do NOT add measurements here. Statevector requires pure state.
        return Statevector.from_instruction(qc)

    # --- IO ---
    def to_json(self):
        return json.dumps({"num_qubits": self.num_qubits, "operations": self.operations})

    def load_from_json(self, json_str):
        self.save_snapshot()
        data = json.loads(json_str)
        self.num_qubits = data["num_qubits"]
        self.operations = data["operations"]
