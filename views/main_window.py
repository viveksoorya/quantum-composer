from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QTabWidget, QToolBar, QFileDialog, QMessageBox)
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt
from .palette_view import PaletteView
from .circuit_view import CircuitView
from .code_editor_view import CodeEditorView
from .visualization_view import VisualizationView
from .styles import LIGHT_THEME

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Quantum Composer - Pro")
        self.resize(1400, 850)
        self.setStyleSheet(LIGHT_THEME)
        
        # --- 1. Menu Bar & Actions ---
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        self.save_action = QAction("Save Project", self)
        self.load_action = QAction("Load Project", self)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.load_action)

        # Edit Menu (Undo/Redo)
        edit_menu = menubar.addMenu("Edit")
        self.undo_action = QAction("Undo", self)
        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.redo_action = QAction("Redo", self)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        
        # Export Menu
        export_menu = menubar.addMenu("Export")
        self.export_image_action = QAction("Export Image", self)
        self.export_code_action = QAction("Export Code", self)
        export_menu.addAction(self.export_image_action)
        export_menu.addAction(self.export_code_action)

        # --- 2. Toolbar ---
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        self.run_action = QAction("▶ Run Simulation", self)
        toolbar.addAction(self.run_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)

        # --- 3. Layout & Views ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Initialize Views
        self.palette_view = PaletteView()
        self.circuit_view = CircuitView(num_qubits=3, num_steps=12)
        
        # --- 4. TABS SETUP (Critical Order) ---
        self.right_tabs = QTabWidget()
        
        # Initialize Sub-views BEFORE adding them to tabs
        self.code_view = CodeEditorView()
        self.viz_view = VisualizationView()
        
        # Add Tabs
        self.right_tabs.addTab(self.code_view, "Qiskit Code")
        self.right_tabs.addTab(self.viz_view, "Results (Histogram)")
        
        # Create a placeholder widget for the 3rd tab
        # The controller will swap 'viz_view' into this tab when selected
        self.bloch_tab = QWidget()
        bloch_layout = QVBoxLayout()
        self.bloch_tab.setLayout(bloch_layout)
        self.right_tabs.addTab(self.bloch_tab, "Bloch Sphere") 
        
        # Add to Splitter
        splitter.addWidget(self.palette_view)
        splitter.addWidget(self.circuit_view)
        splitter.addWidget(self.right_tabs)
        splitter.setSizes([180, 750, 470])

        main_layout.addWidget(splitter)
    
    # --- Helper Methods ---
    def show_save_dialog(self, title, ext):
        fname, _ = QFileDialog.getSaveFileName(self, title, "", ext)
        return fname

    def show_load_dialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Circuit", "", "JSON Files (*.json)")
        return fname
        
    def show_input_dialog(self, title, label):
        from PyQt6.QtWidgets import QInputDialog
        i, ok = QInputDialog.getInt(self, title, label, 0, 0, 10, 1)
        return i if ok else None
