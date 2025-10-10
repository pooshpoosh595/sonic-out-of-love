import sys
import os

# Resource loading system for PyInstaller compatibility
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Test if assets are accessible
test_assets = [
    'sawnick.png',
    'joyful_lover.png',
    'SawnickTitleScreen.mp3',
    'key_bindings.json'
]

print("=== Asset Test ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Base path: {resource_path('.')}")
print()

for asset in test_assets:
    asset_path = resource_path(asset)
    exists = os.path.exists(asset_path)
    print(f"{asset}: {'✓' if exists else '✗'} - {asset_path}")

print("\n=== Directory Contents ===")
try:
    base_path = resource_path('.')
    contents = os.listdir(base_path)
    print(f"Contents of {base_path}:")
    for item in sorted(contents):
        print(f"  {item}")
except Exception as e:
    print(f"Error listing directory: {e}")
