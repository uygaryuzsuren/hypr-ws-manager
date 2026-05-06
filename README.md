# Hyprland Workspace Manager

A lightweight Python GUI for managing and naming Hyprland workspaces.

## Features
- **Search:** Quickly find workspaces by name or ID.
- **Naming:** Assign custom names to workspaces.
- **Navigation:** Click on a workspace to switch to it.
- **Settings:**
  - Change visual theme (Light/Dark).
  - Adjust window transparency.
  - Configure custom `hyprctl` path.

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python3 src/main.py
   ```

## Configuration
Settings are stored in `~/.config/hypr-ws-manager/config.json`.
