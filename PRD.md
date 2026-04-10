PRODUCT REQUIREMENTS DOCUMENT (PRD)
1. PRODUCT OVERVIEW

Build a cross-platform desktop application (Linux + Windows) to control a GRBL-based Arduino Uno Sisyphus-style sand table.

The application must:

Convert SVG vector graphics into smooth G-code
Stream G-code to GRBL via serial communication
Provide two main modes:
Idle Mode (looping playlist of patterns)
Custom Pattern Mode (user-selected SVG)
Include a Simulation Mode to preview motion without hardware
Support an advanced “Transform Mode” for smooth morphing between patterns

The system operates WITHOUT limit switches, so safety and boundary handling must be handled in software.

2. TARGET PLATFORM
Primary: Linux (development)
Secondary: Windows (runtime compatibility)
Language: Python
UI Framework: PySide6 (Qt for Python)
3. CORE SYSTEM ARCHITECTURE

Organize the project into the following modules:

core/
svg_parser.py
gcode_generator.py
motion_planner.py
resampler.py

hardware/
serial_controller.py

simulation/
renderer.py
animator.py

ui/
main_window.py
idle_mode.py
custom_mode.py
simulation_mode.py

config/
config.json

4. HARDWARE ASSUMPTIONS
Controller: Arduino Uno running GRBL
No limit switches
Manual centering required at startup
Default parameters:
Feed rate: 2000 mm/min
Acceleration: 180 mm/s²
Workspace: 210mm x 148.5mm
Safety margin must be enforced
5. CONFIGURATION SYSTEM

Provide a config.json:

{
"feed_rate": 2000,
"acceleration": 180,
"workspace": {
"width": 210,
"height": 148.5,
"margin": 10
},
"serial": {
"port": "auto",
"baudrate": 115200
}
}

6. CORE FEATURES
6.1 SVG → G-code Conversion
Accept SVG input ONLY
Extract paths (ignore fills)
Convert to:
G1 (lines)
G2/G3 (arcs where possible)
Normalize coordinate system
Ensure smooth motion (no sharp discontinuities)
6.2 Scaling and Safety
Automatically scale SVG to fit within:

max_x = (width / 2) - margin
max_y = (height / 2) - margin

Clamp all generated coordinates:

x = max(min(x, max_x), -max_x)
y = max(min(y, max_y), -max_y)

Prevent any out-of-bounds motion
6.3 Centering System
User manually positions gantry at center
On "Set Center" button:

Send:
G92 X0 Y0

All motion is relative to this origin
6.4 Serial Communication
Use pyserial
Send G-code line-by-line
Wait for "ok" response before next line
On error:
Immediately stop execution
Notify UI
Show restart option
7. APPLICATION MODES
7.1 Idle Mode (Playlist Mode)
User selects folder containing SVG files
App loads and displays as reorderable playlist (like Spotify)
Supports:
drag-and-drop reorder
add/remove patterns

Execution loop:

for pattern in playlist:
generate gcode
execute
smoothly return to center
continue

7.2 Custom Pattern Mode
User selects a single SVG
App converts and draws once
7.3 Simulation Mode
Load SVG or G-code
Render 2D path preview
Animate toolhead movement

Requirements:

Smooth animation of motion
Time-based interpolation
Optional trail visualization

No physics simulation required (kinematic only)

8. TRANSFORM MODE (ADVANCED FEATURE)

Optional toggle in Idle Mode:

Enable Transform Mode

Behavior:

Instead of discrete patterns, morph one pattern into the next
8.1 Algorithm
Resample both paths into N evenly spaced points
Ensure equal point count
Interpolate:

P_i(t) = (1 - α) * A_i + α * B_i

Stream resulting points as continuous motion
8.2 Constraints
No return to center in transform mode
Continuous motion required
If paths incompatible → fallback to normal mode
9. RETURN-TO-CENTER BEHAVIOR

Must NOT be abrupt.

DO NOT:
G1 X0 Y0 at high speed

Instead:

Use gradual interpolation or arc-based return
Maintain same feed rate as drawing
Ensure visually smooth motion
10. UI REQUIREMENTS
Home Screen
Idle Mode button
Custom Mode button
Simulation Mode button
Idle Mode Screen
Playlist panel
Controls:
Start
Pause
Stop
Return to Center
Reset Center
Transform Mode toggle
Custom Mode Screen
Load SVG
Draw button
Simulation Mode Screen
Load file
Play / Pause animation
11. ERROR HANDLING
Serial disconnect → immediate stop
GRBL error → stop + alert
Invalid SVG → show error message
Provide “Restart” option in UI
12. PERFORMANCE REQUIREMENTS
Smooth motion without jitter
Efficient G-code streaming (no buffer overflow)
UI must remain responsive during execution
13. FUTURE EXTENSIONS (NOT IMPLEMENTED NOW)
OpenCV-based drawing input
Physics-based simulation
Real-time drawing from camera
Endless morphing chains
14. DEVELOPMENT PRIORITY ORDER

Phase 1:

Serial communication
Basic UI
Manual G-code execution

Phase 2:

SVG parsing
Scaling and centering

Phase 3:

Simulation mode

Phase 4:

Idle mode playlist

Phase 5:

Transform mode
15. KEY DESIGN PRINCIPLES
Smoothness over speed
Safety without hardware switches
Deterministic motion
Modular architecture
Clean, modern UI
