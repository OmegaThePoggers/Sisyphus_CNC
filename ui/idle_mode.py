import os
import json
import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QListWidgetItem, QFileDialog, 
                             QCheckBox, QProgressBar, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal, QMutex, QMutexLocker

from core.svg_parser import SVGParser
from core.gcode_generator import GCodeGenerator
from core.motion_planner import MotionPlanner

class PlaylistWorker(QThread):
    progress_changed = Signal(str, int) # status text, percent 0-100
    pattern_started = Signal(str)
    all_finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, serial_controller, config):
        super().__init__()
        self.serial_controller = serial_controller
        self.parser = SVGParser()
        self.generator = GCodeGenerator(config)
        self.planner = MotionPlanner(config)
        
        self.playlist = [] # list of file paths
        self._is_running = False
        self._mutex = QMutex()
        
        self.transform_mode = False # For phase 5

    def set_playlist(self, paths):
        with QMutexLocker(self._mutex):
            self.playlist = paths

    def run(self):
        self._is_running = True
        
        with QMutexLocker(self._mutex):
            paths = list(self.playlist)
            
        if not paths:
            self.all_finished.emit()
            return
            
        loop_index = 0
        while self._is_running:
            if not self.serial_controller.is_connected():
                self.error_occurred.emit("Serial disconnected")
                break
                
            path = paths[loop_index]
            filename = os.path.basename(path)
            self.pattern_started.emit(filename)
            self.progress_changed.emit(f"Parsing {filename}...", 10)
            
            try:
                svg_paths = self.parser.parse_file(path)
                if not svg_paths:
                    self.error_occurred.emit(f"No valid paths in {filename}")
                    loop_index = (loop_index + 1) % len(paths)
                    continue
                    
                gcode = self.generator.generate(svg_paths)
                
                # In Phase 4, we always append return to center
                curr_x, curr_y = 0.0, 0.0
                if gcode:
                    last = gcode[-1]
                    mx = re.search(r'X([-0-9.]+)', last)
                    my = re.search(r'Y([-0-9.]+)', last)
                    if mx and my:
                        curr_x, curr_y = float(mx.group(1)), float(my.group(1))
                        
                if not self.transform_mode:
                    gcode.extend(self.planner.plan_return_to_center(curr_x, curr_y))
                
                self.progress_changed.emit(f"Drawing {filename}...", 50)
                
                # Stream the entire pattern
                self.serial_controller.stream_gcode(gcode)
                
                # Wait for stream to finish securely (in a loop so we check is_running)
                # This could be event-driven but since we're in a QThread, we can poll
                # Wait, stream_gcode is threaded. Let's just monitor the queue size in a loop
                import time
                while self._is_running and self.serial_controller.worker and len(self.serial_controller.worker._command_queue) > 0:
                    time.sleep(0.5)
                
                if not self._is_running:
                    break

            except Exception as e:
                self.error_occurred.emit(f"Error drawing {filename}: {e}")
                
            loop_index = (loop_index + 1) % len(paths)
            
        self.all_finished.emit()
        
    def stop(self):
        self._is_running = False

class IdleModeWidget(QWidget):
    def __init__(self, serial_controller, parent=None):
        super().__init__(parent)
        self.serial_controller = serial_controller
        
        try:
            with open("config/config.json", "r") as f:
                self.config = json.load(f)
        except Exception:
            self.config = {}
            
        self.worker = PlaylistWorker(serial_controller, self.config)
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        # Playlist Panel (Left)
        playlist_layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("Add File")
        self.btn_add_folder = QPushButton("Add Folder")
        self.btn_remove = QPushButton("Remove")
        
        btn_layout.addWidget(self.btn_add_file)
        btn_layout.addWidget(self.btn_add_folder)
        btn_layout.addWidget(self.btn_remove)
        
        playlist_layout.addWidget(QLabel("Playlist (Drag to reorder):"))
        playlist_layout.addWidget(self.list_widget)
        playlist_layout.addLayout(btn_layout)
        
        layout.addLayout(playlist_layout, stretch=1)

        # Controls Panel (Right)
        controls_layout = QVBoxLayout()
        
        self.btn_start = QPushButton("Start Playlist")
        self.btn_pause = QPushButton("Pause Stream")
        self.btn_stop = QPushButton("Stop")
        
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        
        self.chk_transform = QCheckBox("Enable Transform Mode (Phase 5)")
        self.chk_transform.setEnabled(False) # Wait for Phase 5
        
        self.lbl_status = QLabel("Ready")
        self.progress = QProgressBar()
        
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.chk_transform)
        controls_layout.addStretch()
        controls_layout.addWidget(self.lbl_status)
        controls_layout.addWidget(self.progress)
        
        layout.addLayout(controls_layout, stretch=1)

    def connect_signals(self):
        self.btn_add_file.clicked.connect(self.add_file)
        self.btn_add_folder.clicked.connect(self.add_folder)
        self.btn_remove.clicked.connect(self.remove_item)
        
        self.btn_start.clicked.connect(self.start_playlist)
        self.btn_pause.clicked.connect(self.toggle_pause)
        self.btn_stop.clicked.connect(self.stop_playlist)
        
        self.worker.progress_changed.connect(self.on_progress)
        self.worker.pattern_started.connect(self.on_pattern_started)
        self.worker.all_finished.connect(self.on_finished)
        self.worker.error_occurred.connect(self.on_error)
        
        self.serial_controller.connection_state_changed.connect(self.on_connection_changed)

    def add_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Add SVGs", "", "SVG Files (*.svg)")
        for f in files:
            item = QListWidgetItem(os.path.basename(f))
            item.setData(Qt.UserRole, f)
            self.list_widget.addItem(item)
        self.update_ui_state()

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Add Folder")
        if folder:
            for root, dirs, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith('.svg'):
                        filepath = os.path.join(root, f)
                        item = QListWidgetItem(f)
                        item.setData(Qt.UserRole, filepath)
                        self.list_widget.addItem(item)
            self.update_ui_state()

    def remove_item(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))
        self.update_ui_state()

    def get_playlist_paths(self):
        return [self.list_widget.item(i).data(Qt.UserRole) for i in range(self.list_widget.count())]

    def start_playlist(self):
        paths = self.get_playlist_paths()
        if not paths:
            return
            
        self.worker.set_playlist(paths)
        self.worker.start()
        
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.list_widget.setEnabled(False)

    def toggle_pause(self):
        if self.btn_pause.text() == "Pause Stream":
            self.serial_controller.pause_stream()
            self.btn_pause.setText("Resume Stream")
            self.lbl_status.setText("Paused")
        else:
            self.serial_controller.resume_stream()
            self.btn_pause.setText("Pause Stream")
            self.lbl_status.setText("Resumed")

    def stop_playlist(self):
        self.worker.stop()
        self.serial_controller.soft_reset()
        
    def on_progress(self, status, val):
        self.lbl_status.setText(status)
        self.progress.setValue(val)
        
    def on_pattern_started(self, name):
         pass # Highlight in list could go here

    def on_finished(self):
        self.btn_start.setEnabled(self.serial_controller.is_connected() and self.list_widget.count() > 0)
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.list_widget.setEnabled(True)
        self.progress.setValue(0)
        self.lbl_status.setText("Stopped")

    def on_error(self, msg):
        QMessageBox.warning(self, "Playlist Error", msg)
        self.stop_playlist()

    def update_ui_state(self):
        has_items = self.list_widget.count() > 0
        is_conn = self.serial_controller.is_connected()
        self.btn_start.setEnabled(has_items and is_conn and not self.worker.isRunning())
        
    def on_connection_changed(self, is_connected):
        self.update_ui_state()
        if not is_connected and self.worker.isRunning():
            self.stop_playlist()
