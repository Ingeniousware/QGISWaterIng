#!/bin/bash

# Determine QGIS Watering folder to be added to QGIS plugin’s folder
if command -v realpath >/dev/null 2>&1; then
    scriptDir="$(dirname "$(realpath "$0")")"
else
    # Fallback for systems without realpath (works on macOS)
    scriptDir="$(cd "$(dirname "$0")" && pwd)"
fi

folderToCopy="$(dirname "$scriptDir")"
folderName=$(basename "$folderToCopy")

# Check if the folder exists
if [ -d "$folderToCopy" ]; then
    echo "Folder exists. Proceeding..."
else
    echo "Folder does not exist. Try again. Exiting..."
    exit 1
fi

# Check if QGIS Python path is provided as an argument
if [ $# -ge 1 ]; then
    QGIS_PYTHON_PATH="$1"
else
    # If no argument provided, check if on macOS and use default path
    if [ "$(uname)" != "Darwin" ]; then
        echo "Error: This script requires the QGIS Python path to be provided as an argument on non-macOS systems."
        echo "Usage: $0 [QGIS_PYTHON_PATH]"
        exit 1
    fi
    QGIS_APP_PATH="/Applications/QGIS.app"
    if [ ! -d "$QGIS_APP_PATH" ]; then
        echo "Error: QGIS application not found in the default macOS location. Please provide the QGIS Python path as an argument."
        echo "Usage: $0 [QGIS_PYTHON_PATH]"
        exit 1
    fi
    # Use the proper executable path inside the QGIS app bundle
    QGIS_PYTHON_PATH="$QGIS_APP_PATH/Contents/MacOS/bin/python3"
fi

# Check if QGIS Python executable exists
if ! [ -x "$QGIS_PYTHON_PATH" ]; then
    echo "Error: QGIS Python executable not found at '$QGIS_PYTHON_PATH'."
    exit 1
else
    echo "Using QGIS Python executable: $QGIS_PYTHON_PATH"
fi

# Install required Python packages using QGIS's Python
echo "Installing Python package: signalrcore..."
$QGIS_PYTHON_PATH -m pip install signalrcore

echo "Installing Python package: wntr..."
$QGIS_PYTHON_PATH -m pip install wntr

# Determine QGIS plugins directory based on OS
case "$(uname)" in
    Darwin*)
        QGIS_PLUGIN_DIR="$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
        ;;
    Linux*)
        QGIS_PLUGIN_DIR="$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins"
        ;;
    *)
        echo "Unsupported operating system. Please set the QGIS plugins directory manually."
        exit 1
        ;;
esac

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
