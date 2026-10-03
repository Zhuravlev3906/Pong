from dataclasses import replace
from math import ceil, cos, hypot, radians, sin
from random import Random

import pyxel

from pong.ai import PaddleAI
from pong.effects import Effect, Effects
from pong.graphics import ACCENT, BACKGROUND, INK, MUTED, centered, text
from pong.model import Ball, Paddle
from pong.physics import Rect, advance_ball
from pong.settings import FPS, HEIGHT, WIDTH, Difficulty, PADDLE_PROFILES, Settings

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
        self.effects = Effects(settings.difficulty, self.rng)
        self._applied_effects = [None, None]
        self._chaos_remaining = 0.5
        self._frame = None
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
            2 if self.effects.has(Effect.SMALL) else BALL_RADIUS,
        )
        self.serve_remaining = SERVE_DELAY
        self.ai.reset((COURT.left + COURT.right) / 2)

    def sync_effects(self) -> None:
        base = PADDLE_PROFILES[self.settings.difficulty]
        for player, paddle in enumerate((self.bottom, self.top)):
            effect = self.effects.active[player]
            kind = effect.kind if effect else None
            if kind == self._applied_effects[player]:
                continue
            center = paddle.position + paddle.length / 2
            paddle.length = 18 if kind == Effect.EDGE else PADDLE_LENGTH
            paddle.position = max(COURT.left, min(center - paddle.length / 2,
                                                  COURT.right - paddle.length))
            speed = self.ai.profile.speed if player == 1 and self.settings.players == 1 else base.speed
            paddle.speed = speed * 0.3 if kind == Effect.LAZY else speed
            paddle.motion = replace(base, acceleration=100.0, braking=35.0) if kind == Effect.LAZY else base
            paddle.velocity = max(-paddle.speed, min(paddle.velocity, paddle.speed))
            paddle.reset_input()
            self._applied_effects[player] = kind
        self.ball.radius = 2 if self.effects.has(Effect.SMALL) else BALL_RADIUS
        self.ball.x = max(COURT.left + self.ball.radius,
                          min(self.ball.x, COURT.right - self.ball.radius))

    def update_ball(self, dt: float) -> None:
        if self.serve_remaining > 0:
            remaining = max(0.0, dt - self.serve_remaining)
            self.serve_remaining = max(0.0, self.serve_remaining - dt)
            dt = remaining
            if dt == 0:
                return
        if self.effects.has(Effect.CHAOS):
            self._chaos_remaining -= dt
            if self._chaos_remaining <= 0:
                speed = hypot(self.ball.vx, self.ball.vy)
                angle = radians(self.rng.uniform(20, 65))
                self.ball.vx = sin(angle) * speed * self.rng.choice((-1, 1))
                self.ball.vy = cos(angle) * speed * (1 if self.ball.vy >= 0 else -1)
                self._chaos_remaining = self.rng.uniform(0.35, 0.7)
        else:
            self._chaos_remaining = 0.5
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
            activated = self.effects.concede(1 - scorer)
            self.serve()
            self.sync_effects()
            pyxel.play(3, 11 if activated else 10)
        elif 'paddle' in events:
            pyxel.play(3, 8)
        elif 'wall' in events:
            pyxel.play(3, 9)

    def update(self) -> None:
        keys = {effect.key for player, effect in enumerate(self.effects.active)
                if effect and effect.kind == Effect.BLOCK
                and not (player == 1 and self.settings.players == 1)}
        down = {key for key in keys if pyxel.btn(getattr(pyxel, 'KEY_' + key))}
        pressed = {key for key in keys if pyxel.btnp(getattr(pyxel, 'KEY_' + key))}
        active_dt = max(0.0, 1 / FPS - self.serve_remaining)
        if self.effects.update(active_dt, down, pressed, self.settings.players == 1):
            pyxel.play(3, 12)
        self.sync_effects()
        bottom_direction = int(pyxel.btn(pyxel.KEY_D)) - int(pyxel.btn(pyxel.KEY_A))
        if self.effects.has(Effect.INVERT, 0):
            bottom_direction *= -1
        self.bottom.move(bottom_direction, 1 / FPS, COURT_LEFT + 1, COURT_RIGHT)
        if self.settings.players == 2:
            top_direction = int(pyxel.btn(pyxel.KEY_RIGHT)) - int(pyxel.btn(pyxel.KEY_LEFT))
            if self.effects.has(Effect.INVERT, 1):
                top_direction *= -1
            self.top.move(top_direction, 1 / FPS, COURT_LEFT + 1, COURT_RIGHT)
        else:
            self.ai.update(self.top, self.ball, 1 / FPS, COURT,
                           TOP_PADDLE_Y + PADDLE_THICKNESS, self.serve_remaining > 0,
                           inverted=self.effects.has(Effect.INVERT, 1),
                           observing=not self.effects.has(Effect.BLOCK, 1))
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

        for player, effect in enumerate(self.effects.active):
            if effect is None:
                continue
            label_y = 306 if player == 0 else 80
            centered(label_y, f"P{player + 1}: {effect.kind.value} {ceil(effect.remaining)}s", ACCENT, 1)
            if effect.kind == Effect.BLOCK:
                panel_y = 320 if player == 0 else 42
                pyxel.rect(COURT_LEFT + 1, panel_y, COURT_RIGHT - COURT_LEFT - 1, 35, BACKGROUND)
                pyxel.rectb(COURT_LEFT + 1, panel_y, COURT_RIGHT - COURT_LEFT - 1, 35, ACCENT)
                message = 'AI SIGNAL LOST' if player == 1 and self.settings.players == 1 else f'PRESS {effect.key} TO UNLOCK'
                centered(panel_y + 14, message, INK, 1)
        if self.effects.has(Effect.FLIP):
            if self._frame is None:
                self._frame = pyxel.Image(WIDTH, HEIGHT)
            self._frame.blt(0, 0, pyxel.screen, 0, 0, WIDTH, HEIGHT)
            pyxel.blt(0, 0, self._frame, 0, 0, -WIDTH, -HEIGHT)
