# Hyprland Workspace Manager (hypr-ws-manager)

A Python-based GUI utility to manage and navigate Hyprland workspaces with custom naming and search capabilities.

## Tech Stack
- **Language:** Python 3.10+
- **GUI Framework:** PySide6 (Qt for Python)
- **Configuration:** JSON (stored in `~/.config/hypr-ws-manager/config.json`)
- **Process Communication:** `subprocess` for `hyprctl` commands.

## Architecture & Design
- **Core Logic (`hypr_manager.py`):** Handles execution of `hyprctl` commands and parsing JSON output. Includes logic for forcing floating/centered state via Hyprland dispatchers.
- **Config Management (`config.py`):** Manages user preferences (theme, transparency, workspace names, `hyprctl` path). Automatically resolves the absolute path of `hyprctl` on first run.
- **GUI Layer (`ui/`):**
    - `main_window.py`: The primary interface with search and workspace list. Implements auto-close and Escape-to-close behavior.
    - `settings_window.py`: Window for theme and transparency settings. Includes a reset button for the `hyprctl` path.
    - `widgets.py`: Custom components for workspace items.

## Conventions
- **Naming:** Use `snake_case` for variables and functions, `PascalCase` for classes.
- **Styling:** Use QSS (Qt Style Sheets) for theming.
- **JSON Handling:** Always use `hyprctl -j` for robust parsing.
- **Error Handling:** Gracefully handle cases where `hyprctl` is missing or fails.

## Key Workflows
1. **Fetching & Cleanup:** `hyprctl workspaces -j`. Custom names are pruned if the corresponding workspace no longer exists.
2. **Switching & Closing:** `hyprctl dispatch workspace <id_or_name>` followed by application closure.
3. **Window Management:** Uses `class:^hypr-ws-manager$` selector to force `setfloating`, `centerwindow`, and `pin` on startup.
4. **Search:** Real-time filtering of the workspace list based on names or IDs.

## Configuration Schema
```json
{
  "hyprctl_path": "/usr/bin/hyprctl",
  "theme": "dark",
  "transparency": 0.9,
  "workspace_names": {
    "1": "Web",
    "2": "Dev"
  }
}
```
