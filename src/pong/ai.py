from dataclasses import dataclass

from pong.model import Ball, Paddle
from pong.physics import Rect
from pong.settings import Difficulty


@dataclass(frozen=True)
class AIProfile:
    speed: float
    reaction_time: float
    predicts: bool


AI_PROFILES = {
    Difficulty.EASY: AIProfile(85.0, 0.25, False),
    Difficulty.MEDIUM: AIProfile(130.0, 0.15, False),
    Difficulty.HARD: AIProfile(180.0, 0.10, True),
    Difficulty.EXTREME: AIProfile(260.0, 0.05, True),
}


def predict_intercept(ball: Ball, court: Rect, paddle_bottom: float) -> float | None:
    target_y = paddle_bottom + ball.radius
    if ball.vy >= 0 or ball.y < target_y:
        return None
    distance = (target_y - ball.y) / ball.vy
    unfolded_x = ball.x + ball.vx * distance
    left = court.left + ball.radius
    width = court.right - ball.radius - left
    # Acceleration and wall losses scale both velocity components equally,
    # so they change arrival time, but not this reflected geometric path.
    offset = (unfolded_x - left) % (2 * width)
    return left + (offset if offset <= width else 2 * width - offset)


class PaddleAI:
    def __init__(self, difficulty: Difficulty, center: float) -> None:
        self.profile = AI_PROFILES[difficulty]
        self.target = center
        self.reaction_remaining = self.profile.reaction_time

    def reset(self, center: float) -> None:
        self.target = center
        self.reaction_remaining = self.profile.reaction_time

    def update(self, paddle: Paddle, ball: Ball, dt: float, court: Rect,
               paddle_bottom: float, serving: bool) -> None:
        center = (court.left + court.right) / 2
        if serving:
            self.reset(center)
        else:
            self.reaction_remaining -= dt
            if self.reaction_remaining <= 1e-9:
                self.reaction_remaining = self.profile.reaction_time
                if self.profile.predicts:
                    intercept = predict_intercept(ball, court, paddle_bottom)
                    self.target = center if intercept is None else intercept
                else:
                    self.target = ball.x
        target = max(court.left + paddle.length / 2,
                     min(self.target, court.right - paddle.length / 2))
        difference = target - (paddle.position + paddle.length / 2)
        dead_zone = max(2.0, paddle.speed * dt)
        direction = 0 if abs(difference) <= dead_zone else (1 if difference > 0 else -1)
        if paddle.motion and paddle.motion.braking and difference * paddle.velocity > 0:
            stopping_distance = paddle.velocity ** 2 / (2 * paddle.motion.braking)
            stopping_distance += abs(paddle.velocity) * paddle.motion.input_delay
            if abs(difference) <= stopping_distance + dead_zone:
                direction = 0
        paddle.move(direction, dt, court.left, court.right)
