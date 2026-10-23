# Screen Reaction Bot

High-performance visual automation and reaction bot for desktop applications and gaming with DirectInput DirectX hardware scan codes, custom regions of interest (ROI), and multi-rule automation.

## Features
- **DirectInput Hardware Scancodes**: Compatible with DirectX and 3D game engines (80ms minimum hold).
- **5 High-Contrast Modern Themes**: Discord Slate, Midnight OLED, Cyberpunk Neon, Emerald Forest, Clean Modern Light.
- **Dynamic Text Scaling**: 1-click toggle between Normal (100%) and Large (120%) font stacks.
- **Compact Mini-Widget Mode**: 310x95px floating HUD that stays on top during gaming.
- **Multi-Rule Engine**: Independent trigger rules with custom names, enable/disable toggles, and chained macros.
- **Sub-millisecond Pixel Triggers**: Real-time pixel monitoring (<1ms).
- **Scan Region Bounding (ROI)**: Restrict detection to specific screen areas for up to 10x scanning speed.
- **Anti-Detection Humanization**: Micro-timing jitter and cursor drift variance.
- **Global Hotkeys**:
  - `[F8]` Start / Stop engine
  - `[F9]` Snip active rule target

## Quick Start (Python)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python screen_bot_v10.py
   ```

## Compiling to Standalone .exe
To build a standalone executable that runs without Python:
```bash
python build_exe.py
```
Your compiled executable will appear in `dist/ScreenReactionBot.exe`.
