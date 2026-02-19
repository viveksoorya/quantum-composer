#!/usr/bin/env python3
"""
Validation script for Quantum Circuit Composer.

This script validates that the quantum circuit models work correctly
and produce expected quantum mechanical behavior.

Usage:
    python validation/validate_circuits.py
    python validation/validate_circuits.py --verbose
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.circuit_model import CircuitModel


def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")


def print_result(test_name, passed, details=""):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  [{status}] {test_name}")
    if details and not passed:
        print(f"        {details}")


def validate_superposition():
    """Validate that Hadamard creates equal superposition."""
    model = CircuitModel(num_qubits=1)
    model.add_gate('H', 0, 0)
    
    counts, _ = model.run_simulation()
    total = sum(counts.values())
    
    # Check both outcomes exist and are roughly equal
    has_both = '0' in counts and '1' in counts
    ratio_ok = abs(counts.get('0', 0) - counts.get('1', 0)) < total * 0.2
    
    return has_both and ratio_ok, f"Counts: {counts}"


def validate_pauli_x():
    """Validate that Pauli-X flips |0⟩ to |1⟩."""
    model = CircuitModel(num_qubits=1)
    model.add_gate('X', 0, 0)
    
    counts, _ = model.run_simulation()
    
    # Should measure |1⟩ with high probability
    return counts.get('1', 0) > 1000, f"Counts: {counts}"


def validate_pauli_z():
    """Validate that Pauli-Z doesn't change |0⟩."""
    model = CircuitModel(num_qubits=1)
    model.add_gate('Z', 0, 0)
    
    counts, _ = model.run_simulation()
    
    # Should still measure |0⟩
    return counts.get('0', 0) > 1000, f"Counts: {counts}"


def validate_bell_state():
    """Validate Bell state shows quantum correlations."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('H', 0, 0)
    model.add_gate('CX', 0, 1, target_index=1)
    
    counts, _ = model.run_simulation()
    
    # Should only get |00⟩ or |11⟩
    valid_outcomes = counts.get('00', 0) + counts.get('11', 0)
    total = sum(counts.values())
    
    return valid_outcomes > total * 0.95, f"Counts: {counts}"


def validate_identity():
    """Validate that no gates leaves qubit in |0⟩."""
    model = CircuitModel(num_qubits=1)
    # No gates
    
    counts, _ = model.run_simulation()
    
    return counts.get('0', 0) > 1000, f"Counts: {counts}"


def validate_cnot_control():
    """Validate CNOT doesn't flip when control is |0⟩."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('CX', 0, 0, target_index=1)
    
    counts, _ = model.run_simulation()
    
    # Control is |0⟩, so target should stay |0⟩
    return counts.get('00', 0) > 1000, f"Counts: {counts}"


def validate_cnot_target():
    """Validate CNOT flips target when control is |1⟩."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('X', 0, 0)  # Set control to |1⟩
    model.add_gate('CX', 0, 1, target_index=1)
    
    counts, _ = model.run_simulation()
    
    # Target should flip to |1⟩
    return counts.get('11', 0) > 1000, f"Counts: {counts}"


def validate_swap():
    """Validate SWAP gate exchanges qubit states."""
    model = CircuitModel(num_qubits=2)
    model.add_gate('X', 0, 0)  # Set qubit 0 to |1⟩
    model.add_gate('SWAP', 0, 1, target_index=1)
    
    counts, _ = model.run_simulation()
    
    # After SWAP, qubit 1 should be |1⟩ (measured as '10')
    return counts.get('10', 0) > 1000, f"Counts: {counts}"


def validate_hadamard_cascade():
    """Validate H-H = Identity."""
    model = CircuitModel(num_qubits=1)
    model.add_gate('H', 0, 0)
    model.add_gate('H', 0, 1)
    
    counts, _ = model.run_simulation()
    
    # Two Hadamards should return to |0⟩
    return counts.get('0', 0) > 1000, f"Counts: {counts}"


def validate_rotation_gate():
    """Validate rotation gate produces expected state."""
    import numpy as np
    
    model = CircuitModel(num_qubits=1)
    model.add_gate('RX', 0, 0, params=np.pi)  # 180 degree rotation
    
    counts, _ = model.run_simulation()
    
    # RX(π)|0⟩ ≈ |1⟩ (approximately)
    return counts.get('1', 0) > 900, f"Counts: {counts}"


def main():
    parser = argparse.ArgumentParser(description='Validate Quantum Circuit Composer')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    print_header("Quantum Circuit Composer Validation")
    print("Testing quantum mechanical correctness...\n")
    
    tests = [
        ("Superposition (Hadamard)", validate_superposition),
        ("Pauli-X Gate", validate_pauli_x),
        ("Pauli-Z Gate", validate_pauli_z),
        ("Bell State Creation", validate_bell_state),
        ("Identity (No Gates)", validate_identity),
        ("CNOT Control |0⟩", validate_cnot_control),
        ("CNOT Control |1⟩", validate_cnot_target),
        ("SWAP Gate", validate_swap),
        ("Hadamard Cascade (H-H = I)", validate_hadamard_cascade),
        ("Rotation Gate (RX)", validate_rotation_gate),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            result, details = test_func()
            print_result(test_name, result, details)
            if result:
                passed += 1
            else:
                failed += 1
            if args.verbose:
                print(f"        Details: {details}")
        except Exception as e:
            print_result(test_name, False, str(e))
            failed += 1
    
    print(f"\n{'='*60}")
    print(f" Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print(f"{'='*60}\n")
    
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
