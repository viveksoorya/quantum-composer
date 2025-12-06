from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Necessary for 3D plotting
from mpl_toolkits.mplot3d import Axes3D 

class VisualizationView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Matplotlib Canvas Setup
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#F4F6F8') 
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def plot_histogram(self, counts):
        """Renders 2D Bar Chart"""
        self.figure.clear()
        # Add 2D subplot
        ax = self.figure.add_subplot(111)
        
        states = list(counts.keys())
        values = list(counts.values())
        
        ax.bar(states, values, color='#6929C4')
        ax.set_title("Final State Counts (Probability)", color='#333')
        ax.set_ylabel("Count", color='#333')
        ax.tick_params(colors='#333')
        
        # Styling
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_facecolor('#F4F6F8')

        self.canvas.draw()

    def plot_bloch_multivector(self, statevector, num_qubits):
        """Renders 3D Bloch Spheres for each qubit"""
        self.figure.clear()
        
        # Import partial trace here to avoid circular dependencies
        from qiskit.quantum_info import partial_trace
        
        for i in range(num_qubits):
            # Add 3D subplot (1 row, N columns, index i+1)
            ax = self.figure.add_subplot(1, num_qubits, i+1, projection='3d')
            ax.set_aspect("auto")
            
            # 1. Trace out other qubits to get the state of Qubit[i]
            # Statevector is a complex vector of size 2^N
            traced_indices = [q for q in range(num_qubits) if q != i]
            rho = partial_trace(statevector, traced_indices)
            
            # 2. Extract Coordinates from Density Matrix
            # Bloch vector components: x=Tr(Xρ), y=Tr(Yρ), z=Tr(Zρ)
            # Accessing the underlying numpy array of the density matrix
            data = rho.data
            x = 2 * data[0, 1].real
            y = 2 * data[1, 0].imag
            z = data[0, 0].real - data[1, 1].real
            
            # 3. Draw Sphere Wireframe
            u = np.linspace(0, 2 * np.pi, 20)
            v = np.linspace(0, np.pi, 10)
            sx = np.outer(np.cos(u), np.sin(v))
            sy = np.outer(np.sin(u), np.sin(v))
            sz = np.outer(np.ones(np.size(u)), np.cos(v))
            
            ax.plot_wireframe(sx, sy, sz, color="#D0D0D0", alpha=0.2)
            
            # 4. Draw Axes inside sphere
            ax.plot([-1, 1], [0, 0], [0, 0], 'k-', lw=1, alpha=0.3) # X Axis
            ax.plot([0, 0], [-1, 1], [0, 0], 'k-', lw=1, alpha=0.3) # Y Axis
            ax.plot([0, 0], [0, 0], [-1, 1], 'k-', lw=1, alpha=0.3) # Z Axis
            
            # 5. Draw the State Vector (Purple Arrow)
            ax.quiver(0, 0, 0, x, y, z, color='#6929C4', arrow_length_ratio=0.2, lw=2.5)
            
            # 6. Labels
            ax.set_title(f"Qubit {i}", fontsize=10, y=1.1)
            ax.set_axis_off() # Hide the square box around the sphere
            
        self.canvas.draw()
