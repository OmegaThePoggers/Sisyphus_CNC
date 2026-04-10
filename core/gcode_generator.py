import numpy as np

class GCodeGenerator:
    def __init__(self, config):
        self.config = config
        ws = config.get("workspace", {})
        self.width = ws.get("width", 210)
        self.height = ws.get("height", 148.5)
        self.margin = ws.get("margin", 10)
        
        self.feed_rate = config.get("feed_rate", 2000)
        
        self.max_x = (self.width / 2) - self.margin
        self.max_y = (self.height / 2) - self.margin

    def generate(self, paths):
        if not paths:
            return []

        # Find bounds of original SVG
        min_x = min_y = float('inf')
        max_px = max_py = float('-inf')
        
        for path in paths:
            xs = path[:, 0]
            ys = path[:, 1]
            min_x = min(min_x, np.min(xs))
            max_px = max(max_px, np.max(xs))
            min_y = min(min_y, np.min(ys))
            max_py = max(max_py, np.max(ys))
            
        svg_width = max_px - min_x
        svg_height = max_py - min_y
        
        if svg_width == 0 or svg_height == 0:
            return []
            
        # Aspect-preserving scale
        scale_x = (self.width - 2 * self.margin) / svg_width
        scale_y = (self.height - 2 * self.margin) / svg_height
        scale = min(scale_x, scale_y)
        
        # Center of original
        cx = min_x + svg_width / 2
        cy = min_y + svg_height / 2

        gcode_lines = []
        # Optimization: start with travel move
        
        for path in paths:
            for i, point in enumerate(path):
                # Standardize to center and scale
                raw_x = (point[0] - cx) * scale
                # SVG y-axis is inverted compared to physical cartesian space
                raw_y = -(point[1] - cy) * scale 
                
                # Apply safety clamps (CRITICAL PER PRD)
                x = max(min(raw_x, self.max_x), -self.max_x)
                y = max(min(raw_y, self.max_y), -self.max_y)
                
                # First point of path is a rapid or feed-travel 
                # (Sisyphus doesn't lift Z, so all moves are drawing moves)
                if i == 0:
                     gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{self.feed_rate}")
                else:
                     gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f}")
                     
        return gcode_lines
