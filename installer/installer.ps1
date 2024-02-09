# Determine QGIS Watering folder to be added to QGIS plugin’s folder
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$folderToCopy = Split-Path -Parent $scriptDir

# Check if the folder exists
if (-Not (Test-Path $folderToCopy)) {
    Write-Host "Folder does not exist. Exiting..."
    exit
}

# Check for Python installation
$pythonInstalled = $null -ne (Get-Command python -ErrorAction SilentlyContinue)
if (-Not $pythonInstalled) {
    Write-Host "Python could not be found. Please install Python manually and try again."
    exit
} else {
    Write-Host "Python is installed."
}

# Install necessary Python packages
Write-Host "Installing Python packages: signalrcore and PyQt5..."
python -m pip install signalrcore PyQt5

# Determine QGIS plugins directory path for Windows
$QGIS_PLUGIN_DIR = Join-Path $env:UserProfile "AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins"

# Check if QGIS plugins directory exists, if not, create it
if (-Not (Test-Path $QGIS_PLUGIN_DIR)) {
    Write-Host "QGIS plugins directory does not exist. Creating it..."
    New-Item -ItemType Directory -Force -Path $QGIS_PLUGIN_DIR
}

# Copy the parent folder of the script to the QGIS plugins directory
Copy-Item -Recurse -Force $folderToCopy $QGIS_PLUGIN_DIR

Write-Host "QGIS Watering Plugin has been successfully added to the QGIS plugins directory. Installation completed."
