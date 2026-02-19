"""
Demonstration of Custom Gate Visual Icons

This script demonstrates the visual icon system for custom unitary gates.
"""

import numpy as np
from views.custom_gate_analyzer import CustomGateAnalyzer


def demonstrate_icons():
    """Demonstrate different custom gate icons based on matrix properties."""
    
    print("=" * 70)
    print("CUSTOM GATE VISUAL ICONS DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Test different gate types
    test_gates = [
        ("Hadamard", np.array([[1, 1], [1, -1]]) / np.sqrt(2)),
        ("Pauli-X", np.array([[0, 1], [1, 0]])),
        ("Pauli-Y", np.array([[0, -1j], [1j, 0]])),
        ("Pauli-Z", np.array([[1, 0], [0, -1]])),
        ("Identity", np.eye(2)),
        ("Phase (S)", np.array([[1, 0], [0, 1j]])),
        ("π/8 (T)", np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]])),
        ("RX(π/2)", np.array([[1, -1j], [-1j, 1]]) / np.sqrt(2)),
        ("RY(π/2)", np.array([[1, -1], [1, 1]]) / np.sqrt(2)),
        ("RZ(π/2)", np.array([[np.exp(-1j * np.pi / 4), 0], 
                                [0, np.exp(1j * np.pi / 4)]])),
        ("CNOT (4x4)", np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ])),
        ("SWAP (4x4)", np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ])),
    ]
    
    for name, matrix in test_gates:
        props = CustomGateAnalyzer.analyze_matrix(matrix)
        
        print(f"\n{'─' * 70}")
        print(f"Gate: {name}")
        print(f"{'─' * 70}")
        print(f"  Icon: {props['icon']}")
        print(f"  Color: {props['color']}")
        print(f"  Type: {props['gate_type']}")
        print(f"  Description: {props['description']}")
        print(f"  Qubits: {props['qubit_count']}")
        print(f"  Properties:")
        print(f"    - Diagonal: {'✓' if props['is_diagonal'] else '✗'}")
        print(f"    - Real: {'✓' if props['is_real'] else '✗'}")
        print(f"    - Hermitian: {'✓' if props['is_hermitian'] else '✗'}")
        print(f"    - Hadamard-like: {'✓' if props['is_hadamard_like'] else '✗'}")
        print(f"    - Special (det=±1): {'✓' if props['is_special'] else '✗'}")
        det = props['determinant']
        if np.iscomplex(det):
            print(f"    - Determinant: {det:.4f}")
        else:
            print(f"    - Determinant: {det:.4f}")
        
        print(f"\n  Tooltip Preview:")
        tooltip = CustomGateAnalyzer.get_tooltip(props)
        for line in tooltip.split('\n'):
            print(f"    {line}")
    
    print(f"\n{'=' * 70}")
    print("COLOR LEGEND:")
    print(f"{'=' * 70}")
    colors = CustomGateAnalyzer.COLORS
    for gate_type, color in colors.items():
        print(f"  {gate_type:20s} : {color}")
    
    print()
    print("ICON LEGEND:")
    print(f"{'=' * 70}")
    icons = {
        'I': 'Identity',
        'X': 'Pauli-X',
        'Y': 'Pauli-Y',
        'Z': 'Pauli-Z',
        'H': 'Hadamard',
        'S': 'Phase gate',
        'P': 'Phase rotation',
        'D': 'Diagonal',
        'R': 'Real / Rotation',
        '⊕': 'Hermitian',
        'U': 'General unitary'
    }
    for icon, meaning in icons.items():
        print(f"  {icon} : {meaning}")
    
    print()
    print("=" * 70)
    print("VISUAL FEATURES:")
    print("=" * 70)
    print("• Color-coded backgrounds identify gate type at a glance")
    print("• Meaningful icons instead of generic 'U'")
    print("• Hover tooltips show detailed gate properties")
    print("• Different styles for single vs multi-qubit gates")
    print("• Colored control dots for 2-qubit custom gates")
    print()


if __name__ == "__main__":
    demonstrate_icons()
