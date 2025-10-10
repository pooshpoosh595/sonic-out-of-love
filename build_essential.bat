@echo off
echo Building Sawnick Out of Love with essential assets only...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Building with PyInstaller...
pyinstaller --onefile ^
    --add-data "sawnick.png;." ^
    --add-data "joyful_lover.png;." ^
    --add-data "brokenHeartEnemy.png;." ^
    --add-data "chiliDog.png;." ^
    --add-data "coinNoBG.png;." ^
    --add-data "collectHeart.png;." ^
    --add-data "tails.png;." ^
    --add-data "knuckles.png;." ^
    --add-data "lover.png;." ^
    --add-data "lover2.png;." ^
    --add-data "sonicMainMenu.png;." ^
    --add-data "SawnickTitleScreen.mp3;." ^
    --add-data "Sawnick Out of Love.mp3;." ^
    --add-data "key_bindings.json;." ^
    --name "Sawnick_Out_of_Love" ^
    --windowed ^
    airportGameV2.py

echo.
echo Build complete! Testing executable...
echo.
.\dist\Sawnick_Out_of_Love.exe

echo.
echo Game has exited. Press any key to close this window.
pause >nul
