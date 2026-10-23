"""
One-Click Executable Builder for Screen Reaction Bot
Compiles screen_bot_v10.py into a standalone ScreenReactionBot.exe
using PyInstaller with a single command.
"""

import os
import subprocess
import sys

TARGET_SCRIPT = "screen_bot_v10.py"
EXE_NAME = "ScreenReactionBot"

def main():
    print("==========================================")
    print("  Screen Reaction Bot - Standalone Builder")
    print("==========================================")

    # 1. Check if PyInstaller is installed
    try:
        import PyInstaller
        print("[✓] PyInstaller is already installed.")
    except ImportError:
        print("[!] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[✓] PyInstaller installed successfully.")

    if not os.path.exists(TARGET_SCRIPT):
        print(f"[-] Error: '{TARGET_SCRIPT}' not found in current folder.")
        print(f"Please place build_exe.py in the same folder as {TARGET_SCRIPT}.")
        input("\nPress Enter to exit...")
        return

    # 2. Run PyInstaller build command
    print(f"\nBuilding standalone '{EXE_NAME}.exe' from '{TARGET_SCRIPT}'...")
    print("This will bundle Python, Tkinter, PyAutoGUI, and Pillow into a single file.")
    print("Please wait 30-60 seconds...\n")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",          # Hide black cmd window on launch
        "--onefile",            # Bundle everything into a single .exe
        "--name", EXE_NAME,     # Output executable name
        "--clean",              # Clear cache before building
        TARGET_SCRIPT
    ]

    try:
        subprocess.check_call(cmd)
        print("\n==========================================")
        print("[✓] Build Complete!")
        print(f"Your executable is ready at: dist\\{EXE_NAME}.exe")
        print("You can copy this .exe to your desktop or any folder and double-click to run!")
        print("==========================================")
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Build failed with error code: {e}")

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()