@echo off
setlocal

:: Step 1: Copy specified folder into QGIS plugins directory
:: Determine QGIS Watering folder to be added to QGIS plugin's folder
set "scriptDir=%~dp0"
set "folderToCopy=%~dp0.."
for %%F in ("%folderToCopy%") do set "folderName=%%~nxF"

:: Check if the folder exists
if not exist "%folderToCopy%" (
    echo Folder to be copied does not exist. Exiting...
    exit /b 1
)

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

echo QGIS Plugin has been successfully added (or updated) in the QGIS plugins directory. Installation completed.

:: Step 2 Attempt to find and use OSGeo4W to install signalrcore
:: Find the QGIS directory in the Program Files
for /d %%D in ("%ProgramFiles%\QGIS *") do (
    set "QGIS_DIR=%%D"
)

:: Check if the QGIS directory was found
if defined QGIS_DIR (
    echo QGIS directory found at %QGIS_DIR%

    :: Setup OSGeo4W environment
    cd %QGIS_DIR%
    
    call "%QGIS_DIR%\bin\o4w_env.bat"
    
    :: Use pip from the OSGeo4W environment to install signalrcore
    echo Installing signalrcore...
    pip install signalrcore

    if errorlevel 1 (
        echo Failed to install signalrcore.
    ) else (
        echo Successfully installed signalrcore.
    )

    :: Use pip from the OSGeo4W environment to install wntr
    echo Installing wntr...
    pip install wntr

    if errorlevel 1 (
        echo Failed to install wntr.
    ) else (
        echo Successfully installed wntr.
    )
) else (
    echo QGIS directory not found in Program Files.
)

echo QGIS Watering plugin successfully installed.

endlocal
pause