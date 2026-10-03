import pyxel

from pong import audio
from pong.graphics import configure_palette
from pong.match import Match
from pong.menu import Menu
from pong.settings import FPS, HEIGHT, SCALE, WIDTH, Settings
from pong.window import lock_window_size


class App:
    def __init__(self, *, headless: bool = False) -> None:
        pyxel.init(
            WIDTH,
            HEIGHT,
            title="Ping Pong",
            fps=FPS,
            display_scale=SCALE,
            quit_key=pyxel.KEY_NONE,
            headless=headless,
        )
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
        self.match = Match(self.settings)
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
            else:
                self.match.update()
        elif self.menu.update():
            self.match = Match(self.settings)
            self.in_match = True
            for channel in range(3):
                pyxel.stop(channel)

    def draw(self) -> None:
        if not self.in_match:
            self.menu.draw()
            return
        self.match.draw()
