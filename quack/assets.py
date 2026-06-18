"""Programmatic generation of all assets: pixel-art duck sprites and quack WAV."""

from __future__ import annotations

import io
import math
import struct
import wave

from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
PALETTE: dict[str, tuple[int, int, int, int]] = {
    "Y": (255, 212, 59, 255),   # main rubber-duck yellow
    "H": (255, 233, 130, 255),  # highlight (glossy top sheen)
    "D": (226, 168, 38, 255),   # shadow / underside
    "G": (240, 192, 45, 255),   # mid-shadow gradient
    "O": (255, 158, 44, 255),   # beak orange
    "R": (224, 123, 26, 255),   # beak dark edge
    "B": (40, 30, 20, 255),     # pupil / outline
    "W": (255, 255, 255, 255),  # eye white / glossy highlight
    "P": (255, 170, 160, 255),  # cheek blush
    ".": (0, 0, 0, 0),          # transparent
}

# ---------------------------------------------------------------------------
# Duck pixel grids  (32 × 32, each char = 1 px)
# ---------------------------------------------------------------------------

# Eyes open — normal idle frame (right-facing rubber duck)
_IDLE_GRID = [
    "................................",
    "................................",
    "...............HHHH.............",
    ".............HHYYYYYH...........",
    "............HYYYYYYYYY..........",
    "...........HYYYYYYYYYYY.........",
    "...........YYYYYYYYYYYY.........",
    "..........YYYYYWWYYYYYY.........",
    "..........YYYYYWBYYYYYYOOOO.....",
    "..........YYYYYYBYYYYYYOOOOOOO..",
    "..........YYYYYYYYYYYYYOOOOOOOO.",
    "..........YYYYYYYYYYYYRRRRRRRR..",
    "..........YYYYYYYYYYYYYRR.......",
    ".........YYYYYYYYYYYYYYYY.......",
    "....HH...YYYYYYYYYYYYYYYYY......",
    "...HYYYYYYYYYYYYYYYYYYYYYY......",
    "..HYYYYYYYYYYYYYYYYYYYYYYYY.....",
    "..YHHYYYYYYYYYYYYYYYYYYYYYYY....",
    ".YYHHYYYYYYYYYYYYYYYYYYYYYYY....",
    ".YYYHYYYYYYYYYYYYYYYYYYYYYYY....",
    ".YYYYYYYYYYYYYYYYYYYYYYYYYYYY...",
    ".YYYYYYYYYYYYYYYYYYYYYYYYYYYY...",
    ".GYYYYYYYYYYYYYYYYYYYYYYYYYYG...",
    "..GDYYYYYYYYYYYYYYYYYYYYYYDG....",
    "..DDDDYYYYYYYYYYYYYYYYYYDDDD....",
    "...DDDDDDDYYYYYYYYYYYDDDDDD.....",
    ".....DDDDDDDDDDDDDDDDDDDDD......",
    ".......DDDDDDDDDDDDDDDDD........",
    "................................",
    "................................",
    "................................",
    "................................",
]

def _swap_eye(grid: list[str], replacements: dict[int, tuple[int, str]]) -> list[str]:
    """Return a copy of `grid` with eye pixels overwritten.

    `replacements` maps row index -> (start_col, substring) to splice in.
    """
    out = list(grid)
    for row, (col, sub) in replacements.items():
        line = out[row]
        out[row] = line[:col] + sub + line[col + len(sub):]
    return out


# Eyes closed — asleep (closed eye = dark horizontal lash line)
_SLEEP_GRID = _swap_eye(_IDLE_GRID, {
    7: (14, "YYYY"),
    8: (14, "BBBB"),
    9: (14, "YYYY"),
})

# Eyes half-open — waking up (squinting pupil, no white sheen)
_WAKE_GRID = _swap_eye(_IDLE_GRID, {
    7: (14, "YYYY"),
    8: (14, "YBBY"),
    9: (14, "YYYY"),
})


def _render_grid(grid: list[str], scale: int = 3) -> Image.Image:
    size = 32
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for row_i, row in enumerate(grid):
        for col_i, ch in enumerate(row):
            if ch != ".":
                draw.point((col_i, row_i), fill=PALETTE[ch])
    return img.resize((size * scale, size * scale), Image.NEAREST)


class DuckSprite:
    """Holds all rendered duck frames, each as a PIL RGBA image."""

    def __init__(self, scale: int = 3):
        self.scale = scale
        self.frames: dict[str, list[Image.Image]] = {
            "idle":  [_render_grid(_IDLE_GRID, scale)],
            "sleep": [_render_grid(_SLEEP_GRID, scale)],
            "wake":  [_render_grid(_WAKE_GRID, scale),
                      _render_grid(_IDLE_GRID, scale)],
        }


# ---------------------------------------------------------------------------
# Sound synthesis
# ---------------------------------------------------------------------------

_SAMPLE_RATE = 22050


def _samples_to_wav(samples: list[float], rate: int = _SAMPLE_RATE) -> bytes:
    buf = io.BytesIO()
    pcm = [max(-32768, min(32767, int(s * 32767))) for s in samples]
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(struct.pack(f"<{len(pcm)}h", *pcm))
    return buf.getvalue()


def make_quack_wav() -> bytes:
    """Synthesise a short rubber-duck squeak (~200 ms)."""
    duration = 0.20
    n = int(_SAMPLE_RATE * duration)
    samples = []
    for i in range(n):
        t = i / _SAMPLE_RATE
        env_t = i / n
        attack = min(env_t / 0.04, 1.0)
        decay  = math.exp(-env_t * 14)
        amp    = attack * decay * 0.65

        f0 = 920 - 420 * env_t          # glide 920 → 500 Hz
        sig  =       math.sin(2 * math.pi * f0       * t)
        sig += 0.40 * math.sin(2 * math.pi * f0 * 2  * t)
        sig += 0.18 * math.sin(2 * math.pi * f0 * 3  * t)
        sig += 0.06 * math.sin(2 * math.pi * f0 * 0.5 * t)  # sub
        sig += 0.03 * (2 * (i % 11) / 11 - 1)              # light noise
        samples.append(amp * sig)
    return _samples_to_wav(samples)
