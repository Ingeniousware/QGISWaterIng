# Get the parent's parent directory of the script
$parentParentDir = Split-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# Attempt to locate QGIS Python executable
$qgisPythonPaths = @(
    "$env:ProgramFiles\QGIS 3.*\apps\Python39\python.exe", # Adjust the Python version if necessary
    "$env:ProgramFiles(x86)\QGIS 3.*\apps\Python39\python.exe"
)

$qgisPythonExe = $null

foreach ($path in $qgisPythonPaths) {
    $resolvedPath = Resolve-Path $path -ErrorAction SilentlyContinue
    if ($resolvedPath) {
        $qgisPythonExe = $resolvedPath.Path
        break
    }
}

if (-not $qgisPythonExe) {
    Write-Host "Could not find QGIS Python executable. Please ensure QGIS is installed."
} else {
    Write-Host "Found QGIS Python at: $qgisPythonExe"
    
    # Install signalrcore using QGIS Python
    Write-Host "Installing signalrcore..."
    Start-Process -FilePath $qgisPythonExe -ArgumentList "-m", "pip", "install", "signalrcore" -Wait -NoNewWindow
    Write-Host "signalrcore installation complete."
}

# Define the QGIS plugins folder path
$qgisPluginsFolder = "$env:APPDATA\QGIS\QGIS3\profiles\default\python\plugins"
$destinationPath = Join-Path $qgisPluginsFolder (Split-Path -Leaf $parentParentDir)

# Check if the destination directory already exists
if (Test-Path $destinationPath) {
    Write-Host "QGIS Watering plugin already exists in QGIS plugins directory. Overwriting..."
    Remove-Item $destinationPath -Recurse -Force
}

# Copy Watering Plugin to QGIS plugin’s folder
Copy-Item $parentParentDir $qgisPluginsFolder -Recurse -Force
Write-Host "QGIS Watering plugin installation completed."
