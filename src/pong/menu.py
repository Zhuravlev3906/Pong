from enum import IntEnum

import pyxel

from pong import audio
from pong.graphics import ACCENT, BACKGROUND, INK, MUTED, TEXT, centered, frame, text
from pong.settings import Difficulty, Settings

DIFFICULTY_Y = (98, 118, 138, 158)
PLAYERS_HEADING_Y = 224
PLAYERS_Y = 247
PLAYER_OPTIONS = ((1, 65), (2, 169))
START_RECT = (178, 307, 64, 23)
SOUND_RECT = (205, 378, 60, 12)
DIFFICULTY_DESCRIPTIONS = (
    "RESPONSIVE / SLOW AI",
    "LIGHT INERTIA / RISING SPEED",
    "HEAVY INERTIA / PREDICTIVE AI",
    "EXTREME SPEED / NO BRAKES",
)


class Focus(IntEnum):
    DIFFICULTY = 0
    PLAYERS = 1
    START = 2


class Menu:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.focus = Focus.DIFFICULTY
        self.marker_y = float(DIFFICULTY_Y[settings.difficulty])
        self.start_countdown = 0
        self.hover_target: int | None = None

    def hit_target(self, x: int, y: int) -> int | None:
        for index, top in enumerate(DIFFICULTY_Y):
            if 53 <= x < 177 and top - 4 <= y < top + 15:
                return index
        for players, left in PLAYER_OPTIONS:
            if left - 8 <= x < left + 72 and PLAYERS_Y - 5 <= y < PLAYERS_Y + 22:
                return players + 3
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

    def toggle_sound(self) -> None:
        self.settings.sound_enabled = not self.settings.sound_enabled
        audio.set_enabled(self.settings.sound_enabled)

    def update(self) -> bool:
        self.marker_y += (DIFFICULTY_Y[self.settings.difficulty] - self.marker_y) * 0.3
        if self.start_countdown:
            self.start_countdown -= 1
            return self.start_countdown == 0

        target = self.hit_target(pyxel.mouse_x, pyxel.mouse_y)
        self.hover_target = target
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x, y, width, height = SOUND_RECT
            if x <= pyxel.mouse_x < x + width and y <= pyxel.mouse_y < y + height:
                self.toggle_sound()
                return False
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and target is not None:
            self.focus = (
                Focus.DIFFICULTY
                if target < 4
                else (Focus.PLAYERS if target < 6 else Focus.START)
            )
            self.choose(target)
            return False

        if pyxel.btnp(pyxel.KEY_TAB):
            direction = -1 if pyxel.btn(pyxel.KEY_SHIFT) else 1
            self.focus = Focus((self.focus + direction) % len(Focus))
            pyxel.play(3, 4)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            if self.focus == Focus.START:
                self.choose(6)
            else:
                self.focus = Focus(self.focus + 1)
                pyxel.play(3, 4)
        elif self.focus == Focus.DIFFICULTY:
            if pyxel.btnp(pyxel.KEY_UP, 20, 8):
                self.choose(max(0, self.settings.difficulty - 1))
            elif pyxel.btnp(pyxel.KEY_DOWN, 20, 8):
                self.choose(min(3, self.settings.difficulty + 1))
        elif self.focus == Focus.PLAYERS:
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.choose(4)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.choose(5)
        return False

    def draw(self) -> None:
        pyxel.cls(BACKGROUND)
        frame()
        text(55, 75, "Difficulty", INK)
        if self.focus == Focus.DIFFICULTY:
            text(45, 77, ">", INK, 1)
        selected = self.settings.difficulty
        marker_color = ACCENT if selected == Difficulty.EXTREME else INK
        pyxel.rect(55, round(self.marker_y), 9, 10, marker_color)
        for index, difficulty in enumerate(Difficulty):
            color = ACCENT if difficulty == Difficulty.EXTREME else TEXT
            label = difficulty.name if index == 3 else difficulty.name.title()
            text(69, DIFFICULTY_Y[index], label, color)
            if self.hover_target == index:
                pyxel.line(69, DIFFICULTY_Y[index] + 14,
                           69 + (len(label) * 4 - 1) * 2 - 1,
                           DIFFICULTY_Y[index] + 14, MUTED)

        text(55, 187, DIFFICULTY_DESCRIPTIONS[selected], MUTED, 1)
        centered(PLAYERS_HEADING_Y, "Players", INK)
        if self.focus == Focus.PLAYERS:
            text(113, PLAYERS_HEADING_Y + 2, ">", INK, 1)
        for players, x in PLAYER_OPTIONS:
            text(
                x, PLAYERS_Y, f"{players} player" + ("s" if players == 2 else ""), TEXT
            )
            if players == self.settings.players:
                pyxel.rect(x, PLAYERS_Y + 18, 12, 2, INK)
            if self.hover_target == players + 3:
                width = (len(f"{players} player" + ("s" if players == 2 else "")) * 4 - 1) * 2
                pyxel.line(x, PLAYERS_Y + 14, x + width - 1, PLAYERS_Y + 14, MUTED)

        x, y, width, height = START_RECT
        pressed = bool(self.start_countdown)
        pyxel.rect(x + 4, y + 4, width, height, MUTED)
        offset = 3 if pressed else 0
        pyxel.rect(x + offset, y + offset, width, height, BACKGROUND)
        pyxel.rectb(x + offset, y + offset, width, height, INK)
        if self.hover_target == 6 and not pressed:
            pyxel.rect(x + 1, y + 1, width - 2, height - 2, 1)
        text(x + 12 + offset, y + 6 + offset, "START", INK)
        if self.focus == Focus.START and not pressed:
            text(x - 10, y + 8, ">", INK, 1)

        hints = (
            "UP/DOWN: CHANGE   ENTER: NEXT",
            "LEFT/RIGHT: CHANGE   ENTER: NEXT",
            "ENTER: START",
        )
        centered(366, hints[self.focus], TEXT, 1)
        text(36, 382, "TAB: NEXT  SHIFT+TAB: BACK", MUTED, 1)
        text(211, 382, "M: SOUND " + ("ON" if self.settings.sound_enabled else "OFF"), TEXT, 1)
