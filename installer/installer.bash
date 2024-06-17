#!/bin/bash

# Determine QGIS Watering folder to be added to QGIS plugin’s folder
scriptDir="$(dirname "$(readlink -f "$0")")"
folderToCopy="$(dirname "$scriptDir")"
folderName=$(basename "$folderToCopy")

# Check if the folder exists
if [ -d "$folderToCopy" ]; then
    echo "Folder exists. Proceeding..."
else
    echo "Folder does not exist. Try again. Exiting..."
    exit 1
fi

# Determine OS and set QGIS Python path accordingly
if [ "$(uname)" == "Darwin" ]; then
    # Attempt to find the QGIS application path on macOS
    QGIS_APP_PATH="/Applications/QGIS.app"
    if [ ! -d "$QGIS_APP_PATH" ]; then
        echo "QGIS application could not be found in the default location (/Applications/QGIS.app). Please check your QGIS installation and try again."
        exit 1
    fi
    QGIS_PYTHON_PATH="$QGIS_APP_PATH/Contents/MacOS/bin/python3"
else
    echo "This script is intended for use on macOS with QGIS installed in the default location. For other operating systems, please modify the script accordingly."
    exit 1
fi

# Check for QGIS Python installation
if ! [ -x "$QGIS_PYTHON_PATH" ]; then
    echo "QGIS Python could not be found. Please check your QGIS installation and try again."
    exit 1
else
    echo "QGIS Python is installed."
fi

# Install signalrcore using QGIS's Python
echo "Installing Python package: signalrcore..."
$QGIS_PYTHON_PATH -m pip install signalrcore

# Install wntr using QGIS's Python
echo "Installing Python package: wntr..."
$QGIS_PYTHON_PATH -m pip install wntr

# Determine QGIS plugins directory path for macOS
QGIS_PLUGIN_DIR="$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"

# Ensure QGIS plugins directory exists
if [ ! -d "$QGIS_PLUGIN_DIR" ]; then
    echo "QGIS plugins directory does not exist. Creating it..."
    mkdir -p "$QGIS_PLUGIN_DIR"
fi

# Remove existing folder with the same name, if any, and copy the new folder
destinationFolder="$QGIS_PLUGIN_DIR/$folderName"
if [ -d "$destinationFolder" ]; then
    echo "Replacing existing plugin folder in the QGIS plugins directory..."
    rm -rf "$destinationFolder"
fi

cp -r "$folderToCopy" "$QGIS_PLUGIN_DIR"

echo "QGIS Watering Plugin has been successfully added (or updated) in the QGIS plugins directory. Installation completed."
