from math import cos, hypot, radians, sin
from random import Random

import pyxel

from pong.ai import PaddleAI
from pong.graphics import BACKGROUND, INK, MUTED, centered, text
from pong.model import Ball, Paddle
from pong.physics import Rect, advance_ball
from pong.settings import FPS, WIDTH, Difficulty, PADDLE_PROFILES, Settings

COURT_LEFT = 22
COURT_RIGHT = WIDTH - COURT_LEFT
COURT_TOP = 32
COURT_BOTTOM = 358
PADDLE_LENGTH = 70
PADDLE_THICKNESS = 6
TOP_PADDLE_Y = COURT_TOP + 20
BOTTOM_PADDLE_Y = COURT_BOTTOM - 20 - PADDLE_THICKNESS

BALL_RADIUS = 6
SERVE_DELAY = 0.75
COURT = Rect(COURT_LEFT + 1, COURT_TOP + 1, COURT_RIGHT, COURT_BOTTOM)
# Initial speed, acceleration, maximum speed, wall retention.
BALL_PROFILES = {
    Difficulty.EASY: (120.0, 0.0, 120.0, 0.92),
    Difficulty.MEDIUM: (150.0, 4.0, 280.0, 0.94),
    Difficulty.HARD: (180.0, 10.0, 380.0, 0.96),
    Difficulty.EXTREME: (260.0, 16.0, 520.0, 1.0),
}


class Match:
    def __init__(self, settings: Settings, rng: Random | None = None) -> None:
        self.settings = settings
        self.rng = rng if rng is not None else Random()
        self.score = [0, 0]
        position = (WIDTH - PADDLE_LENGTH) / 2
        motion = PADDLE_PROFILES[settings.difficulty]
        self.bottom = Paddle(position, PADDLE_LENGTH, motion.speed, motion)
        self.top = Paddle(position, PADDLE_LENGTH, motion.speed, motion)
        self.ai = PaddleAI(settings.difficulty, (COURT.left + COURT.right) / 2)
        if settings.players == 1:
            self.top.speed = self.ai.profile.speed
        self.serve()

    def serve(self) -> None:
        speed = BALL_PROFILES[self.settings.difficulty][0]
        angle = radians(self.rng.uniform(20, 50))
        self.ball = Ball(
            (COURT_LEFT + COURT_RIGHT) / 2,
            (COURT_TOP + COURT_BOTTOM) / 2,
            sin(angle) * speed * self.rng.choice((-1, 1)),
            cos(angle) * speed * self.rng.choice((-1, 1)),
            BALL_RADIUS,
        )
        self.serve_remaining = SERVE_DELAY
        self.ai.reset((COURT.left + COURT.right) / 2)

    def update_ball(self, dt: float) -> None:
        if self.serve_remaining > 0:
            remaining = max(0.0, dt - self.serve_remaining)
            self.serve_remaining = max(0.0, self.serve_remaining - dt)
            dt = remaining
            if dt == 0:
                return
        initial, acceleration, maximum, retention = BALL_PROFILES[self.settings.difficulty]
        speed = hypot(self.ball.vx, self.ball.vy)
        if speed > 0:
            factor = min(maximum, speed + acceleration * dt) / speed
            self.ball.vx *= factor
            self.ball.vy *= factor
        paddles = (
            Rect(self.top.position, TOP_PADDLE_Y,
                 self.top.position + self.top.length, TOP_PADDLE_Y + PADDLE_THICKNESS),
            Rect(self.bottom.position, BOTTOM_PADDLE_Y,
                 self.bottom.position + self.bottom.length, BOTTOM_PADDLE_Y + PADDLE_THICKNESS),
        )
        events = advance_ball(self.ball, dt, COURT, paddles, retention, initial * 0.6)
        if 'goal_top' in events or 'goal_bottom' in events:
            scorer = 0 if 'goal_top' in events else 1
            self.score[scorer] += 1
            self.serve()
            pyxel.play(3, 10)
        elif 'paddle' in events:
            pyxel.play(3, 8)
        elif 'wall' in events:
            pyxel.play(3, 9)

    def update(self) -> None:
        bottom_direction = int(pyxel.btn(pyxel.KEY_D)) - int(pyxel.btn(pyxel.KEY_A))
        self.bottom.move(bottom_direction, 1 / FPS, COURT_LEFT + 1, COURT_RIGHT)
        if self.settings.players == 2:
            top_direction = int(pyxel.btn(pyxel.KEY_RIGHT)) - int(pyxel.btn(pyxel.KEY_LEFT))
            self.top.move(top_direction, 1 / FPS, COURT_LEFT + 1, COURT_RIGHT)
        else:
            self.ai.update(self.top, self.ball, 1 / FPS, COURT,
                           TOP_PADDLE_Y + PADDLE_THICKNESS, self.serve_remaining > 0)
        self.update_ball(1 / FPS)

    def draw(self) -> None:
        pyxel.cls(BACKGROUND)
        pyxel.line(COURT_LEFT, COURT_TOP, 53, COURT_TOP, INK)
        score_text = f"Score {self.score[0]} : {self.score[1]}"
        score_end = 64 + (len(score_text) * 4 - 1) * 2 + 12
        if score_end < COURT_RIGHT:
            pyxel.line(score_end, COURT_TOP, COURT_RIGHT, COURT_TOP, INK)
        pyxel.line(COURT_LEFT, COURT_TOP, COURT_LEFT, COURT_BOTTOM, INK)
        pyxel.line(COURT_RIGHT, COURT_TOP, COURT_RIGHT, COURT_BOTTOM, INK)
        pyxel.line(COURT_LEFT, COURT_BOTTOM, COURT_RIGHT, COURT_BOTTOM, INK)
        text(64, COURT_TOP - 6, score_text)
        opponent = 'AI' if self.settings.players == 1 else 'P2'
        text(64, COURT_TOP - 17, f'P1: BOTTOM / {opponent}: TOP', MUTED, 1)

        middle_y = (COURT_TOP + COURT_BOTTOM) // 2
        for x in range(COURT_LEFT + 10, COURT_RIGHT - 8, 10):
            pyxel.rect(x, middle_y, 4, 1, 2)
        pyxel.rect(round(self.top.position), TOP_PADDLE_Y,
                   self.top.length, PADDLE_THICKNESS, INK)
        pyxel.rect(round(self.bottom.position), BOTTOM_PADDLE_Y,
                   self.bottom.length, PADDLE_THICKNESS, INK)
        pyxel.circ(round(self.ball.x), round(self.ball.y), self.ball.radius, INK)
        if self.serve_remaining > 0:
            centered(middle_y + 16, 'READY', MUTED, 1)

        if self.settings.players == 2:
            centered(368, 'P1: A/D    P2: LEFT/RIGHT', MUTED, 1)
        else:
            centered(368, f'P1: A/D    AI: {self.settings.difficulty.name}', MUTED, 1)
        centered(381, 'ESC: MENU    M: SOUND ' +
                 ('ON' if self.settings.sound_enabled else 'OFF'), MUTED, 1)
