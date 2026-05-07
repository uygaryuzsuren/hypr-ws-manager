# Hyprland Workspace Manager

![Version](https://img.shields.io/badge/version-0.9.0--beta-orange)
A lightweight Python GUI for managing, naming, and navigating Hyprland workspaces.

![App Icon](assets/icon.svg)

## Features
- **Custom Naming:** Assign custom names to workspaces.
- **Explode Workspace:**
    - **All:** Distribute windows individually.
    - **By App:** Group windows by application type.
    - **By Token:** Group windows by title match.
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

## Usage

After running the installer, **Hyprland Workspace Manager** will appear in your application launcher. You can also run it via terminal using `./launch.sh`.

### Basic Navigation
- **Search Bar**: Type to filter workspaces by ID, custom name, or application class.
- **Switching**: Use **Arrow Keys** to select a workspace and press **Enter**, or simply **Click** an item to switch to it instantly.
- **Closing**: Press **Escape** to dismiss the manager without switching.
- **Renaming**: Click the **✎** icon next to a workspace name to enter a custom title. Press **Enter** to save or **✕** to cancel.

---

### The "Explode" Suite (Redistribute)
The Explode tools help you clean up a cluttered workspace by moving its windows to new, dedicated workspaces. Select the workspace you want to "explode" in the list, then use:

- **Explode**: Moves **every window** from the selected workspace into its own separate, new workspace.
- **Explode by App**: Groups windows of the **same application type** (e.g., all Firefox windows) into their own new workspaces.
- **Explode by Token**: Type a keyword in the **Token...** box. Clicking this will move all windows containing that keyword in their title to a new workspace.

---

### The "Collect" Suite (Gather)
The Collect tools do the opposite—they gather windows from across your entire system into your **selected workspace**.

- **Collect**: Pulls **all windows** from every other workspace into the one you have selected.
- **Collect by App**: Select an application from the **dropdown menu** (e.g., `kitty`). Clicking this pulls all windows of that specific type into your selected workspace.
- **Collect by Token**: Type a keyword in the **Token...** box. Clicking this pulls all windows containing that keyword in their title from across all workspaces into the selected one.

---

### Settings & Theming
Click the **⚙** icon in the top right to access settings:
- **Theme**: Switch between Light and Dark modes.
- **Transparency**: Adjust the window opacity (from Opaque to Glass-like).
- **hyprctl Path**: If you are using a non-standard Hyprland installation, you can configure the path to your `hyprctl` binary here.

---

## Configuration
Settings are stored in `~/.config/hypr-ws-manager/config.json`. You can adjust the `hyprctl` path, theme, and transparency directly through the in-app settings menu.

## Uninstallation
To remove the desktop launcher and icon from your system:
```bash
chmod +x uninstall.sh
./uninstall.sh
```
