# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['airportGameV2.py'],
    pathex=[],
    binaries=[],
    datas=[('sawnick.png', '.'), ('brokenHeartEnemy.png', '.'), ('chiliDog.png', '.'), ('joyful_lover.png', '.'), ('coinNoBG.png', '.'), ('collectHeart.png', '.'), ('companion1cutscene.png', '.'), ('companion2cutscene.png', '.'), ('tails.png', '.'), ('knuckles.png', '.'), ('lover.png', '.'), ('lover2.png', '.'), ('loverSelectionScreen.jpg', '.'), ('lover2SelectionScreen.jpg', '.'), ('loveyDoveyAmy.png', '.'), ('loveyDoveyShadow.png', '.'), ('gameOver.png', '.'), ('anotherTry.png', '.'), ('uhOh.png', '.'), ('chiliOrLove.png', '.'), ('hungryEnding.png', '.'), ('defeatedDog.png', '.'), ('settingsImageNoBG.png', '.'), ('knucklesCreditsNoGB.png', '.'), ('bgInfoTails.png', '.'), ('sonicMainMenu.png', '.'), ('SawnickTitleScreen.mp3', '.'), ('Sawnick Out of Love.mp3', '.'), ('Sawnick_ Out of LoveEmoVersion.mp3', '.'), ('Sawnick_ Out of Love Theme 3.0.mp3', '.'), ("The Valentine's Day Game of Love.mp3", '.'), ('Finally Together.mp3', '.'), ('Finally Together no intro.wav', '.'), ('Chili Dog Delight.mp3', '.'), ('gameoverjinglecustom.mp3', '.'), ('key_bindings.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Sawnick_Out_of_Love',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
