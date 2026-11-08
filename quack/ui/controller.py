"""Central event dispatcher for the duck app."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import tkinter as tk
    from quack.animator import Animator
    from quack.ui.bubble import SpeechBubble
    from quack.ui.input_popup import TextInputPopup
    from quack.ui.quit_menu import QuitMenu


class AppController:
    def __init__(
        self,
        root: "tk.Tk",
        animator: "Animator",
        quack_wav: bytes,
        bubble: "SpeechBubble",
        input_popup: "TextInputPopup",
        quit_menu: "QuitMenu",
    ) -> None:
        self._root = root
        self._animator = animator
        self._quack_wav = quack_wav
        self._bubble = bubble
        self._input_popup = input_popup
        self._quit_menu = quit_menu

    # ------------------------------------------------------------------
    def handle_left_click(self, duck_cx: int, duck_cy: int) -> None:
        self._close_all_popups()
        self._wake_if_sleeping()
        self._bubble.show("...", duck_cx, duck_cy)
        self._play_quack()

    def handle_right_single(self, duck_cx: int, duck_cy: int) -> None:
        self._close_all_popups()
        self._wake_if_sleeping()
        self._input_popup.show(duck_cx, duck_cy)

    def handle_right_double(self, cursor_x: int, cursor_y: int) -> None:
        self._close_all_popups()
        self._quit_menu.show(cursor_x, cursor_y)

    def handle_input_submit(self, _text: str) -> None:
        # duck responds the same regardless of what was typed
        win_x = self._root.winfo_x()
        win_y = self._root.winfo_y()
        cx = win_x + 100 + self._animator.last_x_off
        cy = win_y + 100 + self._animator.last_y_off
        self._bubble.show("...", cx, cy)
        self._play_quack()

    def handle_idle_sleep(self) -> None:
        self._bubble.hide()
        self._input_popup.hide()
        self._animator.set_mode("sleeping")

    def handle_wake(self) -> None:
        if self._animator.mode == "sleeping":
            self._animator.set_mode("waking")

    # ------------------------------------------------------------------
    def _close_all_popups(self) -> None:
        self._bubble.hide()
        self._input_popup.hide()
        self._quit_menu.hide()

    def _wake_if_sleeping(self) -> None:
        if self._animator.mode == "sleeping":
            self._animator.set_mode("waking")

    def _play_quack(self) -> None:
        wav = self._quack_wav

        if sys.platform == "win32":
            import winsound

            def _play() -> None:
                winsound.PlaySound(wav, winsound.SND_MEMORY)
        else:
            path = self._wav_file()

            def _play() -> None:
                # afplay ships with macOS; aplay is the usual Linux fallback
                cmd = "afplay" if sys.platform == "darwin" else "aplay"
                try:
                    subprocess.run([cmd, path], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, check=False)
                except OSError:
                    pass

        threading.Thread(target=_play, daemon=True).start()

    def _wav_file(self) -> str:
        """Write the quack once to a temp file (afplay can't read from memory)."""
        if getattr(self, "_wav_path", None) is None:
            fd, path = tempfile.mkstemp(prefix="quack-", suffix=".wav")
            with os.fdopen(fd, "wb") as f:
                f.write(self._quack_wav)
            self._wav_path = path
        return self._wav_path
