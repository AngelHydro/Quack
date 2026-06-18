# 🦆 Quack

Quack is a rubber duck debugger that lives on your desktop. It's a duck. It listens.
It doesn't judge.

A small pixel-art rubber duck floats in a transparent, always-on-top window. It
gently bobs as if drifting on water, falls asleep when ignored, and quacks when
you talk to it — the classic [rubber duck debugging](https://en.wikipedia.org/wiki/Rubber_duck_debugging)
companion, on screen.

Everything is generated programmatically — the pixel-art sprite is drawn with
Pillow and the quack sound is synthesised with pure math. No external asset files.

## Features

- **Always on top** of every other window (transparent, borderless overlay)
- **Floating animation** — the duck bobs and sways as if swimming
- **Left click** → a `...` speech bubble appears and the duck quacks
- **Right click** → a text box where you can type your problem; on submit the duck
  quacks back (it never answers — that's the point)
- **Double right click** → a small menu to quit the app
- **Sleeps** after 15 minutes of inactivity (eyes close, Zzz) and wakes on any click
- **Draggable** — left-click and drag to reposition the duck

## Run from source

Requires Python 3.10+ and [Pillow](https://python-pillow.org/).

```sh
pip install pillow
python -m quack
```

## Build a standalone executable

Produces a single self-contained `dist/Quack.exe` (no Python install needed) with
the duck icon and no console window:

```sh
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name Quack ^
    --icon icon.ico --collect-submodules quack run.py
```

## Project layout

```
quack/
├── __main__.py        entry point (python -m quack)
├── assets.py          pixel-art sprite + quack sound generation
├── animator.py        bob/sway/sleep/wake state machine
└── ui/
    ├── window.py      transparent always-on-top window + animation loop
    ├── controller.py  event dispatch
    ├── bubble.py      speech bubble
    ├── input_popup.py text input box
    └── quit_menu.py   quit menu
run.py                 launcher used for packaging
icon.ico               duck icon for the executable
```

## License

See [LICENSE](LICENSE).
