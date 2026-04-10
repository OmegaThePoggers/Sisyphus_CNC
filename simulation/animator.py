import math
from PySide6.QtCore import QObject, QTimer, Signal

class SimulationAnimator(QObject):
    position_updated = Signal(float, float, int) # x, y, progress_index
    animation_finished = Signal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        
        self.path_points = []
        self.feed_rates = []
        
        self.current_index = 0
        self.current_x = 0
        self.current_y = 0
        
        self.speed_multiplier = 1.0
        self.fps = 60
        self.dt = 1.0 / self.fps
        
        self.timer.setInterval(int(1000 * self.dt))

    def load_path(self, points, feed_rates):
        self.path_points = points
        self.feed_rates = feed_rates
        self.reset()

    def reset(self):
        self.stop()
        self.current_index = 0
        if self.path_points:
            self.current_x = self.path_points[0][0]
            self.current_y = self.path_points[0][1]
            self.position_updated.emit(self.current_x, self.current_y, 0)

    def play(self):
        if not self.path_points or self.current_index >= len(self.path_points) - 1:
            self.reset()
        if self.path_points:
            self.timer.start()

    def pause(self):
        self.timer.stop()
        
    def stop(self):
        self.timer.stop()

    def set_speed(self, multiplier):
        self.speed_multiplier = multiplier

    def _step(self):
        if not self.path_points or self.current_index >= len(self.path_points) - 1:
            self.stop()
            self.animation_finished.emit()
            return

        target_x, target_y = self.path_points[self.current_index + 1]
        fr = self.feed_rates[self.current_index] if self.current_index < len(self.feed_rates) else 2000
        
        # feed_rate is mm/min. Convert to mm/s
        v = (fr / 60.0) * self.speed_multiplier
        
        dist_to_move = v * self.dt
        
        dx = target_x - self.current_x
        dy = target_y - self.current_y
        dist_to_target = math.hypot(dx, dy)
        
        if dist_to_target <= dist_to_move:
            # Reached next point
            self.current_x = target_x
            self.current_y = target_y
            self.current_index += 1
            self.position_updated.emit(self.current_x, self.current_y, self.current_index)
        else:
            # Move towards it
            self.current_x += (dx / dist_to_target) * dist_to_move
            self.current_y += (dy / dist_to_target) * dist_to_move
            self.position_updated.emit(self.current_x, self.current_y, self.current_index + 1)
