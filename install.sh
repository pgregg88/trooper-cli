#!/bin/bash

set -e  # Exit on error

# Detect OS
OS="$(uname -s)"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install CLI wrapper
install_cli() {
    echo "Installing CLI wrapper..."
    sudo cp "${SCRIPT_DIR}/trooper.sh" /usr/local/bin/trooper
    sudo chmod +x /usr/local/bin/trooper
}

# Install web service (Linux only)
install_web_service() {
    if [ "$OS" = "Linux" ]; then
        echo "Installing web service..."
        mkdir -p ~/.config/systemd/user/
        cp "${SCRIPT_DIR}/trooper-web.service" ~/.config/systemd/user/
        systemctl --user daemon-reload
        echo "Web service installed. To start it:"
        echo "systemctl --user enable trooper-web.service"
        echo "systemctl --user start trooper-web.service"
    fi
}

# Validate installation
validate_install() {
    if [ -x "/usr/local/bin/trooper" ]; then
        echo "✓ CLI wrapper installed"
    else
        echo "✗ CLI wrapper installation failed"
        exit 1
    fi

    if [ "$OS" = "Linux" ]; then
        if [ -f "$HOME/.config/systemd/user/trooper-web.service" ]; then
            echo "✓ Web service installed"
        else
            echo "✗ Web service installation failed"
            exit 1
        fi
    fi
}

# Main installation
echo "Installing Trooper CLI..."
install_cli
install_web_service
validate_install
echo "Installation complete!" 