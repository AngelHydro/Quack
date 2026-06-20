"""Floating speech bubble shown above the duck."""

from __future__ import annotations

import tkinter as tk

from quack.ui.screen import clamp_to_screens

TRANSPARENT_KEY = "#010101"
BG   = "#FFFDE7"
BORDER = "#F5C518"
TEXT_COLOR = "#333333"

# Half the rendered duck height (96 px tall sprite) — used to lift the bubble
# clear of the duck's head instead of overlapping the face.
DUCK_HALF_H = 48


class SpeechBubble:
    W = 90
    H = 46
    TAIL_H = 10
    CORNER = 8
    DISPLAY_MS = 3000

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._win: tk.Toplevel | None = None
        self._hide_job: str | None = None

    # ------------------------------------------------------------------
    def show(self, text: str, duck_screen_x: int, duck_screen_y: int) -> None:
        self._cancel_hide()
        if self._win is None:
            self._build()
        self._update_text(text)
        self._position(duck_screen_x, duck_screen_y)
        self._win.deiconify()
        self._win.lift()
        self._hide_job = self._root.after(self.DISPLAY_MS, self.hide)

    def hide(self) -> None:
        self._cancel_hide()
        if self._win:
            self._win.withdraw()

    # ------------------------------------------------------------------
    def _cancel_hide(self) -> None:
        if self._hide_job:
            self._root.after_cancel(self._hide_job)
            self._hide_job = None

    def _build(self) -> None:
        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        total_h = self.H + self.TAIL_H
        win.geometry(f"{self.W}x{total_h}")
        win.config(bg=TRANSPARENT_KEY)

        canvas = tk.Canvas(
            win, width=self.W, height=total_h,
            bg=TRANSPARENT_KEY, highlightthickness=0,
        )
        canvas.pack()
        self._canvas = canvas
        self._text_id = None
        self._win = win
        self._draw_bubble()

    def _draw_bubble(self) -> None:
        c = self._canvas
        c.delete("all")
        w, h, r = self.W, self.H, self.CORNER
        # rounded rect
        c.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=BG, outline=BORDER, width=2)
        c.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=BG, outline=BORDER, width=2)
        c.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=BG, outline=BORDER, width=2)
        c.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=BG, outline=BORDER, width=2)
        c.create_rectangle(r, 0, w-r, h, fill=BG, outline="")
        c.create_rectangle(0, r, w, h-r, fill=BG, outline="")
        # border lines
        c.create_line(r, 0, w-r, 0, fill=BORDER, width=2)
        c.create_line(r, h, w-r, h, fill=BORDER, width=2)
        c.create_line(0, r, 0, h-r, fill=BORDER, width=2)
        c.create_line(w, r, w, h-r, fill=BORDER, width=2)
        # tail (triangle pointing down-left)
        tx = w // 3
        tail_pts = [tx, h, tx - 8, h + self.TAIL_H, tx + 8, h]
        c.create_polygon(tail_pts, fill=BG, outline=BORDER, width=2)
        # cover tail seam
        c.create_line(tx - 7, h + 1, tx + 7, h + 1, fill=BG, width=2)
        # text placeholder
        self._text_id = c.create_text(
            w // 2, h // 2,
            text="...", fill=TEXT_COLOR,
            font=("Courier", 11, "bold"),
        )

    def _update_text(self, text: str) -> None:
        if self._text_id is not None:
            self._canvas.itemconfig(self._text_id, text=text)

    def _position(self, duck_cx: int, duck_cy: int) -> None:
        total_h = self.H + self.TAIL_H
        x = duck_cx - self.W // 3       # tail roughly over duck head
        # Lift the whole bubble above the head: the tail tip lands just at the
        # top of the duck instead of over its face.
        y = duck_cy - DUCK_HALF_H - total_h + 6
        x, y = clamp_to_screens(x, y, self.W, total_h)
        self._win.geometry(f"{self.W}x{total_h}+{x}+{y}")
