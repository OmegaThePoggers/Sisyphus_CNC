# Sisyphus Controller

A custom cross-platform desktop application for controlling GRBL-based Sisyphus sand tables. Stream SVGs directly to your table without needing intermediate converting steps, simulate pathing, and manage drawing playlists.

## Features

- **Direct SVG Parsing:** Load SVGs directly. The app flattens Bézier curves and arcs into safe G-code.
- **Auto-Scaling & Clamping:** Geometries are automatically scaled to fit your configured table dimensions. Built-in software clamping ensures your hardware won't crash (critical for tables without limit switches).
- **Smooth Returns:** Planners inject natural multi-loop spiral return-to-center motions, eliminating abrupt tool-head jumps.
- **Simulation Mode:** Visually preview generated toolpaths before sending commands to the table.
- **Idle Playlist Mode:** Create endless drawing sessions. Queue multiple SVGs and let the app continuously morph/transition and execute patterns in the background.

## Setup

Requires Python 3.10+ and [`uv`](https://docs.astral.sh/uv/) for package management.

```bash
# Clone the repository
git clone https://github.com/yourusername/sisyphus.git
cd sisyphus

# Run the app directly
uv run sisyphus
```

## Configuration

Settings (like bed size and feed rate) are stored in `config/config.json`.
Adjust the internal dimensions and default serial connection settings inside to fit your specific build.

```json
{
  "serial": {
    "port": "auto",
    "baudrate": 115200
  },
  "workspace": {
    "width": 210.0,
    "height": 148.5,
    "margin": 10.0
  },
  "feed_rate": 2000
}
```

## Contributing
Happy creating! Pull requests welcome.
