import math

import pyxel

from pong import audio
from pong.graphics import ACCENT, BACKGROUND, INK, MUTED, centered, frame, text
from pong.settings import Difficulty, Settings

DIFFICULTY_Y = (108, 128, 148, 168)
START_RECT = (178, 307, 64, 23)


class Menu:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.focus = int(settings.difficulty)
        self.marker_y = float(DIFFICULTY_Y[self.focus])
        self.age = 0
        self.start_countdown = 0
        self.mouse_position = (pyxel.mouse_x, pyxel.mouse_y)

    def hit_target(self, x: int, y: int) -> int | None:
        for index, top in enumerate(DIFFICULTY_Y):
            if 53 <= x < 177 and top - 4 <= y < top + 15:
                return index
        if 56 <= x < 135 and 248 <= y < 274:
            return 4
        if 178 <= x < 255 and 248 <= y < 274:
            return 5
        left, top, width, height = START_RECT
        if left <= x < left + width and top <= y < top + height:
            return 6
        return None

    def choose(self, target: int) -> None:
        if target < 4:
            difficulty = Difficulty(target)
            if difficulty != self.settings.difficulty:
                self.settings.difficulty = difficulty
                audio.play_difficulty(difficulty)
        elif target < 6:
            players = target - 3
            if players != self.settings.players:
                self.settings.players = players
                pyxel.play(3, 5)
        elif not self.start_countdown:
            self.start_countdown = 12
            pyxel.play(3, 6)

    def update(self) -> bool:
        self.age += 1
        self.marker_y += (DIFFICULTY_Y[self.settings.difficulty] - self.marker_y) * 0.3
        if self.start_countdown:
            self.start_countdown -= 1
            return self.start_countdown == 0

        mouse = (pyxel.mouse_x, pyxel.mouse_y)
        target = self.hit_target(*mouse)
        if mouse != self.mouse_position and target is not None:
            self.focus = target
        self.mouse_position = mouse
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and target is not None:
            self.focus = target
            self.choose(target)
            return False

        previous = self.focus
        if pyxel.btnp(pyxel.KEY_UP, 20, 8):
            if self.focus in (4, 5):
                self.focus = 3
            elif self.focus == 6:
                self.focus = self.settings.players + 3
            else:
                self.focus = max(0, self.focus - 1)
        elif pyxel.btnp(pyxel.KEY_DOWN, 20, 8):
            if self.focus in (4, 5):
                self.focus = 6
            elif self.focus == 3:
                self.focus = self.settings.players + 3
            else:
                self.focus = min(6, self.focus + 1)
        elif pyxel.btnp(pyxel.KEY_TAB):
            self.focus = (self.focus + 1) % 7
        elif self.focus in (4, 5):
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.focus = 4
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.focus = 5
        if self.focus != previous:
            if self.focus < 6:
                self.choose(self.focus)
            else:
                pyxel.play(3, 4)
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.choose(self.focus)
        return False

    def draw(self) -> None:
        pyxel.cls(BACKGROUND)
        frame()
        text(50, 75, "Difficulty")
        selected = self.settings.difficulty
        pulse = 1 + math.sin(self.age / 12) * 0.15
        marker_color = ACCENT if selected == Difficulty.EXTREME else INK
        pyxel.rect(55, round(self.marker_y), 9, 10, marker_color)
        for index, difficulty in enumerate(Difficulty):
            color = ACCENT if difficulty == Difficulty.EXTREME else INK
            label = difficulty.name if index == 3 else difficulty.name.title()
            text(69, DIFFICULTY_Y[index], label, color)
            if self.focus == index:
                pyxel.line(
                    69,
                    DIFFICULTY_Y[index] + 14,
                    69 + (len(label) * 4 - 1) * 2 * pulse - 4,
                    DIFFICULTY_Y[index] + 14,
                    MUTED,
                )

        centered(212, "Players")
        for players, x in ((1, 64), (2, 181)):
            text(x, 253, f"{players} player" + ("s" if players == 2 else ""))
            if players == self.settings.players:
                pyxel.rect(x, 271, 12, 2, INK)
            if self.focus == players + 3:
                text(x - 9, 255, ">", MUTED, scale=1)

        x, y, width, height = START_RECT
        pressed = bool(self.start_countdown)
        pyxel.rect(x + 4, y + 4, width, height, MUTED)
        offset = 3 if pressed else 0
        pyxel.rect(x + offset, y + offset, width, height, BACKGROUND)
        pyxel.rectb(x + offset, y + offset, width, height, INK)
        text(x + 12 + offset, y + 6 + offset, "START")
        if self.focus == 6 and not pressed:
            text(x - 10, y + 8, ">", INK, 1)
