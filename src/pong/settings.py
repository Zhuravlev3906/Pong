from dataclasses import dataclass
from enum import IntEnum

WIDTH = 300
HEIGHT = 400
SCALE = 2
FPS = 60


class Difficulty(IntEnum):
    EASY = 0
    MEDIUM = 1
    HARD = 2
    EXTREME = 3


@dataclass
class Settings:
    difficulty: Difficulty = Difficulty.MEDIUM
    players: int = 1
    sound_enabled: bool = True
