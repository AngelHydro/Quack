"""Entry point: python -m quack"""

from __future__ import annotations

import tkinter as tk

from quack.assets import DuckSprite, make_quack_wav
from quack.animator import Animator
from quack.ui.bubble import SpeechBubble
from quack.ui.input_popup import TextInputPopup
from quack.ui.quit_menu import QuitMenu
from quack.ui.controller import AppController
from quack.ui.window import DuckWindow


def main() -> None:
    sprite    = DuckSprite(scale=3)
    quack_wav = make_quack_wav()
    animator  = Animator()

    root = tk.Tk()
    root.withdraw()   # hide while building

    bubble      = SpeechBubble(root)
    input_popup = TextInputPopup(root, on_submit=lambda text: controller.handle_input_submit(text))
    quit_menu   = QuitMenu(root, on_quit=root.destroy)

    controller = AppController(
        root=root,
        animator=animator,
        quack_wav=quack_wav,
        bubble=bubble,
        input_popup=input_popup,
        quit_menu=quit_menu,
    )

    window = DuckWindow(
        root=root,
        sprite=sprite,
        animator=animator,
        controller=controller,
    )

    root.deiconify()
    window.start_loop()
    root.mainloop()


if __name__ == "__main__":
    main()
