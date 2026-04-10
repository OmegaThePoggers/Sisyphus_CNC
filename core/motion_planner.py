import math
import numpy as np

class MotionPlanner:
    def __init__(self, config):
        self.config = config
        ws = config.get("workspace", {})
        self.max_x = (ws.get("width", 210) / 2) - ws.get("margin", 10)
        self.max_y = (ws.get("height", 148.5) / 2) - ws.get("margin", 10)
        self.feed_rate = config.get("feed_rate", 2000)

    def plan_return_to_center(self, current_x, current_y, num_revolutions=2, segments=60):
        """
        Generates a smooth inward spiral back to (0,0).
        Creates a visible spiral pattern in the sand rather than an abrupt line.
        """
        gcode = []
        start_x = max(min(current_x, self.max_x), -self.max_x)
        start_y = max(min(current_y, self.max_y), -self.max_y)

        dist = math.hypot(start_x, start_y)
        
        if dist < 1.0:
            gcode.append(f"G1 X0.000 Y0.000 F{self.feed_rate}")
            return gcode

        start_theta = math.atan2(start_y, start_x)
        total_angle = num_revolutions * 2 * math.pi
        
        for t in np.linspace(0.01, 1.0, segments):
            r = dist * (1 - t)
            theta = start_theta + t * total_angle
            
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            
            x = max(min(x, self.max_x), -self.max_x)
            y = max(min(y, self.max_y), -self.max_y)
            
            gcode.append(f"G1 X{x:.3f} Y{y:.3f}")

        gcode.append(f"G1 X0.000 Y0.000")
        return gcode
