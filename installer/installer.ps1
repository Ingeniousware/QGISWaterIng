# Determine the QGIS Watering folder to be added to the QGIS plugin's folder
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$folderToCopy = Split-Path -Parent $scriptDir
$folderName = Split-Path -Leaf $folderToCopy

# Check if the folder exists
if (-Not (Test-Path $folderToCopy)) {
    Write-Host "Folder does not exist. Try again. Exiting..."
    exit 1
}

# Define the path to the QGIS application and its Python executable
$QGIS_APP_PATH = "/Applications/QGIS.app"
$QGIS_PYTHON_PATH = "$QGIS_APP_PATH/Contents/MacOS/bin/python3"

# Check for QGIS Python installation
if (-Not (Test-Path $QGIS_PYTHON_PATH)) {
    Write-Host "QGIS Python could not be found. Please check your QGIS installation and try again."
    exit 1
} else {
    Write-Host "QGIS Python is installed."
}

# Install signalrcore using QGIS's Python
Write-Host "Installing Python package: signalrcore..."
& $QGIS_PYTHON_PATH -m pip install signalrcore

# Determine QGIS plugins directory path for macOS
$QGIS_PLUGIN_DIR = "$HOME/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins"

# Ensure QGIS plugins directory exists
if (-Not (Test-Path $QGIS_PLUGIN_DIR)) {
    Write-Host "QGIS plugins directory does not exist. Creating it..."
    New-Item -ItemType Directory -Force -Path $QGIS_PLUGIN_DIR
}

# Remove existing folder with the same name, if any, and copy the new folder
$destinationFolder = Join-Path $QGIS_PLUGIN_DIR $folderName
if (Test-Path $destinationFolder) {
    Write-Host "Replacing existing plugin folder in the QGIS plugins directory..."
    Remove-Item -Recurse -Force $destinationFolder
}

Copy-Item -Recurse -Force $folderToCopy $QGIS_PLUGIN_DIR

Write-Host "QGIS Watering Plugin has been successfully added (or updated) in the QGIS plugins directory. Installation completed."