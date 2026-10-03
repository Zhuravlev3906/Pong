from functools import lru_cache

import pyxel

from pong.settings import WIDTH

BACKGROUND = 0
INK = 7
MUTED = 13
ACCENT = 14
TEXT = 6


def configure_palette() -> None:
    pyxel.colors[BACKGROUND] = 0x111112
    pyxel.colors[INK] = 0xD6D5D1
    pyxel.colors[MUTED] = 0x747477
    pyxel.colors[ACCENT] = 0xFFA2AA
    pyxel.colors[TEXT] = 0x98989D
    pyxel.colors[1] = 0x212124
    pyxel.colors[2] = 0x39393D


@lru_cache(maxsize=64)
def text_image(text: str, color: int) -> pyxel.Image:
    image = pyxel.Image(max(1, len(text) * 4 - 1), 6)
    image.cls(BACKGROUND)
    image.text(0, 0, text, color)
    return image


def text(x: float, y: float, value: str, color: int = INK, scale: int = 2) -> None:
    image = text_image(value, color)
    # blt scales around its centre; compensate to keep x/y at the top left.
    pyxel.blt(
        x + image.width * (scale - 1) / 2,
        y + image.height * (scale - 1) / 2,
        image,
        0,
        0,
        image.width,
        image.height,
        BACKGROUND,
        scale=scale,
    )


def centered(y: float, value: str, color: int = INK, scale: int = 2) -> None:
    text((WIDTH - (len(value) * 4 - 1) * scale) / 2, y, value, color, scale)


def frame() -> None:
    # pyxel.rectb(10, 14, 280, 376, INK)
    pyxel.line(36, 40, 65, 40, INK)
    pyxel.line(235, 40, 264, 40, INK)
    pyxel.line(36, 40, 36, 358, INK)
    pyxel.line(264, 40, 264, 358, INK)
    pyxel.line(36, 358, 264, 358, INK)
    text(76, 35, "Ping", scale=3)
    text(180, 35, "Pong", scale=3)
