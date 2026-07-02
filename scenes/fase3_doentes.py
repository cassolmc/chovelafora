"""
Fase 3 - Galinhas Doentes
Puzzle de correspondencia: cada galinha doente mostra um icone de sintoma;
a bandeja tem remedios diferentes. Arraste o remedio certo ate a galinha
certa. 3 galinhas por rodada, 60 segundos, 3 rodadas.
"""
import pygame
import math
import random
from engine.scene_manager import Scene
from engine.dialog import DialogBox
from engine.ui import Button, HUD, ProgressBar
from engine.vfx import VFX
import engine.sounds as snd
from constants import *
import characters.sprites as spr

DIALOGO_INTRO = [
    ("Mamae",    "Marina! Tres galinhas amanheceram doentes!"),
    ("Marina",   "Calma! A doutora Marina vai cuidar de voces!"),
    ("Narrador", "Arraste o remedio certo para cada galinha antes do tempo acabar!"),
]

DIALOGO_DONE = [
    ("Marina", "Todas as galinhas sararam!"),
    ("Ramona", "Co-co-COROCO!!!"),
]

RODADAS    = 3
TEMPO_MAX  = 60.0

# Sintoma -> remedio que cura
SINTOMAS = ["febre", "frio", "tosse", "barriga", "dodoi"]
CURA = {
    "febre":   "comprimido",
    "frio":    "cachecol",
    "tosse":   "xarope",
    "barriga": "cha",
    "dodoi":   "curativo",
}
NOME_SINTOMA = {
    "febre": "Febre", "frio": "Frio", "tosse": "Tosse",
    "barriga": "Barriga", "dodoi": "Dodoi",
}
REMEDIOS = ["comprimido", "cachecol", "xarope", "cha", "curativo"]
NOME_REMEDIO = {
    "comprimido": "Comprimido", "cachecol": "Cachecol",
    "xarope": "Xarope", "cha": "Cha", "curativo": "Curativo",
}

# Posicao das 3 galinhas pacientes (centro do corpo)
GALINHA_POS = [(380, 385), (660, 370), (940, 385)]

# Bandeja de remedios
BANDEJA = pygame.Rect(250, 494, 790, 96)
MED_SLOTS = [pygame.Rect(268 + i * 152, 502, 136, 74) for i in range(5)]


# --------------------------------------------------------------------- icones
def _draw_sintoma(surf, sintoma, cx, cy, frame=0):
    if sintoma == "febre":
        # Termometro vermelho
        pygame.draw.rect(surf, (225, 228, 232), (cx - 4, cy - 18, 8, 28), border_radius=4)
        pygame.draw.rect(surf, (150, 155, 160), (cx - 4, cy - 18, 8, 28), 1, border_radius=4)
        pygame.draw.rect(surf, RED, (cx - 2, cy - 10, 4, 20))
        pygame.draw.circle(surf, RED, (cx, cy + 13), 6)
        for ty in range(cy - 15, cy + 4, 5):
            pygame.draw.line(surf, (150, 155, 160), (cx + 4, ty), (cx + 7, ty), 1)

    elif sintoma == "frio":
        # Floco de neve
        c = (110, 190, 255)
        for ang in (0, 60, 120):
            r  = math.radians(ang)
            dx = int(math.cos(r) * 14)
            dy = int(math.sin(r) * 14)
            pygame.draw.line(surf, c, (cx - dx, cy - dy), (cx + dx, cy + dy), 3)
            for t in (-0.65, 0.65):
                px, py = cx + int(dx * t), cy + int(dy * t)
                pr = math.radians(ang + 90)
                bx, by = int(math.cos(pr) * 5), int(math.sin(pr) * 5)
                pygame.draw.line(surf, c, (px - bx, py - by), (px + bx, py + by), 2)

    elif sintoma == "tosse":
        # Nuvem de tosse "cof cof"
        c = (165, 170, 178)
        pygame.draw.circle(surf, c, (cx - 8, cy + 2), 8)
        pygame.draw.circle(surf, c, (cx + 2, cy - 3), 10)
        pygame.draw.circle(surf, c, (cx + 11, cy + 3), 7)
        for i in range(3):
            lx = cx - 16 + i * 3
            pygame.draw.line(surf, (120, 126, 134),
                             (lx - 8, cy - 10 - i * 4), (lx, cy - 8 - i * 4), 2)

    elif sintoma == "barriga":
        # Espiral verde de enjoo
        c = (90, 185, 70)
        for i, rr in enumerate((14, 10, 6)):
            pygame.draw.arc(surf, c, (cx - rr, cy - rr, rr * 2, rr * 2),
                            i * 0.9, i * 0.9 + 4.6, 3)
        pygame.draw.circle(surf, c, (cx, cy), 2)

    elif sintoma == "dodoi":
        # Estrela de dor
        pts = []
        for i in range(10):
            r  = 15 if i % 2 == 0 else 6
            a  = math.radians(i * 36 - 90)
            pts.append((cx + int(math.cos(a) * r), cy + int(math.sin(a) * r)))
        pygame.draw.polygon(surf, (255, 210, 60), pts)
        pygame.draw.polygon(surf, (230, 90, 60), pts, 2)


def _draw_remedio(surf, med, cx, cy):
    if med == "comprimido":
        # Capsula vermelha e branca
        r = pygame.Rect(cx - 22, cy - 9, 44, 18)
        pygame.draw.rect(surf, WHITE, r, border_radius=9)
        pygame.draw.rect(surf, RED, (cx - 22, cy - 9, 22, 18),
                         border_top_left_radius=9, border_bottom_left_radius=9)
        pygame.draw.rect(surf, (140, 140, 145), r, 2, border_radius=9)
        pygame.draw.line(surf, (140, 140, 145), (cx, cy - 8), (cx, cy + 8), 1)

    elif med == "cachecol":
        # Cachecol laranja com franjas
        c  = (240, 130, 40)
        cs = (200, 100, 25)
        pts = [(cx - 24, cy - 6), (cx - 8, cy + 2), (cx + 8, cy - 6), (cx + 24, cy + 2)]
        for a, b in zip(pts, pts[1:]):
            pygame.draw.line(surf, c, a, b, 10)
        pygame.draw.rect(surf, c, (cx + 16, cy, 12, 18), border_radius=2)
        for i in range(3):
            fx = cx + 18 + i * 4
            pygame.draw.line(surf, cs, (fx, cy + 18), (fx, cy + 24), 2)
        for a, b in zip(pts, pts[1:]):
            pygame.draw.line(surf, cs, a, b, 1)

    elif med == "xarope":
        # Frasco ambar com tampa vermelha e colher
        pygame.draw.rect(surf, (196, 120, 40), (cx - 16, cy - 8, 24, 26), border_radius=4)
        pygame.draw.rect(surf, (150, 88, 26), (cx - 16, cy - 8, 24, 26), 2, border_radius=4)
        pygame.draw.rect(surf, (150, 88, 26), (cx - 8, cy - 14, 8, 7))
        pygame.draw.rect(surf, RED, (cx - 10, cy - 20, 12, 8), border_radius=2)
        pygame.draw.rect(surf, WHITE, (cx - 12, cy - 2, 16, 12), border_radius=2)
        pygame.draw.line(surf, (170, 175, 182), (cx + 12, cy + 14), (cx + 22, cy - 2), 3)
        pygame.draw.ellipse(surf, (170, 175, 182), (cx + 19, cy - 8, 9, 7))

    elif med == "cha":
        # Xicara de cha verde com vapor
        pygame.draw.ellipse(surf, (230, 235, 238), (cx - 22, cy + 12, 44, 8))
        pygame.draw.rect(surf, (95, 175, 90), (cx - 16, cy - 2, 32, 16),
                         border_bottom_left_radius=10, border_bottom_right_radius=10)
        pygame.draw.ellipse(surf, (70, 140, 65), (cx - 16, cy - 6, 32, 9))
        pygame.draw.arc(surf, (95, 175, 90), (cx + 12, cy - 2, 14, 14), -1.4, 1.4, 3)
        for sx in (cx - 7, cx + 4):
            pygame.draw.arc(surf, (210, 215, 220), (sx, cy - 20, 7, 9), 1.6, 4.6, 2)
            pygame.draw.arc(surf, (210, 215, 220), (sx + 2, cy - 14, 7, 8), -1.6, 1.6, 2)

    elif med == "curativo":
        # Band-aid
        r = pygame.Rect(cx - 24, cy - 8, 48, 16)
        pygame.draw.rect(surf, (235, 198, 150), r, border_radius=8)
        pygame.draw.rect(surf, (200, 160, 112), r, 2, border_radius=8)
        pygame.draw.rect(surf, (245, 222, 188), (cx - 8, cy - 8, 16, 16))
        for dx in (-16, 16):
            for dy in (-3, 2):
                pygame.draw.circle(surf, (200, 160, 112), (cx + dx, cy + dy), 1)


def _draw_paciente(surf, x, y, frame, sintoma, curada):
    """Galinha grande (paciente). Doente: palida e caidinha. Curada: feliz."""
    bob = int(math.sin(frame * 0.1 + x * 0.05) * 2)
    if not curada and sintoma == "frio":
        x += int(math.sin(frame * 0.8) * 2)   # tremendo de frio
    y += bob

    corpo = (222, 214, 188) if not curada else (250, 248, 240)
    asa   = tuple(max(0, c - 26) for c in corpo)

    # Sombra
    pygame.draw.ellipse(surf, (30, 82, 24), (x - 40, y + 30, 80, 14))
    # Corpo
    pygame.draw.ellipse(surf, corpo, (x - 42, y - 26, 84, 60))
    pygame.draw.ellipse(surf, (150, 140, 118), (x - 42, y - 26, 84, 60), 2)
    # Rabo
    for i in range(3):
        pygame.draw.ellipse(surf, asa, (x - 58 + i * 5, y - 22 + i * 7, 26, 12))
    # Asa
    pygame.draw.ellipse(surf, asa, (x - 24, y - 10, 40, 26))
    pygame.draw.ellipse(surf, (150, 140, 118), (x - 24, y - 10, 40, 26), 1)

    # Cabeca (doente: mais baixa, caidinha)
    hx = x + 34
    hy = y - 34 if curada else y - 26
    pygame.draw.circle(surf, corpo, (hx, hy), 20)
    pygame.draw.circle(surf, (150, 140, 118), (hx, hy), 20, 2)

    # Crista (doente: caida pro lado)
    if curada:
        pygame.draw.polygon(surf, RED, [
            (hx - 10, hy - 18), (hx - 6, hy - 28), (hx - 2, hy - 19),
            (hx + 2, hy - 30), (hx + 6, hy - 19), (hx + 10, hy - 26), (hx + 12, hy - 16),
        ])
    else:
        pygame.draw.polygon(surf, (200, 90, 90), [
            (hx - 10, hy - 17), (hx - 2, hy - 24), (hx + 4, hy - 17),
            (hx + 12, hy - 21), (hx + 14, hy - 13),
        ])

    # Bico
    pygame.draw.polygon(surf, ORANGE, [
        (hx + 18, hy - 2), (hx + 30, hy + 2), (hx + 18, hy + 6),
    ])

    # Olho
    if curada:
        pygame.draw.circle(surf, BLACK, (hx + 8, hy - 4), 4)
        pygame.draw.circle(surf, WHITE, (hx + 9, hy - 5), 1)
        pygame.draw.circle(surf, (255, 170, 190), (hx + 2, hy + 8), 4)  # bochecha
    else:
        pygame.draw.line(surf, BLACK, (hx + 3, hy - 4), (hx + 13, hy - 2), 3)
        if sintoma == "febre":
            pygame.draw.circle(surf, (240, 120, 100), (hx + 2, hy + 8), 5)

    # Pernas
    for lx in (x - 10, x + 8):
        pygame.draw.line(surf, ORANGE, (lx, y + 32), (lx, y + 44), 3)
        pygame.draw.line(surf, ORANGE, (lx - 4, y + 44), (lx + 5, y + 44), 3)


class Fase3Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog   = DialogBox()
        self.hud      = HUD()
        self.vfx      = VFX()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.rodada   = 1
        self.timer    = TEMPO_MAX
        self.pacientes = []
        self.drag     = None       # {"med": id, "pos": (x, y)}
        self.msg_t    = 0.0
        self.err_t    = 0.0
        self.err_pos  = (0, 0)
        self.tbar     = ProgressBar((SCREEN_W // 2 - 150, 56, 300, 16))
        self.font_lbl = pygame.font.SysFont("Segoe UI", 14, bold=True)
        self.font_msg = pygame.font.SysFont("Segoe UI", 46, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 19, bold=True)
        self._bg       = None   # fundo estatico em cache

    def on_enter(self):
        snd.musica_start()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.rodada   = 1
        self.drag     = None
        self.err_t    = 0.0
        self.vfx.clear()
        self._monta_rodada()
        self.btn_voltar = Button((30, SCREEN_H - 65, 200, 50), "Menu", DARK_GRAY, font_size=22)
        self.dialog.show(DIALOGO_INTRO, callback=self._intro_done)

    def _monta_rodada(self):
        sintomas = random.sample(SINTOMAS, 3)
        self.pacientes = [
            {"pos": GALINHA_POS[i], "sintoma": sintomas[i], "curada": False}
            for i in range(3)
        ]
        self.timer = TEMPO_MAX
        self.hud.set_objective(
            f"Cure as galinhas - Rodada {self.rodada}/{RODADAS}",
            "Fase 3 - Galinhas Doentes")

    def _intro_done(self):
        self.state = "playing"

    def _rect_paciente(self, p):
        x, y = p["pos"]
        return pygame.Rect(x - 62, y - 66, 124, 140)

    # ----------------------------------------------------------------- events
    def handle_event(self, event):
        if self.dialog.handle_event(event):
            return
        if self.btn_voltar.handle_event(event) and self.btn_voltar.clicked:
            self.btn_voltar.reset()
            self.manager.go_to("menu")

        if self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, slot in enumerate(MED_SLOTS):
                    if slot.collidepoint(event.pos):
                        self.drag = {"med": REMEDIOS[i], "pos": event.pos}
                        snd.play('click')
                        break

            elif event.type == pygame.MOUSEMOTION and self.drag:
                self.drag["pos"] = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag:
                self._soltar_remedio(self.drag)
                self.drag = None

        elif self.state == "fail":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._monta_rodada()
                self.state = "playing"

        elif self.state == "complete" and self.complete:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.go_to("fase4")

    def _soltar_remedio(self, drag):
        for p in self.pacientes:
            if not p["curada"] and self._rect_paciente(p).collidepoint(drag["pos"]):
                x, y = p["pos"]
                if CURA[p["sintoma"]] == drag["med"]:
                    p["curada"] = True
                    snd.play('cacarejo')
                    self.vfx.burst(x, y - 30, count=14,
                                   colors=[(255, 120, 160), (255, 170, 200), (255, 220, 230)],
                                   speed=4, size=4, gravity=-30)
                    self._checa_rodada()
                else:
                    snd.play('erro')
                    self.err_t   = 0.7
                    self.err_pos = (x, y - 70)
                return

    def _checa_rodada(self):
        if not all(p["curada"] for p in self.pacientes):
            return
        if self.rodada < RODADAS:
            self.state = "round_ok"
            self.msg_t = 1.6
            snd.play('encaixe')
        else:
            self.state = "done"
            snd.play('fanfarra')
            self.vfx.fireworks(SCREEN_W, SCREEN_H)
            self.dialog.show(DIALOGO_DONE, callback=self._done)

    def _done(self):
        self.complete = True
        self.state    = "complete"

    # ----------------------------------------------------------------- update
    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)
        self.vfx.update(dt)
        self.err_t = max(0.0, self.err_t - dt)

        if self.state == "playing" and not self.dialog.active:
            self.timer -= dt
            if self.timer <= 0:
                self.timer = 0
                self.drag  = None
                self.state = "fail"
                snd.play('erro')
                snd.play('gameover')

        elif self.state == "round_ok":
            self.msg_t -= dt
            if self.msg_t <= 0:
                self.rodada += 1
                self._monta_rodada()
                self.state = "playing"

    # ----------------------------------------------------------------- draw
    def _draw_bg(self, screen):
        # Fundo 100% estatico: desenha uma vez e reusa (performance no celular)
        if self._bg is None:
            self._bg = pygame.Surface((SCREEN_W, SCREEN_H))
            self._render_bg(self._bg)
        screen.blit(self._bg, (0, 0))

    def _render_bg(self, screen):
        w, h = SCREEN_W, SCREEN_H
        # Ceu
        for sy in range(330):
            t = sy / 330
            pygame.draw.line(screen,
                (int(100 + 110 * t), int(160 + 66 * t), int(215 + 25 * t)),
                (0, sy), (w, sy))
        # Sol
        pygame.draw.circle(screen, (255, 235, 140), (1150, 80), 38)
        pygame.draw.circle(screen, (255, 245, 190), (1150, 80), 30)
        # Floresta ao fundo
        morro = [(0, 300), (0, 215), (140, 190), (330, 205), (520, 180),
                 (760, 198), (980, 178), (1180, 196), (w, 186), (w, 300)]
        pygame.draw.polygon(screen, (18, 56, 14), morro)
        for tx in range(-20, w + 50, 56):
            ty = 175 + (tx * 3 % 7) * 4
            pygame.draw.circle(screen, (14 + tx % 5 * 4, 52 + tx % 4 * 6, 12),
                               (tx + 26, ty + 20), 26)
        # Gramado
        pygame.draw.rect(screen, (64, 140, 44), (0, 330, w, h - 330))
        pygame.draw.rect(screen, (76, 154, 52), (0, 330, w, 24))
        for gx in range(0, w, 18):
            pygame.draw.line(screen, (48, 118, 34), (gx, 352), (gx + 3, 344), 1)

        # Galinheiro pronto ao fundo (construido na fase 2)
        gx, gy = 60, 218
        pygame.draw.polygon(screen, (140, 58, 40),
                            [(gx - 12, gy + 42), (gx + 184, gy + 42), (gx + 86, gy)])
        pygame.draw.rect(screen, (150, 104, 54), (gx, gy + 42, 172, 84))
        pygame.draw.rect(screen, (104, 68, 30), (gx, gy + 42, 172, 84), 2)
        pygame.draw.rect(screen, (74, 52, 30), (gx + 14, gy + 50, 60, 40))
        for d in range(0, 100, 8):
            pygame.draw.line(screen, (150, 160, 150), (gx + 14 + d - 20, gy + 90), (gx + 14 + d, gy + 50), 1)
        pygame.draw.rect(screen, (104, 68, 30), (gx + 14, gy + 50, 60, 40), 2)
        pygame.draw.rect(screen, (118, 78, 36), (gx + 96, gy + 62, 34, 64))
        pygame.draw.rect(screen, (84, 54, 24), (gx + 96, gy + 62, 34, 64), 2)

    def _draw_bubble(self, screen, p):
        """Balao de sintoma acima da galinha doente."""
        x, y = p["pos"]
        bw, bh = 84, 78
        bx, by = x - bw // 2, y - 76 - bh
        flt = int(math.sin(self.frame * 0.07 + x) * 3)
        by += flt
        r = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(screen, WHITE, r, border_radius=10)
        pygame.draw.polygon(screen, WHITE,
                            [(x - 8, r.bottom - 2), (x + 8, r.bottom - 2), (x + 2, r.bottom + 12)])
        pygame.draw.rect(screen, (170, 175, 182), r, 2, border_radius=10)
        _draw_sintoma(screen, p["sintoma"], x, by + 30, self.frame)
        t = self.font_lbl.render(NOME_SINTOMA[p["sintoma"]], True, (90, 95, 104))
        screen.blit(t, t.get_rect(center=(x, by + bh - 14)))

    def _draw_bandeja(self, screen):
        pygame.draw.rect(screen, (146, 100, 52), BANDEJA, border_radius=10)
        pygame.draw.rect(screen, (108, 72, 34), BANDEJA, 3, border_radius=10)
        pygame.draw.rect(screen, (168, 120, 66), BANDEJA.inflate(-10, -10), 2, border_radius=8)
        for i, slot in enumerate(MED_SLOTS):
            med   = REMEDIOS[i]
            hover = slot.collidepoint(pygame.mouse.get_pos())
            cor   = (255, 250, 235) if hover else (246, 238, 218)
            pygame.draw.rect(screen, cor, slot, border_radius=8)
            pygame.draw.rect(screen, (188, 158, 110), slot, 2, border_radius=8)
            _draw_remedio(screen, med, slot.centerx, slot.centery - 8)
            t = self.font_lbl.render(NOME_REMEDIO[med], True, (110, 84, 44))
            screen.blit(t, t.get_rect(center=(slot.centerx, slot.bottom - 12)))

    def _draw_timer(self, screen):
        frac = self.timer / TEMPO_MAX
        self.tbar.value = frac
        self.tbar.color = GREEN if frac > 0.5 else (ORANGE if frac > 0.25 else RED)
        self.tbar.draw(screen)
        t = self.font_lbl.render(f"{int(self.timer)}s", True, WHITE)
        ts = self.font_lbl.render(f"{int(self.timer)}s", True, BLACK)
        screen.blit(ts, ts.get_rect(center=(SCREEN_W // 2 + 1, 65)))
        screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 64)))

    def draw(self, screen):
        self._draw_bg(screen)

        # Marina doutora ao lado das pacientes
        spr.draw_marina(screen, 150, 440, self.frame)
        pygame.draw.rect(screen, WHITE, (194, 428, 22, 16), border_radius=3)
        pygame.draw.line(screen, RED, (205, 431), (205, 441), 4)
        pygame.draw.line(screen, RED, (200, 436), (210, 436), 4)

        # Pacientes
        for p in self.pacientes:
            x, y = p["pos"]
            _draw_paciente(screen, x, y, self.frame, p["sintoma"], p["curada"])
            if not p["curada"] and self.state in ("playing", "fail"):
                self._draw_bubble(screen, p)
                # Destaque quando arrastando remedio por cima
                if self.drag and self._rect_paciente(p).collidepoint(self.drag["pos"]):
                    pygame.draw.ellipse(screen, YELLOW, (x - 52, y - 40, 104, 88), 3)

        # X vermelho de remedio errado
        if self.err_t > 0:
            ex, ey = self.err_pos
            a = int(255 * min(1.0, self.err_t / 0.4))
            xs = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.line(xs, (230, 40, 40, a), (6, 6), (38, 38), 8)
            pygame.draw.line(xs, (230, 40, 40, a), (38, 6), (6, 38), 8)
            screen.blit(xs, (ex - 22, ey - 22))

        if self.state in ("playing", "round_ok", "fail"):
            self._draw_bandeja(screen)
            self._draw_timer(screen)

        # Remedio sendo arrastado
        if self.drag:
            mx, my = self.drag["pos"]
            pygame.draw.ellipse(screen, (0, 0, 0, 0), (mx - 26, my + 18, 52, 8))
            _draw_remedio(screen, self.drag["med"], mx, my)

        # Mensagem entre rodadas
        if self.state == "round_ok":
            t  = self.font_msg.render("GALINHAS CURADAS!", True, YELLOW)
            ts = self.font_msg.render("GALINHAS CURADAS!", True, BLACK)
            screen.blit(ts, ts.get_rect(center=(SCREEN_W // 2 + 2, 262)))
            screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 260)))

        self.vfx.draw(screen)
        self.hud.draw(screen)
        self.dialog.draw(screen)
        self.btn_voltar.draw(screen)

        if self.state == "fail":
            self._draw_fail(screen)
        if self.state == "complete" and self.complete:
            self._draw_complete(screen)

    def _draw_fail(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((40, 0, 0, 150))
        screen.blit(ov, (0, 0))
        t1 = self.font_msg.render("O TEMPO ACABOU!", True, (255, 120, 100))
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 40)))
        t2 = self.font_hint.render("Clique para tentar a rodada de novo", True, WHITE)
        if (self.frame // 35) % 2 == 0:
            screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20)))

    def _draw_complete(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        screen.blit(ov, (0, 0))
        fb = pygame.font.SysFont("Segoe UI", 58, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 24)
        t1 = fb.render("FASE 3 COMPLETA!", True, YELLOW)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60)))
        t2 = fs.render("Doutora Marina curou todas as galinhas!", True, WHITE)
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para continuar ->", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 55)))
        spr.draw_ramona(screen, SCREEN_W // 2, SCREEN_H // 2 + 160, self.frame)
