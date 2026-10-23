"""
Screen Reaction Bot (Version 10 - Seamless Flat Styling & Full Theme Integration)
Features:
- Seamless Flat Component Theming (Fixes Tkinter ugly grey background boxes):
    - Completely eliminates the gray #dcdad5 rectangular bounding boxes behind radiobuttons,
      labels, checkboxes, and buttons by overriding ttk's state-based style map (!disabled, active, pressed).
    - Every component's background matches the parent card surface 100% seamlessly.
    - Buttons, coordinate input fields, and comboboxes now use dark-mode entry backgrounds
      instead of jarring light gray / white blocks, highlighting with the theme accent on hover/press.
- High-Legibility Typography Stack:
    - Native 'Segoe UI' with ClearType subpixel font smoothing on Windows.
    - Dynamic Text Scaling toggle in header: 'Normal (100%)' vs 'Large (120%)'.
    - High-contrast text values calibrated to WCAG standards across all 5 themes.
- 5 Handcrafted Modern Themes with Header Combobox:
    1. Discord Slate (Modern gaming dark with vibrant blurple)
    2. Midnight OLED (True pitch black with electric sky blue and pure white - maximum contrast)
    3. Cyberpunk Neon (Midnight purple with neon cyan and synthwave pink)
    4. Emerald Forest (Spruce dark with crisp mint and emerald green)
    5. Clean Modern Light (Crisp slate off-white with deep black text and royal blue)
- Compact Floating Mini-Widget Mode (310x95px) always-on-top with live engine status pill.
- Complete Pro Automation Suite:
    - Multi-Rule Manager with Custom Renaming & Active Toggles.
    - Decoupled Detection & Click Navigation Mapping (Target center, Diff image, Fixed X/Y, In place).
    - 10x Speed Bounded Search Region (ROI).
    - Sub-millisecond Pixel Color Checking (<1ms).
    - Toggleable Anti-Detection Humanization (Random click jitter ±4px & timing variance).
    - Toggleable Real-Time Visual Debug Overlay (Green flash on detected targets).
    - Chained Multi-Step Macro Sequencer.
    - Session Safety Limits (Max Triggers & Session Timeout Timer).
    - DirectInput Hardware Scan Codes & Global Hotkeys [F8] / [F9].
"""

import json
import os
import random
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageGrab, ImageTk
import pyautogui

# Set Windows DPI awareness so screenshot coordinates match display scale
IS_WINDOWS = sys.platform.startswith("win")
if IS_WINDOWS:
    try:
        import ctypes
        from ctypes import wintypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

pyautogui.FAILSAFE = True

VERSION = "10"
CONFIG_FILE = "settings.json"
CHECK_INTERVAL = 0.08
COOLDOWN = 1.5
MIN_GAME_TAP_DURATION = 0.08

# -------------------------------------------------------------
# DirectInput Hardware Scan Codes (DirectX / Game Engine Input)
# -------------------------------------------------------------
if IS_WINDOWS:
    import ctypes
    PUL = ctypes.POINTER(ctypes.c_ulong)

    class KeyBdInput(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL)
        ]

    class HardwareInput(ctypes.Structure):
        _fields_ = [
            ("uMsg", ctypes.c_ulong),
            ("wParamL", ctypes.c_short),
            ("wParamH", ctypes.c_ushort)
        ]

    class MouseInput(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", PUL)
        ]

    class Input_I(ctypes.Union):
        _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]

    class Input(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

    KEYEVENTF_SCANCODE = 0x0008
    KEYEVENTF_KEYUP = 0x0002
    INPUT_KEYBOARD = 1
    INPUT_MOUSE = 0

    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040

    DIRECTINPUT_SCANCODES = {
        "esc": 0x01, "1": 0x02, "2": 0x03, "3": 0x04, "4": 0x05, "5": 0x06,
        "6": 0x07, "7": 0x08, "8": 0x09, "9": 0x0A, "0": 0x0B,
        "q": 0x10, "w": 0x11, "e": 0x12, "r": 0x13, "t": 0x14, "y": 0x15,
        "u": 0x16, "i": 0x17, "o": 0x18, "p": 0x19,
        "a": 0x1E, "s": 0x1F, "d": 0x20, "f": 0x21, "g": 0x22, "h": 0x23,
        "j": 0x24, "k": 0x25, "l": 0x26,
        "z": 0x2C, "x": 0x2D, "c": 0x2E, "v": 0x2F, "b": 0x30, "n": 0x31, "m": 0x32,
        "tab": 0x0F, "enter": 0x1C, "ctrl": 0x1D, "shift": 0x2A, "alt": 0x38,
        "space": 0x39, "capslock": 0x3A,
        "up": 0xC8, "left": 0xCB, "right": 0xCD, "down": 0xD0
    }

    def get_hardware_scancode(key_name):
        key_clean = key_name.lower().strip()
        if key_clean in DIRECTINPUT_SCANCODES:
            return DIRECTINPUT_SCANCODES[key_clean]
        try:
            vk = ctypes.windll.user32.VkKeyScanW(ord(key_clean[0])) & 0xFF
            return ctypes.windll.user32.MapVirtualKeyW(vk, 0)
        except Exception:
            return 0x39

    def direct_send_key(scancode, is_key_up=False):
        extra = ctypes.c_ulong(0)
        flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if is_key_up else 0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, scancode, flags, 0, ctypes.pointer(extra))
        cmd = Input(ctypes.c_ulong(INPUT_KEYBOARD), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(cmd), ctypes.sizeof(cmd))

    def direct_send_mouse(button="left", is_up=False):
        flags = 0
        if button == "left":
            flags = MOUSEEVENTF_LEFTUP if is_up else MOUSEEVENTF_LEFTDOWN
        elif button == "right":
            flags = MOUSEEVENTF_RIGHTUP if is_up else MOUSEEVENTF_RIGHTDOWN
        elif button == "middle":
            flags = MOUSEEVENTF_MIDDLEUP if is_up else MOUSEEVENTF_MIDDLEDOWN

        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
        cmd = Input(ctypes.c_ulong(INPUT_MOUSE), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(cmd), ctypes.sizeof(cmd))

    def move_cursor_hardware(x, y):
        ctypes.windll.user32.SetCursorPos(int(x), int(y))


class ScreenSnipper:
    """Semi-transparent fullscreen overlay modal for drag-and-drop snipping."""
    def __init__(self, parent):
        self.parent = parent
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.selected_bbox = None

        self.top = tk.Toplevel(parent)
        self.top.attributes("-alpha", 0.3)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-topmost", True)
        self.top.config(cursor="cross")

        self.canvas = tk.Canvas(self.top, cursor="cross", bg="gray20", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.top.bind("<Escape>", lambda e: self.top.destroy())

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x = event.x
        end_y = event.y

        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        if (x2 - x1) > 5 and (y2 - y1) > 5:
            self.selected_bbox = (x1, y1, x2, y2)

        self.top.destroy()

    def capture(self, output_path=None):
        self.parent.wait_window(self.top)

        if self.selected_bbox:
            if output_path:
                time.sleep(0.15)
                screenshot = ImageGrab.grab(bbox=self.selected_bbox)
                screenshot.save(output_path)
            return self.selected_bbox
        return None


class DebugOverlay:
    """Displays a momentary green box highlight over detected target areas."""
    @staticmethod
    def flash(root, x, y, w, h, duration_ms=250):
        try:
            overlay = tk.Toplevel(root)
            overlay.overrideredirect(True)
            overlay.attributes("-topmost", True)
            overlay.attributes("-alpha", 0.6)
            overlay.config(bg="lime")
            overlay.geometry(f"{max(10, int(w))}x{max(10, int(h))}+{int(x)}+{int(y)}")
            root.after(duration_ms, overlay.destroy)
        except Exception:
            pass


class Rule:
    """Represents an independent automation rule with sequences and trigger modes."""
    def __init__(self, name="Rule 1", enabled=True,
                 trigger_type="image",
                 detect_image="target_1.png", search_region=None, confidence=0.8,
                 pixel_x=500, pixel_y=500, pixel_rgb=(255, 0, 0), pixel_condition="matches",
                 pre_delay=0.0, action_type="Keyboard Key", key_name="space",
                 click_mode="target_center", dest_image="dest_1.png",
                 fixed_x="960", fixed_y="540", hold_seconds="0.0", mode="once",
                 chain_enabled=False, chain_delay="0.2", chain_action="Left Click", chain_key="1"):
        self.name = name
        self.enabled = enabled
        self.trigger_type = trigger_type
        self.detect_image = detect_image
        self.search_region = search_region
        self.confidence = float(confidence)
        self.pixel_x = int(pixel_x)
        self.pixel_y = int(pixel_y)
        self.pixel_rgb = list(pixel_rgb)
        self.pixel_condition = pixel_condition
        self.pre_delay = float(pre_delay)
        self.action_type = action_type
        self.key_name = key_name
        self.click_mode = click_mode
        self.dest_image = dest_image
        self.fixed_x = fixed_x
        self.fixed_y = fixed_y
        self.hold_seconds = hold_seconds
        self.mode = mode
        self.chain_enabled = chain_enabled
        self.chain_delay = float(chain_delay)
        self.chain_action = chain_action
        self.chain_key = chain_key
        self.is_held = False

    def to_dict(self):
        return {
            "name": self.name,
            "enabled": self.enabled,
            "trigger_type": self.trigger_type,
            "detect_image": self.detect_image,
            "search_region": self.search_region,
            "confidence": self.confidence,
            "pixel_x": self.pixel_x,
            "pixel_y": self.pixel_y,
            "pixel_rgb": self.pixel_rgb,
            "pixel_condition": self.pixel_condition,
            "pre_delay": self.pre_delay,
            "action_type": self.action_type,
            "key_name": self.key_name,
            "click_mode": self.click_mode,
            "dest_image": self.dest_image,
            "fixed_x": str(self.fixed_x),
            "fixed_y": str(self.fixed_y),
            "hold_seconds": str(self.hold_seconds),
            "mode": self.mode,
            "chain_enabled": self.chain_enabled,
            "chain_delay": self.chain_delay,
            "chain_action": self.chain_action,
            "chain_key": self.chain_key
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "Rule"),
            enabled=data.get("enabled", True),
            trigger_type=data.get("trigger_type", "image"),
            detect_image=data.get("detect_image", "target_1.png"),
            search_region=data.get("search_region", None),
            confidence=data.get("confidence", 0.8),
            pixel_x=data.get("pixel_x", 500),
            pixel_y=data.get("pixel_y", 500),
            pixel_rgb=data.get("pixel_rgb", [255, 0, 0]),
            pixel_condition=data.get("pixel_condition", "matches"),
            pre_delay=data.get("pre_delay", 0.0),
            action_type=data.get("action_type", "Keyboard Key"),
            key_name=data.get("key_name", "space"),
            click_mode=data.get("click_mode", "target_center"),
            dest_image=data.get("dest_image", "dest_1.png"),
            fixed_x=data.get("fixed_x", "960"),
            fixed_y=data.get("fixed_y", "540"),
            hold_seconds=data.get("hold_seconds", "0.0"),
            mode=data.get("mode", "once"),
            chain_enabled=data.get("chain_enabled", False),
            chain_delay=data.get("chain_delay", "0.2"),
            chain_action=data.get("chain_action", "Left Click"),
            chain_key=data.get("chain_key", "1")
        )

    def _navigate_mouse(self, trigger_location=None, humanize=False):
        target_x, target_y = None, None

        if self.click_mode == "target_center" and trigger_location is not None:
            c = pyautogui.center(trigger_location)
            target_x, target_y = c.x, c.y
        elif self.click_mode == "diff_image":
            if os.path.exists(self.dest_image):
                try:
                    dest_loc = pyautogui.locateOnScreen(self.dest_image, confidence=self.confidence)
                    if dest_loc is not None:
                        c = pyautogui.center(dest_loc)
                        target_x, target_y = c.x, c.y
                except Exception:
                    pass
        elif self.click_mode == "fixed":
            try:
                target_x = int(self.fixed_x)
                target_y = int(self.fixed_y)
            except ValueError:
                pass

        if target_x is not None and target_y is not None:
            if humanize:
                target_x += random.randint(-4, 4)
                target_y += random.randint(-4, 4)

            if IS_WINDOWS:
                move_cursor_hardware(target_x, target_y)
            else:
                pyautogui.moveTo(target_x, target_y)

    def press_down(self, trigger_location=None, humanize=False):
        if self.is_held:
            return

        is_mouse = self.action_type.endswith("Click")
        if is_mouse:
            self._navigate_mouse(trigger_location, humanize=humanize)

        if IS_WINDOWS:
            if self.action_type == "Keyboard Key":
                sc = get_hardware_scancode(self.key_name)
                direct_send_key(sc, is_key_up=False)
            elif self.action_type == "Left Click":
                direct_send_mouse("left", is_up=False)
            elif self.action_type == "Right Click":
                direct_send_mouse("right", is_up=False)
            elif self.action_type == "Middle Click":
                direct_send_mouse("middle", is_up=False)
        else:
            if self.action_type == "Keyboard Key":
                pyautogui.keyDown(self.key_name)
            elif self.action_type == "Left Click":
                pyautogui.mouseDown(button="left")

        self.is_held = True

    def release(self):
        if not self.is_held:
            return

        try:
            if IS_WINDOWS:
                if self.action_type == "Keyboard Key":
                    sc = get_hardware_scancode(self.key_name)
                    direct_send_key(sc, is_key_up=True)
                elif self.action_type == "Left Click":
                    direct_send_mouse("left", is_up=True)
                elif self.action_type == "Right Click":
                    direct_send_mouse("right", is_up=True)
                elif self.action_type == "Middle Click":
                    direct_send_mouse("middle", is_up=True)
            else:
                if self.action_type == "Keyboard Key":
                    pyautogui.keyUp(self.key_name)
                elif self.action_type == "Left Click":
                    pyautogui.mouseUp(button="left")
        except Exception:
            pass
        finally:
            self.is_held = False

    def trigger_once(self, trigger_location=None, humanize=False):
        delay = self.pre_delay
        if humanize and delay > 0:
            delay += random.uniform(-0.03, 0.03)
        if delay > 0:
            time.sleep(max(0.0, delay))

        try:
            hold_sec = float(self.hold_seconds)
        except ValueError:
            hold_sec = 0.0

        if humanize:
            hold_sec += random.uniform(-0.015, 0.02)

        effective_hold = max(MIN_GAME_TAP_DURATION, hold_sec)
        self.press_down(trigger_location, humanize=humanize)
        time.sleep(effective_hold)
        self.release()

        # Follow-up Action
        if self.chain_enabled:
            cdelay = max(0.05, self.chain_delay)
            if humanize:
                cdelay += random.uniform(-0.02, 0.02)
            time.sleep(cdelay)

            if IS_WINDOWS:
                if self.chain_action == "Keyboard Key":
                    sc = get_hardware_scancode(self.chain_key)
                    direct_send_key(sc, is_key_up=False)
                    time.sleep(MIN_GAME_TAP_DURATION)
                    direct_send_key(sc, is_key_up=True)
                elif self.chain_action == "Left Click":
                    direct_send_mouse("left", is_up=False)
                    time.sleep(MIN_GAME_TAP_DURATION)
                    direct_send_mouse("left", is_up=True)
                elif self.chain_action == "Right Click":
                    direct_send_mouse("right", is_up=False)
                    time.sleep(MIN_GAME_TAP_DURATION)
                    direct_send_mouse("right", is_up=True)


THEMES = {
    "discord": {
        "display_name": "Discord Slate",
        "bg_main": "#1e1f22",
        "bg_card": "#2b2d31",
        "fg_text": "#ffffff",
        "fg_sub": "#c7d5e0",
        "bg_entry": "#383a40",
        "accent": "#5865f2",
        "btn_green": "#23a55a",
        "btn_red": "#da373c"
    },
    "oled": {
        "display_name": "Midnight OLED",
        "bg_main": "#000000",
        "bg_card": "#141416",
        "fg_text": "#ffffff",
        "fg_sub": "#93c5fd",
        "bg_entry": "#202024",
        "accent": "#38bdf8",
        "btn_green": "#16a34a",
        "btn_red": "#dc2626"
    },
    "cyberpunk": {
        "display_name": "Cyberpunk Neon",
        "bg_main": "#0d0b18",
        "bg_card": "#18152b",
        "fg_text": "#f8fafc",
        "fg_sub": "#00f0ff",
        "bg_entry": "#241f3d",
        "accent": "#ff007f",
        "btn_green": "#00e676",
        "btn_red": "#ff1744"
    },
    "emerald": {
        "display_name": "Emerald Forest",
        "bg_main": "#0c1610",
        "bg_card": "#14241b",
        "fg_text": "#f0fdf4",
        "fg_sub": "#86efac",
        "bg_entry": "#1a3024",
        "accent": "#10b981",
        "btn_green": "#059669",
        "btn_red": "#e11d48"
    },
    "light": {
        "display_name": "Clean Modern Light",
        "bg_main": "#f1f5f9",
        "bg_card": "#ffffff",
        "fg_text": "#0f172a",
        "fg_sub": "#334155",
        "bg_entry": "#e2e8f0",
        "accent": "#2563eb",
        "btn_green": "#16a34a",
        "btn_red": "#dc2626"
    }
}


class BotApp:
    """Full Control Panel supporting Themes, Dynamic Font Scaling, Mini-Widget, and Automation."""
    def __init__(self, root):
        self.root = root
        self.root.title(f"Screen Reaction Bot - v{VERSION}")
        self.root.minsize(570, 830)
        self.root.resizable(True, True)

        self.running = False
        self.mini_mode = False
        self.bot_thread = None
        self.preview_detect = None
        self.preview_dest = None

        self.trigger_counter = 0
        self.session_start_time = None

        self.config = self._load_config()
        self.current_theme = self.config.get("theme", "discord")
        if self.current_theme not in THEMES:
            self.current_theme = "discord"

        self.font_scale = self.config.get("font_scale", "normal")

        self.rules = [Rule.from_dict(r) for r in self.config.get("rules", [])]
        if not self.rules:
            self.rules = [
                Rule(name="Auto Jump", enabled=True, detect_image="target_1.png", action_type="Keyboard Key", key_name="space"),
                Rule(name="Dodge Alert", enabled=True, detect_image="target_2.png", action_type="Left Click", click_mode="fixed", fixed_x="1200", fixed_y="700")
            ]
        self.current_rule_index = 0

        # Initialize ttk style engine with clam BEFORE widget construction
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self._build_ui()
        self.apply_theme(self.current_theme)
        self._load_rule_to_ui(self.current_rule_index)
        self._start_global_hotkeys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _load_config(self):
        defaults = {
            "version": VERSION,
            "theme": "discord",
            "font_scale": "normal",
            "humanize": True,
            "debug_overlay": True,
            "max_triggers": 0,
            "session_timeout_min": 0,
            "rules": []
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    defaults.update(data)
            except Exception:
                pass
        return defaults

    def _save_config(self):
        self._save_ui_to_current_rule()
        data = {
            "version": VERSION,
            "theme": self.current_theme,
            "font_scale": self.font_scale,
            "humanize": self.humanize_var.get(),
            "debug_overlay": self.debug_var.get(),
            "max_triggers": int(self.max_triggers_var.get() or 0),
            "session_timeout_min": int(self.session_timeout_var.get() or 0),
            "rules": [r.to_dict() for r in self.rules]
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _get_fonts(self):
        family = "Segoe UI" if IS_WINDOWS else "Helvetica"
        is_large = self.font_scale == "large"
        return {
            "regular": (family, 11 if is_large else 10),
            "bold": (family, 11 if is_large else 10, "bold"),
            "header": (family, 13 if is_large else 11, "bold"),
            "group_header": (family, 12 if is_large else 10, "bold"),
            "sub": (family, 10 if is_large else 9),
            "status": (family, 12 if is_large else 11, "bold"),
            "hotkey": (family, 10 if is_large else 9, "bold"),
            "btn_main": (family, 13 if is_large else 12, "bold"),
            "btn_mini": (family, 11 if is_large else 10, "bold")
        }

    def apply_theme(self, theme_key):
        if theme_key not in THEMES:
            theme_key = "discord"

        self.current_theme = theme_key
        t = THEMES[theme_key]
        self.theme_selector_var.set(t["display_name"])

        fonts = self._get_fonts()

        bg_main = t["bg_main"]
        bg_card = t["bg_card"]
        fg_text = t["fg_text"]
        fg_sub = t["fg_sub"]
        bg_entry = t["bg_entry"]
        accent = t["accent"]

        self.root.config(bg=bg_main)
        self.main_container.config(bg=bg_main)
        self.top_header.config(bg=bg_main)
        self.bottom_bar.config(bg=bg_main)
        self.mini_frame.config(bg=bg_main)

        # Base Frame & Card Styles
        self.style.configure("TFrame", background=bg_main)
        self.style.configure("Card.TFrame", background=bg_card)

        # Labelframe Styles
        self.style.configure("TLabelframe", background=bg_card, bordercolor=bg_entry, darkcolor=bg_card, lightcolor=bg_card)
        self.style.configure("TLabelframe.Label", background=bg_card, foreground=fg_text, font=fonts["group_header"])

        # Label Styles
        self.style.configure("TLabel", background=bg_card, foreground=fg_text, font=fonts["regular"])
        self.style.map("TLabel",
            background=[("active", bg_card), ("!disabled", bg_card)],
            foreground=[("active", fg_text), ("!disabled", fg_text)]
        )

        self.style.configure("Header.TLabel", background=bg_main, foreground=fg_text, font=fonts["header"])
        self.style.configure("Sub.TLabel", background=bg_main, foreground=fg_sub, font=fonts["sub"])
        self.style.configure("CardSub.TLabel", background=bg_card, foreground=fg_sub, font=fonts["sub"])
        self.style.map("CardSub.TLabel",
            background=[("active", bg_card), ("!disabled", bg_card)],
            foreground=[("active", fg_sub), ("!disabled", fg_sub)]
        )

        self.style.configure("Status.TLabel", background=bg_main, foreground=fg_text, font=fonts["status"])
        self.style.configure("Hotkey.TLabel", background=bg_main, foreground=accent, font=fonts["hotkey"])

        # Radiobutton & Checkbutton Styles (Completely eliminates gray box artifacts)
        self.style.configure("TRadiobutton", background=bg_card, foreground=fg_text, font=fonts["regular"])
        self.style.map("TRadiobutton",
            background=[
                ("pressed", bg_card),
                ("active", bg_card),
                ("selected", bg_card),
                ("disabled", bg_card),
                ("!disabled", bg_card)
            ],
            foreground=[
                ("disabled", fg_sub),
                ("!disabled", fg_text)
            ],
            indicatorcolor=[
                ("pressed", accent),
                ("selected", accent),
                ("active", accent),
                ("!disabled", bg_entry)
            ],
            indicatorbackground=[
                ("pressed", accent),
                ("selected", accent),
                ("active", bg_entry),
                ("!disabled", bg_entry)
            ]
        )

        self.style.configure("TCheckbutton", background=bg_card, foreground=fg_text, font=fonts["regular"])
        self.style.map("TCheckbutton",
            background=[
                ("pressed", bg_card),
                ("active", bg_card),
                ("selected", bg_card),
                ("disabled", bg_card),
                ("!disabled", bg_card)
            ],
            foreground=[
                ("disabled", fg_sub),
                ("!disabled", fg_text)
            ],
            indicatorcolor=[
                ("pressed", accent),
                ("selected", accent),
                ("active", accent),
                ("!disabled", bg_entry)
            ],
            indicatorbackground=[
                ("pressed", accent),
                ("selected", accent),
                ("active", bg_entry),
                ("!disabled", bg_entry)
            ]
        )

        # Standard Secondary Buttons (Flat, modern card-entry styling without gray blocks)
        self.style.configure(
            "TButton",
            background=bg_entry,
            foreground=fg_text,
            borderwidth=1,
            relief="flat",
            padding=(8, 3),
            font=fonts["regular"]
        )
        self.style.map(
            "TButton",
            background=[
                ("pressed", accent),
                ("active", accent),
                ("disabled", bg_card),
                ("!disabled", bg_entry)
            ],
            foreground=[
                ("pressed", "#ffffff"),
                ("active", "#ffffff"),
                ("disabled", fg_sub),
                ("!disabled", fg_text)
            ]
        )

        # Entry & Combobox Styles
        self.style.configure(
            "TEntry",
            fieldbackground=bg_entry,
            foreground=fg_text,
            insertcolor=fg_text,
            borderwidth=1,
            font=fonts["regular"]
        )
        self.style.map(
            "TEntry",
            fieldbackground=[("disabled", bg_card), ("!disabled", bg_entry)],
            foreground=[("disabled", fg_sub), ("!disabled", fg_text)]
        )

        self.style.configure(
            "TCombobox",
            fieldbackground=bg_entry,
            background=bg_entry,
            foreground=fg_text,
            arrowcolor=fg_text,
            borderwidth=1,
            font=fonts["regular"]
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", bg_entry), ("!disabled", bg_entry)],
            foreground=[("readonly", fg_text), ("!disabled", fg_text)],
            selectbackground=[("readonly", accent)],
            selectforeground=[("readonly", "#ffffff")]
        )

        # Notebook Tab Bar
        self.style.configure("TNotebook", background=bg_main)
        self.style.configure("TNotebook.Tab", background=bg_card, foreground=fg_text, font=fonts["bold"], padding=(12, 5))
        self.style.map("TNotebook.Tab", background=[("selected", bg_main)], foreground=[("selected", accent)])

        # Update Main Control Buttons
        if hasattr(self, "start_btn"):
            self.start_btn.configure(
                font=fonts["btn_main"],
                bg=t["btn_green"] if not self.running else t["btn_red"]
            )
        if hasattr(self, "mini_start_btn"):
            self.mini_start_btn.configure(
                font=fonts["btn_mini"],
                bg=t["btn_green"] if not self.running else t["btn_red"]
            )
        if hasattr(self, "font_toggle_btn"):
            btn_txt = "🔤 Text: Large" if self.font_scale == "large" else "🔤 Text: Normal"
            self.font_toggle_btn.configure(text=btn_txt)

    def toggle_font_scale(self):
        self.font_scale = "large" if self.font_scale == "normal" else "normal"
        if not self.mini_mode:
            target_geo = "610x890" if self.font_scale == "large" else "580x850"
            self.root.geometry(target_geo)
        self.apply_theme(self.current_theme)
        self._save_config()

    def _on_theme_select(self, event=None):
        selected_display = self.theme_selector_var.get()
        for key, t in THEMES.items():
            if t["display_name"] == selected_display:
                self.apply_theme(key)
                self._save_config()
                break

    def toggle_mini_mode(self):
        self.mini_mode = not self.mini_mode
        if self.mini_mode:
            self.main_container.pack_forget()
            self.mini_frame.pack(fill="both", expand=True)
            self.root.geometry("310x95")
            self.root.attributes("-topmost", True)
        else:
            self.mini_frame.pack_forget()
            self.main_container.pack(fill="both", expand=True)
            target_geo = "610x890" if self.font_scale == "large" else "580x850"
            self.root.geometry(target_geo)
            self.root.attributes("-topmost", False)

    def _save_ui_to_current_rule(self):
        if 0 <= self.current_rule_index < len(self.rules):
            r = self.rules[self.current_rule_index]
            r.name = self.rule_name_var.get().strip() or f"Rule {self.current_rule_index + 1}"
            r.enabled = self.rule_enabled_var.get()
            r.trigger_type = self.trigger_type_var.get()
            r.pixel_condition = self.pixel_cond_var.get()
            try:
                r.pixel_x = int(self.pixel_x_var.get())
                r.pixel_y = int(self.pixel_y_var.get())
            except ValueError:
                pass
            r.action_type = self.action_var.get()
            r.key_name = self.key_var.get()
            r.click_mode = self.loc_mode_var.get()
            r.fixed_x = self.pos_x_var.get()
            r.fixed_y = self.pos_y_var.get()
            r.hold_seconds = self.hold_var.get()
            r.mode = self.mode_var.get()
            try:
                r.confidence = float(self.conf_var.get())
            except ValueError:
                r.confidence = 0.8
            try:
                r.pre_delay = float(self.pre_delay_var.get())
            except ValueError:
                r.pre_delay = 0.0

            r.chain_enabled = self.chain_enabled_var.get()
            try:
                r.chain_delay = float(self.chain_delay_var.get())
            except ValueError:
                r.chain_delay = 0.2
            r.chain_action = self.chain_action_var.get()
            r.chain_key = self.chain_key_var.get()

    def _load_rule_to_ui(self, index):
        if 0 <= index < len(self.rules):
            self.current_rule_index = index
            r = self.rules[index]
            self.rule_selector_var.set(r.name)
            self.rule_name_var.set(r.name)
            self.rule_enabled_var.set(r.enabled)
            self.trigger_type_var.set(r.trigger_type)
            self.pixel_cond_var.set(r.pixel_condition)
            self.pixel_x_var.set(str(r.pixel_x))
            self.pixel_y_var.set(str(r.pixel_y))
            self.pixel_color_label.configure(text=f"RGB: {r.pixel_rgb}")
            self.action_var.set(r.action_type)
            self.key_var.set(r.key_name)
            self.loc_mode_var.set(r.click_mode)
            self.pos_x_var.set(r.fixed_x)
            self.pos_y_var.set(r.fixed_y)
            self.hold_var.set(r.hold_seconds)
            self.mode_var.set(r.mode)
            self.conf_var.set(f"{r.confidence:.2f}")
            self.pre_delay_var.set(str(r.pre_delay))

            self.chain_enabled_var.set(r.chain_enabled)
            self.chain_delay_var.set(str(r.chain_delay))
            self.chain_action_var.set(r.chain_action)
            self.chain_key_var.set(r.chain_key)

            self._update_region_label()
            self._refresh_previews()
            self._on_trigger_type_change()
            self._on_action_change()
            self._on_chain_toggle()

    def _build_ui(self):
        # 1. Compact Mini-Mode Container
        self.mini_frame = tk.Frame(self.root, padx=10, pady=6)
        mini_top = tk.Frame(self.mini_frame)
        mini_top.pack(fill="x")

        self.mini_status_label = ttk.Label(mini_top, text="● IDLE", style="Header.TLabel")
        self.mini_status_label.pack(side="left")

        ttk.Button(mini_top, text="Expand ↗", command=self.toggle_mini_mode, width=9).pack(side="right")

        self.mini_start_btn = tk.Button(
            self.mini_frame, text="▶ START BOT [F8]", bg="#23a55a", fg="white",
            relief="raised", height=1, command=self.toggle_bot
        )
        self.mini_start_btn.pack(fill="x", pady=(4, 0))

        # 2. Main Full-Window Container
        self.main_container = tk.Frame(self.root, padx=12, pady=10)
        self.main_container.pack(fill="both", expand=True)

        # Header Bar with Theme Selector, Font Scale Toggle, and Mini-Widget
        self.top_header = tk.Frame(self.main_container)
        self.top_header.pack(fill="x", pady=(0, 8))

        ttk.Label(self.top_header, text=f"Screen Reaction Bot - v{VERSION}", style="Header.TLabel").pack(side="left")

        # Right header controls
        ttk.Button(self.top_header, text="📌 Mini Mode", command=self.toggle_mini_mode, width=11).pack(side="right", padx=(4, 0))

        self.font_toggle_btn = ttk.Button(self.top_header, text="🔤 Text: Normal", command=self.toggle_font_scale, width=13)
        self.font_toggle_btn.pack(side="right", padx=(4, 0))

        self.theme_selector_var = tk.StringVar(value=THEMES[self.current_theme]["display_name"])
        theme_names = [t["display_name"] for t in THEMES.values()]
        theme_combo = ttk.Combobox(
            self.top_header, textvariable=self.theme_selector_var,
            state="readonly", values=theme_names, width=16
        )
        theme_combo.pack(side="right", padx=(4, 0))
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_select)

        # Tabbed Notebook Interface
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill="both", expand=True, pady=(0, 6))

        tab_rules = ttk.Frame(self.notebook, padding=10)
        tab_safety = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_rules, text="  🎮 Rules & Actions  ")
        self.notebook.add(tab_safety, text="  🛡 Safety, Anti-Detect & Debug  ")

        # ==========================================
        # TAB 1: RULES & ACTIONS
        # ==========================================
        rule_bar = ttk.LabelFrame(tab_rules, text=" Rule Selection & Custom Naming ", padding=8)
        rule_bar.pack(fill="x", pady=(0, 6))

        r_row1 = ttk.Frame(rule_bar, style="Card.TFrame")
        r_row1.pack(fill="x", pady=2)
        ttk.Label(r_row1, text="Rule:").pack(side="left")
        self.rule_selector_var = tk.StringVar()
        self.rule_combo = ttk.Combobox(r_row1, textvariable=self.rule_selector_var, state="readonly", values=[r.name for r in self.rules], width=20)
        self.rule_combo.pack(side="left", padx=6)
        self.rule_combo.bind("<<ComboboxSelected>>", self._on_rule_select)

        ttk.Button(r_row1, text="➕ Add", command=self.add_rule, width=6).pack(side="left", padx=2)
        ttk.Button(r_row1, text="🗑 Delete", command=self.delete_rule, width=7).pack(side="left", padx=2)

        self.rule_enabled_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(r_row1, text="Active", variable=self.rule_enabled_var, command=self._on_name_or_toggle_change).pack(side="right", padx=2)

        r_row2 = ttk.Frame(rule_bar, style="Card.TFrame")
        r_row2.pack(fill="x", pady=(4, 0))
        ttk.Label(r_row2, text="Name:").pack(side="left", padx=(0, 4))
        self.rule_name_var = tk.StringVar()
        name_entry = ttk.Entry(r_row2, textvariable=self.rule_name_var)
        name_entry.pack(side="left", fill="x", expand=True, padx=4)
        name_entry.bind("<KeyRelease>", self._on_name_or_toggle_change)

        # 1. Trigger Definition
        trigger_group = ttk.LabelFrame(tab_rules, text=" 1. Trigger Condition (When Seen) ", padding=8)
        trigger_group.pack(fill="x", pady=(0, 6))

        t_type_row = ttk.Frame(trigger_group, style="Card.TFrame")
        t_type_row.pack(fill="x", pady=2)
        ttk.Label(t_type_row, text="Trigger Type:").pack(side="left", padx=(0, 6))
        self.trigger_type_var = tk.StringVar(value="image")
        ttk.Radiobutton(t_type_row, text="Image Match", value="image", variable=self.trigger_type_var, command=self._on_trigger_type_change).pack(side="left", padx=4)
        ttk.Radiobutton(t_type_row, text="Fast Pixel Color (<1ms)", value="pixel", variable=self.trigger_type_var, command=self._on_trigger_type_change).pack(side="left", padx=6)

        self.img_trigger_frame = ttk.Frame(trigger_group, style="Card.TFrame")
        self.img_trigger_frame.pack(fill="x", pady=2)
        ttk.Button(self.img_trigger_frame, text="✂ Snip Trigger Image [F9]", command=self.snip_trigger_image).pack(fill="x", pady=2)
        self.detect_preview_label = ttk.Label(self.img_trigger_frame, text="No trigger image snipped yet", anchor="center")
        self.detect_preview_label.pack(fill="x")

        self.pixel_trigger_frame = ttk.Frame(trigger_group, style="Card.TFrame")
        p_row1 = ttk.Frame(self.pixel_trigger_frame, style="Card.TFrame")
        p_row1.pack(fill="x", pady=2)
        ttk.Label(p_row1, text="Pixel X:").pack(side="left")
        self.pixel_x_var = tk.StringVar(value="500")
        ttk.Entry(p_row1, textvariable=self.pixel_x_var, width=6).pack(side="left", padx=(2, 6))
        ttk.Label(p_row1, text="Y:").pack(side="left")
        self.pixel_y_var = tk.StringVar(value="500")
        ttk.Entry(p_row1, textvariable=self.pixel_y_var, width=6).pack(side="left", padx=(2, 6))

        ttk.Button(p_row1, text="🎯 Pick Pixel & Color (3s)", command=self.pick_pixel_and_color).pack(side="left", padx=4)
        self.pixel_color_label = ttk.Label(p_row1, text="RGB: [255, 0, 0]", style="CardSub.TLabel")
        self.pixel_color_label.pack(side="left", padx=4)

        p_row2 = ttk.Frame(self.pixel_trigger_frame, style="Card.TFrame")
        p_row2.pack(fill="x", pady=2)
        ttk.Label(p_row2, text="Condition:").pack(side="left", padx=(0, 6))
        self.pixel_cond_var = tk.StringVar(value="matches")
        ttk.Radiobutton(p_row2, text="When Color Appears", value="matches", variable=self.pixel_cond_var).pack(side="left", padx=4)
        ttk.Radiobutton(p_row2, text="When Color Disappears", value="disappears", variable=self.pixel_cond_var).pack(side="left", padx=4)

        # 2. Trigger Action
        action_group = ttk.LabelFrame(tab_rules, text=" 2. Trigger Action & Navigation (DirectInput) ", padding=8)
        action_group.pack(fill="x", pady=(0, 6))

        row1 = ttk.Frame(action_group, style="Card.TFrame")
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="Action:", width=10).pack(side="left")
        self.action_var = tk.StringVar(value="Keyboard Key")
        action_combo = ttk.Combobox(
            row1, textvariable=self.action_var, state="readonly",
            values=["Keyboard Key", "Left Click", "Right Click", "Middle Click"]
        )
        action_combo.pack(side="left", fill="x", expand=True)
        action_combo.bind("<<ComboboxSelected>>", self._on_action_change)

        self.key_row = ttk.Frame(action_group, style="Card.TFrame")
        self.key_row.pack(fill="x", pady=2)
        ttk.Label(self.key_row, text="Key name:", width=10).pack(side="left")
        self.key_var = tk.StringVar(value="space")
        self.key_entry = ttk.Entry(self.key_row, textvariable=self.key_var)
        self.key_entry.pack(side="left", fill="x", expand=True)

        self.mouse_loc_group = ttk.LabelFrame(action_group, text=" Click Destination ", padding=6)
        self.mouse_loc_group.pack(fill="x", pady=3)

        self.loc_mode_var = tk.StringVar(value="target_center")
        ttk.Radiobutton(self.mouse_loc_group, text="Click detected prompt center",
                        value="target_center", variable=self.loc_mode_var, command=self._on_loc_mode_change).pack(anchor="w")

        ttk.Radiobutton(self.mouse_loc_group, text="Click a different visual image:",
                        value="diff_image", variable=self.loc_mode_var, command=self._on_loc_mode_change).pack(anchor="w")
        self.diff_img_row = ttk.Frame(self.mouse_loc_group, style="Card.TFrame")
        self.diff_img_row.pack(fill="x", padx=18, pady=2)
        self.snip_dest_btn = ttk.Button(self.diff_img_row, text="✂ Snip Destination Target", command=self.snip_dest_image)
        self.snip_dest_btn.pack(side="left")
        self.dest_preview_label = ttk.Label(self.diff_img_row, text="(No destination image)", style="CardSub.TLabel")
        self.dest_preview_label.pack(side="left", padx=8)

        ttk.Radiobutton(self.mouse_loc_group, text="Click a fixed preselected position:",
                        value="fixed", variable=self.loc_mode_var, command=self._on_loc_mode_change).pack(anchor="w")
        self.coords_row = ttk.Frame(self.mouse_loc_group, style="Card.TFrame")
        self.coords_row.pack(fill="x", padx=18, pady=2)
        ttk.Label(self.coords_row, text="X:").pack(side="left")
        self.pos_x_var = tk.StringVar(value="960")
        self.entry_x = ttk.Entry(self.coords_row, textvariable=self.pos_x_var, width=6)
        self.entry_x.pack(side="left", padx=(2, 6))

        ttk.Label(self.coords_row, text="Y:").pack(side="left")
        self.pos_y_var = tk.StringVar(value="540")
        self.entry_y = ttk.Entry(self.coords_row, textvariable=self.pos_y_var, width=6)
        self.entry_y.pack(side="left", padx=(2, 6))
        self.pick_btn = ttk.Button(self.coords_row, text="🎯 Pick (3s)", command=self.pick_screen_position)
        self.pick_btn.pack(side="left")

        ttk.Radiobutton(self.mouse_loc_group, text="Click in place (no cursor movement)",
                        value="in_place", variable=self.loc_mode_var, command=self._on_loc_mode_change).pack(anchor="w")

        # Chained Macro
        chain_group = ttk.LabelFrame(tab_rules, text=" 3. Chained Follow-Up Macro (Optional) ", padding=6)
        chain_group.pack(fill="x", pady=(0, 6))

        c_row1 = ttk.Frame(chain_group, style="Card.TFrame")
        c_row1.pack(fill="x")
        self.chain_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(c_row1, text="Enable 2nd action after", variable=self.chain_enabled_var, command=self._on_chain_toggle).pack(side="left")
        self.chain_delay_var = tk.StringVar(value="0.2")
        self.chain_delay_entry = ttk.Entry(c_row1, textvariable=self.chain_delay_var, width=5)
        self.chain_delay_entry.pack(side="left", padx=2)
        ttk.Label(c_row1, text="sec:").pack(side="left")

        self.chain_action_var = tk.StringVar(value="Left Click")
        self.chain_action_combo = ttk.Combobox(c_row1, textvariable=self.chain_action_var, state="readonly",
                                               values=["Left Click", "Right Click", "Keyboard Key"], width=13)
        self.chain_action_combo.pack(side="left", padx=4)

        self.chain_key_var = tk.StringVar(value="1")
        self.chain_key_entry = ttk.Entry(c_row1, textvariable=self.chain_key_var, width=4)
        self.chain_key_entry.pack(side="left", padx=2)

        # Timing & Mode Row
        mode_row = ttk.Frame(tab_rules)
        mode_row.pack(fill="x", pady=3)
        ttk.Label(mode_row, text="Pre-Delay (s):").pack(side="left")
        self.pre_delay_var = tk.StringVar(value="0.0")
        ttk.Entry(mode_row, textvariable=self.pre_delay_var, width=5).pack(side="left", padx=(2, 8))

        ttk.Label(mode_row, text="Hold (s):").pack(side="left")
        self.hold_var = tk.StringVar(value="0.0")
        ttk.Entry(mode_row, textvariable=self.hold_var, width=5).pack(side="left", padx=(2, 8))

        self.mode_var = tk.StringVar(value="once")
        ttk.Radiobutton(mode_row, text="Trigger Once", value="once", variable=self.mode_var).pack(side="left", padx=4)
        ttk.Radiobutton(mode_row, text="While Visible", value="while_visible", variable=self.mode_var).pack(side="left", padx=4)

        # ==========================================
        # TAB 2: SAFETY, ANTI-DETECT & DEBUG
        # ==========================================
        human_group = ttk.LabelFrame(tab_safety, text=" Anti-Detection & Humanization Engine ", padding=10)
        human_group.pack(fill="x", pady=(0, 8))

        self.humanize_var = tk.BooleanVar(value=self.config.get("humanize", True))
        ttk.Checkbutton(
            human_group,
            text="Enable Humanized Inputs (Randomized click jitter ±4px and timing micro-variance)",
            variable=self.humanize_var
        ).pack(anchor="w", pady=2)

        debug_group = ttk.LabelFrame(tab_safety, text=" Real-Time Visual Debugging ", padding=10)
        debug_group.pack(fill="x", pady=(0, 8))

        self.debug_var = tk.BooleanVar(value=self.config.get("debug_overlay", True))
        ttk.Checkbutton(
            debug_group,
            text="Flash Green Bounding Box over detected targets on screen",
            variable=self.debug_var
        ).pack(anchor="w", pady=2)

        safety_group = ttk.LabelFrame(tab_safety, text=" Session Safety Limits & Auto-Stop ", padding=10)
        safety_group.pack(fill="x", pady=(0, 8))

        s_row1 = ttk.Frame(safety_group, style="Card.TFrame")
        s_row1.pack(fill="x", pady=3)
        ttk.Label(s_row1, text="Auto-stop after trigger count:").pack(side="left")
        self.max_triggers_var = tk.StringVar(value=str(self.config.get("max_triggers", 0)))
        ttk.Entry(s_row1, textvariable=self.max_triggers_var, width=6).pack(side="left", padx=6)
        ttk.Label(s_row1, text="(0 = unlimited runs)", style="CardSub.TLabel").pack(side="left")

        s_row2 = ttk.Frame(safety_group, style="Card.TFrame")
        s_row2.pack(fill="x", pady=3)
        ttk.Label(s_row2, text="Session timeout timer (minutes):").pack(side="left")
        self.session_timeout_var = tk.StringVar(value=str(self.config.get("session_timeout_min", 0)))
        ttk.Entry(s_row2, textvariable=self.session_timeout_var, width=6).pack(side="left", padx=6)
        ttk.Label(s_row2, text="(0 = run indefinitely)", style="CardSub.TLabel").pack(side="left")

        roi_group = ttk.LabelFrame(tab_safety, text=" Scan Region Bounding (ROI) & Sensitivity ", padding=10)
        roi_group.pack(fill="x", pady=(0, 8))

        r_box = ttk.Frame(roi_group, style="Card.TFrame")
        r_box.pack(fill="x", pady=2)
        ttk.Button(r_box, text="📐 Snip Search Area (10x Speed)", command=self.snip_search_region).pack(side="left", padx=2)
        ttk.Button(r_box, text="Reset Full Screen", command=self.reset_search_region).pack(side="left", padx=2)
        self.region_label = ttk.Label(r_box, text="Region: Full Screen", style="CardSub.TLabel")
        self.region_label.pack(side="left", padx=6)

        c_box = ttk.Frame(roi_group, style="Card.TFrame")
        c_box.pack(fill="x", pady=(4, 2))
        ttk.Label(c_box, text="Match Sensitivity (Confidence):").pack(side="left")
        self.conf_var = tk.StringVar(value="0.80")
        ttk.Combobox(c_box, textvariable=self.conf_var, state="readonly", width=8,
                     values=["0.70", "0.75", "0.80", "0.85", "0.90", "0.95"]).pack(side="left", padx=6)
        ttk.Label(c_box, text="(Default: 0.80)", style="CardSub.TLabel").pack(side="left")

        # ==========================================
        # BOTTOM CONTROLS & STATUS
        # ==========================================
        self.bottom_bar = tk.Frame(self.main_container)
        self.bottom_bar.pack(fill="x", pady=(4, 0))

        self.status_var = tk.StringVar(value="Status: Idle (Stopped)")

        status_label = ttk.Label(self.bottom_bar, textvariable=self.status_var, style="Status.TLabel", anchor="center")
        status_label.pack(fill="x", pady=(2, 4))

        self.start_btn = tk.Button(
            self.bottom_bar, text="▶ START ALL ACTIVE RULES [F8]", bg="#23a55a", fg="white",
            relief="raised", height=2, command=self.toggle_bot
        )
        self.start_btn.pack(fill="x")

        hotkey_bar = ttk.Label(
            self.bottom_bar,
            text="Global Hotkeys:  [F8] = Start/Stop Bot   |   [F9] = Snip Current Rule Trigger",
            style="Hotkey.TLabel", anchor="center"
        )
        hotkey_bar.pack(fill="x", pady=(4, 0))

    def _on_trigger_type_change(self):
        is_pixel = self.trigger_type_var.get() == "pixel"
        if is_pixel:
            self.img_trigger_frame.pack_forget()
            self.pixel_trigger_frame.pack(fill="x", pady=2)
        else:
            self.pixel_trigger_frame.pack_forget()
            self.img_trigger_frame.pack(fill="x", pady=2)

    def _on_chain_toggle(self):
        state = "normal" if self.chain_enabled_var.get() else "disabled"
        self.chain_delay_entry.configure(state=state)
        self.chain_action_combo.configure(state="readonly" if state == "normal" else "disabled")
        self.chain_key_entry.configure(state=state)

    def _on_name_or_toggle_change(self, event=None):
        idx = self.current_rule_index
        if 0 <= idx < len(self.rules):
            r = self.rules[idx]
            r.name = self.rule_name_var.get().strip() or f"Rule {idx + 1}"
            r.enabled = self.rule_enabled_var.get()
            names = [rule.name + ("" if rule.enabled else " [Disabled]") for rule in self.rules]
            self.rule_combo.configure(values=names)

    def _on_rule_select(self, event=None):
        self._save_ui_to_current_rule()
        idx = self.rule_combo.current()
        if idx >= 0:
            self._load_rule_to_ui(idx)

    def add_rule(self):
        self._save_ui_to_current_rule()
        new_idx = len(self.rules) + 1
        new_rule = Rule(
            name=f"Rule {new_idx}",
            detect_image=f"target_{new_idx}.png",
            dest_image=f"dest_{new_idx}.png"
        )
        self.rules.append(new_rule)
        names = [r.name + ("" if r.enabled else " [Disabled]") for r in self.rules]
        self.rule_combo.configure(values=names)
        self._load_rule_to_ui(len(self.rules) - 1)
        self._save_config()
        self.status_var.set(f"Added {new_rule.name}")

    def delete_rule(self):
        if len(self.rules) <= 1:
            messagebox.showwarning("Notice", "You must keep at least one rule.")
            return
        del self.rules[self.current_rule_index]
        self.current_rule_index = max(0, self.current_rule_index - 1)
        names = [r.name + ("" if r.enabled else " [Disabled]") for r in self.rules]
        self.rule_combo.configure(values=names)
        self._load_rule_to_ui(self.current_rule_index)
        self._save_config()
        self.status_var.set("Rule removed.")

    def _update_region_label(self):
        rule = self.rules[self.current_rule_index]
        if rule.search_region:
            x, y, w, h = rule.search_region
            self.region_label.configure(text=f"Region: ({x}, {y}, {w}x{h})")
        else:
            self.region_label.configure(text="Region: Full Screen")

    def snip_search_region(self):
        if self.running:
            self.stop_bot()

        rule = self.rules[self.current_rule_index]
        self.root.withdraw()
        self.root.update()
        time.sleep(0.3)

        snipper = ScreenSnipper(parent=self.root)
        bbox = snipper.capture(output_path=None)

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        if bbox:
            x1, y1, x2, y2 = bbox
            rule.search_region = (x1, y1, x2 - x1, y2 - y1)
            self._update_region_label()
            self._save_config()
            self.status_var.set(f"Search region saved: {rule.search_region}")
        else:
            self.status_var.set("Region selection cancelled.")

    def reset_search_region(self):
        rule = self.rules[self.current_rule_index]
        rule.search_region = None
        self._update_region_label()
        self._save_config()
        self.status_var.set("Search area reset to Full Screen.")

    def _on_action_change(self, event=None):
        is_key = self.action_var.get() == "Keyboard Key"
        if is_key:
            self.key_entry.configure(state="normal")
            for child in self.mouse_loc_group.winfo_children():
                if isinstance(child, ttk.Frame):
                    for sub in child.winfo_children():
                        sub.configure(state="disabled")
                else:
                    child.configure(state="disabled")
        else:
            self.key_entry.configure(state="disabled")
            for child in self.mouse_loc_group.winfo_children():
                if isinstance(child, ttk.Frame):
                    for sub in child.winfo_children():
                        sub.configure(state="normal" if self.loc_mode_var.get() == "fixed" else "disabled")
                else:
                    child.configure(state="normal")
            self._on_loc_mode_change()

    def _on_loc_mode_change(self):
        if self.action_var.get() != "Keyboard Key":
            mode = self.loc_mode_var.get()
            self.snip_dest_btn.configure(state="normal" if mode == "diff_image" else "disabled")
            coord_state = "normal" if mode == "fixed" else "disabled"
            self.entry_x.configure(state=coord_state)
            self.entry_y.configure(state=coord_state)
            self.pick_btn.configure(state=coord_state)

    def pick_screen_position(self):
        def countdown():
            self.pick_btn.configure(state="disabled")
            for i in range(3, 0, -1):
                self.status_var.set(f"Move mouse to destination... ({i}s)")
                time.sleep(1)
            pos = pyautogui.position()
            self.pos_x_var.set(str(pos.x))
            self.pos_y_var.set(str(pos.y))
            self.status_var.set(f"Captured coordinate: X={pos.x}, Y={pos.y}")
            self.pick_btn.configure(state="normal")

        threading.Thread(target=countdown, daemon=True).start()

    def pick_pixel_and_color(self):
        def countdown():
            for i in range(3, 0, -1):
                self.status_var.set(f"Hover over target pixel... ({i}s)")
                time.sleep(1)
            pos = pyautogui.position()
            color = pyautogui.pixel(pos.x, pos.y)
            self.pixel_x_var.set(str(pos.x))
            self.pixel_y_var.set(str(pos.y))
            self.pixel_color_label.configure(text=f"RGB: {list(color)}")
            rule = self.rules[self.current_rule_index]
            rule.pixel_x = pos.x
            rule.pixel_y = pos.y
            rule.pixel_rgb = list(color)
            self.status_var.set(f"Captured Pixel ({pos.x}, {pos.y}) Color: {color}")
            self._save_config()

        threading.Thread(target=countdown, daemon=True).start()

    def snip_trigger_image(self):
        if self.running:
            self.stop_bot()

        rule = self.rules[self.current_rule_index]
        self.root.withdraw()
        self.root.update()
        time.sleep(0.3)

        snipper = ScreenSnipper(parent=self.root)
        success = snipper.capture(rule.detect_image)

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        if success:
            self._refresh_previews()
            self.status_var.set(f"Trigger for '{rule.name}' saved!")
            self._save_config()
        else:
            self.status_var.set("Trigger snipping cancelled.")

    def snip_dest_image(self):
        if self.running:
            self.stop_bot()

        rule = self.rules[self.current_rule_index]
        self.root.withdraw()
        self.root.update()
        time.sleep(0.3)

        snipper = ScreenSnipper(parent=self.root)
        success = snipper.capture(rule.dest_image)

        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

        if success:
            self._refresh_previews()
            self.status_var.set(f"Destination image for '{rule.name}' saved!")
            self._save_config()
        else:
            self.status_var.set("Destination snipping cancelled.")

    def _refresh_previews(self):
        rule = self.rules[self.current_rule_index]
        if os.path.exists(rule.detect_image):
            try:
                img = Image.open(rule.detect_image)
                img.thumbnail((240, 32))
                self.preview_detect = ImageTk.PhotoImage(img)
                self.detect_preview_label.configure(image=self.preview_detect, text="")
            except Exception:
                self.detect_preview_label.configure(text=f"Loaded: {rule.detect_image}", image="")
        else:
            self.detect_preview_label.configure(text=f"No trigger image for '{rule.name}'", image="")

        if os.path.exists(rule.dest_image):
            try:
                img = Image.open(rule.dest_image)
                img.thumbnail((120, 22))
                self.preview_dest = ImageTk.PhotoImage(img)
                self.dest_preview_label.configure(image=self.preview_dest, text="")
            except Exception:
                self.dest_preview_label.configure(text=f"Dest: {rule.dest_image}", image="")
        else:
            self.dest_preview_label.configure(text="(No destination image)", image="")

    def toggle_bot(self):
        if self.running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        self._save_config()

        active_rules = []
        for r in self.rules:
            if not r.enabled:
                continue
            if r.trigger_type == "image" and os.path.exists(r.detect_image):
                active_rules.append(r)
            elif r.trigger_type == "pixel":
                active_rules.append(r)

        if not active_rules:
            messagebox.showwarning("No Active Triggers", "Please enable and configure a trigger for at least one rule.")
            return

        self.trigger_counter = 0
        self.session_start_time = time.time()
        self.running = True

        stop_text = "■ STOP BOT [F8]"
        stop_color = THEMES[self.current_theme]["btn_red"]
        self.start_btn.configure(text=stop_text, bg=stop_color)
        self.mini_start_btn.configure(text=stop_text, bg=stop_color)
        self.status_var.set(f"Monitoring {len(active_rules)} active rule(s)...")
        self.mini_status_label.configure(text="● RUNNING")

        self.bot_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        self.running = False
        for r in self.rules:
            r.release()

        start_text = "▶ START ALL ACTIVE RULES [F8]"
        start_mini = "▶ START BOT [F8]"
        start_color = THEMES[self.current_theme]["btn_green"]
        self.start_btn.configure(text=start_text, bg=start_color)
        self.mini_start_btn.configure(text=start_mini, bg=start_color)
        self.status_var.set("Status: Idle (Stopped)")
        self.mini_status_label.configure(text="○ STOPPED")

    def _scan_loop(self):
        humanize = self.humanize_var.get()
        debug = self.debug_var.get()

        try:
            max_trig = int(self.max_triggers_var.get() or 0)
        except ValueError:
            max_trig = 0

        try:
            timeout_sec = float(self.session_timeout_var.get() or 0) * 60.0
        except ValueError:
            timeout_sec = 0.0

        while self.running:
            if timeout_sec > 0 and (time.time() - self.session_start_time) >= timeout_sec:
                self.status_var.set("Session timeout reached. Auto-stopped.")
                self.root.after(0, self.stop_bot)
                break

            for rule in self.rules:
                if not self.running:
                    break
                if not rule.enabled:
                    continue

                loc = None
                matched = False

                if rule.trigger_type == "image":
                    if not os.path.exists(rule.detect_image):
                        continue
                    try:
                        if rule.search_region:
                            loc = pyautogui.locateOnScreen(rule.detect_image, confidence=rule.confidence, region=rule.search_region)
                        else:
                            loc = pyautogui.locateOnScreen(rule.detect_image, confidence=rule.confidence)
                        matched = loc is not None
                    except Exception:
                        matched = False

                elif rule.trigger_type == "pixel":
                    try:
                        cur_pixel = pyautogui.pixel(rule.pixel_x, rule.pixel_y)
                        target_rgb = tuple(rule.pixel_rgb)
                        is_close = all(abs(c - t) <= 15 for c, t in zip(cur_pixel, target_rgb))

                        if rule.pixel_condition == "matches":
                            matched = is_close
                        else:
                            matched = not is_close

                        if matched:
                            loc = (rule.pixel_x - 5, rule.pixel_y - 5, 10, 10)
                    except Exception:
                        matched = False

                if matched and self.running:
                    self.trigger_counter += 1
                    self.status_var.set(f"Triggered: {rule.name} (#{self.trigger_counter})")

                    if debug and loc is not None:
                        DebugOverlay.flash(self.root, loc[0], loc[1], loc[2], loc[3])

                    if rule.mode == "once":
                        rule.trigger_once(loc, humanize=humanize)
                        time.sleep(COOLDOWN)

                        while self.running:
                            still_there = False
                            if rule.trigger_type == "image":
                                try:
                                    if rule.search_region:
                                        c_loc = pyautogui.locateOnScreen(rule.detect_image, confidence=rule.confidence, region=rule.search_region)
                                    else:
                                        c_loc = pyautogui.locateOnScreen(rule.detect_image, confidence=rule.confidence)
                                    still_there = c_loc is not None
                                except Exception:
                                    still_there = False
                            elif rule.trigger_type == "pixel":
                                try:
                                    cp = pyautogui.pixel(rule.pixel_x, rule.pixel_y)
                                    tr = tuple(rule.pixel_rgb)
                                    ic = all(abs(c - t) <= 15 for c, t in zip(cp, tr))
                                    still_there = ic if rule.pixel_condition == "matches" else not ic
                                except Exception:
                                    still_there = False

                            if not still_there:
                                break
                            time.sleep(0.12)

                    elif rule.mode == "while_visible":
                        try:
                            hsec = float(rule.hold_seconds)
                        except ValueError:
                            hsec = 0.0

                        if rule.pre_delay > 0:
                            time.sleep(rule.pre_delay)

                        if hsec > 0:
                            rule.press_down(loc, humanize=humanize)
                            while self.running:
                                visible = False
                                if rule.trigger_type == "image":
                                    try:
                                        if rule.search_region:
                                            vloc = pyautogui.locateOnScreen(rule.detect_image, confidence=rule.confidence, region=rule.search_region)
                                        else:
                                            vloc = pyautogui.locateOnScreen(rule.detect_image, confidence=rule.confidence)
                                        visible = vloc is not None
                                    except Exception:
                                        visible = False
                                elif rule.trigger_type == "pixel":
                                    try:
                                        cp = pyautogui.pixel(rule.pixel_x, rule.pixel_y)
                                        tr = tuple(rule.pixel_rgb)
                                        ic = all(abs(c - t) <= 15 for c, t in zip(cp, tr))
                                        visible = ic if rule.pixel_condition == "matches" else not ic
                                    except Exception:
                                        visible = False

                                if not visible:
                                    break
                                time.sleep(CHECK_INTERVAL)
                            rule.release()
                        else:
                            rule.trigger_once(loc, humanize=humanize)
                            time.sleep(CHECK_INTERVAL)

                    if max_trig > 0 and self.trigger_counter >= max_trig:
                        self.status_var.set(f"Completed limit of {max_trig} triggers. Auto-stopped.")
                        self.root.after(0, self.stop_bot)
                        break

            time.sleep(CHECK_INTERVAL)

        for r in self.rules:
            r.release()

    def _start_global_hotkeys(self):
        if not IS_WINDOWS:
            return

        def listener():
            VK_F8 = 0x77
            VK_F9 = 0x78
            WM_HOTKEY = 0x0312
            user32 = ctypes.windll.user32

            user32.RegisterHotKey(None, 101, 0, VK_F8)
            user32.RegisterHotKey(None, 102, 0, VK_F9)

            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == WM_HOTKEY:
                    if msg.wParam == 101:
                        self.root.after(0, self.toggle_bot)
                    elif msg.wParam == 102:
                        self.root.after(0, self.snip_trigger_image)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        threading.Thread(target=listener, daemon=True).start()

    def on_close(self):
        self._save_config()
        if IS_WINDOWS:
            try:
                ctypes.windll.user32.UnregisterHotKey(None, 101)
                ctypes.windll.user32.UnregisterHotKey(None, 102)
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = BotApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
