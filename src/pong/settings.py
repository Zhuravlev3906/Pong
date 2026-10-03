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


@dataclass(frozen=True)
class PaddleMotion:
    speed: float
    acceleration: float | None
    braking: float | None
    input_delay: float = 0.0


PADDLE_PROFILES = {
    Difficulty.EASY: PaddleMotion(180.0, None, None),
    Difficulty.MEDIUM: PaddleMotion(180.0, 2400.0, 1400.0),
    Difficulty.HARD: PaddleMotion(180.0, 600.0, 300.0, 0.08),
    Difficulty.EXTREME: PaddleMotion(320.0, 900.0, 400.0),
}
