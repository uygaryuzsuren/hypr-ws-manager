#!/bin/bash

DESKTOP_FILE="$HOME/.local/share/applications/hypr-ws-manager.desktop"
ICON_FILE="$HOME/.local/share/icons/hypr-ws-manager.svg"

echo "Uninstalling Hyprland Workspace Manager..."

if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "Removed: $DESKTOP_FILE"
else
    echo "Desktop entry not found, skipping."
fi

if [ -f "$ICON_FILE" ]; then
    rm "$ICON_FILE"
    echo "Removed: $ICON_FILE"
else
    echo "Icon file not found, skipping."
fi

echo "Uninstallation complete."
