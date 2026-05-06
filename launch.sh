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
    echo "Creating virtual environment in $VENV_DIR using $PYTHON_CMD..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activate and install requirements immediately after creation
    source "$VENV_DIR/bin/activate"
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    # Activate existing environment
    source "$VENV_DIR/bin/activate"
fi

# Run the application
echo "Launching Hyprland Workspace Manager..."
exec python run.py
