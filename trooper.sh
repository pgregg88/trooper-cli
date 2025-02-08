#!/bin/bash

# Get the directory where trooper is installed
TROOPER_PATH="$HOME/github_curser/trooper-cli"
VENV_PATH="$TROOPER_PATH/.venv"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please make sure you have installed trooper correctly"
    exit 1
fi

# Activate virtual environment and run trooper
source "$VENV_PATH/bin/activate"
trooper "$@" 