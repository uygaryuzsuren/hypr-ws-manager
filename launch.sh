#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Find the best python interpreter
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    # Check if 'python' is actually version 3
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    else
        echo "Error: Python 3 is required but not found."
        exit 1
    fi
else
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Define the virtual environment directory
VENV_DIR=".venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "-------------------------------------------------------"
    echo "  Hyprland Workspace Manager - First Run Setup"
    echo "-------------------------------------------------------"
    echo "Creating virtual environment and installing dependencies..."
    echo "This may take a minute. Please wait..."
    
    # Show a notification with the logo if notify-send is available
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Hyprland Workspace Manager" "Installing dependencies...\nPlease wait while we set things up." -i "$DIR/assets/icon.svg" -t 10000
    fi
    
    # Fallback/Additional Hyprland notification
    if command -v hyprctl >/dev/null 2>&1; then
        hyprctl notify 1 10000 "rgb(4c4f69)" "Installing dependencies... Please wait."
    fi

    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activate and install requirements immediately after creation
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Hyprland Workspace Manager" "Setup complete! Launching app..." -i "$DIR/assets/icon.svg" -t 3000
    fi
else
    # Activate existing environment
    source "$VENV_DIR/bin/activate"
fi

# Run the application in the background and detach from terminal
echo "Launching Hyprland Workspace Manager..."
setsid python run.py >/dev/null 2>&1 &
