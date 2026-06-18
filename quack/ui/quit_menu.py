"""Mini quit menu shown on double right-click."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

BG       = "#2B2B2B"
FG       = "#EEEEEE"
HOVER_BG = "#F5C518"
HOVER_FG = "#2B2B2B"


class QuitMenu:
    W = 160
    H = 104

    def __init__(self, root: tk.Tk, on_quit: Callable[[], None]) -> None:
        self._root = root
        self._on_quit = on_quit
        self._win: tk.Toplevel | None = None

    # ------------------------------------------------------------------
    def show(self, x: int, y: int) -> None:
        if self._win is None:
            self._build()
        sw = self._root.winfo_screenwidth()
        sh = self._root.winfo_screenheight()
        px = max(4, min(x, sw - self.W - 4))
        py = max(4, min(y, sh - self.H - 4))
        self._win.geometry(f"{self.W}x{self.H}+{px}+{py}")
        self._win.deiconify()
        self._win.lift()
        self._win.focus_set()

    def hide(self) -> None:
        if self._win:
            self._win.withdraw()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        win = tk.Toplevel(self._root)
        win.overrideredirect(True)
        win.wm_attributes("-topmost", True)
        win.geometry(f"{self.W}x{self.H}")
        win.config(bg="#F5C518")  # border colour via padding

        inner = tk.Frame(win, bg=BG, padx=0, pady=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        title = tk.Label(
            inner, text="Quack", bg=BG, fg="#F5C518",
            font=("Courier", 9, "bold"),
        )
        title.pack(fill=tk.X, pady=(4, 0))

        quit_btn = tk.Button(
            inner, text="Quitter", bg=BG, fg=FG,
            font=("Courier", 9),
            relief=tk.FLAT, cursor="hand2",
            activebackground=HOVER_BG, activeforeground=HOVER_FG,
            command=self._quit,
        )
        quit_btn.pack(fill=tk.X, padx=8, pady=2)

        cancel_btn = tk.Button(
            inner, text="Annuler", bg=BG, fg=FG,
            font=("Courier", 9),
            relief=tk.FLAT, cursor="hand2",
            activebackground="#555555", activeforeground=FG,
            command=self.hide,
        )
        cancel_btn.pack(fill=tk.X, padx=8, pady=(0, 4))

        win.bind("<FocusOut>", lambda _e: self.hide())
        win.bind("<Escape>", lambda _e: self.hide())
        self._win = win

    def _quit(self) -> None:
        self._on_quit()
