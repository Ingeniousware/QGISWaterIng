# Installation Script for QGIS Watering Plugin

This repository contains scripts to automate the installation of certain software packages and dependencies in order to run QGIS Watering plugin. There are two scripts provided:

1. **Bash script** for Linux and macOS systems.
2. **PowerShell script** for Windows systems.

### Running installer on Linux

1. Open a terminal.
2. Navigate to the directory containing `installer.sh`. 
```
cd ~/QGISWaterIng-main/installer
```
3. Make the script executable by running:
```
chmod +x install.sh
```
4. Execute the script:
```
./install.sh
```

### Running the Script on MacOS

1. Open the Terminal app.
2. Navigate to the directory containing `installer.sh`.
```
cd ~/QGISWaterIng-main/installer
```
3. Ensure you have Homebrew installed. If not, the script will attempt to install it.
4. Make the script executable:
```
chmod +x install.sh
```
5. Run the script:
```
./install.sh
```

### Running the Script on Windows

1. Open PowerShell as an Administrator.
2. Navigate to the directory containing `install.ps1`.
```
cd ~/QGISWaterIng-main/installer
```
3. Execute the script:
```
.\installer.ps1
```
**Note:** If you encounter an error related to script execution policies, you may need to adjust the execution policy with the following command and then try running the script again:
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```