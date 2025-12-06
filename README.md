# Open Quantum Composer Pro

A professional, drag-and-drop Quantum Circuit Composer built with Python. Design quantum circuits, visualize the code in real-time, and run simulations on a local quantum simulator.

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/viveksoorya/quantum-composer)](https://github.com/viveksoorya/quantum-composer/releases/latest)

## 🚀 How to Install and Run (No Coding Knowledge Required)

Follow these 3 simple steps to get started.

### 1. Install Python
You need Python installed on your computer to run this program.
* **Download Python here:** [python.org/downloads](https://www.python.org/downloads/)
* **IMPORTANT:** When installing, make sure to check the box that says **"Add Python to PATH"**.

### 2. Download this Program
1.  Scroll to the top of this page.
2.  Click the green button that says **<> Code**.
3.  Click **Download ZIP**.
4.  Find the downloaded `.zip` file on your computer and **extract (unzip)** it to a folder.

### 3. Run the App

#### 🪟 For Windows Users
1.  Open the folder where you extracted the files.
2.  **Double-click** the file named `run_app.bat` (if included) OR open a terminal in this folder.
3.  Run the following commands to install libraries and start the app:
    ```bash
    pip install -r requirements.txt
    python main.py
    ```

#### 🍎 For Mac/Linux Users
1.  Open your **Terminal**.
2.  Type `cd ` (with a space) and drag the project folder into the terminal window. Press Enter.
3.  Type the following command to install libraries:
    ```bash
    pip3 install -r requirements.txt
    ```
4.  Run the app:
    ```bash
    python3 main.py
    ```

---

## 🎮 How to Use

### Basic Controls
* **Add Gate:** Drag a gate (like **H**, **X**, **CNOT**) from the left palette onto the grid.
* **Move Gate:** Click and drag a gate already on the grid to move it.
* **Delete Gate:** Right-click a gate and select **Delete**.
* **Edit Code:** You can type Qiskit code manually in the editor on the right. The grid will update automatically!

### Advanced Features
* **Multi-Qubit Gates (CNOT, SWAP):**
    1. Drag a **CX** or **SWAP** gate onto a wire.
    2. A popup will ask for the **Target Qubit** index.
    3. Enter the number of the qubit you want to connect to (e.g., `1` or `2`).
* **Rotation Gates (RX, RY, RZ):**
    1. Drag an **RX** gate onto the grid.
    2. A popup will ask for the rotation angle (in radians).
    3. Type a number (e.g., `3.14` or `1.57`).

### Exporting & Saving
* **Save Project:** Go to `File -> Save Project` to save your work.
* **Export Image:** Go to `Export -> Export Circuit Image` to save a PNG of your circuit.
* **Export Code:** Go to `Export -> Export Qiskit Code` to get a Python file ready for IBM Quantum.

---

## 🛠️ Architecture (For Developers)

This project follows a strict **Model-View-Controller (MVC)** architecture for modularity and scalability.

* **Models:** Handle the business logic (Circuit state, Qiskit code generation, Parsing).
* **Views:** Handle the UI (PyQt6 widgets, Drawing logic, Styling).
* **Controllers:** Bridge the Models and Views (Event handling, Signal routing).

### Directory Structure
```text
quantum_composer/
├── main.py                   # Entry point
├── requirements.txt          # Dependencies
├── models/
│   ├── circuit_model.py      # Circuit State Logic
│   ├── code_generator.py     # Model -> Code
│   └── code_parser.py        # Code -> Model
├── views/
│   ├── main_window.py        # Main UI Shell
│   ├── palette_view.py       # Draggable Gates
│   ├── circuit_view.py       # Custom Drawing Engine (Grid)
│   ├── code_editor_view.py   # Text Editor
│   └── styles.py             # CSS Themes
└── controllers/
    └── main_controller.py    # Logic Controller
