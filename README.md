# Hyprland Workspace Manager

A lightweight Python GUI for managing, naming, and navigating Hyprland workspaces.

![App Icon](assets/icon.svg)

## Features
- **Custom Naming:** Assign custom names to workspaces.
- **Explode Workspace:** Distribute all windows in the active workspace to new, uniquely named workspaces (ID-[APP_CLASS]-Original_Title).
- **Auto-Reset:** Automatically clears names when a workspace becomes empty.
- **Smart Launching:** Opens centered in floating mode and stays on top.
- **Auto-Close:** Automatically closes after navigating to a workspace.
- **Quick Search:** Filter workspaces by name or ID.
- **Dark/Light Themes:** Built-in theme support with adjustable transparency.
- **Escape to Close:** Quickly dismiss the manager with the `Esc` key.

## Installation & Setup

### Quick Launch
The project includes a `launch.sh` script that automatically manages a virtual environment and dependencies.
```bash
chmod +x launch.sh
./launch.sh
```

### Manual Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python run.py
   ```

### Desktop Integration
To add the manager to your application menu:
1. Copy the desktop entry:
   ```bash
   cp hypr-ws-manager.desktop ~/.local/share/applications/
   ```
2. Install the icon:
   ```bash
   mkdir -p ~/.local/share/icons
   cp assets/icon.svg ~/.local/share/icons/hypr-ws-manager.svg
   ```

## Configuration
Settings are stored in `~/.config/hypr-ws-manager/config.json`. You can adjust the `hyprctl` path, theme, and transparency directly through the in-app settings menu.

## License
BSD 3-Clause "New" or "Revised" License
