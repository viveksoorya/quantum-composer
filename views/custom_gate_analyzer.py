"""
Custom Gate Visual Analyzer

Analyzes unitary matrices to determine visual properties for meaningful icons.
"""

import numpy as np
from typing import Dict, Any, Tuple


class CustomGateAnalyzer:
    """Analyzes custom gate matrices to determine visual representation."""
    
    # Color schemes for different gate types
    COLORS = {
        'diagonal': '#2980b9',      # Blue - diagonal gates (phase, Z, etc.)
        'real': '#27ae60',          # Green - real matrices (Pauli-X, etc.)
        'hermitian': '#8e44ad',     # Purple - Hermitian gates (self-adjoint)
        'unitary': '#d35400',       # Orange - general unitary
        'hadamard': '#16a085',      # Teal - Hadamard-like (balanced superposition)
        'rotation': '#e74c3c',      # Red - rotation gates
        'identity': '#95a5a6',      # Gray - identity or close to it
        'special': '#c0392b',       # Dark red - special unitary (det=1)
    }
    
    @staticmethod
    def analyze_matrix(matrix: np.ndarray) -> Dict[str, Any]:
        """
        Analyze a unitary matrix and return visual properties.
        
        Returns dict with:
        - 'qubit_count': 1 or 2
        - 'gate_type': string describing the type
        - 'color': hex color code
        - 'icon': icon character/symbol
        - 'description': human-readable description
        - 'is_diagonal': bool
        - 'is_real': bool
        - 'is_hermitian': bool
        - 'is_hadamard_like': bool
        - 'determinant': complex
        """
        if matrix is None:
            return {
                'qubit_count': 1,
                'gate_type': 'unknown',
                'color': CustomGateAnalyzer.COLORS['unitary'],
                'icon': '?',
                'description': 'Unknown gate',
                'is_diagonal': False,
                'is_real': False,
                'is_hermitian': False,
                'is_hadamard_like': False,
                'determinant': 1.0
            }
        
        dim = matrix.shape[0]
        qubit_count = int(np.log2(dim))
        
        # Check properties
        is_diagonal = CustomGateAnalyzer._is_diagonal(matrix)
        is_real = CustomGateAnalyzer._is_real(matrix)
        is_hermitian = CustomGateAnalyzer._is_hermitian(matrix)
        is_hadamard_like = CustomGateAnalyzer._is_hadamard_like(matrix)
        is_identity = CustomGateAnalyzer._is_identity(matrix)
        is_rotation = CustomGateAnalyzer._is_rotation_gate(matrix, qubit_count)
        determinant = np.linalg.det(matrix)
        is_special = np.isclose(abs(determinant), 1.0)
        
        # Determine gate type and icon
        if is_identity:
            gate_type = 'identity'
            icon = 'I'
            description = 'Identity gate'
            color = CustomGateAnalyzer.COLORS['identity']
        elif is_diagonal:
            if qubit_count == 1:
                if np.isclose(matrix[1, 1], -1):
                    gate_type = 'pauli_z'
                    icon = 'Z'
                    description = 'Pauli-Z (phase flip)'
                elif np.isclose(matrix[1, 1], 1j) or np.isclose(matrix[1, 1], -1j):
                    gate_type = 'phase'
                    icon = 'S'
                    description = 'Phase gate'
                else:
                    gate_type = 'phase_rotation'
                    icon = 'P'
                    description = 'Phase rotation'
            else:
                gate_type = 'diagonal'
                icon = 'D'
                description = f'{qubit_count}-qubit diagonal'
            color = CustomGateAnalyzer.COLORS['diagonal']
        elif is_hadamard_like:
            gate_type = 'hadamard'
            icon = 'H'
            description = 'Hadamard (superposition)'
            color = CustomGateAnalyzer.COLORS['hadamard']
        elif is_rotation:
            gate_type = 'rotation'
            icon = 'R'
            description = 'Rotation gate'
            color = CustomGateAnalyzer.COLORS['rotation']
        elif is_hermitian:
            if qubit_count == 1 and is_real:
                if np.allclose(matrix, [[0, 1], [1, 0]]):
                    gate_type = 'pauli_x'
                    icon = 'X'
                    description = 'Pauli-X (NOT)'
                elif np.allclose(matrix, [[0, -1j], [1j, 0]]):
                    gate_type = 'pauli_y'
                    icon = 'Y'
                    description = 'Pauli-Y'
                else:
                    gate_type = 'hermitian_real'
                    icon = '⊕'
                    description = 'Hermitian gate'
            else:
                gate_type = 'hermitian'
                icon = 'H'
                description = 'Hermitian gate'
            color = CustomGateAnalyzer.COLORS['hermitian']
        elif is_real:
            gate_type = 'real'
            icon = 'R'
            description = 'Real unitary'
            color = CustomGateAnalyzer.COLORS['real']
        elif is_special:
            gate_type = 'special'
            icon = 'U'
            description = 'Special unitary'
            color = CustomGateAnalyzer.COLORS['special']
        else:
            gate_type = 'unitary'
            icon = 'U'
            description = 'Unitary gate'
            color = CustomGateAnalyzer.COLORS['unitary']
        
        return {
            'qubit_count': qubit_count,
            'gate_type': gate_type,
            'color': color,
            'icon': icon,
            'description': description,
            'is_diagonal': is_diagonal,
            'is_real': is_real,
            'is_hermitian': is_hermitian,
            'is_hadamard_like': is_hadamard_like,
            'determinant': determinant,
            'is_special': is_special
        }
    
    @staticmethod
    def _is_diagonal(matrix: np.ndarray, tol: float = 1e-10) -> bool:
        """Check if matrix is diagonal."""
        return np.allclose(matrix - np.diag(np.diag(matrix)), 0, atol=tol)
    
    @staticmethod
    def _is_real(matrix: np.ndarray, tol: float = 1e-10) -> bool:
        """Check if matrix is real (no imaginary parts)."""
        return np.allclose(np.imag(matrix), 0, atol=tol)
    
    @staticmethod
    def _is_hermitian(matrix: np.ndarray, tol: float = 1e-10) -> bool:
        """Check if matrix is Hermitian (U† = U)."""
        return np.allclose(matrix, matrix.conj().T, atol=tol)
    
    @staticmethod
    def _is_hadamard_like(matrix: np.ndarray, tol: float = 1e-10) -> bool:
        """Check if matrix has Hadamard-like structure (balanced superposition)."""
        if matrix.shape != (2, 2):
            return False
        # Check if all entries have equal magnitude (1/√2)
        expected_mag = 1 / np.sqrt(2)
        mags = np.abs(matrix)
        return np.allclose(mags, expected_mag, atol=tol)
    
    @staticmethod
    def _is_identity(matrix: np.ndarray, tol: float = 1e-10) -> bool:
        """Check if matrix is identity."""
        return np.allclose(matrix, np.eye(matrix.shape[0]), atol=tol)
    
    @staticmethod
    def _is_rotation_gate(matrix: np.ndarray, qubit_count: int, tol: float = 1e-10) -> bool:
        """Check if matrix looks like a rotation gate."""
        if qubit_count != 1:
            return False
        # Rotation gates are unitary with det = 1 (special unitary for 1 qubit)
        det = np.linalg.det(matrix)
        return np.isclose(det, 1, atol=tol) or np.isclose(det, -1, atol=tol)
    
    @staticmethod
    def get_css_style(properties: Dict[str, Any]) -> str:
        """Generate CSS style for custom gate based on properties."""
        color = properties['color']
        qubit_count = properties['qubit_count']
        
        # Base style
        style = f"""
            background-color: {color};
            color: white;
            border: 2px solid {color};
            border-radius: 4px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            font-size: 16px;
            min-width: 46px;
            min-width: 46px;
        """
        
        return style
    
    @staticmethod
    def get_tooltip(properties: Dict[str, Any]) -> str:
        """Generate tooltip text for custom gate."""
        lines = [
            f"Custom Gate: {properties['icon']}",
            f"Type: {properties['description']}",
            f"Qubits: {properties['qubit_count']}",
        ]
        
        if properties['is_diagonal']:
            lines.append("Diagonal: Yes")
        if properties['is_real']:
            lines.append("Real: Yes")
        if properties['is_hermitian']:
            lines.append("Hermitian: Yes")
        if properties['is_special']:
            lines.append("Special (det=1): Yes")
        
        det = properties['determinant']
        if np.iscomplex(det):
            lines.append(f"Determinant: {det:.3f}")
        else:
            lines.append(f"Determinant: {det:.3f}")
        
        return "\n".join(lines)
