import math
import os

def generate_svg(filename, path_string, width=200, height=200):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
    <path fill="none" stroke="black" stroke-width="1" d="{path_string}" />
</svg>'''
    with open(filename, 'w') as f:
        f.write(svg)

def polyline_to_svg_path(points):
    if not points: return ""
    d = f"M {points[0][0]:.3f} {points[0][1]:.3f}"
    for x, y in points[1:]:
        d += f" L {x:.3f} {y:.3f}"
    return d

def make_spiral(turns=15, points_per_turn=50, max_radius=90):
    points = []
    total_points = turns * points_per_turn
    for i in range(total_points):
        theta = (i / points_per_turn) * 2 * math.pi
        # Make it start right at the center nicely
        r = max_radius * (i / total_points)
        x = 100 + r * math.cos(theta)
        y = 100 + r * math.sin(theta)
        points.append((x, y))
    return polyline_to_svg_path(points)

def make_rose(k=6, max_radius=90, points_per_turn=50):
    points = []
    num_loops = 1 if k % 2 != 0 else 2
    total_points = num_loops * int(math.pi * k * points_per_turn)
    max_t = num_loops * math.pi
    
    for i in range(total_points):
        theta = (i / total_points) * max_t * 2
        r = max_radius * math.cos(k * theta)
        x = 100 + r * math.cos(theta)
        y = 100 + r * math.sin(theta)
        points.append((x, y))
    points.append(points[0]) # Close path
    return polyline_to_svg_path(points)

def make_spirograph(R=50, r=16, d=45, num_points=1000):
    # Hypotrochoid
    # For R=50, r=16, the GCD is 2, LCM(50, 16) is 400. We need t to go to 16*pi to close.
    points = []
    max_t = 16 * math.pi
    for i in range(num_points + 1):
        t = (i / num_points) * max_t
        xr = (R - r) * math.cos(t) + d * math.cos(((R - r) / r) * t)
        yr = (R - r) * math.sin(t) - d * math.sin(((R - r) / r) * t)
        x = 100 + xr
        y = 100 + yr
        points.append((x, y))
    return polyline_to_svg_path(points)

def make_lissajous(A=90, B=90, a=5, b=4, delta=math.pi/2, num_points=1000):
    points = []
    for i in range(num_points + 1):
        t = (i / num_points) * 2 * math.pi
        x = 100 + A * math.sin(a * t + delta)
        y = 100 + B * math.sin(b * t)
        points.append((x, y))
    return polyline_to_svg_path(points)

if __name__ == "__main__":
    os.makedirs('patterns', exist_ok=True)
    generate_svg('patterns/spiral.svg', make_spiral())
    generate_svg('patterns/flower.svg', make_rose(k=6)) 
    generate_svg('patterns/mandala.svg', make_spirograph())
    generate_svg('patterns/lissajous.svg', make_lissajous())
    print("Generated all patterns in the 'patterns' directory.")
