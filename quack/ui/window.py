"""Main duck window: transparent overlay, always-on-top, animation loop."""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import tkinter as tk
from PIL import Image, ImageTk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quack.animator import Animator, AnimFrame
    from quack.assets import DuckSprite
    from quack.ui.controller import AppController

TRANSPARENT_KEY = "#010101"
CANVAS_SIZE     = 200       # px — generous bounding box for bubble tail clearance
IDLE_MS         = 15 * 60 * 1000   # 15 minutes

# Win32 constants
HWND_TOPMOST       = -1
SWP_NOMOVE         = 0x0002
SWP_NOSIZE         = 0x0001
GWL_EXSTYLE        = -20
WS_EX_NOACTIVATE   = 0x08000000
WS_EX_TOOLWINDOW   = 0x00000080
TOPMOST_REASSERT_MS = 5_000


def _pil_to_photoimage(img: Image.Image) -> ImageTk.PhotoImage:
    """Composite RGBA image onto TRANSPARENT_KEY background."""
    bg = Image.new("RGB", img.size, TRANSPARENT_KEY)
    bg.paste(img, mask=img.split()[3])
    return ImageTk.PhotoImage(bg)


class DuckWindow:
    def __init__(
        self,
        root: tk.Tk,
        sprite: "DuckSprite",
        animator: "Animator",
        controller: "AppController",
    ) -> None:
        self._root = root
        self._sprite = sprite
        self._animator = animator
        self._controller = controller

        # Idle timer state
        self._idle_job: str | None = None

        # Right-click debounce
        self._rc_pending: str | None = None
        _RC_DOUBLE_MS = 400
        self._RC_DOUBLE_MS = _RC_DOUBLE_MS

        # Drag state
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_moved = False

        # ZZZ animation state
        self._zzz_items: list[int] = []
        self._zzz_phase = 0

        self._setup_window()
        self._setup_canvas()
        self._apply_win32_flags()
        self._reset_idle_timer()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------
    def _setup_window(self) -> None:
        root = self._root
        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)
        root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        root.config(bg=TRANSPARENT_KEY)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = sw - CANVAS_SIZE - 60
        y = sh - CANVAS_SIZE - 80
        root.geometry(f"{CANVAS_SIZE}x{CANVAS_SIZE}+{x}+{y}")

    def _setup_canvas(self) -> None:
        canvas = tk.Canvas(
            self._root,
            width=CANVAS_SIZE, height=CANVAS_SIZE,
            bg=TRANSPARENT_KEY, highlightthickness=0,
        )
        canvas.pack()
        self._canvas = canvas

        # Pre-render first frame
        frame = self._sprite.frames["idle"][0]
        self._current_photo = _pil_to_photoimage(frame)
        cx = cy = CANVAS_SIZE // 2
        duck_w, duck_h = frame.size
        self._img_id = canvas.create_image(
            cx, cy, anchor=tk.CENTER, image=self._current_photo
        )
        self._prev_x_off = 0
        self._prev_y_off = 0
        self._prev_frame_key = "idle"
        self._prev_frame_idx = 0

        # Events
        canvas.bind("<Button-1>",    self._on_left_press)
        canvas.bind("<B1-Motion>",   self._on_drag)
        canvas.bind("<ButtonRelease-1>", self._on_left_release)
        canvas.bind("<Button-3>",    self._on_right_click)

    def _apply_win32_flags(self) -> None:
        self._root.update_idletasks()
        try:
            hwnd = ctypes.windll.user32.GetParent(self._root.winfo_id())
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
            )
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, GWL_EXSTYLE,
                style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW,
            )
            self._hwnd = hwnd
        except Exception:
            self._hwnd = None

    def _reassert_topmost(self) -> None:
        if self._hwnd:
            try:
                ctypes.windll.user32.SetWindowPos(
                    self._hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE,
                )
            except Exception:
                pass
        self._root.after(TOPMOST_REASSERT_MS, self._reassert_topmost)

    # ------------------------------------------------------------------
    # Main animation loop
    # ------------------------------------------------------------------
    def start_loop(self) -> None:
        self._reassert_topmost()
        self._loop()

    def _loop(self) -> None:
        frame_data = self._animator.tick(40)
        self._render(frame_data)
        self._root.after(40, self._loop)

    def _render(self, fd: "AnimFrame") -> None:
        changed = (
            fd.frame_key != self._prev_frame_key
            or fd.frame_idx != self._prev_frame_idx
        )
        if changed:
            frames = self._sprite.frames.get(fd.frame_key, self._sprite.frames["idle"])
            idx = min(fd.frame_idx, len(frames) - 1)
            pil_frame = frames[idx]
            self._current_photo = _pil_to_photoimage(pil_frame)
            self._canvas.itemconfig(self._img_id, image=self._current_photo)

        dx = fd.x_off - self._prev_x_off
        dy = fd.y_off - self._prev_y_off
        if dx or dy:
            self._canvas.move(self._img_id, dx, dy)

        self._prev_frame_key = fd.frame_key
        self._prev_frame_idx = fd.frame_idx
        self._prev_x_off = fd.x_off
        self._prev_y_off = fd.y_off

        # ZZZ overlay when sleeping
        if fd.frame_key == "sleep":
            self._update_zzz()
        else:
            self._clear_zzz()

    # ------------------------------------------------------------------
    # ZZZ overlay
    # ------------------------------------------------------------------
    def _update_zzz(self) -> None:
        self._zzz_phase = (self._zzz_phase + 1) % 60
        self._clear_zzz()
        cx = CANVAS_SIZE // 2 + self._prev_x_off + 16
        cy = CANVAS_SIZE // 2 + self._prev_y_off - 28
        phase = self._zzz_phase
        # three Z glyphs fading in sequence
        configs = [
            (cx,      cy,      "z",  "#F5C518", 8),
            (cx + 8,  cy - 10, "z",  "#F5C518", 10),
            (cx + 18, cy - 22, "Z",  "#F5C518", 13),
        ]
        for i, (x, y, char, color, size) in enumerate(configs):
            offset = (phase + i * 20) % 60
            if offset < 40:
                alpha_step = min(offset, 20)
                brightness = int(80 + alpha_step * 8)
                hex_b = f"#{brightness:02x}{brightness:02x}00"
                item = self._canvas.create_text(
                    x, y, text=char,
                    fill=hex_b,
                    font=("Courier", size, "bold"),
                )
                self._zzz_items.append(item)

    def _clear_zzz(self) -> None:
        for item in self._zzz_items:
            self._canvas.delete(item)
        self._zzz_items.clear()

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _duck_screen_center(self) -> tuple[int, int]:
        wx = self._root.winfo_x()
        wy = self._root.winfo_y()
        cx = wx + CANVAS_SIZE // 2 + self._animator.last_x_off
        cy = wy + CANVAS_SIZE // 2 + self._animator.last_y_off
        return cx, cy

    def _on_left_press(self, event: tk.Event) -> None:
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._drag_moved = False

    def _on_drag(self, event: tk.Event) -> None:
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        if abs(dx) > 5 or abs(dy) > 5:
            self._drag_moved = True
        wx = self._root.winfo_x() + dx
        wy = self._root.winfo_y() + dy
        self._root.geometry(f"+{wx}+{wy}")
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_left_release(self, event: tk.Event) -> None:
        if self._drag_moved:
            return
        self._reset_idle_timer()
        cx, cy = self._duck_screen_center()
        self._controller.handle_left_click(cx, cy)

    def _on_right_click(self, event: tk.Event) -> None:
        if self._rc_pending is not None:
            self._root.after_cancel(self._rc_pending)
            self._rc_pending = None
            self._reset_idle_timer()
            self._controller.handle_right_double(event.x_root, event.y_root)
        else:
            # Save event coords; fire single after delay
            x_root, y_root = event.x_root, event.y_root
            self._rc_pending = self._root.after(
                self._RC_DOUBLE_MS,
                lambda: self._fire_right_single(x_root, y_root),
            )

    def _fire_right_single(self, x_root: int, y_root: int) -> None:
        self._rc_pending = None
        self._reset_idle_timer()
        cx, cy = self._duck_screen_center()
        self._controller.handle_right_single(cx, cy)

    # ------------------------------------------------------------------
    # Idle timer
    # ------------------------------------------------------------------
    def _reset_idle_timer(self) -> None:
        if self._idle_job:
            self._root.after_cancel(self._idle_job)
        self._idle_job = self._root.after(IDLE_MS, self._on_idle_timeout)

    def _on_idle_timeout(self) -> None:
        self._controller.handle_idle_sleep()
