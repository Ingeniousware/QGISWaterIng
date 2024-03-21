@echo off
setlocal enabledelayedexpansion

:: Set the paths to search for OSGeo
set "paths=%ProgramFiles%;%ProgramFiles(x86)%"

:: Flag to check if OSGeo was found
set "osgeoFound=false"

:: Loop through the paths
for %%a in (%paths%) do (
    if exist "%%a\QGIS\bin" (
        set "osgeoFound=true"
        set "osgeoPath=%%a\QGIS\bin"
        goto installPackage
    )
)

:installPackage
if "%osgeoFound%"=="true" (
    echo OSGeo found in !osgeoPath!
    pushd !osgeoPath!
    call o4w_env.bat
    call qt5_env.bat
    call py3_env.bat
    call python3 -m pip install signalrcore
    popd
    echo Installation completed.
) else (
    echo OSGeo not found.
)

endlocal
