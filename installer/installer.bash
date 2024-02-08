#!/bin/bash

# Prompt user to select a folder
echo "Please, enter the path of the folder that contains the QGIS Watering Plugin:"
read folderPath

# Check if the folder exists
if [ -d "$folderPath" ]; then
    echo "Folder exists. Proceeding..."
else
    echo "Folder does not exist. Try again. Exiting..."
    exit 1
fi

# Check for Python installation
if ! command -v python3 &> /dev/null; then
    echo "Python could not be found. Please install Python manually and try again."
    exit 1
else
    echo "Python is installed."
fi

# Install necessary Python packages
echo "Installing Python packages: signalrcore and PyQt5..."
python3 -m pip install signalrcore PyQt5

# Determine QGIS plugins directory path
# For MacOS
if [ "$(uname)" == "Darwin" ]; then
    QGIS_PLUGIN_DIR="$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
# For Linux
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    QGIS_PLUGIN_DIR="$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins"
else
    echo "Unsupported operating system. Exiting..."
    exit 1
fi

# Check if QGIS plugins directory exists, if not, create it
if [ ! -d "$QGIS_PLUGIN_DIR" ]; then
    echo "QGIS plugins directory does not exist. Creating it..."
    mkdir -p "$QGIS_PLUGIN_DIR"
fi

# Copy the selected folder to the QGIS plugins directory
cp -r "$folderPath" "$QGIS_PLUGIN_DIR"

echo "QGIS Watering Plugin has been successfully added to the QGIS plugins directory. Installation completed."
