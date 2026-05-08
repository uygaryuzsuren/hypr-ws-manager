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

# Check if setup is needed and if we should open a terminal for visibility
if [ ! -d "$VENV_DIR" ] && [ "$1" != "--setup" ] && [ ! -t 0 ]; then
    # List of common terminal emulators
    for term in kitty alacritty foot xfce4-terminal gnome-terminal konsole xterm; do
        if command -v $term >/dev/null 2>&1; then
            case $term in
                gnome-terminal|konsole|xfce4-terminal) exec $term -- "$DIR/launch.sh" --setup ;;
                *) exec $term "$DIR/launch.sh" --setup ;;
            esac
        fi
    done
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "-------------------------------------------------------"
    echo "  Hyprland Workspace Manager - First Run Setup"
    echo "-------------------------------------------------------"
    echo "Creating virtual environment and installing dependencies..."
    echo "This may take a minute depending on your connection."
    
    # Notifications for those who might not see the terminal immediately
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "Hyprland Workspace Manager" "Installing dependencies...\nPlease see the terminal for progress." -i "$DIR/assets/icon.svg" -t 5000
    fi

    if ! $PYTHON_CMD -m venv "$VENV_DIR"; then
        echo "Error: Failed to create virtual environment."
        [ ! -t 0 ] || { echo "Press any key to exit..."; read -n 1; }
        exit 1
    fi
    
    source "$VENV_DIR/bin/activate"
    echo "Upgrading pip..."
    pip install --upgrade pip --quiet
    
    echo "Installing requirements..."
    if ! pip install -r requirements.txt; then
        echo "-------------------------------------------------------"
        echo "Error: Failed to install dependencies."
        echo "Please check your internet connection and try again."
        echo "-------------------------------------------------------"
        [ ! -t 0 ] || { echo "Press any key to exit..."; read -n 1; }
        exit 1
    fi
    
    echo "-------------------------------------------------------"
    echo "Setup complete! Launching app..."
    echo "-------------------------------------------------------"
    sleep 2
else
    # Activate existing environment
    source "$VENV_DIR/bin/activate"
fi

# Run the application in the background and detach from terminal
echo "Launching Hyprland Workspace Manager..."
VENV_PYTHON="$DIR/$VENV_DIR/bin/python"

if [ "$1" == "--setup" ]; then
    # When finishing setup in a terminal, we must ensure the process is fully 
    # detached before the terminal closes, or the connection to the compositor might break.
    ( setsid "$VENV_PYTHON" "$DIR/run.py" >/dev/null 2>&1 & )
    sleep 0.5
else
    # Standard silent launch
    setsid "$VENV_PYTHON" "$DIR/run.py" >/dev/null 2>&1 &
fi
