"""Sons gerados proceduralmente - zero arquivos externos."""
import pygame
import math
import array

_sounds: dict = {}


def _buf(pts, dur, vol=0.35):
    """
    pts = [(frac, freq), ...] – breakpoints de pitch
    Gera onda senoidal com envelope de fade-out.
    """
    sr  = 44100
    n   = int(sr * dur)
    buf = array.array('h')
    ph  = 0.0
    for i in range(n):
        frac = i / max(n - 1, 1)
        freq = pts[0][1]
        for j in range(len(pts) - 1):
            t0, f0 = pts[j]
            t1, f1 = pts[j + 1]
            if t0 <= frac <= t1:
                a    = (frac - t0) / (t1 - t0) if t1 > t0 else 0.0
                freq = f0 + a * (f1 - f0)
                break
        ph  += 2 * math.pi * freq / sr
        env  = (1.0 - frac) ** 0.55
        val  = int(math.sin(ph) * env * vol * 32767)
        buf.append(val)
        buf.append(val)   # stereo
    return pygame.mixer.Sound(buffer=buf)


def _seq(notes, vol=0.4):
    """
    notes = [(freq, dur), ...] – sequencia de notas separadas.
    freq=None gera silencio. Cada nota tem ataque rapido e decay proprio.
    """
    sr  = 44100
    buf = array.array('h')
    for freq, dur in notes:
        n  = int(sr * dur)
        ph = 0.0
        for i in range(n):
            frac = i / max(n - 1, 1)
            if freq is None:
                buf.append(0)
                buf.append(0)
                continue
            ph += 2 * math.pi * freq / sr
            env = min(1.0, frac * 14) * (1.0 - frac) ** 0.6
            val = int(math.sin(ph) * env * vol * 32767)
            buf.append(val)
            buf.append(val)   # stereo
    return pygame.mixer.Sound(buffer=buf)


def init():
    global _sounds
    if not pygame.mixer.get_init():
        return
    # Fanfarra curta de vitoria - usada em toda fase completa
    fanfarra = _seq([(523, 0.11), (523, 0.07), (659, 0.11), (784, 0.11),
                     (None, 0.04), (1047, 0.34)], 0.45)
    _sounds = {
        # Gaviao/inimigo espantado: chirp descendente
        'kill':     _buf([(0, 740), (0.3, 520), (1, 240)], 0.20, 0.40),
        # Fase completa: fanfarra curta (mesma em todas as fases)
        'complete': fanfarra,
        'fanfarra': fanfarra,
        # Acao errada / fase falhou: boing de mola
        'erro':     _buf([(0, 320), (0.2, 130), (0.45, 230), (0.7, 110), (1, 150)], 0.32, 0.45),
        # Item coletado: ding brilhante
        'ding':     _seq([(1319, 0.06), (1760, 0.20)], 0.40),
        # Galinha curada: cacarejo "co-co-co-COH!"
        'cacarejo': _seq([(587, 0.07), (None, 0.03), (587, 0.07), (None, 0.03),
                          (659, 0.07), (None, 0.04), (880, 0.22)], 0.42),
        # Ovo normal: plop suave
        'ovo':      _buf([(0, 370), (0.22, 510), (1, 370)], 0.09, 0.28),
        # Ovo azul da Ganiza: brilho especial
        'ovo_azul': _buf([(0, 880), (0.48, 1100), (1, 1320)], 0.17, 0.38),
        # Ovo ruim: som negativo
        'ovo_ruim': _buf([(0, 200), (0.35, 130), (1, 80)],  0.20, 0.42),
        # Vida perdida: thud grave
        'vida':     _buf([(0, 155), (0.28, 88),  (1, 52)],  0.28, 0.50),
        # Cobra morta: pancada seca
        'cobra':    _buf([(0, 270), (0.18, 135), (1, 68)],  0.22, 0.44),
        # Game over: descida triste
        'gameover': _buf([(0, 440), (0.45, 330), (1, 220)], 0.44, 0.44),
        # Peca encaixada / clique positivo
        'encaixe':  _buf([(0, 520), (0.5, 660), (1, 520)],  0.10, 0.30),
        # Click neutro de UI
        'click':    _buf([(0, 460), (1, 460)],               0.05, 0.18),
    }


def play(name: str):
    s = _sounds.get(name)
    if s:
        s.play()
