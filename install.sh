#!/bin/bash

set -e  # Exit on error

# Detect OS
OS="$(uname -s)"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load environment variables if .env exists
if [ -f "${SCRIPT_DIR}/.env" ]; then
    source "${SCRIPT_DIR}/.env"
fi

# Set TROOPER_INSTALL_PATH if not already set
export TROOPER_INSTALL_PATH="${TROOPER_INSTALL_PATH:-${SCRIPT_DIR}}"

# Print functions
print_status() {
    echo "$1"
}

print_warning() {
    echo "Warning: $1"
}

print_error() {
    echo "Error: $1"
}

# Install CLI wrapper
install_cli() {
    print_status "Installing CLI wrapper..."
    
    # Check if trooper.sh exists
    if [ ! -f "${SCRIPT_DIR}/trooper.sh" ]; then
        print_error "trooper.sh not found in ${SCRIPT_DIR}"
        exit 1
    fi
    
    # Create a temporary file with the correct path
    TMP_TROOPER=$(mktemp)
    sed "s|TROOPER_PATH=.*|TROOPER_PATH=\"${TROOPER_INSTALL_PATH}\"|" "${SCRIPT_DIR}/trooper.sh" > "$TMP_TROOPER"
    
    # Install wrapper
    sudo mv "$TMP_TROOPER" /usr/local/bin/trooper
    sudo chmod +x /usr/local/bin/trooper
    print_status "CLI wrapper installed successfully"
}

# Install web service (Linux only)
install_web_service() {
    if [ "$OS" = "Linux" ]; then
        print_status "Installing web service..."
        
        # Check if service file exists
        if [ ! -f "${SCRIPT_DIR}/trooper-web.service" ]; then
            print_error "trooper-web.service not found in ${SCRIPT_DIR}"
            exit 1
        fi
        
        # Create user systemd directory if it doesn't exist
        mkdir -p ~/.config/systemd/user/
        
        # Create a temporary file with the correct path
        TMP_SERVICE=$(mktemp)
        sed "s|\${TROOPER_INSTALL_PATH}|${TROOPER_INSTALL_PATH}|g" "${SCRIPT_DIR}/trooper-web.service" > "$TMP_SERVICE"
        
        # Install service file
        mv "$TMP_SERVICE" ~/.config/systemd/user/trooper-web.service
        systemctl --user daemon-reload
        
        print_status "Web service installed successfully"
        print_status "To start the web service, run:"
        echo "systemctl --user enable trooper-web.service"
        echo "systemctl --user start trooper-web.service"
    else
        print_warning "Skipping web service installation (Linux only feature)"
    fi
}

# Validate installation
validate_install() {
    local status=0
    
    if [ -x "/usr/local/bin/trooper" ]; then
        print_status "✓ CLI wrapper installed"
    else
        print_error "✗ CLI wrapper installation failed"
        status=1
    fi

    if [ "$OS" = "Linux" ]; then
        if [ -f "$HOME/.config/systemd/user/trooper-web.service" ]; then
            print_status "✓ Web service installed"
        else
            print_error "✗ Web service installation failed"
            status=1
        fi
    fi
    
    return $status
}

# Main installation
print_status "Installing Trooper CLI..."

# Check for required files
if [ ! -f "${SCRIPT_DIR}/trooper.sh" ]; then
    print_error "Required file trooper.sh not found"
    exit 1
fi

if [ "$OS" = "Linux" ] && [ ! -f "${SCRIPT_DIR}/trooper-web.service" ]; then
    print_error "Required file trooper-web.service not found for Linux installation"
    exit 1
fi

# Perform installation
install_cli
install_web_service

# Validate installation
validate_install
print_status "Installation complete!" 