# Open Quantum Composer Pro

A professional, drag-and-drop Quantum Circuit Composer built with Python. Design quantum circuits, visualize the Qiskit code in real-time, simulate results locally, and verify states on the Bloch Sphere.

---

## 📥 Download & Run (No Install Required)

We provide standalone apps for Windows, Mac, and Linux. You do **not** need to install Python to use these.

**[Click here to view the Latest Release](https://github.com/viveksoorya/quantum-composer/releases/latest)**

| OS | File to Download | How to Run |
| :--- | :--- | :--- |
| **Windows** | `QuantumComposer.exe` | **Double-click** to run.<br>*(See note below if Windows warns you)* |
| **Mac** | `QuantumComposer_Mac` | Download, unzip.<br>**Right-Click** the app and select **Open**. |
| **Linux** | `QuantumComposer_Linux` | Open terminal in the folder.<br>Run: `chmod +x QuantumComposer_Linux`<br>Run: `./QuantumComposer_Linux` |

### ⚠️ "Unverified Developer" Warning?
Because this is a free open-source project, we don't buy expensive certificates from Microsoft/Apple.
* **Windows:** If you see "Windows protected your PC", click **More Info** -> **Run Anyway**.
* **Mac:** If you see "Cannot be opened...", click **Done**. Then **Right-Click** the app and choose **Open**.

---

## 🐍 For Python Developers (Run from Source)

If you prefer to run the code directly or want to contribute:

1.  **Clone the Repo:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
    cd YOUR_REPO_NAME
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run:**
    ```bash
    python main.py
    ```

---

## 🎮 Features & Usage

### 1. Drag-and-Drop Circuit Design
* **Place Gates:** Drag gates (H, X, Z, etc.) from the left palette onto the circuit wires.
* **Move Gates:** Click and drag existing gates to move them to new positions.
* **Delete Gates:** Right-click any gate and select **Delete**.

### 2. Advanced Gates
* **Multi-Qubit (CNOT, SWAP, CZ):** Drag the gate to the control qubit. A popup will ask for the **Target Qubit** index.
    * *Visuals:* CNOTs render as a Control Dot (●) connected to a Target Cross (⊕).
* **Rotation Gates (RX, RY, RZ, P):** Drag the gate to the grid. A popup will ask for the rotation angle (in radians).

### 3. Simulation & Visualization
The app includes a built-in **Qiskit Aer** simulator.
* **Results Tab:** Shows a histogram of measurement counts (probabilities).
* **Run:** Click the `▶` Play button in the toolbar to run the simulation.

### 4. Code & Exporting
* **Two-Way Sync:** As you drag gates, the **Qiskit Code** tab updates instantly. You can also type code manually, and the grid will update!
* **Export Image:** `File -> Export -> Export Image` saves a high-res PNG of your circuit.
* **Export Code:** `File -> Export -> Export Code` saves a `.py` file ready to run on IBM Quantum.

---

## 🛠️ Architecture

This project uses a strict **Model-View-Controller (MVC)** architecture.

```text
quantum_composer/
├── main.py                   # Entry point
├── models/
│   ├── circuit_model.py      # Circuit State & Undo Stack
│   ├── code_generator.py     # Grid -> Qiskit String
│   └── code_parser.py        # Qiskit String -> Grid
├── views/
│   ├── main_window.py        # UI Shell & Tab Management
│   ├── palette_view.py       # Draggable Gates
│   ├── circuit_view.py       # Custom Painting Engine (The Grid)
│   ├── visualization_view.py # Matplotlib Charts (Histogram & Bloch)
│   └── styles.py             # CSS Themes
└── controllers/
    └── main_controller.py    # Logic, Event Handling, Simulation
