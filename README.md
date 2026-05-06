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

### Quick Start
Run the installer script, which will set up your desktop launcher, icon, and environment:
```bash
chmod +x install.sh
./install.sh
```

### Usage
After running the installer, "Hyprland Workspace Manager" will appear in your application launcher.

## Configuration
Settings are stored in `~/.config/hypr-ws-manager/config.json`. You can adjust the `hyprctl` path, theme, and transparency directly through the in-app settings menu.

## License
BSD 3-Clause "New" or "Revised" License
