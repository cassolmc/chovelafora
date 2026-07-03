"""
Fase 5 - Catar os Ovos
Dentro do galinheiro: as galinhas botam ovos nos ninhos (alturas diferentes)
e eles caem. Marina se move na horizontal com o cesto e pega os ovos:
  ovo azul pequeno  -> Ganiza
  ovo marrom grande -> Bunda Pelada
  ovo branco grande -> Bicadona
Vitoria: pegar 20 ovos antes do timer (90s).
"""
import pygame
import math
import random
from engine.scene_manager import Scene
from engine.dialog import DialogBox
from engine.ui import HUD, Button, ProgressBar
from engine.vfx import VFX
import engine.sounds as snd
from constants import *
import characters.sprites as spr

META_OVOS = 24
TEMPO_MAX = 90.0
CHAO_Y    = 505   # altura onde o ovo espatifa

DIALOGO_INTRO = [
    ("Mamae",    "Marina! As galinhas botaram! Hora de catar os ovos!"),
    ("Narrador", "Arraste o dedo (ou mouse) em QUALQUER lugar da tela: a Marina segue!"),
]

DIALOGO_DONE = [
    ("Marina", "Vinte ovos! Cesto cheio!"),
    ("Mamae",  "Perfeito! Vou fazer uma omelete deliciosa!"),
]

# Tipos de ovo
OVO_COR = {
    "azul":   ((150, 195, 235), (95, 140, 190)),
    "marrom": ((176, 116, 62),  (124, 78, 36)),
    "branco": ((248, 245, 235), (190, 184, 168)),
}
OVO_TAM = {"azul": (13, 17), "marrom": (19, 25), "branco": (19, 25)}
CESTO_COR = ((208, 162, 92), (140, 100, 48))   # cesto de vime
GALINHA_DONA = {"azul": "Ganiza", "marrom": "Bunda Pelada", "branco": "Bicadona"}
GALINHA_COR  = {
    "azul":   (128, 138, 158),   # Ganiza: cinza-azulada, pequena
    "marrom": (168, 84, 40),     # Bunda Pelada: vermelha-marrom, grande
    "branco": (246, 243, 235),   # Bicadona: branca, grande
}

# Ninhos na parede do galinheiro: (cx, topo, tipo) - alturas variadas
NINHOS = [
    (230,  70, "azul"),
    (400, 132, "marrom"),
    (570,  92, "branco"),
    (740, 148, "marrom"),
    (910,  74, "azul"),
    (1080, 138, "branco"),
]
NINHO_W, NINHO_H = 104, 72


def _draw_ovo(surf, tipo, x, y):
    w, h = OVO_TAM[tipo]
    cor, borda = OVO_COR[tipo]
    r = pygame.Rect(int(x) - w // 2, int(y) - h // 2, w, h)
    # Halo claro para destacar o ovo da parede/chao marrom
    pygame.draw.ellipse(surf, (255, 250, 215), r.inflate(5, 5), 2)
    pygame.draw.ellipse(surf, cor, r)
    pygame.draw.ellipse(surf, borda, r, 2)
    pygame.draw.arc(surf, WHITE, (r.x + 2, r.y + 2, w - 6, h - 8), 1.4, 2.6, 2)


def _draw_cesto(surf, cx, cy, s=1.0):
    cor, borda = CESTO_COR
    w1, w2, h = int(30 * s), int(21 * s), int(20 * s)
    pygame.draw.polygon(surf, cor, [
        (cx - w1, cy), (cx + w1, cy), (cx + w2, cy + h), (cx - w2, cy + h)])
    for i in range(1, 3):
        fy = cy + h * i // 3
        fw = w1 - (w1 - w2) * i // 3
        pygame.draw.line(surf, borda, (cx - fw + 2, fy), (cx + fw - 2, fy), 1)
    pygame.draw.polygon(surf, borda, [
        (cx - w1, cy), (cx + w1, cy), (cx + w2, cy + h), (cx - w2, cy + h)], 2)
    pygame.draw.ellipse(surf, borda, (cx - w1, cy - int(5 * s), w1 * 2, int(10 * s)))
    pygame.draw.ellipse(surf, cor, (cx - w1 + 3, cy - int(3 * s), w1 * 2 - 6, int(6 * s)))


def _draw_galinha_ninho(surf, tipo, cx, cy, frame, hop=0.0):
    """Galinha sentada no ninho. cy = base (palha)."""
    s = 0.72 if tipo == "azul" else 1.0
    corpo = GALINHA_COR[tipo]
    borda = tuple(max(0, c - 60) for c in corpo)
    lift  = int(math.sin(min(1.0, hop / 0.35) * math.pi) * 9) if hop > 0 else 0
    bob   = int(math.sin(frame * 0.12 + cx) * 1.5)
    y     = cy - lift + bob

    bw, bh = int(52 * s), int(34 * s)
    pygame.draw.ellipse(surf, corpo, (cx - bw // 2, y - bh, bw, bh))
    pygame.draw.ellipse(surf, borda, (cx - bw // 2, y - bh, bw, bh), 2)
    # Rabo
    for i in range(3):
        pygame.draw.ellipse(surf, borda,
                            (cx - bw // 2 - int(10 * s) + i * 3, y - bh - int(6 * s) + i * 5,
                             int(18 * s), int(9 * s)))
    # Cabeca
    hx, hy = cx + int(20 * s), y - bh - int(8 * s)
    hr = int(11 * s)
    pygame.draw.circle(surf, corpo, (hx, hy), hr)
    pygame.draw.circle(surf, borda, (hx, hy), hr, 2)
    pygame.draw.polygon(surf, RED, [
        (hx - 5, hy - hr), (hx - 2, hy - hr - 6), (hx + 1, hy - hr - 1),
        (hx + 4, hy - hr - 5), (hx + 6, hy - hr)])
    pygame.draw.polygon(surf, ORANGE, [
        (hx + hr, hy - 1), (hx + hr + 7, hy + 2), (hx + hr, hy + 4)])
    pygame.draw.circle(surf, BLACK, (hx + 4, hy - 2), 2)


class Ovo:
    def __init__(self, ninho, vel_bonus=0.0):
        cx, topo, tipo = ninho
        self.tipo  = tipo
        self.x     = float(cx + random.randint(-10, 10))
        self.y     = float(topo + NINHO_H)
        self.vy    = random.uniform(150, 235) + vel_bonus
        self.ativo = True
        self.break_t = 0.0

    def update(self, dt):
        if self.ativo:
            self.y += self.vy * dt
        elif self.break_t > 0:
            self.break_t -= dt

    @property
    def done(self):
        return not self.ativo and self.break_t <= 0

    @property
    def rect(self):
        w, h = OVO_TAM[self.tipo]
        return pygame.Rect(int(self.x) - w // 2, int(self.y) - h // 2, w, h)

    def draw(self, surf):
        if self.ativo:
            _draw_ovo(surf, self.tipo, self.x, self.y)
        elif self.break_t > 0:
            cor = OVO_COR[self.tipo][0]
            for dx, dy in ((-8, 3), (5, -1), (0, 6), (-3, -4), (9, 4)):
                pygame.draw.ellipse(surf, cor,
                                    (int(self.x) + dx - 4, int(self.y) + dy, 10, 6))
            pygame.draw.ellipse(surf, (255, 235, 140),
                                (int(self.x) - 5, int(self.y) + 1, 10, 7))


class Fase5Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog   = DialogBox()
        self.hud      = HUD()
        self.vfx      = VFX()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.tbar     = ProgressBar((SCREEN_W // 2 - 150, 56, 300, 16))
        self.font_lbl = pygame.font.SysFont("Segoe UI", 13, bold=True)
        self.font_pts = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_msg = pygame.font.SysFont("Segoe UI", 46, bold=True)
        self.font_hint = pygame.font.SysFont("Segoe UI", 19, bold=True)
        self.hops     = [0.0] * len(NINHOS)
        self.textos   = []   # [x, y, txt, cor, t]
        self._bg      = None   # fundo estatico em cache

    def on_enter(self):
        snd.musica_start()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.vfx.clear()
        self._reinicia()
        # Menu no canto superior direito: embaixo a Marina corre e clica
        self.btn_menu = Button((SCREEN_W - 130, 52, 110, 36), "Menu", DARK_GRAY, font_size=18)
        self.dialog.show(DIALOGO_INTRO, callback=self._intro_done)

    def _reinicia(self):
        self.ovos     = []
        self.certos   = 0
        self.timer    = TEMPO_MAX
        self.marina_x = float(SCREEN_W // 2)
        self.spawn_cd = 1.0
        self.textos   = []
        self.hops     = [0.0] * len(NINHOS)
        self.hud.set_objective(f"Ovos: 0/{META_OVOS}", "Fase 5 - Catar os Ovos")

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
                self.manager.go_to("fase6")

    # ----------------------------------------------------------------- update
    def _flutua(self, x, y, txt, cor):
        self.textos.append([float(x), float(y), txt, cor, 0.9])

    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)
        self.vfx.update(dt)

        for t in self.textos:
            t[1] -= 42 * dt
            t[4] -= dt
        self.textos = [t for t in self.textos if t[4] > 0]
        self.hops = [max(0.0, h - dt) for h in self.hops]

        if self.state != "playing" or self.dialog.active:
            return

        # Movimento: setas/A-D ou mouse
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.marina_x -= 430 * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.marina_x += 430 * dt
        mx, _ = pygame.mouse.get_pos()
        diff = mx - self.marina_x
        if abs(diff) > 4:
            self.marina_x += diff * min(1.0, 8.5 * dt)
        self.marina_x = max(50.0, min(float(SCREEN_W - 50), self.marina_x))

        # Spawn nos ninhos
        self.spawn_cd -= dt
        if self.spawn_cd <= 0:
            i = random.randrange(len(NINHOS))
            self.ovos.append(Ovo(NINHOS[i], vel_bonus=self.certos * 2.0))
            self.hops[i] = 0.35
            self.spawn_cd = max(0.85, 1.25 - self.certos * 0.015)

        # Timer
        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0
            self.state = "fail"
            snd.play('erro')
            snd.play('gameover')
            return

        # Colisoes
        basket = pygame.Rect(int(self.marina_x) - 34, 506, 68, 26)
        for ovo in self.ovos:
            ovo.update(dt)
            if not ovo.ativo:
                continue
            if ovo.vy > 0 and basket.colliderect(ovo.rect):
                ovo.ativo = False
                self.certos += 1
                snd.play('ding')
                self.vfx.stars(ovo.x, ovo.y, color=(255, 250, 150))
                self._flutua(ovo.x, ovo.y - 16, "+1", (140, 255, 140))
                self.hud.set_objective(
                    f"Ovos: {self.certos}/{META_OVOS}", "Fase 5 - Catar os Ovos")
                if self.certos >= META_OVOS:
                    self.state = "win_dialog"
                    snd.play('complete')
                    self.vfx.fireworks(SCREEN_W, SCREEN_H)
                    self.dialog.show(DIALOGO_DONE, callback=self._done)
                    return
            elif ovo.y >= CHAO_Y:
                ovo.ativo   = False
                ovo.break_t = 0.6
                snd.play('erro')

        self.ovos = [o for o in self.ovos if not o.done]

    def _done(self):
        self.complete = True
        self.state    = "complete"

    # ----------------------------------------------------------------- draw
    def _draw_bg(self, screen):
        # Fundo 100% estatico: desenha uma vez e reusa (performance no celular)
        if self._bg is None:
            self._bg = pygame.Surface((SCREEN_W, SCREEN_H))
            self._render_bg(self._bg)
        screen.blit(self._bg, (0, 0))

    def _render_bg(self, screen):
        w, h = SCREEN_W, SCREEN_H
        # Parede de tabuas do galinheiro (estamos la dentro!)
        screen.fill((198, 152, 98))
        for px in range(0, w, 64):
            pygame.draw.line(screen, (172, 128, 76), (px, 0), (px, 490), 2)
            pygame.draw.line(screen, (214, 170, 116), (px + 2, 0), (px + 2, 490), 1)
        # Viga horizontal
        pygame.draw.rect(screen, (140, 96, 48), (0, 240, w, 12))
        pygame.draw.rect(screen, (104, 68, 30), (0, 240, w, 12), 1)

        # Janela com tela de arame mostrando o quintal
        jr  = pygame.Rect(52, 300, 140, 130)
        tmp = pygame.Surface((jr.width, jr.height))
        tmp.fill((150, 200, 235))
        pygame.draw.rect(tmp, (74, 150, 52), (0, 78, jr.width, 52))
        for d in range(-jr.height, jr.width + jr.height, 12):
            pygame.draw.line(tmp, (168, 178, 168), (d, 0), (d + jr.height, jr.height), 1)
            pygame.draw.line(tmp, (168, 178, 168), (d + jr.height, 0), (d, jr.height), 1)
        screen.blit(tmp, jr.topleft)
        pygame.draw.rect(screen, (120, 80, 38), jr, 4)

        # Chao de terra com palha
        pygame.draw.rect(screen, (160, 118, 70), (0, 490, w, h - 490))
        pygame.draw.rect(screen, (128, 92, 52), (0, 490, w, 8))
        for sx in range(20, w, 90):
            sy = 520 + (sx * 7 % 50)
            for k in range(4):
                pygame.draw.line(screen, (224, 186, 100),
                                 (sx + k * 5, sy + 4), (sx + 10 + k * 5, sy - 3), 2)

    def _draw_ninhos(self, screen):
        for i, (cx, topo, tipo) in enumerate(NINHOS):
            r = pygame.Rect(cx - NINHO_W // 2, topo, NINHO_W, NINHO_H)
            # Caixa do ninho
            pygame.draw.rect(screen, (60, 42, 22), r)
            pygame.draw.rect(screen, (134, 92, 46), r.inflate(12, 12), 6, border_radius=4)
            # Palha
            for k in range(6):
                px = r.x + 6 + k * 16
                pygame.draw.line(screen, (226, 188, 98),
                                 (px, r.bottom - 6), (px + 12, r.bottom - 14), 3)
            # Galinha dona do ninho
            _draw_galinha_ninho(screen, tipo, cx, r.bottom - 8, self.frame, self.hops[i])
            # Nome
            nome = GALINHA_DONA[tipo]
            t  = self.font_lbl.render(nome, True, WHITE)
            ts = self.font_lbl.render(nome, True, BLACK)
            screen.blit(ts, ts.get_rect(center=(cx + 1, r.bottom + 15)))
            screen.blit(t, t.get_rect(center=(cx, r.bottom + 14)))

    def _draw_timer(self, screen):
        frac = self.timer / TEMPO_MAX
        self.tbar.value = frac
        self.tbar.color = GREEN if frac > 0.5 else (ORANGE if frac > 0.25 else RED)
        self.tbar.draw(screen)
        t  = self.font_lbl.render(f"{int(self.timer)}s", True, WHITE)
        ts = self.font_lbl.render(f"{int(self.timer)}s", True, BLACK)
        screen.blit(ts, ts.get_rect(center=(SCREEN_W // 2 + 1, 65)))
        screen.blit(t, t.get_rect(center=(SCREEN_W // 2, 64)))

    def draw(self, screen):
        self._draw_bg(screen)
        self._draw_ninhos(screen)

        # Ovos
        for ovo in self.ovos:
            ovo.draw(screen)

        # Marina com o cesto na cabeca
        mx = int(self.marina_x)
        spr.draw_marina(screen, mx, 545, self.frame)
        _draw_cesto(screen, mx, 506, s=1.1)

        # Seta pulsante acima do cesto: acha a Marina mesmo com o dedo na tela
        if self.state == "playing":
            ay = 468 + int(math.sin(self.frame * 0.15) * 5)
            pts = [(mx - 11, ay), (mx + 11, ay), (mx, ay + 14)]
            pygame.draw.polygon(screen, YELLOW, pts)
            pygame.draw.polygon(screen, (140, 110, 0), pts, 2)

        # Textos flutuantes
        for x, y, txt, cor, t in self.textos:
            a = min(1.0, t / 0.35)
            f  = self.font_pts.render(txt, True, cor)
            fs = self.font_pts.render(txt, True, BLACK)
            f.set_alpha(int(255 * a)); fs.set_alpha(int(255 * a))
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
        ov.fill((40, 0, 0, 150))
        screen.blit(ov, (0, 0))
        t1 = self.font_msg.render("O TEMPO ACABOU!", True, (255, 120, 100))
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 55)))
        t2 = self.font_hint.render(
            f"Voce pegou {self.certos} de {META_OVOS} ovos.", True, WHITE)
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
        t1 = fb.render("FASE 5 COMPLETA!", True, YELLOW)
        t2 = fs.render(f"Marina catou {META_OVOS} ovos! Que colheita!", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 62)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para continuar ->", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 56)))
        spr.draw_marina(screen, SCREEN_W // 2 - 50, SCREEN_H // 2 + 175, self.frame)
        spr.draw_ramona(screen, SCREEN_W // 2 + 40, SCREEN_H // 2 + 170, self.frame)
