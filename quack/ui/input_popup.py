"""Text input popup shown on right-click."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

TRANSPARENT_KEY = "#010101"
BG_POPUP = "#FFFDE7"
BORDER_COLOR = "#F5C518"


class TextInputPopup:
    W = 220
    H = 38

    def __init__(self, root: tk.Tk, on_submit: Callable[[str], None]) -> None:
        self._root = root
        self._on_submit = on_submit
        self._win: tk.Toplevel | None = None
        self._entry: tk.Entry | None = None
        self._visible = False

    # ------------------------------------------------------------------
    def show(self, duck_screen_x: int, duck_screen_y: int) -> None:
        if self._win is None:
            self._build()
        self._position(duck_screen_x, duck_screen_y)
        self._entry.delete(0, tk.END)
        self._win.deiconify()
        self._win.lift()
        self._entry.focus_set()
        self._visible = True

    def hide(self) -> None:
        if self._win:
            self._win.withdraw()
        self._visible = False

    @property
    def visible(self) -> bool:
        return self._visible

    # ------------------------------------------------------------------
    def _build(self) -> None:
        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.geometry(f"{self.W}x{self.H}")
        win.config(bg=BORDER_COLOR)

        frame = tk.Frame(win, bg=BG_POPUP, padx=2, pady=2)
        frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        entry = tk.Entry(
            frame, bg=BG_POPUP, fg="#333333",
            font=("Courier", 10),
            relief=tk.FLAT, insertbackground="#F5C518",
        )
        entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 2))
        entry.bind("<Return>", self._on_enter)
        entry.bind("<Escape>", lambda _e: self.hide())
        entry.bind("<FocusOut>", self._on_focus_out)

        send_btn = tk.Button(
            frame, text="▶", bg="#F5C518", fg="#333333",
            font=("Courier", 9, "bold"),
            relief=tk.FLAT, cursor="hand2",
            command=self._submit,
        )
        send_btn.pack(side=tk.RIGHT, padx=(2, 4))

        self._win = win
        self._entry = entry

    def _on_enter(self, _event: tk.Event) -> None:
        self._submit()

    def _on_focus_out(self, event: tk.Event) -> None:
        # Ignore if focus moved to our own send button
        try:
            focused = self._root.focus_get()
        except Exception:
            focused = None
        if focused and str(focused).startswith(str(self._win)):
            return
        self.hide()

    def _submit(self) -> None:
        text = self._entry.get().strip()
        self.hide()
        if text:
            self._on_submit(text)

    def _position(self, duck_cx: int, duck_cy: int) -> None:
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        x = duck_cx + 20
        y = duck_cy - self.H // 2
        x = max(4, min(x, sw - self.W - 4))
        y = max(4, min(y, sh - self.H - 4))
        self._win.geometry(f"{self.W}x{self.H}+{x}+{y}")
