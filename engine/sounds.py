"""Sons gerados proceduralmente - zero arquivos externos."""
import pygame
import math
import array
import sys

_sounds: dict = {}
_mus_channel = None

# No navegador a musica continua toca via WebAudio (chvMusica no
# index.html, injetado pelo deploy.py): loop na thread de audio, sem os
# estalos do mixer em WASM. Os efeitos curtos continuam no mixer.
_IS_WEB = sys.platform == "emscripten"


def _musica_fundo(vol=1.0):
    """
    Musica de fundo alegre (loop de 8s): melodia em Do maior + baixo I-IV-V.
    Gerada por notas cacheadas para o init ficar rapido.
    """
    sr   = 44100
    # Melodia: 32 colcheias de 0.25s (0 = pausa)
    MEL  = [523, 587, 659, 784,  659, 587, 523, 587,
            659, 784, 880, 784,  659, 523, 587, 0,
            523, 587, 659, 784,  880, 784, 659, 784,
            1047, 880, 784, 659, 587, 659, 523, 0]
    # Baixo: 16 minimas de 0.5s (C / F / G)
    BAIXO = [131, 131, 175, 175, 131, 131, 196, 196,
             131, 131, 175, 175, 196, 196, 131, 131]

    cache = {}
    def nota(freq, dur, v):
        key = (freq, dur, v)
        if key in cache:
            return cache[key]
        n   = int(sr * dur)
        out = array.array('h', bytes(2 * n))
        if freq:
            for i in range(n):
                t    = i / sr
                frac = i / max(n - 1, 1)
                # Envelope trapezoidal: sustain continuo com fade de ~11ms
                # nas pontas - sem vales de silencio nem cliques entre notas
                env  = min(1.0, frac * 22, (1.0 - frac) * 22)
                out[i] = int((math.sin(2 * math.pi * freq * t)
                              + 0.35 * math.sin(4 * math.pi * freq * t))
                             * env * v * 32767)
        cache[key] = out
        return out

    mel = array.array('h')
    for f in MEL:
        mel.extend(nota(f, 0.25, 0.34 * vol))
    baixo = array.array('h')
    for f in BAIXO:
        baixo.extend(nota(f, 0.5, 0.24 * vol))

    n   = min(len(mel), len(baixo))
    buf = array.array('h')
    for i in range(n):
        v = max(-32767, min(32767, mel[i] + baixo[i]))
        buf.append(v)
        buf.append(v)   # stereo
    return pygame.mixer.Sound(buffer=buf)


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
        # Pegou o ovo podre: "wah wah waaah" (trombone triste)
        'podre':    _seq([(196, 0.15), (165, 0.15), (None, 0.03), (131, 0.34)], 0.45),
        # Ovo podre caindo: zumbido de mosca (aviso sonoro)
        'zumbido':  _seq([(98, 0.07), (117, 0.06), (98, 0.07), (121, 0.06),
                          (98, 0.07), (110, 0.10)], 0.34),
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
    if not _IS_WEB:
        # Musica de fundo alegre (loop durante as fases)
        _sounds['musica'] = _musica_fundo()
        _sounds['musica'].set_volume(0.32)


def play(name: str):
    s = _sounds.get(name)
    if s:
        s.play()


def musica_start():
    """Comeca a musica de fundo em loop (idempotente entre fases)."""
    global _mus_channel
    if _IS_WEB:
        try:
            import platform
            platform.window.chvMusica.start()
        except Exception:
            pass
        return
    s = _sounds.get('musica')
    if not s:
        return
    if _mus_channel is not None and _mus_channel.get_busy():
        return
    _mus_channel = s.play(loops=-1)


def musica_stop():
    global _mus_channel
    if _IS_WEB:
        try:
            import platform
            platform.window.chvMusica.stop()
        except Exception:
            pass
        return
    if _mus_channel is not None:
        _mus_channel.stop()
        _mus_channel = None
