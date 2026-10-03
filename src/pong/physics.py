from dataclasses import dataclass
from math import hypot, sqrt

from pong.model import Ball

EPSILON = 1e-9


@dataclass(frozen=True)
class Rect:
    left: float
    top: float
    right: float
    bottom: float


def paddle_hit(ball: Ball, paddle: Rect, dt: float) -> tuple[float, float, float] | None:
    """Sweep a circle against the faces and rounded corners of a rectangle."""
    hits = []
    for position, velocity, edge, nx, ny, low, high in (
        (ball.x, ball.vx, paddle.left - ball.radius, -1, 0, paddle.top, paddle.bottom),
        (ball.x, ball.vx, paddle.right + ball.radius, 1, 0, paddle.top, paddle.bottom),
        (ball.y, ball.vy, paddle.top - ball.radius, 0, -1, paddle.left, paddle.right),
        (ball.y, ball.vy, paddle.bottom + ball.radius, 0, 1, paddle.left, paddle.right),
    ):
        if velocity == 0 or ball.vx * nx + ball.vy * ny >= 0:
            continue
        time = (edge - position) / velocity
        cross = ball.y + ball.vy * time if nx else ball.x + ball.vx * time
        if -EPSILON <= time <= dt and low <= cross <= high:
            hits.append((max(0.0, time), nx, ny))

    speed_squared = ball.vx ** 2 + ball.vy ** 2
    if speed_squared > 0:
        for x, y, sx, sy in (
            (paddle.left, paddle.top, -1, -1),
            (paddle.right, paddle.top, 1, -1),
            (paddle.left, paddle.bottom, -1, 1),
            (paddle.right, paddle.bottom, 1, 1),
        ):
            dx, dy = ball.x - x, ball.y - y
            projection = dx * ball.vx + dy * ball.vy
            discriminant = projection ** 2 - speed_squared * (dx * dx + dy * dy - ball.radius ** 2)
            if discriminant < 0:
                continue
            time = (-projection - sqrt(discriminant)) / speed_squared
            if not -EPSILON <= time <= dt:
                continue
            nx = (dx + ball.vx * time) / ball.radius
            ny = (dy + ball.vy * time) / ball.radius
            if nx * sx >= 0 and ny * sy >= 0 and ball.vx * nx + ball.vy * ny < -EPSILON:
                hits.append((max(0.0, time), nx, ny))
    return min(hits, key=lambda hit: hit[0]) if hits else None


def reflect(ball: Ball, nx: float, ny: float) -> None:
    projection = ball.vx * nx + ball.vy * ny
    ball.vx -= 2 * projection * nx
    ball.vy -= 2 * projection * ny


def separate_paddle(ball: Ball, paddle: Rect) -> None:
    """Resolve overlap if a moving paddle has entered the ball this tick."""
    nearest_x = max(paddle.left, min(ball.x, paddle.right))
    nearest_y = max(paddle.top, min(ball.y, paddle.bottom))
    dx, dy = ball.x - nearest_x, ball.y - nearest_y
    distance = hypot(dx, dy)
    if distance >= ball.radius:
        return
    if distance > EPSILON:
        nx, ny = dx / distance, dy / distance
        depth = ball.radius - distance
    else:
        depth, nx, ny = min(
            (ball.x - paddle.left + ball.radius, -1, 0),
            (paddle.right - ball.x + ball.radius, 1, 0),
            (ball.y - paddle.top + ball.radius, 0, -1),
            (paddle.bottom - ball.y + ball.radius, 0, 1),
        )
    ball.x += nx * depth
    ball.y += ny * depth
    if ball.vx * nx + ball.vy * ny < 0:
        reflect(ball, nx, ny)


def advance_ball(ball: Ball, dt: float, court: Rect, paddles: tuple[Rect, ...],
                 wall_retention: float, minimum_speed: float) -> list[str]:
    events = []
    for paddle in paddles:
        separate_paddle(ball, paddle)
    ball.x = max(court.left + ball.radius, min(ball.x, court.right - ball.radius))

    # Consume the remaining time after each impact, including multiple impacts per tick.
    while dt > EPSILON:
        if ball.y + ball.radius <= court.top:
            return events + ['goal_top']
        if ball.y - ball.radius >= court.bottom:
            return events + ['goal_bottom']
        hits = []
        if ball.vx < 0:
            hits.append(((court.left + ball.radius - ball.x) / ball.vx, 'wall', 1, 0))
        elif ball.vx > 0:
            hits.append(((court.right - ball.radius - ball.x) / ball.vx, 'wall', -1, 0))
        if ball.vy < 0:
            hits.append(((court.top - ball.radius - ball.y) / ball.vy, 'goal_top', 0, 0))
        elif ball.vy > 0:
            hits.append(((court.bottom + ball.radius - ball.y) / ball.vy, 'goal_bottom', 0, 0))
        for paddle in paddles:
            hit = paddle_hit(ball, paddle, dt)
            if hit is not None:
                time, nx, ny = hit
                hits.append((time, 'paddle', nx, ny))
        hits = [hit for hit in hits if -EPSILON <= hit[0] <= dt]
        if not hits:
            ball.x += ball.vx * dt
            ball.y += ball.vy * dt
            break
        time, event, nx, ny = min(hits, key=lambda hit: hit[0])
        time = max(0.0, time)
        ball.x += ball.vx * time
        ball.y += ball.vy * time
        dt -= time
        events.append(event)
        if event.startswith('goal_'):
            return events
        reflect(ball, nx, ny)
        if event == 'wall':
            speed = hypot(ball.vx, ball.vy)
            retained_speed = min(speed, max(minimum_speed, speed * wall_retention))
            ball.vx *= retained_speed / speed
            ball.vy *= retained_speed / speed
    return events
