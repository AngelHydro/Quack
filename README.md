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

## Install (just run it — no Python needed)

Download **`Quack.exe`** from the
[Releases page](https://github.com/AngelHydro/Quack/releases) and double-click it.
That's it — it's fully self-contained, no Python or any install required. You can
move it to your Desktop or pin a shortcut anywhere.

> The `.exe` is intentionally **not** stored in the repository (it's a 29 MB
> binary). It is published on the Releases page instead, built automatically by
> GitHub. See [Building](#building-from-source) below if you want to make it yourself.

## Run from source

For developers who have Python 3.10+ installed:

```sh
pip install pillow
python -m quack
```

## Building from source

Building the `.exe` **requires Python**, because [PyInstaller](https://pyinstaller.org/)
(the packager) is a Python tool. Pick whichever fits:

**1. Let GitHub build it — no Python on your machine.** The
[build workflow](.github/workflows/build.yml) builds the exe in the cloud on every
push (downloadable from the run's *Artifacts*). Push a version tag and it publishes
a Release with `Quack.exe` attached:

```sh
git tag v1.0.0
git push origin v1.0.0
```

**2. Double-click `build.bat`** (Windows, Python installed) — installs the build
deps and produces `dist\Quack.exe`. If Python is missing it tells you where to get
the prebuilt exe instead.

**3. Run the command manually:**

```sh
pip install pillow pyinstaller
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
