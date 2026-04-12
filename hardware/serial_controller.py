import serial
import serial.tools.list_ports
import time
from PySide6.QtCore import QObject, QThread, Signal, Slot, QMutex, QMutexLocker

class SerialWorker(QThread):
    line_sent = Signal(str)
    response_received = Signal(str)
    error_occurred = Signal(str)
    connection_lost = Signal()
    streaming_finished = Signal()

    def __init__(self, port, baudrate):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self._is_running = False
        self._command_queue = []
        self._queue_mutex = QMutex()
        self._pause_requested = False

    def run(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2) # Wait for GRBL boot
            self.serial.reset_input_buffer()
            self._is_running = True
            
            # Send initial reset (Ctrl-X)
            self.serial.write(b'\x18')
            time.sleep(1)
            self.serial.reset_input_buffer()
            
            # Send unlock ($X) and Absolute mode (G90) just in case
            self._command_queue.insert(0, '$X')
            self._command_queue.insert(1, 'G90')

        except serial.SerialException as e:
            self.error_occurred.emit(f"Connection failed: {e}")
            return

        while self._is_running:
            if not self.serial.is_open:
                self.connection_lost.emit()
                break

            cmd = None
            with QMutexLocker(self._queue_mutex):
                if self._command_queue and not self._pause_requested:
                    cmd = self._command_queue.pop(0)
            
            if cmd:
                try:
                    # Clean and format command (Grbl accepts \n or \r\n, \r\n is safer)
                    cmd_str = cmd.strip() + '\r\n'
                    self.serial.write(cmd_str.encode('utf-8'))
                    self.line_sent.emit(cmd)
                    
                    # Wait for explicitly "ok" or "error"
                    while self._is_running:
                        line = self.serial.readline()
                        if not line:
                            continue # Timeout, loop again
                        
                        resp = line.decode('utf-8').strip()
                        if resp:
                            self.response_received.emit(resp)
                            
                        if resp == 'ok':
                            break
                        elif resp.lower().startswith('error') or resp.lower().startswith('alarm'):
                            self.error_occurred.emit(f"GRBL Error: {resp}")
                            self._is_running = False # Halt on error (per PRD)
                            break
                            
                    # If queue empty, emit finished
                    with QMutexLocker(self._queue_mutex):
                        if not self._command_queue and self._is_running:
                            self.streaming_finished.emit()

                except serial.SerialException as e:
                    self.error_occurred.emit(f"Serial write failed: {e}")
                    self.connection_lost.emit()
                    break
            else:
                # No commands or paused, sleep briefly to avoid pegging CPU
                time.sleep(0.01)

        if self.serial and self.serial.is_open:
            self.serial.close()

    def enqueue_command(self, cmd):
        with QMutexLocker(self._queue_mutex):
            self._command_queue.append(cmd)

    def clear_queue(self):
        with QMutexLocker(self._queue_mutex):
            self._command_queue.clear()
            
    def set_paused(self, paused):
        with QMutexLocker(self._queue_mutex):
             self._pause_requested = paused

    def stop(self):
        self._is_running = False


class SerialController(QObject):
    # Pass-through signals for UI
    line_sent = Signal(str)
    response_received = Signal(str)
    error_occurred = Signal(str)
    connection_lost = Signal()
    streaming_finished = Signal()
    connection_state_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None

    @staticmethod
    def get_available_ports():
        return [port.device for port in serial.tools.list_ports.comports()]

    @staticmethod
    def auto_detect_port():
        # Look for typical Arduino VID/PIDs
        arduino_vids = [(0x2341, 0x0043), (0x2341, 0x0001), (0x2A03, 0x0043), (0x1A86, 0x7523)] # Uno and CH340 clones
        for port in serial.tools.list_ports.comports():
            if (port.vid, port.pid) in arduino_vids:
                return port.device
        
        # Fallback to first available if any
        ports = SerialController.get_available_ports()
        if ports:
            return ports[0]
        return None

    def connect_to_device(self, port, baudrate):
        if self.worker is not None and self.worker.isRunning():
            return False

        self.worker = SerialWorker(port, baudrate)
        # Connect signals
        self.worker.line_sent.connect(self.line_sent)
        self.worker.response_received.connect(self.response_received)
        self.worker.error_occurred.connect(self._handle_error)
        self.worker.connection_lost.connect(self._handle_connection_lost)
        self.worker.streaming_finished.connect(self.streaming_finished)
        self.worker.finished.connect(self._worker_finished)

        self.worker.start()
        self.connection_state_changed.emit(True)
        return True

    def disconnect_device(self):
        if self.worker is not None:
            self.worker.stop()
            self.worker.wait()
            self.worker = None
            self.connection_state_changed.emit(False)

    def is_connected(self):
        return self.worker is not None and self.worker.isRunning()

    def send_line(self, line):
        if self.is_connected():
            self.worker.enqueue_command(line)

    def stream_gcode(self, lines):
        if self.is_connected():
            self.worker.clear_queue()
            for line in lines:
                self.worker.enqueue_command(line)

    def pause_stream(self):
        if self.is_connected():
            self.worker.set_paused(True)
            
    def resume_stream(self):
        if self.is_connected():
            self.worker.set_paused(False)

    def soft_reset(self):
        if self.is_connected():
            self.worker.clear_queue()
            self.worker.enqueue_command('\x18') # Send Ctrl-X directly 

    def set_origin(self):
        self.send_line("G92 X0 Y0")

    @Slot(str)
    def _handle_error(self, err_msg):
        self.error_occurred.emit(err_msg)
        # Assuming we don't automatically entirely disconnect on GRBL error, 
        # but the queue is halted in the worker.
        self.worker.clear_queue()

    @Slot()
    def _handle_connection_lost(self):
        self.connection_lost.emit()
        self.disconnect_device()
        
    @Slot()
    def _worker_finished(self):
        self.connection_state_changed.emit(False)
        self.worker = None
