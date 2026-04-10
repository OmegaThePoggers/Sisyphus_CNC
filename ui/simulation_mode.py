import json
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QSlider, QCheckBox)
from PySide6.QtCore import Qt
from simulation.renderer import SimulationRenderer
from simulation.animator import SimulationAnimator
from core.svg_parser import SVGParser
from core.gcode_generator import GCodeGenerator

class SimulationModeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        try:
            with open("config/config.json", "r") as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}
            
        self.animator = SimulationAnimator()
        self.parser = SVGParser()
        self.generator = GCodeGenerator(self.config)
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header controls
        header_layout = QHBoxLayout()
        self.btn_load_gcode = QPushButton("Load G-code")
        self.btn_load_svg = QPushButton("Load SVG")
        self.lbl_file_name = QLabel("No file selected")
        self.lbl_file_name.setStyleSheet("color: gray;")
        
        self.btn_play = QPushButton("Play")
        self.btn_pause = QPushButton("Pause")
        self.btn_reset = QPushButton("Reset")
        
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_reset.setEnabled(False)
        
        header_layout.addWidget(self.btn_load_gcode)
        header_layout.addWidget(self.btn_load_svg)
        header_layout.addWidget(self.lbl_file_name)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_play)
        header_layout.addWidget(self.btn_pause)
        header_layout.addWidget(self.btn_reset)
        
        layout.addLayout(header_layout)

        # Settings controls
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(QLabel("Speed:"))
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(5, 50) # 0.5x to 5.0x
        self.slider_speed.setValue(10) # 1.0x
        self.slider_speed.setMaximumWidth(200)
        
        self.lbl_speed_val = QLabel("1.0x")
        
        self.chk_trail = QCheckBox("Show Path Trail")
        self.chk_trail.setChecked(True)
        
        settings_layout.addWidget(self.slider_speed)
        settings_layout.addWidget(self.lbl_speed_val)
        settings_layout.addStretch()
        settings_layout.addWidget(self.chk_trail)
        
        layout.addLayout(settings_layout)

        # Renderer
        self.renderer = SimulationRenderer(self.config)
        layout.addWidget(self.renderer, stretch=1)

    def connect_signals(self):
        self.btn_load_gcode.clicked.connect(self.load_gcode)
        self.btn_load_svg.clicked.connect(self.load_svg)
        self.btn_play.clicked.connect(self.animator.play)
        self.btn_pause.clicked.connect(self.animator.pause)
        self.btn_reset.clicked.connect(self.animator.reset)
        
        self.slider_speed.valueChanged.connect(self.on_speed_changed)
        self.chk_trail.toggled.connect(self.on_trail_toggled)
        
        self.animator.position_updated.connect(self.renderer.update_position)
        self.animator.animation_finished.connect(self.on_animation_finished)

    def load_gcode(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open G-Code", "", "G-Code Files (*.gcode *.nc);;All Files(*)")
        if file_path:
            self.lbl_file_name.setText(file_path.split('/')[-1])
            self.lbl_file_name.setStyleSheet("")
            
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                self._load_from_gcode_lines(lines)
            except Exception as e:
                print(f"Error loading G-Code: {e}")

    def load_svg(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SVG", "", "SVG Files (*.svg)")
        if file_path:
            self.lbl_file_name.setText(file_path.split('/')[-1])
            self.lbl_file_name.setStyleSheet("")
            
            try:
                paths = self.parser.parse_file(file_path)
                if not paths:
                    print("No valid paths found in SVG")
                    return
                
                gcode_lines = self.generator.generate(paths)
                self._load_from_gcode_lines(gcode_lines)
            except Exception as e:
                print(f"Error loading SVG: {e}")

    def _load_from_gcode_lines(self, lines):
        points = []
        feed_rates = []
        curr_fr = self.config.get("feed_rate", 2000)
        
        for line in lines:
            if line.startswith('G1'):
                m_x = re.search(r'X([-0-9.]+)', line)
                m_y = re.search(r'Y([-0-9.]+)', line)
                m_f = re.search(r'F([-0-9.]+)', line)
                
                if m_f: curr_fr = float(m_f.group(1))
                
                if m_x and m_y:
                    x = float(m_x.group(1))
                    y = float(m_y.group(1))
                    points.append((x, y))
                    feed_rates.append(curr_fr)
                    
        self.renderer.set_path(points)
        self.animator.load_path(points, feed_rates)
        
        has_points = len(points) > 0
        self.btn_play.setEnabled(has_points)
        self.btn_pause.setEnabled(has_points)
        self.btn_reset.setEnabled(has_points)

    def on_speed_changed(self, val):
        mult = val / 10.0
        self.lbl_speed_val.setText(f"{mult:.1f}x")
        self.animator.set_speed(mult)

    def on_trail_toggled(self, checked):
        self.renderer.show_trail = checked
        self.renderer.update()

    def on_animation_finished(self):
        # Could auto-reset or change UI state
        pass
