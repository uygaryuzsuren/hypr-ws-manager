#!/bin/bash

# Get the absolute path to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$HOME/.local/share/applications/hypr-ws-manager.desktop"
ICON_DIR="$HOME/.local/share/icons"

echo "Installing Hyprland Workspace Manager to $PROJECT_DIR..."

# 1. Generate the .desktop file
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=Hyprland Workspace Manager
Comment=Manage and name Hyprland workspaces
Exec=$PROJECT_DIR/launch.sh
Path=$PROJECT_DIR/
Icon=hypr-ws-manager
Terminal=false
Type=Application
Categories=Utility;System;
EOF

# 2. Install the icon
mkdir -p "$ICON_DIR"
cp "$PROJECT_DIR/assets/icon.svg" "$ICON_DIR/hypr-ws-manager.svg"

echo "Installation complete!"
echo "Desktop entry created at: $DESKTOP_FILE"
echo "Icon installed to: $ICON_DIR/hypr-ws-manager.svg"
echo "You can now find the app in your application launcher."
