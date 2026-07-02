"""
Fase 2 - O Galinheiro
Um canteiro de obras de verdade: o galinheiro comeca como um esqueleto de
madeira e o jogador arrasta as pecas (telas, tabuas, porta e telhado) do
monte de materiais ate a baia certa da estrutura. A peca arrastada e
exatamente o que aparece construido.
"""
import pygame
import math
from engine.scene_manager import Scene
from engine.dialog import DialogBox
from engine.ui import Button, HUD
from engine.vfx import VFX
import engine.sounds as snd
from constants import *
import characters.sprites as spr

DIALOGO_INTRO = [
    ("Gilson", "Bom dia! Trouxe madeira, tela e pregos!"),
    ("Marina", "Vamos construir o galinheiro da Ramona!"),
]

DIALOGO_DONE = [
    ("Gilson", "Pronto! Um galinheiro firme e bonito!"),
    ("Ramona", "Co-co-COROCO!!!"),
]

# Paleta da obra
MADEIRA       = (172, 120, 62)
MADEIRA_CLARA = (200, 152, 88)
MADEIRA_ESC   = (112, 74,  32)
VIGA          = (134, 92,  46)
VIGA_ESC      = (92,  60,  26)
TELHA         = (158, 66,  46)
TELHA_CLARA   = (192, 98,  68)
TELHA_ESC     = (112, 44,  30)
ARAME         = (172, 182, 172)
INTERIOR      = (54,  38,  22)
SERRAGEM      = [(214, 190, 150), (190, 160, 110), (240, 220, 180)]

# Pecas: "kind" define o desenho; "slot" e o retangulo de destino na
# estrutura. A peca tem exatamente o tamanho do slot.
PECAS_DEF = [
    {"id": "tela_esq",   "kind": "mesh",   "slot": pygame.Rect(434, 296, 160, 66),  "x0": 56,  "y0": 388},
    {"id": "tela_dir",   "kind": "mesh",   "slot": pygame.Rect(672, 296, 100, 66),  "x0": 240, "y0": 388},
    {"id": "parede_esq", "kind": "planks", "slot": pygame.Rect(434, 376, 160, 76),  "x0": 56,  "y0": 458},
    {"id": "parede_dir", "kind": "planks", "slot": pygame.Rect(672, 376, 100, 76),  "x0": 240, "y0": 458},
    {"id": "porta",      "kind": "door",   "slot": pygame.Rect(604, 296, 58, 156),  "x0": 352, "y0": 368},
    {"id": "telhado",    "kind": "roof",   "slot": pygame.Rect(398, 216, 416, 66),  "x0": 430, "y0": 508},
]

# Esqueleto da estrutura
POSTES = [(424, 294, 10, 158), (594, 294, 10, 158),
          (662, 294, 10, 158), (772, 294, 10, 158)]
VIGAS  = [(418, 282, 372, 12),   # viga superior
          (424, 366, 358, 8),    # travessa do meio
          (418, 452, 372, 12)]   # soleira


def _draw_element(surf, kind, r):
    """Desenha uma peca - igual arrastando ou encaixada na estrutura."""
    if kind == "planks":
        n  = 3
        ph = r.height // n
        for i in range(n):
            y = r.y + i * ph
            c = MADEIRA if i % 2 == 0 else (158, 108, 52)
            pygame.draw.rect(surf, c, (r.x, y, r.width, ph - 2))
            pygame.draw.line(surf, MADEIRA_CLARA, (r.x + 2, y + 1), (r.right - 3, y + 1), 1)
            for gx in range(r.x + 10, r.right - 16, 30):
                pygame.draw.line(surf, MADEIRA_ESC, (gx, y + ph // 2), (gx + 14, y + ph // 2), 1)
        pygame.draw.rect(surf, MADEIRA_ESC, r, 2)

    elif kind == "mesh":
        tmp = pygame.Surface((r.width, r.height))
        tmp.fill(INTERIOR)
        step = 9
        for d in range(-r.height, r.width + r.height + step, step):
            pygame.draw.line(tmp, ARAME, (d, 0), (d + r.height, r.height), 1)
            pygame.draw.line(tmp, ARAME, (d + r.height, 0), (d, r.height), 1)
        surf.blit(tmp, r.topleft)
        pygame.draw.rect(surf, VIGA, r, 3)
        pygame.draw.rect(surf, MADEIRA_CLARA, r, 1)

    elif kind == "door":
        pygame.draw.rect(surf, MADEIRA, r)
        pw = r.width // 3
        for i in range(1, 3):
            pygame.draw.line(surf, MADEIRA_ESC, (r.x + i * pw, r.y + 2), (r.x + i * pw, r.bottom - 3), 1)
        # Travessas e brace diagonal (porta em Z)
        pygame.draw.rect(surf, VIGA, (r.x + 3, r.y + 8, r.width - 6, 7))
        pygame.draw.rect(surf, VIGA, (r.x + 3, r.bottom - 15, r.width - 6, 7))
        pygame.draw.line(surf, VIGA, (r.x + 6, r.bottom - 12), (r.right - 7, r.y + 12), 5)
        # Dobradicas e macaneta
        for hy in (r.y + 18, r.bottom - 26):
            pygame.draw.rect(surf, (70, 74, 80), (r.x + 1, hy, 10, 6))
        pygame.draw.circle(surf, (216, 180, 70), (r.right - 9, r.centery), 4)
        pygame.draw.rect(surf, MADEIRA_ESC, r, 2)

    elif kind == "roof":
        ridge  = (r.centerx, r.y)
        eave_l = (r.x, r.bottom)
        eave_r = (r.right, r.bottom)
        pygame.draw.polygon(surf, TELHA, [eave_l, eave_r, ridge])
        # Fileiras de telha seguindo a inclinacao
        rows = 4
        for i in range(1, rows + 1):
            t = i / rows
            y = r.y + int(r.height * t)
            half = int((r.width // 2) * t)
            x1, x2 = r.centerx - half, r.centerx + half
            pygame.draw.line(surf, TELHA_ESC, (x1 + 2, y - 1), (x2 - 2, y - 1), 2)
            for sx in range(x1 + 2, x2 - 8, 13):
                pygame.draw.arc(surf, TELHA_CLARA, (sx, y - 9, 13, 9), math.pi, 2 * math.pi, 2)
        # Cumeeira e beiral
        pygame.draw.line(surf, VIGA_ESC, (r.centerx - 15, r.y + 3), (r.centerx + 15, r.y + 3), 6)
        pygame.draw.line(surf, VIGA, eave_l, eave_r, 4)
        pygame.draw.polygon(surf, TELHA_ESC, [eave_l, eave_r, ridge], 2)


def _draw_nails(surf, kind, r):
    """Cabecas de prego que aparecem quando a peca e fixada."""
    if kind == "roof":
        pts = [(r.x + 14, r.bottom - 5), (r.centerx, r.bottom - 5), (r.right - 14, r.bottom - 5)]
    else:
        pts = [(r.x + 6, r.y + 6), (r.right - 7, r.y + 6),
               (r.x + 6, r.bottom - 7), (r.right - 7, r.bottom - 7)]
    for nx, ny in pts:
        pygame.draw.circle(surf, (105, 110, 115), (nx, ny), 2)
        pygame.draw.circle(surf, (205, 210, 215), (nx - 1, ny - 1), 1)


def _dashed_line(surf, color, p1, p2, dash=10):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist == 0:
        return
    dx, dy = (x2 - x1) / dist, (y2 - y1) / dist
    d = 0.0
    while d < dist:
        e = min(d + dash * 0.55, dist)
        pygame.draw.line(surf, color, (x1 + dx * d, y1 + dy * d), (x1 + dx * e, y1 + dy * e), 2)
        d += dash


class Fase2Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog   = DialogBox()
        self.hud      = HUD()
        self.vfx      = VFX()
        self.frame    = 0
        self.state    = "intro"
        self.pecas    = []
        self.drag     = None
        self.complete = False
        self.font_tag = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self._bg      = None   # fundo estatico em cache

        # Gilson walk-in animation
        self.gilson_x   = float(SCREEN_W + 60)
        self.gilson_y   = 435
        self.gilson_dst = 1170
        self.gilson_arrived = False
        self.banana_x = self.gilson_dst - 30
        self.banana_y = self.gilson_y - 60

    def on_enter(self):
        snd.musica_start()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.drag     = None
        self.vfx.clear()

        self.gilson_x       = float(SCREEN_W + 60)
        self.gilson_arrived = False

        self.pecas = []
        for d in PECAS_DEF:
            r = pygame.Rect(d["x0"], d["y0"], d["slot"].width, d["slot"].height)
            self.pecas.append({**d, "rect": r, "encaixado": False})

        self._update_objective()
        self.btn_voltar = Button(
            (30, SCREEN_H - 65, 200, 50), "Menu", DARK_GRAY, font_size=22
        )
        self.dialog.show(DIALOGO_INTRO, callback=self._intro_done)

    def _update_objective(self):
        n = sum(p["encaixado"] for p in self.pecas)
        self.hud.set_objective(
            f"Monte o galinheiro - {n}/{len(self.pecas)} pecas",
            "Fase 2 - O Galinheiro")

    def _intro_done(self):
        self.state = "building"

    # ----------------------------------------------------------------- events
    def handle_event(self, event):
        if self.dialog.handle_event(event):
            return
        if self.btn_voltar.handle_event(event) and self.btn_voltar.clicked:
            self.btn_voltar.reset()
            self.manager.go_to("menu")

        if self.state == "building":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for p in reversed(self.pecas):
                    if not p["encaixado"] and p["rect"].collidepoint(mx, my):
                        self.drag = p
                        self.drag["offset"] = (mx - p["rect"].x, my - p["rect"].y)
                        break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drag:
                    if self.drag["slot"].collidepoint(self.drag["rect"].center):
                        self._encaixa(self.drag)
                    self.drag = None

                    if all(p["encaixado"] for p in self.pecas):
                        self.state = "done"
                        snd.play('complete')
                        self.vfx.fireworks(SCREEN_W, SCREEN_H)
                        self.dialog.show(DIALOGO_DONE, callback=self._done)

            elif event.type == pygame.MOUSEMOTION and self.drag:
                mx, my = event.pos
                ox, oy = self.drag["offset"]
                self.drag["rect"].topleft = (mx - ox, my - oy)

        elif self.state == "complete" and self.complete:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.go_to("fase3")

    def _encaixa(self, p):
        p["rect"].topleft = p["slot"].topleft
        p["encaixado"]    = True
        snd.play('encaixe')
        self._update_objective()
        # Serragem voando nos cantos, como se estivesse pregando
        r = p["slot"]
        for cx, cy in ((r.x + 8, r.y + 8), (r.right - 8, r.bottom - 8)):
            self.vfx.burst(cx, cy, count=8, colors=SERRAGEM,
                           speed=4, size=3, gravity=80)
        self.vfx.flash((230, 210, 150), duration=0.06, alpha=45)

    def _done(self):
        self.complete = True
        self.state    = "complete"

    # ----------------------------------------------------------------- update
    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)
        self.vfx.update(dt)

        if self.gilson_x > self.gilson_dst:
            self.gilson_x -= 160 * dt
            if self.gilson_x <= self.gilson_dst:
                self.gilson_x       = self.gilson_dst
                self.gilson_arrived = True

    # ----------------------------------------------------------------- draw
    def _draw_bg(self, screen):
        w, h = SCREEN_W, SCREEN_H
        # Parte estatica em cache (performance no celular)
        if self._bg is None:
            self._bg = pygame.Surface((w, h))
            bg = self._bg
            # Ceu
            for sy in range(328):
                t = sy / 328
                pygame.draw.line(bg,
                    (int(95 + 118 * t), int(158 + 68 * t), int(215 + 25 * t)),
                    (0, sy), (w, sy))
            # Floresta
            morro = [(0,270),(0,195),(90,168),(260,182),(450,155),(640,170),(840,150),(1050,168),(w,158),(w,270)]
            pygame.draw.polygon(bg, (18, 56, 14), morro)
            for tx in range(-20, w + 50, 52):
                th = 48 + (tx * 7 % 5) * 12
                ty = 148 + (tx * 3 % 7) * 4
                pygame.draw.rect(bg, (48, 28, 8), (tx + 22, ty + th // 2, 7, th // 2))
                pygame.draw.circle(bg, (14 + tx % 5 * 4, 50 + tx % 4 * 7, 12), (tx + 26, ty + th // 3), th // 3)
            # Gramado
            pygame.draw.rect(bg, (64, 140, 44), (0, 326, w, h - 326))
            pygame.draw.rect(bg, (76, 154, 52), (0, 326, w, 28))
            for gx in range(0, w, 16):
                pygame.draw.line(bg, (48, 118, 34), (gx, 348), (gx + 3, 340), 1)
        screen.blit(self._bg, (0, 0))
        # Nuvens (unica parte animada)
        ox = int((self.frame * 0.18) % (w + 300)) - 150
        for ccx, ccy, cr in [(ox, 55, 40), (ox + 280, 72, 30), (ox + 580, 50, 46)]:
            cl = (238, 242, 248)
            pygame.draw.ellipse(screen, cl, (ccx - cr, ccy - cr // 2, cr * 2, cr))
            pygame.draw.ellipse(screen, cl, (ccx - cr // 2, ccy - cr, cr, cr))

    def _draw_tarp(self, screen):
        """Lona de materiais onde as pecas ficam empilhadas."""
        r = pygame.Rect(40, 362, 384, 176)
        pygame.draw.rect(screen, (208, 196, 162), r, border_radius=8)
        for fy in range(r.y + 34, r.bottom - 10, 48):
            pygame.draw.line(screen, (190, 176, 140), (r.x + 8, fy), (r.right - 8, fy), 1)
        pygame.draw.rect(screen, (172, 156, 118), r, 2, border_radius=8)
        # Estacas nos cantos da lona
        for px, py in (r.topleft, (r.right - 6, r.y), (r.x, r.bottom - 6), (r.right - 6, r.bottom - 6)):
            pygame.draw.rect(screen, VIGA_ESC, (px + 1, py + 1, 5, 5))
        t = self.font_tag.render("MATERIAIS", True, (128, 110, 74))
        screen.blit(t, (r.x + 14, r.y + 6))

    def _draw_props(self, screen):
        # Caixa de ferramentas perto dos trabalhadores
        bx, by = 800, 546
        pygame.draw.rect(screen, (176, 44, 38), (bx, by, 48, 24), border_radius=3)
        pygame.draw.rect(screen, (120, 28, 24), (bx, by, 48, 24), 2, border_radius=3)
        pygame.draw.line(screen, (120, 28, 24), (bx, by + 8), (bx + 48, by + 8), 1)
        pygame.draw.rect(screen, (90, 94, 100), (bx + 16, by - 6, 16, 7), 2, border_radius=3)
        # Martelo largado no chao
        hx, hy = 760, 570
        pygame.draw.line(screen, MADEIRA, (hx, hy + 8), (hx + 26, hy), 4)
        pygame.draw.rect(screen, (110, 115, 122), (hx + 22, hy - 6, 10, 12), border_radius=2)
        # Pregos espalhados perto da obra
        for nx, ny in ((470, 492), (486, 498), (702, 496)):
            pygame.draw.line(screen, (150, 155, 160), (nx, ny), (nx + 7, ny - 2), 2)

    def _draw_galinheiro(self, screen):
        ok = {p["id"]: p["encaixado"] for p in self.pecas}

        # Terra batida da obra + serragem
        pygame.draw.ellipse(screen, (152, 118, 74), (386, 434, 440, 54))
        pygame.draw.ellipse(screen, (128, 96, 58), (386, 434, 440, 54), 2)
        for sx, sy in ((470, 466), (700, 472), (588, 480)):
            pygame.draw.ellipse(screen, (216, 194, 154), (sx, sy, 34, 8))

        # Interior escuro - estrutura aberta, da pra ver dentro
        pygame.draw.rect(screen, INTERIOR, (434, 294, 348, 160))

        # Caibros do telhado (esqueleto, enquanto o telhado nao vem)
        if not ok["telhado"]:
            ridge = (606, 220)
            pygame.draw.line(screen, VIGA_ESC, ridge, (404, 280), 5)
            pygame.draw.line(screen, VIGA_ESC, ridge, (808, 280), 5)
            pygame.draw.line(screen, VIGA_ESC, ridge, (606, 282), 4)
            pygame.draw.line(screen, VIGA_ESC, (499, 252), (713, 252), 3)

        # Escoras diagonais nas baias vazias das paredes
        for pid in ("parede_esq", "parede_dir"):
            if not ok[pid]:
                s = next(p["slot"] for p in self.pecas if p["id"] == pid)
                pygame.draw.line(screen, VIGA_ESC, (s.x + 2, s.bottom - 2), (s.right - 2, s.y + 2), 4)

        # Pecas ja encaixadas (mesmo desenho da peca arrastada + pregos)
        for p in self.pecas:
            if p["encaixado"] and p["kind"] != "roof":
                _draw_element(screen, p["kind"], p["slot"])
                _draw_nails(screen, p["kind"], p["slot"])

        # Postes e vigas do esqueleto por cima dos paineis
        for bx, by, bw, bh in POSTES + VIGAS:
            pygame.draw.rect(screen, VIGA, (bx, by, bw, bh))
            pygame.draw.line(screen, MADEIRA_CLARA, (bx + 1, by + 1),
                             (bx + (bw - 2 if bh > bw else 1), by + (1 if bh > bw else bh - 2)), 1)
            pygame.draw.rect(screen, VIGA_ESC, (bx, by, bw, bh), 1)

        # Telhado por ultimo (cobre a viga superior)
        for p in self.pecas:
            if p["encaixado"] and p["kind"] == "roof":
                _draw_element(screen, p["kind"], p["slot"])
                _draw_nails(screen, p["kind"], p["slot"])

        # Ramona chega na porta quando a casa fica pronta
        if self.state in ("done", "complete"):
            spr.draw_ramona(screen, 633, 470, self.frame)

    def _draw_ghosts(self, screen):
        pulse = 0.5 + 0.5 * math.sin(self.frame * 0.1)
        col = (int(200 + 55 * pulse), int(205 + 45 * pulse), 80)
        for p in self.pecas:
            if p["encaixado"]:
                continue
            r = p["slot"]
            if p["kind"] == "roof":
                pts = [(r.x, r.bottom), (r.centerx, r.y), (r.right, r.bottom)]
            else:
                pts = [r.topleft, r.topright, r.bottomright, r.bottomleft]
            if p is self.drag and r.collidepoint(p["rect"].center):
                # Preview de encaixe: contorno solido verde
                pygame.draw.lines(screen, (110, 235, 110), True, pts, 3)
            else:
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    _dashed_line(screen, col, a, b)

    def draw(self, screen):
        self._draw_bg(screen)
        self._draw_tarp(screen)
        self._draw_props(screen)
        self._draw_galinheiro(screen)

        if self.state == "building" and not self.dialog.active:
            self._draw_ghosts(screen)

        # Personagens (lado direito, canteiro livre)
        spr.draw_papai(screen, 860, 435, self.frame, tool=True)
        spr.draw_marina(screen, 950, 450, self.frame)
        spr.draw_mamae(screen, 1070, 435, self.frame)

        gx = int(self.gilson_x)
        spr.draw_gilson(screen, gx, self.gilson_y, self.frame,
                        has_banana=not self.gilson_arrived)
        if self.gilson_arrived:
            spr.draw_banana_bunch(screen, self.banana_x, self.banana_y, self.frame)

        # Pecas soltas por cima de tudo (arrastar fica sempre visivel)
        for p in self.pecas:
            if not p["encaixado"]:
                if p is self.drag:
                    sh = pygame.Surface((p["rect"].w + 6, 6), pygame.SRCALPHA)
                    sh.fill((0, 0, 0, 60))
                    screen.blit(sh, (p["rect"].x - 3, p["rect"].bottom + 4))
                _draw_element(screen, p["kind"], p["rect"])

        self.vfx.draw(screen)
        self.hud.draw(screen)
        self.dialog.draw(screen)
        self.btn_voltar.draw(screen)

        if self.state == "complete" and self.complete:
            self._draw_complete(screen)

    def _draw_complete(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        screen.blit(ov, (0, 0))

        for i in range(10):
            ang = (self.frame * 2 + i * 36) % 360
            r   = math.radians(ang)
            sx  = SCREEN_W // 2 + int(math.cos(r) * 200)
            sy  = SCREEN_H // 2 + int(math.sin(r) * 95)
            pygame.draw.circle(screen, YELLOW,
                               (sx, sy), 7 + int(math.sin(self.frame * 0.1 + i) * 3))

        pygame.draw.rect(screen, (22, 72, 22),
                         (SCREEN_W//2-360, SCREEN_H//2-115, 720, 245), border_radius=18)
        pygame.draw.rect(screen, (78, 215, 78),
                         (SCREEN_W//2-360, SCREEN_H//2-115, 720, 245), 3, border_radius=18)

        fb = pygame.font.SysFont("Segoe UI", 58, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 24)
        t1 = fb.render("FASE 2 COMPLETA!", True, YELLOW)
        t2 = fs.render("O galinheiro da Ramona esta pronto!", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 60)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para continuar ->", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 55)))

        spr.draw_ramona(screen, SCREEN_W//2 - 50, SCREEN_H//2 + 160, self.frame)
        spr.draw_banana_bunch(screen, SCREEN_W//2 + 40, SCREEN_H//2 + 148, self.frame)
