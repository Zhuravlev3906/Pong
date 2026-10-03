import pyxel

from pong.graphics import BACKGROUND, INK, MUTED, centered, text
from pong.model import Paddle
from pong.settings import FPS, WIDTH, Settings

COURT_LEFT = 22
COURT_RIGHT = WIDTH - COURT_LEFT
COURT_TOP = 32
COURT_BOTTOM = 358
PADDLE_LENGTH = 70
PADDLE_THICKNESS = 6
PADDLE_SPEED = 180.0
TOP_PADDLE_Y = COURT_TOP + 20
BOTTOM_PADDLE_Y = COURT_BOTTOM - 20 - PADDLE_THICKNESS


class Match:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        position = (WIDTH - PADDLE_LENGTH) / 2
        self.bottom = Paddle(position, PADDLE_LENGTH, PADDLE_SPEED)
        self.top = Paddle(position, PADDLE_LENGTH, PADDLE_SPEED)

    def update(self) -> None:
        bottom_direction = int(pyxel.btn(pyxel.KEY_D)) - int(pyxel.btn(pyxel.KEY_A))
        self.bottom.move(bottom_direction, 1 / FPS, COURT_LEFT + 1, COURT_RIGHT)
        if self.settings.players == 2:
            top_direction = int(pyxel.btn(pyxel.KEY_RIGHT)) - int(pyxel.btn(pyxel.KEY_LEFT))
            self.top.move(top_direction, 1 / FPS, COURT_LEFT + 1, COURT_RIGHT)

    def draw(self) -> None:
        pyxel.cls(BACKGROUND)
        pyxel.line(COURT_LEFT, COURT_TOP, 53, COURT_TOP, INK)
        pyxel.line(160, COURT_TOP, COURT_RIGHT, COURT_TOP, INK)
        pyxel.line(COURT_LEFT, COURT_TOP, COURT_LEFT, COURT_BOTTOM, INK)
        pyxel.line(COURT_RIGHT, COURT_TOP, COURT_RIGHT, COURT_BOTTOM, INK)
        pyxel.line(COURT_LEFT, COURT_BOTTOM, COURT_RIGHT, COURT_BOTTOM, INK)
        text(64, COURT_TOP - 6, 'Score 0 : 0')
        text(64, COURT_TOP - 17, 'P1: BOTTOM / P2: TOP', MUTED, 1)

        middle_y = (COURT_TOP + COURT_BOTTOM) // 2
        for x in range(COURT_LEFT + 10, COURT_RIGHT - 8, 10):
            pyxel.rect(x, middle_y, 4, 1, 2)
        pyxel.rect(round(self.top.position), TOP_PADDLE_Y,
                   self.top.length, PADDLE_THICKNESS, INK)
        pyxel.rect(round(self.bottom.position), BOTTOM_PADDLE_Y,
                   self.bottom.length, PADDLE_THICKNESS, INK)
        pyxel.circ(WIDTH // 2, middle_y + 24, 6, INK)

        if self.settings.players == 2:
            centered(368, 'P1: A/D    P2: LEFT/RIGHT', MUTED, 1)
        else:
            centered(368, 'P1: A/D    AI: COMING NEXT', MUTED, 1)
        centered(381, 'ESC: MENU    M: SOUND ' +
                 ('ON' if self.settings.sound_enabled else 'OFF'), MUTED, 1)
