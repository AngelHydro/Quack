"""Duck animation state machine: bob/sway in idle, sleep cycle, wake."""

from __future__ import annotations

import math
from typing import NamedTuple


class AnimFrame(NamedTuple):
    x_off: int
    y_off: int
    frame_key: str
    frame_idx: int


class Animator:
    BOB_FREQ  = 0.8    # Hz
    SWAY_FREQ = 0.3    # Hz
    BOB_AMP   = 4      # px
    SWAY_AMP  = 2      # px

    SLEEP_BLINK_MS = 900   # ms between sleep frames
    WAKE_FRAME_MS  = 220   # ms per wake frame

    def __init__(self) -> None:
        self.mode: str = "idle"   # idle | sleeping | waking
        self._bob_phase  = 0.0
        self._sway_phase = 0.0

        self._sleep_timer  = 0
        self._sleep_fidx   = 0

        self._wake_timer   = 0
        self._wake_fidx    = 0

        self.last_x_off = 0
        self.last_y_off = 0

    # ------------------------------------------------------------------
    def set_mode(self, mode: str) -> None:
        self.mode = mode
        if mode == "sleeping":
            self._sleep_timer = 0
            self._sleep_fidx  = 0
            self.last_x_off = 0
            self.last_y_off = 0
        elif mode == "waking":
            self._wake_timer = 0
            self._wake_fidx  = 0

    # ------------------------------------------------------------------
    def tick(self, dt_ms: float) -> AnimFrame:
        if self.mode == "idle":
            return self._tick_idle(dt_ms)
        if self.mode == "sleeping":
            return self._tick_sleep(dt_ms)
        if self.mode == "waking":
            return self._tick_wake(dt_ms)
        return AnimFrame(0, 0, "idle", 0)

    # ------------------------------------------------------------------
    def _tick_idle(self, dt_ms: float) -> AnimFrame:
        self._bob_phase  += 2 * math.pi * self.BOB_FREQ  * (dt_ms / 1000)
        self._sway_phase += 2 * math.pi * self.SWAY_FREQ * (dt_ms / 1000)
        x = int(self.SWAY_AMP * math.sin(self._sway_phase))
        y = int(self.BOB_AMP  * math.sin(self._bob_phase))
        self.last_x_off = x
        self.last_y_off = y
        return AnimFrame(x, y, "idle", 0)

    def _tick_sleep(self, dt_ms: float) -> AnimFrame:
        self._sleep_timer += dt_ms
        if self._sleep_timer >= self.SLEEP_BLINK_MS:
            self._sleep_timer -= self.SLEEP_BLINK_MS
            self._sleep_fidx = 1 - self._sleep_fidx  # toggle 0/1
        return AnimFrame(0, 0, "sleep", 0)  # single sleep frame

    def _tick_wake(self, dt_ms: float) -> AnimFrame:
        self._wake_timer += dt_ms
        n_frames = 2  # wake has 2 frames: half-open → open
        frame_dur = self.WAKE_FRAME_MS
        fidx = min(int(self._wake_timer / frame_dur), n_frames - 1)
        if self._wake_timer >= frame_dur * n_frames:
            self.set_mode("idle")
        return AnimFrame(0, 0, "wake", fidx)
