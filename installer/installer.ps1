# Check if Python is installed
$pythonInstalled = $null -ne (Get-Command python -ErrorAction SilentlyContinue)

if (-not $pythonInstalled) {
    Write-Host "Python is not installed. Please install Python before proceeding."
    exit
}

# Install required packages for QGIS Watering Plugin
python -m pip install --upgrade pip
pip install signalrcore pyqt5

Write-Host "Installation complete."
