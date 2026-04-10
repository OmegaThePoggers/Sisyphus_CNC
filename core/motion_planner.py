import math
import numpy as np

class MotionPlanner:
    def __init__(self, config):
        self.config = config
        ws = config.get("workspace", {})
        self.max_x = (ws.get("width", 210) / 2) - ws.get("margin", 10)
        self.max_y = (ws.get("height", 148.5) / 2) - ws.get("margin", 10)
        self.feed_rate = config.get("feed_rate", 2000)

    def plan_return_to_center(self, current_x, current_y, arc_radius=20, segments=20):
        """
        Generates a smooth path back to (0,0) without abrupt moves.
        Instead of a direct G1 line, we curve inward like a spiral.
        As a simple safe v1: we just linearize a curve.
        """
        gcode = []
        # Clamp input
        start_x = max(min(current_x, self.max_x), -self.max_x)
        start_y = max(min(current_y, self.max_y), -self.max_y)

        # Distance to center
        dist = math.hypot(start_x, start_y)
        
        if dist < 1.0:
            # Already basically at center
            gcode.append(f"G1 X0.000 Y0.000 F{self.feed_rate}")
            return gcode

        # Let's generate a parametric curve that spirals inward.
        # r(t) = dist * (1-t)
        # theta(t) = start_theta + t * math.pi (adds a half bow to the return)
        
        start_theta = math.atan2(start_y, start_x)
        
        for t in np.linspace(0.05, 1.0, segments): # Start from 0.05 to avoid duplicating start point exactly if not needed
            r = dist * (1 - t)
            theta = start_theta + t * math.pi
            
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            
            x = max(min(x, self.max_x), -self.max_x)
            y = max(min(y, self.max_y), -self.max_y)
            
            gcode.append(f"G1 X{x:.3f} Y{y:.3f}")
            
        return gcode
