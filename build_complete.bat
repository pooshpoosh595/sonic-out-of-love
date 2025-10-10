@echo off
echo Building Sawnick Out of Love with all assets...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo Building with PyInstaller...
pyinstaller --onefile ^
    --add-data "sawnick.png;." ^
    --add-data "brokenHeartEnemy.png;." ^
    --add-data "chiliDog.png;." ^
    --add-data "joyful_lover.png;." ^
    --add-data "coinNoBG.png;." ^
    --add-data "collectHeart.png;." ^
    --add-data "companion1cutscene.png;." ^
    --add-data "companion2cutscene.png;." ^
    --add-data "tails.png;." ^
    --add-data "knuckles.png;." ^
    --add-data "lover.png;." ^
    --add-data "lover2.png;." ^
    --add-data "loverSelectionScreen.jpg;." ^
    --add-data "lover2SelectionScreen.jpg;." ^
    --add-data "loveyDoveyAmy.png;." ^
    --add-data "loveyDoveyShadow.png;." ^
    --add-data "gameOver.png;." ^
    --add-data "anotherTry.png;." ^
    --add-data "uhOh.png;." ^
    --add-data "chiliOrLove.png;." ^
    --add-data "hungryEnding.png;." ^
    --add-data "defeatedDog.png;." ^
    --add-data "settingsImageNoBG.png;." ^
    --add-data "knucklesCreditsNoGB.png;." ^
    --add-data "bgInfoTails.png;." ^
    --add-data "sonicMainMenu.png;." ^
    --add-data "SawnickTitleScreen.mp3;." ^
    --add-data "Sawnick Out of Love.mp3;." ^
    --add-data "Sawnick_ Out of LoveEmoVersion.mp3;." ^
    --add-data "Sawnick_ Out of Love Theme 3.0.mp3;." ^
    --add-data "The Valentine's Day Game of Love.mp3;." ^
    --add-data "Finally Together.mp3;." ^
    --add-data "Finally Together no intro.wav;." ^
    --add-data "Chili Dog Delight.mp3;." ^
    --add-data "gameoverjinglecustom.mp3;." ^
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
