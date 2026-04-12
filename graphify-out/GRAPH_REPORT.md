# Graph Report - .  (2026-04-12)

## Corpus Check
- Corpus is ~4,679 words - fits in a single context window. You may not need a graph.

## Summary
- 138 nodes · 210 edges · 17 communities detected
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]

## God Nodes (most connected - your core abstractions)
1. `IdleModeWidget` - 24 edges
2. `CustomModeWidget` - 18 edges
3. `MainWindow` - 17 edges
4. `SimulationModeWidget` - 17 edges
5. `SerialController` - 16 edges
6. `PlaylistWorker` - 12 edges
7. `SimulationAnimator` - 11 edges
8. `SerialWorker` - 10 edges
9. `MotionPlanner` - 9 edges
10. `SVGParser` - 8 edges

## Surprising Connections (you probably didn't know these)
- `CustomModeWidget` --uses--> `GCodeGenerator`  [INFERRED]
  ui\custom_mode.py → core\gcode_generator.py
- `PlaylistWorker` --uses--> `GCodeGenerator`  [INFERRED]
  ui\idle_mode.py → core\gcode_generator.py
- `IdleModeWidget` --uses--> `GCodeGenerator`  [INFERRED]
  ui\idle_mode.py → core\gcode_generator.py
- `SerialWorker` --uses--> `MotionPlanner`  [INFERRED]
  hardware\serial_controller.py → core\motion_planner.py
- `SerialController` --uses--> `MotionPlanner`  [INFERRED]
  hardware\serial_controller.py → core\motion_planner.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.11
Nodes (3): IdleModeWidget, PlaylistWorker, PathResampler

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (7): QThread, auto_detect_port(), get_available_ports(), _handle_connection_lost(), _handle_error(), SerialController, SerialWorker

### Community 2 - "Community 2"
Cohesion: 0.18
Nodes (4): HomeWidget, MainWindow, QMainWindow, QWidget

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (2): GCodeGenerator, SimulationModeWidget

### Community 4 - "Community 4"
Cohesion: 0.21
Nodes (1): CustomModeWidget

### Community 5 - "Community 5"
Cohesion: 0.27
Nodes (2): SimulationAnimator, QObject

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (2): points is a list of (x,y) tuples representing the GCode path, SimulationRenderer

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (3): MotionPlanner, Generates a smooth inward spiral back to (0,0).         Creates a visible spira, Clear current queue and spiral back to center.

### Community 8 - "Community 8"
Cohesion: 0.4
Nodes (2): Convert svgpathtools Path into a list of (x,y) coordinates.         Continuous, SVGParser

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (0): 

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (1): Resample a single continuous polyline into `num_points` evenly spaced points.

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (1): Interpolates between two paths (assumed to have the same number of points).

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (0): 

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (0): 

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (0): 

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (0): 

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **5 isolated node(s):** `Generates a smooth inward spiral back to (0,0).         Creates a visible spira`, `Resample a single continuous polyline into `num_points` evenly spaced points.`, `Interpolates between two paths (assumed to have the same number of points).`, `Convert svgpathtools Path into a list of (x,y) coordinates.         Continuous`, `points is a list of (x,y) tuples representing the GCode path`
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (2 nodes): `main()`, `main.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (1 nodes): `Resample a single continuous polyline into `num_points` evenly spaced points.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (1 nodes): `Interpolates between two paths (assumed to have the same number of points).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `IdleModeWidget` connect `Community 0` to `Community 8`, `Community 2`, `Community 3`, `Community 7`?**
  _High betweenness centrality (0.273) - this node is a cross-community bridge._
- **Why does `SimulationModeWidget` connect `Community 3` to `Community 8`, `Community 2`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.259) - this node is a cross-community bridge._
- **Why does `SerialController` connect `Community 1` to `Community 2`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.231) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `IdleModeWidget` (e.g. with `SVGParser` and `GCodeGenerator`) actually correct?**
  _`IdleModeWidget` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `CustomModeWidget` (e.g. with `SVGParser` and `GCodeGenerator`) actually correct?**
  _`CustomModeWidget` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `MainWindow` (e.g. with `SerialController` and `CustomModeWidget`) actually correct?**
  _`MainWindow` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `SimulationModeWidget` (e.g. with `HomeWidget` and `MainWindow`) actually correct?**
  _`SimulationModeWidget` has 6 INFERRED edges - model-reasoned connections that need verification._