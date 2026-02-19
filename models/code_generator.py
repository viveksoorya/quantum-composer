class QiskitCodeGenerator:
    @staticmethod
    def generate(num_qubits, operations):
        code = [
            "from qiskit import QuantumCircuit",
            "from qiskit.circuit.library import UnitaryGate",
            "import numpy as np",
            ""
        ]
        
        # Track custom gates that need to be defined
        custom_gate_defs = []
        custom_gate_names = {}
        custom_gate_counter = 0
        
        sorted_ops = sorted(operations, key=lambda x: x['index'])
        
        # First pass: collect custom gates
        for op in sorted_ops:
            if op['gate'].upper() == 'CUSTOM' and op.get('matrix') is not None:
                matrix = op['matrix']
                # Create a unique name for this custom gate
                gate_id = f"custom_gate_{custom_gate_counter}"
                custom_gate_counter += 1
                custom_gate_names[id(matrix)] = gate_id
                
                # Convert matrix to code representation
                if isinstance(matrix, list):
                    matrix_str = repr(matrix)
                else:
                    # numpy array - convert to nested list
                    matrix_list = matrix.tolist()
                    matrix_str = repr(matrix_list)
                
                custom_gate_defs.append(f"{gate_id} = UnitaryGate(np.array({matrix_str}))")
        
        # Add custom gate definitions
        if custom_gate_defs:
            code.extend(custom_gate_defs)
            code.append("")
        
        code.append(f"qc = QuantumCircuit({num_qubits})")
        code.append("")

        for op in sorted_ops:
            gate = op['gate'].lower()
            q = op['qubit']
            t = op.get('target')
            p = op.get('params')
            m = op.get('matrix')
           
            # Custom Unitary Gates
            if gate == 'custom' and m is not None:
                gate_id = custom_gate_names.get(id(m), f"custom_gate_{list(custom_gate_names.values())[0] if custom_gate_names else 0}")
                if t is not None:
                    code.append(f"qc.append({gate_id}, [{q}, {t}])")
                else:
                    code.append(f"qc.append({gate_id}, [{q}])")
            
            # Rotation Gates (With Parameters)
            elif gate in ['rx', 'ry', 'rz', 'p'] and p is not None:
                code.append(f"qc.{gate}({p}, {q})")
            
            # Standard Single Qubit
            elif gate in ['h', 'x', 'y', 'z', 's', 't']:
                code.append(f"qc.{gate}({q})")
            
            # Multi Qubit
            elif t is not None:
                code.append(f"qc.{gate}({q}, {t})")
            
        code.append("")
        code.append("qc.measure_all()")
        
        return "\n".join(code)
