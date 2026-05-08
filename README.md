# Hyprland Workspace Manager

![Version](https://img.shields.io/badge/version-0.9.0--beta-orange)
A lightweight Python GUI for managing, naming, and navigating Hyprland workspaces.

![App Icon](assets/icon.svg)

## Features
- **Custom Naming:** Assign and manage custom names for your workspaces.
- **Explode Suite (Redistribute):**
    - **All:** Distribute every window to its own new workspace.
    - **Selective:** Distribute only windows of a chosen application type.
    - **By App:** Group multiple windows of the same type into a new workspace.
    - **By Token:** Group windows matching a title keyword into a new workspace.
- **Collect Suite (Gather):**
    - **All:** Pull all windows from every workspace into the selected one.
    - **By App:** Gather all windows of a specific type from across the system.
    - **By Token:** Gather windows matching a title keyword from any workspace.
- **Deep Search:** Instantly filter workspaces by ID, name, application class, or **individual window titles**.
- **Visual Polish:**
    - **Multi-Icon Support:** View up to 5 icons per workspace representing open apps.
    - **Active Workspace Highlight:** Visually identify your current location in the list.
    - **Auto-Theming:** Dark and Light mode support with adjustable transparency.
- **Smart Launching:** Opens centered in floating mode, stays on top, and focuses search automatically.
- **Keyboard Optimized:** Full navigation via Arrow Keys/Tab and Enter; Escape to close.
- **Auto-Reset:** Automatically clears names and configuration for empty workspaces.

## Installation & Setup

### Quick Start
Run the installer script, which will set up your desktop launcher, icon, and environment:
```bash
chmod +x install.sh
./install.sh
```

## Usage

After running the installer, **Hyprland Workspace Manager** will appear in your application launcher. You can also run it via terminal using `./launch.sh`.

### Basic Navigation & Controls
- **Keyboard (Primary)**:
  - **Tab / Arrow Keys**: Navigate through the workspace list.
  - **Enter**: Switch to the selected workspace.
  - **Search**: Start typing immediately upon launch to filter workspaces by name, ID, or window titles.
  - **Escape**: Close the manager instantly.
- **Mouse**:
  - **Click**: Switch to a workspace instantly.
  - **Edit (✎ icon)**: Click to rename a workspace. Press Enter to save.

---

### The "Explode" Suite (Redistribute)
The Explode tools help you clean up a cluttered workspace by moving its windows to new, dedicated workspaces. Select a source workspace from the list, then use:

- **Dropdown Filter**: Hover over **Explode** or **Explode by App** to reveal a dropdown. It lists all application types found in the selected workspace (e.g., `firefox`, `kitty`).
- **Explode**: 
  - With **"All"** selected: Moves **every window** from the source workspace into its own separate, new workspace.
  - With a **specific app** selected: Moves **each window of that type** into its own unique, new workspace.
- **Explode by App**: 
  - With **"All"** selected: Groups windows by their type (e.g., all Firefox windows move together to one new workspace, all terminals move to another).
  - With a **specific app** selected: Moves **all windows of that type** together into a single new workspace.
- **Explode by Token**: Type a keyword in the **Token...** box (revealed on hover). Moves all windows containing that keyword in their title to a new workspace.

---

### The "Collect" Suite (Gather)
The Collect tools gather windows from across your entire system into your **selected workspace**.

- **Dropdown Filter**: Hover over **Collect by App** to see all applications currently running in any workspace.
- **Collect**: Pulls **all windows** from every other workspace into the one you have selected.
- **Collect by App**: Select an application from the dropdown. Pulls all windows of that specific type into your selected workspace.
- **Collect by Token**: Type a keyword in the **Token...** box. Pulls all windows containing that keyword in their title from across all workspaces into the selected one.

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
