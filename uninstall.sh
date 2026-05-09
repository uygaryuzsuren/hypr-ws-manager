#!/bin/bash

DESKTOP_FILE="$HOME/.local/share/applications/hypr-ws-manager.desktop"
ICON_FILE="$HOME/.local/share/icons/hypr-ws-manager.png"
TRACKER_AUTOSTART="$HOME/.config/autostart/hypr-ws-manager-tracker.desktop"
CACHE_DIR="$HOME/.cache/hypr-ws-manager"

echo "Uninstalling Hyprland Workspace Manager..."

# 1. Stop the tracker daemon if running
if pgrep -f "src/tracker.py" > /dev/null; then
    echo "Stopping background tracker daemon..."
    pkill -f "src/tracker.py"
fi

# 2. Remove desktop files
[ -f "$DESKTOP_FILE" ] && rm "$DESKTOP_FILE" && echo "Removed: $DESKTOP_FILE"
[ -f "$TRACKER_AUTOSTART" ] && rm "$TRACKER_AUTOSTART" && echo "Removed: $TRACKER_AUTOSTART"

# 3. Remove icon
[ -f "$ICON_FILE" ] && rm "$ICON_FILE" && echo "Removed: $ICON_FILE"

# 4. Cleanup cache
[ -d "$CACHE_DIR" ] && rm -rf "$CACHE_DIR" && echo "Removed cache: $CACHE_DIR"

echo "Uninstallation complete."
