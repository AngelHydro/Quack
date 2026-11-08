"""Multi-monitor aware screen geometry helpers.

Tk's ``winfo_screenwidth()/winfo_screenheight()`` only report the *primary*
monitor, so clamping popups to those bounds traps them on screen 1 even when the
duck has been dragged onto a second monitor. These helpers query the Windows
*virtual screen* (the bounding box of all monitors) instead.
"""

from __future__ import annotations

import ctypes
import sys
import tkinter as tk

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

# GetSystemMetrics indices for the virtual screen (all monitors combined).
_SM_XVIRTUALSCREEN = 76
_SM_YVIRTUALSCREEN = 77
_SM_CXVIRTUALSCREEN = 78
_SM_CYVIRTUALSCREEN = 79


def make_transparent(win: tk.Misc, key: str) -> str:
    """Make *win* see-through and return the background colour to paint with.

    Windows uses a colour key; macOS has real per-pixel alpha instead.
    """
    if IS_MAC:
        win.wm_attributes("-transparent", True)
        return "systemTransparent"
    win.wm_attributes("-transparentcolor", key)
    return key


def virtual_screen_rect() -> tuple[int, int, int, int]:
    """Return (left, top, width, height) spanning every monitor.

    Off Windows, falls back to Tk's primary-screen size.
    """
    if not IS_WIN:
        # ponytail: primary monitor only on macOS/Linux; use NSScreen via pyobjc if multi-monitor matters
        root = tk._default_root
        if root is not None:
            return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight()
        return 0, 0, 1920, 1080
    try:
        gsm = ctypes.windll.user32.GetSystemMetrics
        left = gsm(_SM_XVIRTUALSCREEN)
        top = gsm(_SM_YVIRTUALSCREEN)
        width = gsm(_SM_CXVIRTUALSCREEN)
        height = gsm(_SM_CYVIRTUALSCREEN)
        if width and height:
            return left, top, width, height
    except Exception:
        pass
    return 0, 0, 1920, 1080


def clamp_to_screens(x: int, y: int, w: int, h: int, margin: int = 4) -> tuple[int, int]:
    """Clamp a w*h window at (x, y) to stay within the virtual screen bounds."""
    vx, vy, vw, vh = virtual_screen_rect()
    x = max(vx + margin, min(x, vx + vw - w - margin))
    y = max(vy + margin, min(y, vy + vh - h - margin))
    return x, y
