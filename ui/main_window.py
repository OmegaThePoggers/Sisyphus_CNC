import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QStatusBar, QStackedWidget,
                             QMessageBox, QGridLayout, QSizePolicy)
from PySide6.QtCore import Qt

from hardware.serial_controller import SerialController
from ui.custom_mode import CustomModeWidget
from ui.simulation_mode import SimulationModeWidget
from ui.idle_mode import IdleModeWidget

class HomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel("Sisyphus Controller")
        font = lbl_title.font()
        font.setPointSize(36)
        font.setBold(True)
        lbl_title.setFont(font)
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_sub = QLabel("Select a drawing mode to begin")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet("color: #aaa; margin-bottom: 30px;")
        
        grid = QGridLayout()
        grid.setSpacing(20)
        
        self.btn_idle = QPushButton("▶ Idle Mode\n(Playlist)")
        self.btn_idle.setMinimumSize(200, 150)
        
        self.btn_custom = QPushButton("⚙ Custom Mode\n(Single Draw)")
        self.btn_custom.setMinimumSize(200, 150)
        
        self.btn_sim = QPushButton("📺 Simulation\n(Preview)")
        self.btn_sim.setMinimumSize(200, 150)
        
        # Style the massive buttons
        btn_style = """
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                background-color: #3b3b3b;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
                border: 2px solid #5a9bd4;
            }
        """
        self.btn_idle.setStyleSheet(btn_style)
        self.btn_custom.setStyleSheet(btn_style)
        self.btn_sim.setStyleSheet(btn_style)
        
        grid.addWidget(self.btn_idle, 0, 0)
        grid.addWidget(self.btn_custom, 0, 1)
        grid.addWidget(self.btn_sim, 0, 2)
        
        layout.addStretch()
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        layout.addLayout(grid)
        layout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sisyphus Controller")
        self.resize(1000, 700)
        
        self.load_config()
        self.serial_controller = SerialController(self)
        self.setup_ui()
        self.connect_signals()

    def load_config(self):
        try:
            with open("config/config.json", "r") as f:
                self.config = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Config Error", f"Failed to load config.json: {e}")
            self.config = {}

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top Bar (Global Controls)
        top_bar = QHBoxLayout()
        
        self.btn_home = QPushButton("🏠 Home")
        self.btn_home.setFixedWidth(100)
        top_bar.addWidget(self.btn_home)
        
        top_bar.addSpacing(20)
        top_bar.addWidget(QLabel("Serial Port:"))
        
        self.combo_ports = QComboBox()
        self.refresh_ports()
        top_bar.addWidget(self.combo_ports)
        
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setCheckable(True)
        top_bar.addWidget(self.btn_connect)
        
        self.btn_set_center = QPushButton("Set Center (G92)")
        self.btn_set_center.setEnabled(False)
        top_bar.addWidget(self.btn_set_center)
        
        top_bar.addStretch()
        
        main_layout.addLayout(top_bar)

        # Separator line
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #555;")
        main_layout.addWidget(line)

        # Main Content Area
        self.stacked_widget = QStackedWidget()
        
        self.home_widget = HomeWidget()
        self.idle_widget = IdleModeWidget(self.serial_controller)
        self.custom_widget = CustomModeWidget(self.serial_controller)
        self.sim_widget = SimulationModeWidget()
        
        self.stacked_widget.addWidget(self.home_widget)
        self.stacked_widget.addWidget(self.idle_widget)
        self.stacked_widget.addWidget(self.custom_widget)
        self.stacked_widget.addWidget(self.sim_widget)
        
        self.stacked_widget.setCurrentWidget(self.home_widget)
        self.btn_home.setEnabled(False)
        
        main_layout.addWidget(self.stacked_widget)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_lbl = QLabel("Disconnected")
        self.status_bar.addWidget(self.status_lbl)

    def refresh_ports(self):
        self.combo_ports.clear()
        ports = self.serial_controller.get_available_ports()
        self.combo_ports.addItems(ports)
        
        if not ports:
             self.combo_ports.addItem("No ports found")
             self.combo_ports.setEnabled(False)
             self.btn_connect.setEnabled(False)
        else:
             self.combo_ports.setEnabled(True)
             self.btn_connect.setEnabled(True)

             # Try to auto-select
             config_port = self.config.get("serial", {}).get("port")
             if config_port == "auto":
                 auto_port = self.serial_controller.auto_detect_port()
                 if auto_port and auto_port in ports:
                     self.combo_ports.setCurrentText(auto_port)
             elif config_port in ports:
                 self.combo_ports.setCurrentText(config_port)

    def connect_signals(self):
        self.btn_connect.toggled.connect(self.toggle_connection)
        self.btn_set_center.clicked.connect(self.serial_controller.set_origin)
        
        # Navigation
        self.btn_home.clicked.connect(lambda: self.switch_mode(self.home_widget))
        self.home_widget.btn_idle.clicked.connect(lambda: self.switch_mode(self.idle_widget))
        self.home_widget.btn_custom.clicked.connect(lambda: self.switch_mode(self.custom_widget))
        self.home_widget.btn_sim.clicked.connect(lambda: self.switch_mode(self.sim_widget))
        
        self.serial_controller.connection_state_changed.connect(self.on_connection_changed)
        self.serial_controller.error_occurred.connect(self.on_serial_error)
        self.serial_controller.connection_lost.connect(self.on_serial_lost)

    def switch_mode(self, widget):
        self.stacked_widget.setCurrentWidget(widget)
        self.btn_home.setEnabled(widget != self.home_widget)

    def toggle_connection(self, checked):
        if checked:
            port = self.combo_ports.currentText()
            baudrate = self.config.get("serial", {}).get("baudrate", 115200)
            
            if not self.serial_controller.connect_to_device(port, baudrate):
                self.btn_connect.setChecked(False)
        else:
            self.serial_controller.disconnect_device()

    def on_connection_changed(self, is_connected):
        self.btn_set_center.setEnabled(is_connected)
        self.combo_ports.setEnabled(not is_connected)
        self.btn_connect.setText("Disconnect" if is_connected else "Connect")
        self.btn_connect.setChecked(is_connected)
        
        if is_connected:
            self.status_lbl.setText(f"Connected to {self.combo_ports.currentText()}")
            self.status_lbl.setStyleSheet("color: #4CAF50;") # brighter green for dark mode
        else:
            self.status_lbl.setText("Disconnected")
            self.status_lbl.setStyleSheet("color: #F44336;") # brighter red for dark mode

    def on_serial_error(self, err_msg):
        QMessageBox.warning(self, "Serial Error", err_msg)
        
    def on_serial_lost(self):
        QMessageBox.critical(self, "Connection Lost", "The connection to the hardware was lost.")
