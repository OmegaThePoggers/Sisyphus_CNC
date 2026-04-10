from svgpathtools import svg2paths, Path, Line, CubicBezier, QuadraticBezier, Arc
import numpy as np

class SVGParser:
    def __init__(self, tolerance=0.1):
        # Flattening tolerance for complex curves
        self.tolerance = tolerance

    def parse_file(self, filepath):
        paths, attributes = svg2paths(filepath)
        segments = []
        
        for path in paths:
            parsed_path = self._process_path(path)
            if parsed_path is not None and len(parsed_path) > 0:
                segments.append(parsed_path)
                
        return segments

    def _process_path(self, path: Path):
        """
        Convert svgpathtools Path into a list of (x,y) coordinates.
        Continuous path segments become an Nx2 numpy array.
        """
        points = []
        
        for segment in path:
            if isinstance(segment, Line):
                if not points:
                    points.append([segment.start.real, segment.start.imag])
                points.append([segment.end.real, segment.end.imag])
            elif isinstance(segment, (CubicBezier, QuadraticBezier, Arc)):
                # Flatten complex curves into polylines
                # For G2/G3 arc detection, we'd keep them analytically, but 
                # as a V1, flattening guarantees compatibility and handles tricky arcs.
                # PRD allows linearizing.
                num_points = int(segment.length() / self.tolerance)
                num_points = max(num_points, 5) # Minimum points per curve
                
                ts = np.linspace(0, 1, num_points)
                for t in ts:
                    point = segment.point(t)
                    if not points or abs(points[-1][0]-point.real) > 1e-6 or abs(points[-1][1]-point.imag) > 1e-6:
                        points.append([point.real, point.imag])
        
        if points:
            return np.array(points)
        return None
