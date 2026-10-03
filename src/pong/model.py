from dataclasses import dataclass


@dataclass
class Paddle:
    position: float
    length: float
    speed: float

    def move(self, direction: int, dt: float, minimum: float, maximum: float) -> None:
        next_position = self.position + direction * self.speed * dt
        self.position = max(minimum, min(next_position, maximum - self.length))


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 6.0
