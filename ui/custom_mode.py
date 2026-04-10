from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QPlainTextEdit, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt

from core.svg_parser import SVGParser
from core.gcode_generator import GCodeGenerator
from core.motion_planner import MotionPlanner

class CustomModeWidget(QWidget):
    def __init__(self, serial_controller, parent=None):
        super().__init__(parent)
        self.serial_controller = serial_controller
        
        # Will be loaded with config from main window in real app
        self.parser = SVGParser()
        # We need config for generator and planner
        import json
        try:
            with open("config/config.json", "r") as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}
            
        self.generator = GCodeGenerator(self.config)
        self.planner = MotionPlanner(self.config)
        
        self.current_gcode = []
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header controls
        header_layout = QHBoxLayout()
        self.btn_load_svg = QPushButton("Load SVG")
        self.lbl_file_name = QLabel("No file selected")
        self.lbl_file_name.setStyleSheet("color: gray;")
        
        self.btn_draw = QPushButton("Draw")
        self.btn_draw.setEnabled(False)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)
        
        header_layout.addWidget(self.btn_load_svg)
        header_layout.addWidget(self.lbl_file_name)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_draw)
        header_layout.addWidget(self.btn_stop)
        
        layout.addLayout(header_layout)

        # Main area (Preview left, Logs right)
        main_layout = QHBoxLayout()
        
        # Placeholder for Canvas (Phase 2)
        self.lbl_preview = QLabel("SVG Preview Area (Phase 2)")
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.lbl_preview.setMinimumSize(400, 300)
        
        # Log view
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumWidth(300)
        
        main_layout.addWidget(self.lbl_preview, stretch=2)
        main_layout.addWidget(self.log_view, stretch=1)
        
        layout.addLayout(main_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def connect_signals(self):
        self.btn_load_svg.clicked.connect(self.load_svg)
        self.btn_draw.clicked.connect(self.start_drawing)
        self.btn_stop.clicked.connect(self.stop_drawing)
        
        self.serial_controller.connection_state_changed.connect(self.on_connection_changed)
        self.serial_controller.line_sent.connect(self.log_sent)
        self.serial_controller.response_received.connect(self.log_received)
        self.serial_controller.streaming_finished.connect(self.on_stream_finished)

    def load_svg(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg)")
        if file_path:
            self.lbl_file_name.setText(file_path.split('/')[-1])
            self.lbl_file_name.setStyleSheet("color: black;")
            
            try:
                paths = self.parser.parse_file(file_path)
                if paths:
                    self.current_gcode = self.generator.generate(paths)
                    
                    # Compute end position to return to center
                    if self.current_gcode:
                        last_line = self.current_gcode[-1]
                        import re
                        m_x = re.search(r'X([-0-9.]+)', last_line)
                        m_y = re.search(r'Y([-0-9.]+)', last_line)
                        
                        curr_x, curr_y = 0.0, 0.0
                        if m_x and m_y:
                            curr_x = float(m_x.group(1))
                            curr_y = float(m_y.group(1))
                            
                        return_moves = self.planner.plan_return_to_center(curr_x, curr_y)
                        self.current_gcode.extend(return_moves)
                    
                    self.log_view.appendPlainText(f"Loaded: {file_path} ({len(self.current_gcode)} instructions)")
                    self.btn_draw.setEnabled(self.serial_controller.is_connected())
                else:
                    self.log_view.appendPlainText(f"Error: No paths found in {file_path}")
            except Exception as e:
                self.log_view.appendPlainText(f"Parse error: {str(e)}")

    def start_drawing(self):
        if not self.current_gcode:
            return
            
        self.btn_draw.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.progress_bar.setRange(0, 0) # Indeterminate for now
        self.log_view.appendPlainText("--- Starting Draw ---")
        self.serial_controller.stream_gcode(self.current_gcode)

    def stop_drawing(self):
        self.serial_controller.soft_reset()
        self.log_view.appendPlainText("--- Stopped ---")
        self.reset_ui_state()

    def on_stream_finished(self):
        self.log_view.appendPlainText("--- Finished ---")
        self.reset_ui_state()

    def reset_ui_state(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.btn_stop.setEnabled(False)
        self.btn_draw.setEnabled(self.serial_controller.is_connected() and len(self.current_gcode) > 0)
        
    def on_connection_changed(self, is_connected):
        if not is_connected:
            self.btn_draw.setEnabled(False)
            self.btn_stop.setEnabled(False)
        elif len(self.current_gcode) > 0:
            self.btn_draw.setEnabled(True)

    def log_sent(self, msg):
        self.log_view.appendPlainText(f"> {msg}")
        
    def log_received(self, msg):
         self.log_view.appendPlainText(f"< {msg}")
