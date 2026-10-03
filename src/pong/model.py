from collections import deque
from dataclasses import dataclass, field

from pong.settings import PaddleMotion


@dataclass
class Paddle:
    position: float
    length: float
    speed: float

    motion: PaddleMotion | None = None
    velocity: float = field(default=0.0, init=False)
    _time: float = field(default=0.0, init=False, repr=False)
    _input: int = field(default=0, init=False, repr=False)
    _direction: int = field(default=0, init=False, repr=False)
    _commands: deque[tuple[float, int]] = field(default_factory=deque, init=False, repr=False)

    def move(self, direction: int, dt: float, minimum: float, maximum: float) -> None:
        if dt <= 0:
            return
        delay = self.motion.input_delay if self.motion else 0.0
        if direction != self._input:
            self._commands.append((self._time + delay, direction))
            self._input = direction
        end = self._time + dt
        # Split at command deadlines so delay does not depend on frame size.
        while self._commands and self._commands[0][0] <= end + 1e-9:
            deadline, self_next_direction = self._commands.popleft()
            deadline = min(end, max(self._time, deadline))
            self._integrate(deadline - self._time, minimum, maximum)
            self._time = deadline
            self._direction = self_next_direction
        self._integrate(end - self._time, minimum, maximum)
        self._time = end

    def _integrate(self, dt: float, minimum: float, maximum: float) -> None:
        if dt <= 0:
            return
        target = self._direction * self.speed
        rate = None
        if self.motion:
            rate = self.motion.acceleration if self._direction else self.motion.braking
        if rate is None:
            self.velocity = target
            displacement = target * dt
        else:
            difference = target - self.velocity
            acceleration = rate if difference > 0 else -rate
            ramp_time = min(dt, abs(difference) / rate)
            displacement = self.velocity * ramp_time + acceleration * ramp_time ** 2 / 2
            self.velocity += acceleration * ramp_time
            if ramp_time < dt:
                self.velocity = target
                displacement += target * (dt - ramp_time)
        next_position = self.position + displacement
        self.position = max(minimum, min(next_position, maximum - self.length))
        if (self.position <= minimum and self.velocity < 0 or
                self.position >= maximum - self.length and self.velocity > 0):
            self.velocity = 0.0


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 6.0
