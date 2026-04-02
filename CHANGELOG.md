# Changelog

All notable changes to Quantum Composer will be documented in this file.

## [1.0.4] - 2026-04-02

### Fixed
- **Multi-qubit gate repositioning**: Fixed bug where dragging a multi-qubit gate (CNOT, CX, SWAP, CZ, etc.) to reposition it would only move the control qubit while the target remained in place. Now when you move either the control or target qubit, the relative offset between them is preserved, ensuring both qubits move together correctly.
- `.gitignore`: Added to prevent `__pycache__` and other generated files from being committed to remote.

### Added
- Comprehensive test cases for multi-qubit gate repositioning in `test_circuit_model.py`

### Changed
- Enhanced `CircuitModel.move_gate()` to handle multi-qubit gates with offset preservation
- Support for moving multi-qubit gates by either control or target qubit

## [1.0.3] - 2026-03-XX

### Features
- Custom gate creation and editing
- Phase visualization for quantum states
- Circuit simulation and state vector display

## [1.0.2] - Earlier

## [1.0.1] - Earlier

## [1.0.0] - Initial Release
- Drag-and-drop quantum circuit designer
- Real-time Qiskit code generation
- Circuit simulation support
- Qubit state visualization
