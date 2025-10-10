# Building Sawnick: Out of Love for itch.io

This guide will help you create a single executable file for your game that can be uploaded to itch.io.

## What We Changed

We've updated your Python code to use a `resource_path()` function that works with PyInstaller. This function:
- Automatically finds assets whether running from source or from the bundled executable
- Uses `sys._MEIPASS` to locate bundled resources when running from the executable
- Falls back to the current directory when running from source

## Prerequisites

1. **Python 3.7+** installed on your system
2. **pip** (Python package installer)

## Method 1: Using the Batch File (Windows - Easiest)

1. Double-click `build_game.bat`
2. The script will automatically:
   - Install PyInstaller if needed
   - Build your game into a single executable
   - Place the result in the `dist/` folder

## Method 2: Manual Build

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Build the Game
```bash
pyinstaller --onefile --windowed --name "Sawnick_Out_of_Love" airportGameV2.py
```

### Step 3: Find Your Executable
The executable will be created in the `dist/` folder as `Sawnick_Out_of_Love.exe`

## Method 3: Using the Spec File

If you want more control over the build process:

```bash
pyinstaller airport_game.spec
```

## Build Options Explained

- `--onefile`: Creates a single executable file (easier to distribute)
- `--windowed`: Hides the console window when running (better for games)
- `--name`: Sets the name of the output executable

## What Gets Bundled

The build process automatically includes:
- All `.png` and `.jpg` image files
- All `.mp3` and `.wav` audio files
- The `key_bindings.json` file
- Your Python script and all dependencies

## Testing Your Build

1. Navigate to the `dist/` folder
2. Run `Sawnick_Out_of_Love.exe`
3. Test all game features to ensure everything works

## Troubleshooting

### Common Issues:

1. **"File not found" errors**: Make sure all asset files are in the same directory as your Python script
2. **Large file size**: This is normal for PyInstaller builds - it includes Python runtime and all dependencies
3. **Antivirus warnings**: Some antivirus software may flag PyInstaller executables - this is a false positive

### If the build fails:

1. Check that all required files are present
2. Ensure you have write permissions in the current directory
3. Try running `pip install --upgrade pyinstaller`

## Uploading to itch.io

1. Create a new project on itch.io
2. Upload your `Sawnick_Out_of_Love.exe` file
3. Set the appropriate tags and description
4. Set your price (or make it free)
5. Publish!

## File Structure After Build

```
Your Project/
├── airportGameV2.py          # Your source code
├── airport_game.spec         # PyInstaller spec file
├── build_game.bat            # Windows build script
├── requirements.txt          # Python dependencies
├── BUILD_INSTRUCTIONS.md     # This file
├── dist/                     # Created after build
│   └── Sawnick_Out_of_Love.exe  # Your game executable
└── build/                    # Build cache (can be deleted)
```

## Notes

- The first run of the executable might be slower as it extracts resources
- The executable file will be larger than your source code (this is normal)
- You can delete the `build/` folder after successful builds to save space
- Consider using `--onefile` for easy distribution, or `--onedir` if you want faster startup times

Good luck with your itch.io release! 🎮✨
