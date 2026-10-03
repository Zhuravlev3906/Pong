import pyxel


# Each phrase is one 16-step bar. Tracks use channels 0–2; channel 3 is for SFX.
def load_track(track: int, first_sound: int, speed: int, lead: tuple[str, ...],
               bass: tuple[str, ...], drums: tuple[str, str],
               lead_tone: str = 'p', lead_effect: str = 'f',
               bass_tone: str = 't') -> None:
    for index, notes in enumerate(lead):
        pyxel.sounds[first_sound + index].set(notes, lead_tone, '3', lead_effect, speed)
    for index, notes in enumerate(bass):
        pyxel.sounds[first_sound + 4 + index].set(notes, bass_tone, '3', 'f', speed)
    for index, notes in enumerate(drums):
        pyxel.sounds[first_sound + 8 + index].set(
            notes, 'tnnnnnnntnnnnnnn', '4121322141213222', 'f', speed,
        )
    order = (0, 1, 0, 2, 0, 1, 2, 3)
    pyxel.musics[track].set(
        [first_sound + index for index in order],
        [first_sound + 4 + index for index in order],
        [first_sound + 8] * 7 + [first_sound + 9],
        [],
    )


def load_match_music() -> None:
    load_track(1, 23, 22, (
        'c3 r e3 r g3 e3 d3 r e3 r g3 r a3 g3 e3 r',
        'f3 r a3 r c4 a3 g3 r f3 e3 d3 r e3 r g3 r',
        'a3 r g3 e3 f3 r e3 c3 d3 r e3 g3 e3 d3 c3 r',
        'd3 r g3 r b3 a3 g3 r e3 r d3 r g2 r r r',
    ), (
        'c1 r g1 r c2 r g1 r c1 r g1 r c2 r g1 r',
        'f1 r c2 r f2 r c2 r f1 r c2 r f2 r c2 r',
        'a1 r e2 r a2 r e2 r f1 r c2 r f2 r c2 r',
        'g1 r d2 r g2 r d2 r g1 r d2 r g1 r r r',
    ), (
        'c0 r r r a2 r r r c0 r r r a2 r r r',
        'c0 r r r a2 r r r c0 r a2 r a2 r a2 r',
    ), lead_tone='t')

    load_track(2, 33, 18, (
        'g3 r e3 g3 a3 r g3 e3 d3 e3 g3 r e3 d3 c3 r',
        'a3 r f3 a3 c4 r a3 g3 f3 g3 a3 r g3 e3 f3 r',
        'e3 g3 a3 r c4 r b3 a3 g3 r e3 d3 e3 g3 a3 r',
        'd3 g3 b3 r a3 g3 d3 r f3 e3 d3 r g2 r b2 r',
    ), (
        'c1 r g1 c2 r g1 c1 r e1 r g1 c2 r g1 e1 r',
        'f1 r c2 f2 r c2 f1 r a1 r c2 f2 r c2 a1 r',
        'a1 r e2 a2 r e2 a1 r f1 r c2 f2 r c2 f1 r',
        'g1 r d2 g2 r d2 g1 r g1 r d2 f2 r d2 g1 r',
    ), (
        'c0 r a3 r a1 r a3 r c0 r a3 r a1 r a3 r',
        'c0 r a3 r a1 r a3 r c0 a3 a1 r a1 a2 a3 r',
    ))

    load_track(3, 43, 16, (
        'a2 r e3 r b-2 r e3 r a2 r f3 r e3 r b-2 r',
        'f2 r c3 r g-2 r c3 r f2 r d3 r c3 r g-2 r',
        'd3 r a3 r e-3 r a3 r f3 r e3 r d3 r c3 r',
        'e3 r f3 r b2 r c3 r e3 d3 c3 b2 a2 r e2 r',
    ), (
        'a0 r a0 r e1 r a0 r a0 r a0 r e1 r b-0 r',
        'f0 r f0 r c1 r f0 r f0 r f0 r c1 r g-0 r',
        'd1 r d1 r a1 r d1 r d1 r d1 r a1 r e-1 r',
        'e1 r e1 r b0 r e1 r e1 r f1 r e1 r e0 r',
    ), (
        'c0 r a3 r a1 r a3 r c0 c0 a3 r a1 r a3 r',
        'c0 r a3 r a1 r a3 r c0 a1 c0 a1 a2 a2 a3 r',
    ), lead_tone='p', lead_effect='vfff')

    # Original syncopated industrial riff: low pedal tones, dissonance, and breaks.
    load_track(4, 53, 12, (
        'c2 c2 r c2 r c2 c2 r c#2 r c2 r f#2 f2 r c2',
        'c2 r c2 c2 r c2 r c2 e-2 r c#2 c2 r g1 r r',
        'f1 f1 r f1 r f1 f1 r g-1 r f1 r b1 b-1 r f1',
        'c2 r r c2 c#2 r g1 r f#2 f2 e-2 c#2 c2 r r r',
    ), (
        'c0 c0 r c0 r c0 c0 r c#0 r c0 r f#0 f0 r c0',
        'c0 r c0 c0 r c0 r c0 e-0 r c#0 c0 r g0 r r',
        'f0 f0 r f0 r f0 f0 r g-0 r f0 r b0 b-0 r f0',
        'c0 r r c0 c#0 r g0 r f#0 f0 e-0 c#0 c0 r r r',
    ), (
        'c0 c0 a3 r a1 r c0 a3 c0 r a3 c0 a1 c0 a3 r',
        'c0 r a3 c0 a1 r c0 r a1 a2 a1 a2 c0 r r r',
    ), lead_tone='s', lead_effect='ffsf', bass_tone='p')
