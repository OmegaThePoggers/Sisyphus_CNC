from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QStatusBar, QStackedWidget,
                             QMessageBox)
from PySide6.QtCore import Qt

from hardware.serial_controller import SerialController
from ui.custom_mode import CustomModeWidget
from ui.simulation_mode import SimulationModeWidget

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
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top Bar (Navigation & Connection)
        top_bar = QHBoxLayout()
        
        # Navigation Buttons
        self.btn_idle = QPushButton("Idle Mode")
        self.btn_idle.setEnabled(False) # Wait for Phase 4
        self.btn_custom = QPushButton("Custom Mode")
        self.btn_sim = QPushButton("Simulation")
        
        top_bar.addWidget(self.btn_idle)
        top_bar.addWidget(self.btn_custom)
        top_bar.addWidget(self.btn_sim)
        
        top_bar.addSpacing(20)
        
        # Serial Controls
        self.combo_ports = QComboBox()
        self.refresh_ports()
        
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.setCheckable(True)
        
        self.btn_set_center = QPushButton("Set Center (G92)")
        self.btn_set_center.setEnabled(False)
        
        top_bar.addWidget(QLabel("Port:"))
        top_bar.addWidget(self.combo_ports)
        top_bar.addWidget(self.btn_connect)
        top_bar.addWidget(self.btn_set_center)
        top_bar.addStretch()

        main_layout.addLayout(top_bar)

        # Main Content Area
        self.stacked_widget = QStackedWidget()
        
        # Placeholder widgets for unimplemented modes
        self.idle_widget = QLabel("Idle Mode (Phase 4)")
        self.idle_widget.setAlignment(Qt.AlignCenter)
        
        self.custom_widget = CustomModeWidget(self.serial_controller)
        
        self.sim_widget = SimulationModeWidget()
        
        self.stacked_widget.addWidget(self.idle_widget)
        self.stacked_widget.addWidget(self.custom_widget)
        self.stacked_widget.addWidget(self.sim_widget)
        
        # Default to Custom Mode for early testing
        self.stacked_widget.setCurrentWidget(self.custom_widget)
        
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
        
        self.btn_custom.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.custom_widget))
        self.btn_idle.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.idle_widget))
        self.btn_sim.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.sim_widget))
        
        self.serial_controller.connection_state_changed.connect(self.on_connection_changed)
        self.serial_controller.error_occurred.connect(self.on_serial_error)
        self.serial_controller.connection_lost.connect(self.on_serial_lost)

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
            self.status_lbl.setStyleSheet("color: green;")
        else:
            self.status_lbl.setText("Disconnected")
            self.status_lbl.setStyleSheet("color: red;")

    def on_serial_error(self, err_msg):
        QMessageBox.warning(self, "Serial Error", err_msg)
        
    def on_serial_lost(self):
        QMessageBox.critical(self, "Connection Lost", "The connection to the hardware was lost.")
