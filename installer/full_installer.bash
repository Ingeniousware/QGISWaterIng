#!/bin/bash

# Prompt for GitHub username
# echo "Please enter your GitHub username:"
# read github_username

# Validate input
# if [ -z "$github_username" ]; then
#    echo "No username entered. Exiting."
#    exit 1
#fi

GITHUB_REPO_URL="https://github.com/Ingeniousware/QGISWaterIng.git"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python could not be found. Please install Python and rerun this script."
    exit 1
fi

# Determine OS and set QGIS plugin directory path accordingly
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    QGIS_PLUGIN_DIR="$HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    QGIS_PLUGIN_DIR="$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"
elif [[ "$OSTYPE" == "msys"* ]]; then
    QGIS_PLUGIN_DIR="$APPDATA/QGIS/QGIS3/profiles/default/python/plugins"
else
    echo "Unsupported OS"
    exit 1
fi

# Watering Plugin directory name
PLUGIN_DIR_NAME="QGISWatering"

# Full path to the plugin directory
PLUGIN_PATH="$QGIS_PLUGIN_DIR/$PLUGIN_DIR_NAME"

# Clone and install plugin if QGIS plugin directory exists
if [ -d "$QGIS_PLUGIN_DIR" ]; then
    # Check if the plugin directory already exists
    if [ ! -d "$PLUGIN_PATH" ]; then
        echo "Cloning plugin into $PLUGIN_PATH..."
        # Clone the GitHub repository
        git clone $GITHUB_REPO_URL "$PLUGIN_PATH"
    else
        echo "Plugin directory already exists at $PLUGIN_PATH. Skipping clone."
    fi
else
    echo "Could not find QGIS plugin directory. Please refer to the README to install the plugin manually."
fi

# Install required Python packages regardless of QGIS plugin directory presence
echo "Installing required Python packages..."
python3 -m pip install signalrcore PyQt5

echo "Installation completed."
