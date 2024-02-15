@echo off
setlocal

:: Determine QGIS Watering folder to be added to QGIS plugin's folder
set "scriptDir=%~dp0"
set "folderToCopy=%~dp0.."
for %%F in ("%folderToCopy%") do set "folderName=%%~nxF"

:: Check if the folder exists
if not exist "%folderToCopy%" (
    echo Folder does not exist. Try again. Exiting...
    exit /b 1
)

:: Search for QGIS Python path
set "QGIS_PYTHON_PATH="
for /r "C:\Program Files" %%a in (python-qgis.bat) do set "QGIS_PYTHON_PATH=%%~dpnxa"

:: Check for QGIS Python installation
if not defined QGIS_PYTHON_PATH (
    echo QGIS Python could not be found. Please check your QGIS installation and try again.
    exit /b 1
) else (
    echo QGIS Python is installed: %QGIS_PYTHON_PATH%
)

:: Install signalrcore using QGIS's Python
echo Installing Python package: signalrcore...
call "%QGIS_PYTHON_PATH%" -m pip install signalrcore

:: Determine QGIS plugins directory path for Windows
set "QGIS_PLUGIN_DIR=%UserProfile%\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins"

:: Ensure QGIS plugins directory exists
if not exist "%QGIS_PLUGIN_DIR%" (
    echo QGIS plugins directory does not exist. Creating it...
    mkdir "%QGIS_PLUGIN_DIR%"
)

:: Remove existing folder with the same name, if any, and copy the new folder
set "destinationFolder=%QGIS_PLUGIN_DIR%\%folderName%"
if exist "%destinationFolder%" (
    echo Replacing existing plugin folder in the QGIS plugins directory...
    rmdir /s /q "%destinationFolder%"
)

xcopy /E /I "%folderToCopy%" "%destinationFolder%"

echo QGIS Watering Plugin has been successfully added (or updated) in the QGIS plugins directory. Installation completed.

endlocal