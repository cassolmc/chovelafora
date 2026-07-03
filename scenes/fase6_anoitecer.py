"""
Fase 6 - Anoitecer no Sitio
Visao de cima: o ceu escurece (laranja -> roxo -> preto, sem numero) e a
Marina precisa levar as 8 galinhas para dentro do galinheiro antes de
escurecer de vez. Cada galinha tem um comportamento:
  Ramona       - segue a Marina quando ela chega perto
  White        - galo ajudante: empurra as outras em direcao ao portao
  Zebrinha     - do contra: corre na direcao da Marina, nao para longe
  As 3 Irmas   - andam juntas, mas param toda hora
  Bunda Pelada - demora a reagir e depois dispara pra longe
  Bicadona     - matriarca tranquila, se toca vai andando
"""
import pygame
import math
import random
from engine.scene_manager import Scene
from engine.dialog import DialogBox
from engine.ui import Button, HUD
from engine.vfx import VFX
import engine.sounds as snd
from constants import *
import characters.sprites as spr

DURACAO = 90.0   # segundos ate escurecer total (so visual, sem numero)

DIALOGO_INTRO = [
    ("Papai",    "Ta anoitecendo, Marina! Leva as galinhas pro galinheiro!"),
    ("Narrador", "Chegue perto para tocar cada galinha. Cada uma tem seu jeito!"),
]

DIALOGO_DONE = [
    ("Papai",    "Voce e uma verdadeira protetora das galinhas!"),
    ("Ramona",   "Co-co-COROCO!!!"),
    ("Narrador", "FIM... por enquanto! Continuem cuidando das galinhas!"),
]

# Area util do quintal e interior do galinheiro (cercado, entrada embaixo)
YARD = pygame.Rect(34, 64, SCREEN_W - 68, SCREEN_H - 110)
RUN  = pygame.Rect(506, 118, 268, 88)
GATE = (RUN.centerx, RUN.bottom + 14)   # ponto do portao (para onde o White guia)

# nome, tipo, cor do corpo, cor da crista, posicao inicial
GALINHAS_DEF = [
    ("Ramona",       "ramona",   (42, 38, 46),    WHITE,           (210, 500)),
    ("White",        "white",    (250, 248, 240), RED,             (640, 430)),
    ("Zebrinha",     "zebrinha", (182, 184, 190), (120, 120, 126), (1010, 300)),
    ("Irma",         "irma",     (135, 135, 142), RED,             (350, 380)),
    ("Irma",         "irma",     (128, 128, 134), RED,             (405, 425)),
    ("Irma",         "irma",     (142, 142, 148), RED,             (330, 445)),
    ("Bunda Pelada", "bunda",    (172, 86, 42),   RED,             (1180, 528)),
    ("Bicadona",     "bicadona", (246, 243, 235), RED,             (150, 300)),
]

# Keyframes do anoitecer: (t, cor, alpha)
CEU = [
    (0.00, (255, 170, 80),  25),
    (0.35, (215, 100, 70),  70),
    (0.60, (115, 55, 135),  125),
    (0.85, (35, 25, 70),    185),
    (1.00, (8, 6, 22),      232),
]


def _lerp(a, b, t):
    return a + (b - a) * t


def _cor_escuridao(t):
    t = max(0.0, min(1.0, t))
    for (t0, c0, a0), (t1, c1, a1) in zip(CEU, CEU[1:]):
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            cor = tuple(int(_lerp(c0[k], c1[k], f)) for k in range(3))
            return cor, int(_lerp(a0, a1, f))
    return CEU[-1][1], CEU[-1][2]


class Fase6Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog   = DialogBox()
        self.hud      = HUD()
        self.vfx      = VFX()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.font_lbl  = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.font_msg  = pygame.font.SysFont("Segoe UI", 46, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 19, bold=True)
        self.vagalumes = [(random.randint(60, 1220), random.randint(100, 540),
                           random.uniform(0, 6.28), random.uniform(0.6, 1.4))
                          for _ in range(9)]
        self._bg = None   # quintal estatico em cache

    def on_enter(self):
        snd.musica_start()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.vfx.clear()
        self._reinicia()
        self.btn_menu = Button((SCREEN_W - 130, 52, 110, 36), "Menu", DARK_GRAY, font_size=18)
        self.dialog.show(DIALOGO_INTRO, callback=self._intro_done)

    def _reinicia(self):
        self.t_escuro = 0.0
        self.t_total  = 0.0
        self.marina_x = 640.0
        self.marina_y = 520.0
        self.galinhas = []
        for nome, tipo, cor, crista, (x, y) in GALINHAS_DEF:
            self.galinhas.append({
                "nome": nome, "tipo": tipo, "cor": cor, "crista": crista,
                "x": float(x), "y": float(y), "in": False,
                "dir": (0.0, 0.0), "wt": 0.0,             # passeio aleatorio
                "off": random.uniform(0, 2.2),            # fase das irmas
                "react": 0.0, "burst": 0.0, "bdir": (0, 0),  # bunda pelada
                "ldir": (0.0, 0.0),                       # zebrinha
                "esc": (0.0, 0.0), "esc_t": 0.0,          # fuga do canto
            })
        self._atualiza_hud()

    def _atualiza_hud(self):
        n = sum(g["in"] for g in self.galinhas)
        self.hud.set_objective(f"Galinhas no galinheiro: {n}/8", "Fase 6 - Anoitecer")

    def _intro_done(self):
        self.state = "playing"

    # ----------------------------------------------------------------- events
    def handle_event(self, event):
        if self.dialog.handle_event(event):
            return
        if self.btn_menu.handle_event(event) and self.btn_menu.clicked:
            self.btn_menu.reset()
            self.manager.go_to("menu")

        if self.state == "fail":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._reinicia()
                self.state = "playing"
        elif self.state == "complete" and self.complete:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.go_to("menu")

    # ----------------------------------------------------------------- update
    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)
        self.vfx.update(dt)

        if self.state != "playing" or self.dialog.active:
            return

        self.t_total  += dt
        self.t_escuro += dt / DURACAO
        if self.t_escuro >= 1.0:
            self.t_escuro = 1.0
            self.state = "fail"
            snd.play('erro')
            snd.play('gameover')
            return

        # Marina: setas/WASD, ou segurar o botao do mouse para andar ate ele
        keys = pygame.key.get_pressed()
        sp = 265 * dt
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.marina_x -= sp
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.marina_x += sp
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.marina_y -= sp
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.marina_y += sp
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - self.marina_x, my - self.marina_y
            d = math.hypot(dx, dy)
            if d > 8:
                self.marina_x += dx / d * sp
                self.marina_y += dy / d * sp
        self.marina_x = max(YARD.left, min(float(YARD.right), self.marina_x))
        self.marina_y = max(YARD.top, min(float(YARD.bottom), self.marina_y))

        for g in self.galinhas:
            self._update_galinha(g, dt)

    def _white(self):
        return next(g for g in self.galinhas if g["tipo"] == "white")

    def _alvo_white(self, white):
        """White mira o ponto ATRAS da galinha solta mais proxima (em relacao
        ao portao), para empurra-la na direcao certa. Ele nao encara a Zebrinha."""
        soltas = [g for g in self.galinhas
                  if not g["in"] and g["tipo"] in ("irma", "bunda", "bicadona")]
        if not soltas:
            return (RUN.centerx, RUN.centery)   # missao cumprida: entra tambem
        alvo = min(soltas, key=lambda g: math.hypot(g["x"] - white["x"], g["y"] - white["y"]))
        dx, dy = alvo["x"] - GATE[0], alvo["y"] - GATE[1]
        d = math.hypot(dx, dy) or 1
        return (alvo["x"] + dx / d * 46, alvo["y"] + dy / d * 46)

    def _update_galinha(self, g, dt):
        # Dentro do galinheiro: so cisca por ali
        if g["in"]:
            g["wt"] -= dt
            if g["wt"] <= 0:
                ang = random.uniform(0, 2 * math.pi)
                g["dir"] = (math.cos(ang), math.sin(ang))
                g["wt"] = random.uniform(0.8, 2.2)
            g["x"] += g["dir"][0] * 16 * dt
            g["y"] += g["dir"][1] * 16 * dt
            g["x"] = max(RUN.left + 14, min(RUN.right - 14, g["x"]))
            g["y"] = max(RUN.top + 12, min(RUN.bottom - 10, g["y"]))
            return

        mdx, mdy = g["x"] - self.marina_x, g["y"] - self.marina_y
        d = math.hypot(mdx, mdy) or 1.0
        tipo = g["tipo"]
        vx = vy = 0.0
        sp = 0.0

        if tipo == "ramona":
            # Segue a Marina de perto
            if d < 175 and d > 36:
                vx, vy = -mdx / d, -mdy / d
                sp = 155

        elif tipo == "white":
            ax, ay = self._alvo_white(g)
            adx, ady = ax - g["x"], ay - g["y"]
            ad = math.hypot(adx, ady) or 1
            if ad > 8:
                vx, vy = adx / ad, ady / ad
                sp = 95
            if d < 65:   # Marina colada: ele tambem pode ser tocado
                vx, vy = mdx / d, mdy / d
                sp = 125

        elif tipo == "zebrinha":
            # Do contra: corre NA DIRECAO da Marina (e passa reto)
            if d < 135:
                if d > 28:
                    g["ldir"] = (-mdx / d, -mdy / d)
                vx, vy = g["ldir"]
                sp = 118

        elif tipo == "irma":
            fase = (self.t_total + g["off"]) % 2.2
            pausada = fase > 1.0 and d > 55
            if not pausada:
                if d < 125:
                    vx, vy = mdx / d, mdy / d
                    sp = 102
                # Coesao: puxa em direcao as outras irmas
                irmas = [o for o in self.galinhas if o["tipo"] == "irma" and o is not g and not o["in"]]
                if irmas and sp > 0:
                    cx = sum(o["x"] for o in irmas) / len(irmas)
                    cy = sum(o["y"] for o in irmas) / len(irmas)
                    cd = math.hypot(cx - g["x"], cy - g["y"]) or 1
                    vx += (cx - g["x"]) / cd * 0.55
                    vy += (cy - g["y"]) / cd * 0.55
                    n = math.hypot(vx, vy) or 1
                    vx, vy = vx / n, vy / n

        elif tipo == "bunda":
            # Demora a reagir, depois dispara longe
            if d < 135:
                g["react"] += dt
            else:
                g["react"] = max(0.0, g["react"] - dt * 2)
            if g["react"] > 0.7:
                g["burst"] = 1.15
                g["bdir"]  = (mdx / d, mdy / d)
                g["react"] = 0.0
            if g["burst"] > 0:
                g["burst"] -= dt
                vx, vy = g["bdir"]
                sp = 150

        else:  # bicadona
            if d < 115:
                vx, vy = mdx / d, mdy / d
                sp = 85

        # O White tambem empurra as tranquilas (aproxima por tras do portao)
        if sp == 0 and tipo in ("irma", "bunda", "bicadona"):
            w = self._white()
            if not w["in"]:
                wdx, wdy = g["x"] - w["x"], g["y"] - w["y"]
                wd = math.hypot(wdx, wdy) or 1
                if wd < 82:
                    vx, vy = wdx / wd, wdy / wd
                    sp = 80

        # Passeio leve quando nada acontece
        if sp == 0:
            g["wt"] -= dt
            if g["wt"] <= 0:
                ang = random.uniform(0, 2 * math.pi)
                g["dir"] = (math.cos(ang), math.sin(ang))
                g["wt"] = random.uniform(1.0, 2.6)
            vx, vy = g["dir"]
            sp = 15

        # Perto da cerca a galinha DESLIZA: corta o componente da fuga que
        # aponta para fora do quintal. Se nao sobra nada (encurralada no
        # canto ou fugindo reto contra a cerca), ela se compromete com uma
        # corrida lateral ao longo da parede em vez de travar no clamp.
        g["esc_t"] = max(0.0, g["esc_t"] - dt)
        if sp > 0:
            m = 26.0
            if (g["x"] < YARD.left + m and vx < 0) or (g["x"] > YARD.right - m and vx > 0):
                vx = 0.0
            if (g["y"] < YARD.top + m and vy < 0) or (g["y"] > YARD.bottom - m and vy > 0):
                vy = 0.0
            n = math.hypot(vx, vy)
            perto = (g["x"] < YARD.left + m or g["x"] > YARD.right - m or
                     g["y"] < YARD.top + m or g["y"] > YARD.bottom - m)

            if g["esc_t"] > 0:
                vx, vy = g["esc"]
                sp *= 1.25   # corrida de panico
            elif n < 0.35 and perto:
                # Direcoes ao longo da parede que nao apontam para outra cerca
                cands = [c for c in ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0))
                         if not (c[0] > 0 and g["x"] > YARD.right - m)
                         and not (c[0] < 0 and g["x"] < YARD.left + m)
                         and not (c[1] > 0 and g["y"] > YARD.bottom - m)
                         and not (c[1] < 0 and g["y"] < YARD.top + m)]
                if cands:
                    ax, ay = mdx / d, mdy / d   # direcao para longe da Marina
                    ex, ey = g["esc"]
                    # Persistencia: prefere continuar a fuga anterior a voltar
                    g["esc"] = max(cands,
                                   key=lambda c: c[0] * ax + c[1] * ay
                                   + (0.5 if (c[0], c[1]) == (ex, ey) else 0.0)
                                   + random.uniform(0, 0.1))
                    g["esc_t"] = 1.0
                    vx, vy = g["esc"]
                    sp *= 1.25
            elif n > 0.001:
                vx, vy = vx / n, vy / n

        g["x"] += vx * sp * dt
        g["y"] += vy * sp * dt
        g["x"] = max(YARD.left, min(float(YARD.right), g["x"]))
        g["y"] = max(YARD.top, min(float(YARD.bottom), g["y"]))

        # Entrou no galinheiro!
        if RUN.collidepoint(g["x"], g["y"]):
            g["in"] = True
            snd.play('cacarejo')
            self.vfx.stars(g["x"], g["y"] - 10, color=(255, 250, 160))
            self._atualiza_hud()
            if all(gg["in"] for gg in self.galinhas):
                self.state = "win_dialog"
                snd.play('complete')
                self.vfx.fireworks(SCREEN_W, SCREEN_H)
                self.dialog.show(DIALOGO_DONE, callback=self._done)

    def _done(self):
        self.complete = True
        self.state    = "complete"

    # ----------------------------------------------------------------- draw
    def _draw_quintal(self, screen):
        # Quintal 100% estatico: desenha uma vez e reusa (performance no celular)
        if self._bg is None:
            self._bg = pygame.Surface((SCREEN_W, SCREEN_H))
            self._render_quintal(self._bg)
        screen.blit(self._bg, (0, 0))

    def _render_quintal(self, screen):
        w, h = SCREEN_W, SCREEN_H
        # Gramado visto de cima, com faixas de corte
        screen.fill((72, 148, 50))
        for fy in range(0, h, 52):
            if (fy // 52) % 2 == 0:
                pygame.draw.rect(screen, (66, 138, 46), (0, fy, w, 52))
        # Tufos e florzinhas
        for gx in range(20, w, 46):
            gy = 70 + (gx * 13 % (h - 120))
            pygame.draw.line(screen, (52, 118, 38), (gx, gy), (gx + 3, gy - 6), 2)
            pygame.draw.line(screen, (52, 118, 38), (gx + 5, gy), (gx + 6, gy - 5), 2)
        for fx in range(60, w, 170):
            fy = 100 + (fx * 7 % (h - 160))
            pygame.draw.circle(screen, WHITE, (fx, fy), 3)
            pygame.draw.circle(screen, YELLOW, (fx, fy), 1)

        # Caminho de terra ate o portao
        pygame.draw.rect(screen, (188, 148, 96), (RUN.centerx - 34, RUN.bottom, 68, h - RUN.bottom - 20), border_radius=18)
        for py in range(RUN.bottom + 16, h - 40, 34):
            pygame.draw.ellipse(screen, (170, 130, 82), (RUN.centerx - 20 + (py % 3) * 8, py, 22, 9))

        # Arbustos nas bordas do quintal
        for bx in range(30, w, 120):
            pygame.draw.circle(screen, (24, 88, 24), (bx, 54), 22)
            pygame.draw.circle(screen, (30, 104, 30), (bx + 14, 50), 16)
        for bx in range(80, w, 150):
            pygame.draw.circle(screen, (24, 88, 24), (bx, h - 16), 24)

        # ---- Galinheiro (de cima): telhado + cercado com entrada embaixo
        # Piso do cercado
        piso = RUN.inflate(16, 12)
        pygame.draw.rect(screen, (176, 136, 86), piso, border_radius=6)
        for sx in range(piso.x + 10, piso.right - 14, 30):
            sy = piso.y + 14 + (sx % 40)
            pygame.draw.line(screen, (216, 182, 104), (sx, sy + 42), (sx + 12, sy + 36), 2)
        # Telhado da casinha (visto de cima)
        telhado = pygame.Rect(RUN.x - 6, 54, RUN.width + 12, 62)
        pygame.draw.rect(screen, (150, 62, 44), telhado, border_radius=4)
        pygame.draw.rect(screen, (112, 44, 30), telhado, 3, border_radius=4)
        pygame.draw.line(screen, (112, 44, 30), (telhado.x + 4, telhado.centery), (telhado.right - 4, telhado.centery), 3)
        for tx in range(telhado.x + 12, telhado.right - 6, 16):
            pygame.draw.line(screen, (170, 82, 60), (tx, telhado.y + 4), (tx, telhado.bottom - 4), 1)
        t = self.font_lbl.render("GALINHEIRO", True, (255, 230, 200))
        screen.blit(t, t.get_rect(center=(telhado.centerx, telhado.centery + 1)))

        # Cerca: laterais + fundo, entrada aberta embaixo no centro
        cor_p, cor_r = (124, 84, 40), (154, 108, 56)
        def poste(px, py):
            pygame.draw.rect(screen, cor_p, (px - 3, py - 3, 7, 7), border_radius=2)
        for py in range(RUN.top - 4, RUN.bottom + 6, 22):
            poste(piso.left, py); poste(piso.right, py)
        pygame.draw.line(screen, cor_r, (piso.left, RUN.top - 4), (piso.left, RUN.bottom + 4), 3)
        pygame.draw.line(screen, cor_r, (piso.right, RUN.top - 4), (piso.right, RUN.bottom + 4), 3)
        # Trecho de cerca embaixo, deixando o portao aberto no centro
        gate_w = 74
        for x1, x2 in ((piso.left, RUN.centerx - gate_w // 2), (RUN.centerx + gate_w // 2, piso.right)):
            pygame.draw.line(screen, cor_r, (x1, piso.bottom), (x2, piso.bottom), 3)
            for px in range(x1, x2, 22):
                poste(px, piso.bottom)
        poste(RUN.centerx - gate_w // 2, piso.bottom)
        poste(RUN.centerx + gate_w // 2, piso.bottom)

    def _draw_escuridao(self, screen):
        cor, alpha = _cor_escuridao(self.t_escuro)
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((*cor, alpha))
        screen.blit(ov, (0, 0))

        # Luzinha em volta da Marina quando ja esta bem escuro
        if self.t_escuro > 0.5:
            a = int(min(1.0, (self.t_escuro - 0.5) / 0.3) * 46)
            luz = pygame.Surface((190, 190), pygame.SRCALPHA)
            pygame.draw.circle(luz, (255, 230, 140, a), (95, 95), 95)
            pygame.draw.circle(luz, (255, 240, 180, a), (95, 95), 55)
            screen.blit(luz, (int(self.marina_x) - 95, int(self.marina_y) - 95))

        # Vagalumes aparecem no crepusculo
        if self.t_escuro > 0.42:
            a = int(min(1.0, (self.t_escuro - 0.42) / 0.25) * 255)
            for bx, by, ph, vel in self.vagalumes:
                fx = bx + math.sin(self.t_total * vel + ph) * 46
                fy = by + math.cos(self.t_total * vel * 0.7 + ph) * 26
                pulso = 0.5 + 0.5 * math.sin(self.t_total * 3 + ph * 5)
                s = pygame.Surface((14, 14), pygame.SRCALPHA)
                pygame.draw.circle(s, (250, 255, 130, int(a * 0.25 * pulso)), (7, 7), 7)
                pygame.draw.circle(s, (250, 255, 150, int(a * pulso)), (7, 7), 2)
                screen.blit(s, (int(fx) - 7, int(fy) - 7))

    def draw(self, screen):
        self._draw_quintal(screen)

        # Personagens ordenados por Y (profundidade)
        atores = [("marina", self.marina_y)] + [(g, g["y"]) for g in self.galinhas]
        atores.sort(key=lambda a: a[1])
        for ator, _ in atores:
            if ator == "marina":
                spr.draw_marina(screen, int(self.marina_x), int(self.marina_y) - 24, self.frame)
            else:
                g = ator
                spr.draw_galinha(screen, int(g["x"]), int(g["y"]),
                                 g["cor"], g["crista"], self.frame,
                                 small=(g["tipo"] in ("ramona", "zebrinha")))
                if not g["in"]:
                    t  = self.font_lbl.render(g["nome"], True, WHITE)
                    ts = self.font_lbl.render(g["nome"], True, BLACK)
                    screen.blit(ts, ts.get_rect(center=(int(g["x"]) + 1, int(g["y"]) - 25)))
                    screen.blit(t, t.get_rect(center=(int(g["x"]), int(g["y"]) - 26)))

        self._draw_escuridao(screen)
        self.vfx.draw(screen)
        self.hud.draw(screen)
        self.dialog.draw(screen)
        self.btn_menu.draw(screen)

        if self.state == "fail":
            self._draw_fail(screen)
        if self.state == "complete" and self.complete:
            self._draw_complete(screen)

    def _draw_fail(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((10, 5, 30, 165))
        screen.blit(ov, (0, 0))
        n = sum(g["in"] for g in self.galinhas)
        t1 = self.font_msg.render("ESCURECEU!", True, (170, 150, 255))
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 55)))
        t2 = self.font_hint.render(
            f"So {n} de 8 galinhas entraram. Elas ficaram com medo do escuro!", True, WHITE)
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 5)))
        if (self.frame // 35) % 2 == 0:
            t3 = self.font_hint.render("Clique para tentar de novo", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50)))

    def _draw_complete(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        screen.blit(ov, (0, 0))
        for i in range(14):
            ang = (self.frame * 2 + i * (360 // 14)) % 360
            r   = math.radians(ang)
            sx  = SCREEN_W // 2 + int(math.cos(r) * 220)
            sy  = SCREEN_H // 2 + int(math.sin(r) * 110)
            pygame.draw.circle(screen, YELLOW, (sx, sy), 7)
        pygame.draw.rect(screen, (22, 72, 22),
                         (SCREEN_W // 2 - 370, SCREEN_H // 2 - 120, 740, 255), border_radius=18)
        pygame.draw.rect(screen, (78, 215, 78),
                         (SCREEN_W // 2 - 370, SCREEN_H // 2 - 120, 740, 255), 3, border_radius=18)
        fb = pygame.font.SysFont("Segoe UI", 56, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 26)
        t1 = fb.render("FASE 6 COMPLETA!", True, YELLOW)
        t2 = fs.render("Todas as galinhas dormem seguras. FIM... por enquanto!", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 62)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para voltar ao menu", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 56)))
        spr.draw_marina(screen, SCREEN_W // 2 - 50, SCREEN_H // 2 + 175, self.frame)
        spr.draw_ramona(screen, SCREEN_W // 2 + 40, SCREEN_H // 2 + 170, self.frame)
