from dataclasses import dataclass
from enum import Enum
from random import Random

from pong.settings import Difficulty


class Effect(Enum):
    FLIP = 'FLIPPED SCREEN'
    BLOCK = 'SCREEN BLOCKED'
    INVERT = 'REVERSED CONTROLS'
    CHAOS = 'CHAOTIC BALL'
    EDGE = 'PADDLE ON EDGE'
    LAZY = 'LAZY PADDLE'
    SMALL = 'TINY BALL'


HARD_PENALTY = (5, 10.0)
PENALTIES = {
    Difficulty.EASY: (0, 0.0),
    Difficulty.MEDIUM: (10, 5.0),
    Difficulty.HARD: HARD_PENALTY,
    Difficulty.EXTREME: HARD_PENALTY,
}
UNLOCK_KEYS = ('JKLUIO', '123456')


@dataclass
class ActiveEffect:
    kind: Effect
    remaining: float
    key: str = ''
    armed: bool = False
    age: float = 0.0


class Effects:
    def __init__(self, difficulty: Difficulty, rng: Random) -> None:
        self.threshold, self.duration = PENALTIES[difficulty]
        self.rng = rng
        self.conceded = [0, 0]
        self.active: list[ActiveEffect | None] = [None, None]

    def concede(self, player: int) -> bool:
        self.conceded[player] += 1
        if not self.threshold or self.conceded[player] % self.threshold:
            return False
        kind = self.rng.choice(list(Effect))
        key = self.rng.choice(UNLOCK_KEYS[player]) if kind == Effect.BLOCK else ''
        self.active[player] = ActiveEffect(kind, self.duration, key)
        return True

    def has(self, kind: Effect, player: int | None = None) -> bool:
        effects = self.active if player is None else [self.active[player]]
        return any(effect is not None and effect.kind == kind for effect in effects)

    def update(self, dt: float, down: set[str], pressed: set[str], ai_top: bool) -> bool:
        ended = False
        for player, effect in enumerate(self.active):
            if effect is None:
                continue
            effect.age += dt
            effect.remaining -= dt
            unlocked = False
            if effect.kind == Effect.BLOCK:
                if player == 1 and ai_top:
                    unlocked = effect.age >= 2.0
                else:
                    if effect.key not in down:
                        effect.armed = True
                    unlocked = effect.armed and effect.key in pressed
            if effect.remaining <= 1e-9 or unlocked:
                self.active[player] = None
                ended = True
        return ended
