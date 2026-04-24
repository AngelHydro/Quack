from enum import Enum
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets" / "images"

from PIL import Image


class DuckState(Enum):
    IDLE = "idle"
    TYPING = "typing"
    CLICKED = "clicked"
    TALKING = "talking"


class Duck:
    def __init__(self):
        self.img_og = Image.open(ASSETS_DIR / "duck.webp")
        self.img = self.img_og.copy()
        self.frame = 0
        self.state = DuckState.IDLE
        self.x = 0
        self.y = 0
