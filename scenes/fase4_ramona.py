"""
Fase 4 - Achar a Ramona
A Ramona se perdeu na floresta! Marina entra no labirinto de arvores,
arbustos e pedras para achar ela antes do tempo acabar. A Grazi vai
junto ajudando. Cogumelos magicos dao tempo extra. Sem inimigos.
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

TEMPO_MAX   = 60.0
BONUS_TEMPO = 8.0

DIALOGO_INTRO = [
    ("Marina",   "A Ramona sumiu! Ela entrou na floresta!"),
    ("Grazi",    "Eu ajudo voce a achar ela, Marina!"),
    ("Narrador", "Ache a Ramona no labirinto antes do tempo acabar!"),
]

DIALOGO_DONE = [
    ("Ramona", "Co co co!"),
    ("Grazi",  "A gente achou ela!"),
]

# Labirinto: '#' = parede (arvore/arbusto/pedra), '.' = caminho,
# 'M' = entrada da Marina, 'R' = Ramona, 'C' = cogumelo (+tempo).
# Gerado por recursive backtracker + 3 atalhos; solvabilidade coberta
# por teste de BFS.
MAPA = [
    "###################",
    "#.............#..R#",
    "#.###########.#.#.#",
    "#.....#.....#...#.#",
    "#.###.#.#.#.#####.#",
    "#C..#...#.#.......#",
    "#..####.#.#########",
    "#M......#.C.......#",
    "###################",
]
CELL = 60
OX   = (SCREEN_W - len(MAPA[0]) * CELL) // 2
OY   = 52
RAIO = 14   # raio de colisao da Marina


def _celula_centro(col, row):
    return (OX + col * CELL + CELL // 2, OY + row * CELL + CELL // 2)


def _draw_grazi(surf, x, y, frame=0):
    """Grazi: cabelo castanho preso, vestido verde (ajudante da Marina)."""
    sw = int(math.sin(frame * 0.12) * 3)
    # Sombra
    pygame.draw.ellipse(surf, (12, 40, 10), (x - 14, y + 38, 28, 8))
    # Vestido
    pygame.draw.polygon(surf, (60, 150, 90), [
        (x - 4, y - 2), (x + 4, y - 2), (x + 13, y + 26), (x - 13, y + 26)])
    pygame.draw.polygon(surf, (40, 110, 65), [
        (x - 4, y - 2), (x + 4, y - 2), (x + 13, y + 26), (x - 13, y + 26)], 1)
    # Bracos
    pygame.draw.line(surf, SKIN, (x - 5, y + 3), (x - 12, y + 12 + sw), 3)
    pygame.draw.line(surf, SKIN, (x + 5, y + 3), (x + 12, y + 12 - sw), 3)
    # Cabeca
    pygame.draw.circle(surf, SKIN, (x, y - 12), 10)
    # Cabelo castanho com coque
    pygame.draw.arc(surf, (94, 60, 30), (x - 11, y - 24, 22, 20), 0, math.pi, 8)
    pygame.draw.circle(surf, (94, 60, 30), (x + 9, y - 20), 5)
    # Olhos e sorriso
    pygame.draw.circle(surf, BLACK, (x - 3, y - 13), 1)
    pygame.draw.circle(surf, BLACK, (x + 3, y - 13), 1)
    pygame.draw.arc(surf, (150, 90, 80), (x - 4, y - 11, 8, 6), math.pi * 1.1, math.pi * 1.9, 1)
    # Pernas
    pygame.draw.line(surf, SKIN, (x - 5, y + 26), (x - 5, y + 36), 3)
    pygame.draw.line(surf, SKIN, (x + 5, y + 26), (x + 5, y + 36), 3)


def _draw_cogumelo(surf, x, y, frame=0):
    bob = int(math.sin(frame * 0.1 + x) * 2)
    y += bob
    pygame.draw.rect(surf, (238, 228, 205), (x - 4, y - 2, 8, 12), border_radius=3)
    pygame.draw.ellipse(surf, (210, 55, 45), (x - 12, y - 14, 24, 15))
    pygame.draw.ellipse(surf, (160, 35, 30), (x - 12, y - 14, 24, 15), 2)
    for dx, dy in ((-6, -8), (2, -11), (6, -6)):
        pygame.draw.circle(surf, WHITE, (x + dx, y + dy), 2)


class Fase4Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog   = DialogBox()
        self.hud      = HUD()
        self.vfx      = VFX()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.tbar     = ProgressBar((SCREEN_W // 2 - 150, 56, 300, 16))
        self.font_lbl  = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_msg  = pygame.font.SysFont("Segoe UI", 46, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 19, bold=True)
        self._bg      = None   # labirinto estatico em cache
        self.textos   = []     # [x, y, txt, cor, t]

        # Posicoes fixas do mapa
        self.paredes = []
        self.ini     = (0, 0)
        self.ramona  = (0, 0)
        self.cogus_0 = []
        for r, linha in enumerate(MAPA):
            for c, ch in enumerate(linha):
                if ch == "#":
                    self.paredes.append(pygame.Rect(OX + c * CELL, OY + r * CELL, CELL, CELL))
                elif ch == "M":
                    self.ini = _celula_centro(c, r)
                elif ch == "R":
                    self.ramona = _celula_centro(c, r)
                elif ch == "C":
                    self.cogus_0.append(_celula_centro(c, r))

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
        self.timer    = TEMPO_MAX
        self.mx, self.my = float(self.ini[0]), float(self.ini[1])
        self.gx, self.gy = self.mx - 34.0, self.my + 6.0   # Grazi ao lado
        self.cogus    = list(self.cogus_0)
        self.avisou   = False   # Grazi ja avisou do cacarejo?
        self.aviso_t  = 0.0
        self.textos   = []
        self.hud.set_objective("Ache a Ramona na floresta!", "Fase 4 - Achar a Ramona")

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
                self.manager.go_to("fase5")

    # ----------------------------------------------------------------- fisica
    def _colide(self, x, y):
        bb = pygame.Rect(int(x) - RAIO, int(y) - RAIO, RAIO * 2, RAIO * 2)
        for p in self.paredes:
            if p.colliderect(bb):
                return True
        return False

    def _move(self, dx, dy):
        """Movimento com colisao por eixo (desliza nas paredes).
        Subdividido em passos de ate ~10px: um frame lento (comum no
        celular) nao pode atravessar parede por tunelamento."""
        passos = max(1, int(max(abs(dx), abs(dy)) / 10) + 1)
        sx, sy = dx / passos, dy / passos
        for _ in range(passos):
            if sx and not self._colide(self.mx + sx, self.my):
                self.mx += sx
            if sy and not self._colide(self.mx, self.my + sy):
                self.my += sy

    # ----------------------------------------------------------------- update
    def _flutua(self, x, y, txt, cor):
        self.textos.append([float(x), float(y), txt, cor, 1.0])

    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)
        self.vfx.update(dt)
        self.aviso_t = max(0.0, self.aviso_t - dt)
        for t in self.textos:
            t[1] -= 40 * dt
            t[4] -= dt
        self.textos = [t for t in self.textos if t[4] > 0]

        if self.state != "playing" or self.dialog.active:
            return

        # Timer
        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0
            self.state = "fail"
            snd.play('erro')
            snd.play('gameover')
            return

        # Marina: setas/WASD ou segurar o dedo/mouse (anda ate o ponto)
        sp = 210 * dt
        keys = pygame.key.get_pressed()
        dx = dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= sp
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += sp
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= sp
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += sp
        if not dx and not dy and pygame.mouse.get_pressed()[0]:
            px, py = pygame.mouse.get_pos()
            ddx, ddy = px - self.mx, py - self.my
            d = math.hypot(ddx, ddy)
            if d > 10:
                dx, dy = ddx / d * sp, ddy / d * sp
        self._move(dx, dy)

        # Grazi segue a Marina
        gdx, gdy = self.mx - self.gx, self.my - self.gy
        gd = math.hypot(gdx, gdy)
        if gd > 52:
            gsp = 200 * dt
            nx, ny = self.gx + gdx / gd * gsp, self.gy + gdy / gd * gsp
            self.gx, self.gy = nx, ny   # a Grazi "conhece o mato": nao trava

        # Cogumelos: tempo extra
        for c in list(self.cogus):
            if math.hypot(c[0] - self.mx, c[1] - self.my) < 30:
                self.cogus.remove(c)
                self.timer += BONUS_TEMPO
                snd.play('ding')
                self.vfx.stars(c[0], c[1], color=(255, 190, 190))
                self._flutua(c[0], c[1] - 18, f"+{int(BONUS_TEMPO)}s", (140, 255, 140))

        # Perto da Ramona: Grazi avisa (uma vez)
        drx = math.hypot(self.ramona[0] - self.mx, self.ramona[1] - self.my)
        if drx < 170 and not self.avisou:
            self.avisou  = True
            self.aviso_t = 3.5
            snd.play('cacarejo')

        # Achou!
        if drx < 40:
            self.state = "done"
            snd.play('complete')
            self.vfx.fireworks(SCREEN_W, SCREEN_H)
            self.dialog.show(DIALOGO_DONE, callback=self._done)

    def _done(self):
        self.complete = True
        self.state    = "complete"

    # ----------------------------------------------------------------- draw
    def _render_bg(self, screen):
        """Chao de floresta + paredes do labirinto (estatico, em cache)."""
        w, h = SCREEN_W, SCREEN_H
        screen.fill((24, 58, 20))
        # Folhas caidas e graminhas
        for lx in range(10, w, 42):
            ly = (lx * 13) % h
            cor = ((30, 74, 22), (36, 84, 26), (28, 66, 20))[lx % 3]
            pygame.draw.ellipse(screen, cor, (lx, ly, 13, 7))
        for gx in range(0, w, 26):
            gy = (gx * 7) % h
            pygame.draw.line(screen, (40, 96, 30), (gx, gy), (gx + 3, gy - 7), 2)
        # Trilha de terra nas celulas do caminho
        for r, linha in enumerate(MAPA):
            for c, ch in enumerate(linha):
                if ch != "#":
                    pygame.draw.rect(screen, (52, 88, 36),
                                     (OX + c * CELL + 2, OY + r * CELL + 2, CELL - 4, CELL - 4),
                                     border_radius=8)
        # Paredes: arvores, arbustos e pedras (variedade deterministica)
        for r, linha in enumerate(MAPA):
            for c, ch in enumerate(linha):
                if ch != "#":
                    continue
                x = OX + c * CELL + CELL // 2
                y = OY + r * CELL + CELL // 2
                tipo = (r * 7 + c * 13) % 5
                if tipo < 2:      # arvore
                    pygame.draw.rect(screen, (66, 40, 16), (x - 5, y, 10, CELL // 2))
                    pygame.draw.circle(screen, (16, 68, 14), (x, y - 8), 26)
                    pygame.draw.circle(screen, (22, 88, 20), (x - 6, y - 14), 18)
                elif tipo < 4:    # arbusto
                    pygame.draw.ellipse(screen, (14, 76, 14), (x - 27, y - 16, 54, 42))
                    pygame.draw.ellipse(screen, (22, 100, 22), (x - 20, y - 24, 40, 34))
                else:             # pedra
                    pygame.draw.polygon(screen, (112, 116, 122), [
                        (x - 22, y + 22), (x - 26, y - 2), (x - 8, y - 20),
                        (x + 14, y - 16), (x + 24, y + 6), (x + 18, y + 22)])
                    pygame.draw.polygon(screen, (86, 90, 96), [
                        (x - 22, y + 22), (x - 26, y - 2), (x - 8, y - 20),
                        (x + 14, y - 16), (x + 24, y + 6), (x + 18, y + 22)], 2)
                    pygame.draw.line(screen, (140, 144, 150), (x - 14, y - 8), (x + 2, y - 12), 2)
        # Placa da entrada
        ex, ey = self.ini
        pygame.draw.rect(screen, (110, 74, 34), (ex - 3, ey + 30, 6, 16))
        pygame.draw.rect(screen, (150, 108, 56), (ex - 30, ey + 20, 60, 16), border_radius=3)
        t = self.font_lbl.render("ENTRADA", True, (70, 44, 16))
        screen.blit(t, t.get_rect(center=(ex, ey + 28)))

    def _draw_bubble_grazi(self, screen):
        """Balaozinho da Grazi avisando do cacarejo (nao pausa o jogo)."""
        gx, gy = int(self.gx), int(self.gy)
        txt = "Ouvi um cacarejo perto!"
        t   = self.font_lbl.render(txt, True, (60, 60, 66))
        r   = t.get_rect(center=(gx, gy - 46)).inflate(16, 10)
        r.left  = max(6, min(SCREEN_W - r.width - 6, r.left))
        pygame.draw.rect(screen, WHITE, r, border_radius=8)
        pygame.draw.polygon(screen, WHITE,
                            [(gx - 6, r.bottom - 1), (gx + 6, r.bottom - 1), (gx, r.bottom + 8)])
        pygame.draw.rect(screen, (170, 175, 182), r, 2, border_radius=8)
        screen.blit(t, t.get_rect(center=r.center))

    def _draw_timer(self, screen):
        frac = max(0.0, min(1.0, self.timer / TEMPO_MAX))
        self.tbar.value = frac
        self.tbar.color = GREEN if frac > 0.5 else (ORANGE if frac > 0.25 else RED)
        self.tbar.draw(screen)
        t  = self.font_lbl.render(f"{int(self.timer)}s", True, WHITE)
        ts = self.font_lbl.render(f"{int(self.timer)}s", True, BLACK)
        screen.blit(ts, ts.get_rect(center=(SCREEN_W // 2 + 1, 65)))
        screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 64)))

    def draw(self, screen):
        if self._bg is None:
            self._bg = pygame.Surface((SCREEN_W, SCREEN_H))
            self._render_bg(self._bg)
        screen.blit(self._bg, (0, 0))

        # Cogumelos
        for c in self.cogus:
            _draw_cogumelo(screen, c[0], c[1], self.frame)

        # Ramona no fim do labirinto (brilho pulsante embaixo)
        rx, ry = self.ramona
        pulso = 10 + int(math.sin(self.frame * 0.1) * 4)
        luz = pygame.Surface((90, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(luz, (255, 240, 150, 46), (45 - pulso * 2, 30 - pulso, pulso * 4, pulso * 2))
        screen.blit(luz, (rx - 45, ry - 12))
        spr.draw_ramona(screen, rx, ry + 6, self.frame)

        # Personagens (ordena por Y para profundidade)
        if self.gy <= self.my:
            _draw_grazi(screen, int(self.gx), int(self.gy) - 12, self.frame)
            spr.draw_marina(screen, int(self.mx), int(self.my) - 12, self.frame)
        else:
            spr.draw_marina(screen, int(self.mx), int(self.my) - 12, self.frame)
            _draw_grazi(screen, int(self.gx), int(self.gy) - 12, self.frame)

        if self.aviso_t > 0:
            self._draw_bubble_grazi(screen)

        # Textos flutuantes (+8s)
        for x, y, txt, cor, t in self.textos:
            f  = self.font_hint.render(txt, True, cor)
            fs = self.font_hint.render(txt, True, BLACK)
            screen.blit(fs, fs.get_rect(center=(int(x) + 1, int(y) + 1)))
            screen.blit(f, f.get_rect(center=(int(x), int(y))))

        self.vfx.draw(screen)

        if self.state in ("playing", "fail"):
            self._draw_timer(screen)

        self.hud.draw(screen)
        self.dialog.draw(screen)
        self.btn_menu.draw(screen)

        if self.state == "fail":
            self._draw_fail(screen)
        if self.state == "complete" and self.complete:
            self._draw_complete(screen)

    def _draw_fail(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((10, 20, 5, 170))
        screen.blit(ov, (0, 0))
        t1 = self.font_msg.render("O TEMPO ACABOU!", True, (255, 150, 100))
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 55)))
        t2 = self.font_hint.render("A Ramona ainda esta perdida na floresta...", True, WHITE)
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
        t1 = fb.render("FASE 4 COMPLETA!", True, YELLOW)
        t2 = fs.render("A Ramona esta salva! Muito bem!", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 62)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para continuar ->", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 56)))
        spr.draw_marina(screen, SCREEN_W // 2 - 50, SCREEN_H // 2 + 175, self.frame)
        spr.draw_ramona(screen, SCREEN_W // 2 + 40, SCREEN_H // 2 + 170, self.frame)
