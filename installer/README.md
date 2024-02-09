# Installation Script for QGIS Watering Plugin

This repository contains scripts to automate the installation of certain software packages and dependencies in order to run QGIS Watering plugin. There are two scripts provided:

1. **Bash script** for Linux and macOS systems.
2. **PowerShell script** for Windows systems.

# Prerequisites
Before running the installation scripts, ensure that Python is installed on your system. The scripts will attempt to install the Python packages signalrcore and PyQt5 automatically.

### Running installer on Linux

1. Open a terminal.
2. Navigate to the directory containing `installer.sh`. 
```
cd path/to/QGISWaterIng/installer
```
3. Make the script executable by running:
```
chmod +x installer.sh
```
4. Execute the script:
```
./installer.sh
```

### Running the Script on MacOS

1. Open the Terminal app.
2. Navigate to the directory containing `installer.sh`.
```
cd path/to/QGISWaterIng/installer
```
3. Ensure you have Homebrew installed. If not, the script will attempt to install it.
4. Make the script executable:
```
chmod +x installer.sh
```
5. Run the script:
```
./installer.sh
```

### Running the Script on Windows

1. Open PowerShell as an Administrator.
2. Navigate to the directory containing `installer.ps1`.
```
cd path\to\QGISWaterIng\installer
```
3. Execute the script:
```
.\installer.ps1
```
**Note:** If you encounter an error related to script execution policies, you may need to adjust the execution policy with the following command and then try running the script again:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

# Post-Installation
Once the installation script has completed, the QGIS Watering Plugin will be added to your QGIS plugins directory, and you should be able to use it within QGIS.

Should you encounter any issues during the installation process, please ensure that Python is correctly installed on your system and that you have the necessary permissions to execute scripts and write to the QGIS plugins directory.