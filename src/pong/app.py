import pyxel

from pong import audio
from pong.graphics import BACKGROUND, INK, MUTED, centered, configure_palette
from pong.menu import Menu
from pong.settings import FPS, HEIGHT, SCALE, WIDTH, Settings
from pong.window import lock_window_size


class App:
    def __init__(self, *, headless: bool = False) -> None:
        pyxel.init(WIDTH, HEIGHT, title='Ping Pong', fps=FPS,
                   display_scale=SCALE, quit_key=pyxel.KEY_NONE, headless=headless)
        if not headless:
            lock_window_size(WIDTH * SCALE, HEIGHT * SCALE)
        pyxel.integer_scale(True)
        pyxel.mouse(True)
        configure_palette()
        audio.load_audio()
        self.settings = Settings()
        audio.set_enabled(self.settings.sound_enabled)
        self.menu = Menu(self.settings)
        self.in_match = False
        audio.start_music()

    def run(self) -> None:
        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_M):
            self.menu.toggle_sound()
        if self.in_match:
            if pyxel.btnp(pyxel.KEY_ESCAPE):
                self.in_match = False
                self.menu = Menu(self.settings)
                audio.start_music()
                pyxel.play(3, 7)
        elif self.menu.update():
            self.in_match = True
            for channel in range(3):
                pyxel.stop(channel)

    def draw(self) -> None:
        if not self.in_match:
            self.menu.draw()
            return
        pyxel.cls(BACKGROUND)
        pyxel.rectb(10, 14, 280, 346, INK)
        for y in range(56, 346, 12):
            pyxel.rect(149, y, 2, 5, 2)
        centered(30, '0     0', scale=3)
        pyxel.rect(25, 171, 5, 36, INK)
        pyxel.rect(270, 171, 5, 36, INK)
        pyxel.rect(148, 187, 4, 4, INK)
        centered(105, 'COURT PREVIEW')
        centered(124, 'GAMEPLAY COMING NEXT', MUTED, 1)
        centered(305, self.settings.difficulty.name, MUTED)
        centered(326, '1 PLAYER / AI' if self.settings.players == 1 else '2 PLAYERS', MUTED, 1)
        centered(370, 'ESC  BACK TO MENU', MUTED, 1)
        centered(382, 'M: SOUND ' + ('ON' if self.settings.sound_enabled else 'OFF'), MUTED, 1)
