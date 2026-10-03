import pyxel

from pong.settings import Difficulty
from pong.music import load_match_music

CHANNEL_GAINS = (0.09, 0.09, 0.07, 0.125)


def load_audio() -> None:
    # Three music channels leave channel 3 free for menu feedback.
    melody = [
        'e3 r g3 a3 r g3 e3 r d3 r e3 g3 r e3 d3 r',
        'c3 r e3 g3 r e3 c3 r d3 r e3 d3 r c3 d3 r',
        'e3 r g3 a3 r b3 g3 r e3 r d3 e3 r g3 d3 r',
        'c3 r e3 g3 r e3 d3 r c3 r d3 e3 r d3 c3 r',
    ]
    bass = ['c2 r r c2 g1 r r g1 a1 r r a1 g1 r r g1',
            'f1 r r f1 c2 r r c2 g1 r r g1 g1 r r g1']
    for i, notes in enumerate(melody):
        pyxel.sounds[16 + i].set(notes, 'p', '3', 'f', 30)
    for i, notes in enumerate(bass):
        pyxel.sounds[20 + i].set(notes, 't', '3', 'f', 30)
    pyxel.sounds[22].set('c0 r r r c0 r r r c0 r r r c0 r r r', 'n', '1', 'f', 30)
    pyxel.musics[0].set([16, 17, 18, 19], [20, 21, 20, 21], [22] * 4, [])

    load_match_music()

    pyxel.sounds[0].set('c3 e3 g3 c4', 't', '4432', 'f', 9)
    pyxel.sounds[1].set('e2 g2 c3', 'p', '432', 'f', 8)
    pyxel.sounds[2].set('c2 c#2 g1', 's', '543', 'vff', 12)
    pyxel.sounds[3].set('c1 c#1 g0 f0 c0 r c0', 'ssnnsnn', '5544321', 'vvvvfff', 12)
    pyxel.sounds[4].set('c3', 't', '2', 'f', 3)
    pyxel.sounds[5].set('g2 c3', 't', '32', 'f', 6)
    pyxel.sounds[6].set('c3 e3 g3 c4', 'p', '4432', 'f', 7)
    pyxel.sounds[7].set('e3 c3', 't', '32', 'f', 6)
    pyxel.sounds[8].set('c3 g3', 't', '43', 'ff', 3)
    pyxel.sounds[9].set('g2', 'p', '2', 'f', 4)
    pyxel.sounds[10].set('g2 e2 c2', 't', '432', 'fff', 10)
    pyxel.sounds[11].set('c2 c#2 g1', 'p', '443', 'vff', 8)
    pyxel.sounds[12].set('g2 c3', 't', '32', 'ff', 6)


def play_difficulty(difficulty: Difficulty) -> None:
    pyxel.play(3, int(difficulty))


def start_music(difficulty: Difficulty | None = None) -> None:
    for channel in range(3):
        pyxel.stop(channel)
    track = 0 if difficulty is None else int(difficulty) + 1
    pyxel.playm(track, loop=True)


def set_enabled(enabled: bool) -> None:
    # Muting the mixer preserves the current music position.
    for channel, gain in zip(pyxel.channels, CHANNEL_GAINS):
        channel.gain = gain if enabled else 0.0
