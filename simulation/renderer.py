import math
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QPointF, QRectF

class SimulationRenderer(QWidget):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        ws = config.get("workspace", {})
        self.ws_width = ws.get("width", 210)
        self.ws_height = ws.get("height", 148.5)
        
        self.path_points = []
        self.current_pos = None # tuple (x,y)
        self.progress_index = 0
        self.show_trail = True

    def set_path(self, points):
        """points is a list of (x,y) tuples representing the GCode path"""
        self.path_points = points
        self.current_pos = points[0] if points else None
        self.progress_index = 0
        self.update()

    def update_position(self, x, y, index):
        self.current_pos = (x, y)
        self.progress_index = index
        self.update()

    def paintEvent(self, event):
        if not self.ws_width or not self.ws_height:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        
        # Calculate aspect-preserving scale and offset
        scale_x = (w - 20) / self.ws_width
        scale_y = (h - 20) / self.ws_height
        scale = min(scale_x, scale_y)
        
        offset_x = (w - (self.ws_width * scale)) / 2
        offset_y = (h - (self.ws_height * scale)) / 2

        def world_to_screen(wx, wy):
            # wx, wy are relative to center
            sx = offset_x + (wx + self.ws_width/2) * scale
            sy = offset_y + (-wy + self.ws_height/2) * scale # -wy because screen Y is down
            return QPointF(sx, sy)

        # Draw Workspace Bounds
        painter.setPen(QPen(Qt.black, 2))
        px_top_left = world_to_screen(-self.ws_width/2, self.ws_height/2)
        px_width = self.ws_width * scale
        px_height = self.ws_height * scale
        painter.drawRect(QRectF(px_top_left.x(), px_top_left.y(), px_width, px_height))

        if not self.path_points:
            return

        # Draw full path footprint (faint)
        faint_pen = QPen(QColor(200, 200, 200), 1)
        painter.setPen(faint_pen)
        for i in range(1, len(self.path_points)):
            p1 = world_to_screen(*self.path_points[i-1])
            p2 = world_to_screen(*self.path_points[i])
            painter.drawLine(p1, p2)

        # Draw trail (drawn so far)
        if self.show_trail and self.progress_index > 0:
            bright_pen = QPen(QColor(0, 120, 255), 2)
            painter.setPen(bright_pen)
            
            # Draw fully traversed segments
            idx = min(self.progress_index, len(self.path_points) - 1)
            for i in range(1, idx):
                p1 = world_to_screen(*self.path_points[i-1])
                p2 = world_to_screen(*self.path_points[i])
                painter.drawLine(p1, p2)
                
            # Draw partial segment to current pos
            if self.current_pos and idx > 0:
                p1 = world_to_screen(*self.path_points[idx-1])
                p2 = world_to_screen(*self.current_pos)
                painter.drawLine(p1, p2)

        # Draw toolhead
        if self.current_pos:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 0, 0))
            head_pos = world_to_screen(*self.current_pos)
            radius = 4
            painter.drawEllipse(head_pos, radius, radius)
