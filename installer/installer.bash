#!/bin/bash

# Via terminal, run the following commands:
# chmod +x installer.sh
# ./installer.sh

command_exists() {
    command -v "$@" >/dev/null 2>&1
}

# Homebrew installation (if required)
install_homebrew() {
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

    if command_exists brew; then
        echo "Homebrew installed successfully."
    else
        echo "Failed to install Homebrew."
        exit 1
    fi
}

# MacOS installation preparation (if required)
install_python_macos() {
    if ! command_exists brew; then
        install_homebrew
    fi

    echo "Installing Python for macOS..."
    brew install python
}

# Linux installation preparation (if required)
install_python_linux() {
    echo "Installing Python and pip for Linux..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
}

# Required Watering plugin packages
install_packages() {
    echo "Installing Python packages..."
    python3 -m pip install --upgrade pip
    python3 -m pip install signalrcore pyqt5
}

# Installation process
main() {
    # Check for Python and pip, install if necessary
    if ! command_exists python3; then
        echo "Python 3 is not installed. Attempting to install..."
        case "$OSTYPE" in
            linux*)
                install_python_linux
                ;;
            darwin*)
                install_python_macos
                ;;
            *)
                echo "Unsupported operating system. Please install Python manually."
                exit 1
                ;;
        esac
    else
        echo "Python 3 is already installed."
    fi

    if ! command_exists pip3; then
        echo "pip is not installed. Installing..."
        python3 -m ensurepip --upgrade
    else
        echo "pip is already installed."
    fi

    # Install the required Python packages
    install_packages

    echo "Installation complete."
}

# Run installer
main
