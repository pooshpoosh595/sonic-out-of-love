@echo off
echo Building Sawnick: Out of Love with PyInstaller...
echo.

REM Check if PyInstaller is installed
py -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    py -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller. Please install it manually:
        echo py -m pip install pyinstaller
        pause
        exit /b 1
    )
)

echo.
echo Building executable...
py -m PyInstaller airportGameV2.spec

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build successful! 
echo The executable is in the dist/ folder.
echo.
pause
