"""
Fase 1 - Xo Gaviao!
Marina precisa espantar gavioes que atacam as galinhas no sitio.
Clique nos gavioes para espanta-los. 3 vidas. Espante 12 gavioes.
"""
import pygame
import math
import random
from engine.scene_manager import Scene
from engine.dialog import DialogBox
from engine.ui import HUD, Button
from engine.vfx import VFX
import engine.sounds as snd
from constants import *
import characters.sprites as spr

META_GAVIOES = 12
VIDAS_INICIO = 3

DIALOGO_INTRO = [
    ("Marina",   "Ramona! Bom diaaa! Vamos tomar cafe junt-- ESPERA! Um GAVIAO!"),
    ("Narrador", "Clique nos gavioes para espanta-los antes que peguem as galinhas!"),
]

DIALOGO_DONE = [
    ("Marina",   "EBAAA! Espantei todos os gavioes!"),
    ("Ramona",   "Co-co-COROCO!!!"),
]


class Gaviao:
    SPEED_BASE = 1.4

    def __init__(self, screen_w, target_x, target_y, nivel=1, force_slow=False):
        self.x = float(random.randint(120, screen_w - 120))
        self.y = float(random.randint(-70, -15))

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy) or 1
        # Velocidade cresce devagar e tem teto de 2.6
        speed = self.SPEED_BASE + min(nivel, 5) * 0.12 + random.uniform(0, 0.3)
        if force_slow:
            speed = min(speed, 1.6)   # gavioes finais mais lentos
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed

        self.state = "flying"   # flying | scared | miss
        self.anim  = 0.0        # timer para estado scared/miss
        self.frame = 0
        self.hit_flash = 0.0

    def update(self, dt, screen_h):
        self.frame    += 1
        self.hit_flash = max(0.0, self.hit_flash - dt)

        if self.state == "flying":
            self.x += self.vx
            self.y += self.vy
            # Chegou perto do alvo = miss
            if self.y > screen_h - 80:
                self.state = "miss"
                self.anim  = 0.8

        elif self.state in ("scared", "miss"):
            self.anim -= dt
            if self.state == "scared":
                self.x += self.vx * -3   # foge rapido
                self.y += self.vy * -3
            # Estado termina quando anim chega a 0
            # (cena remove o gaviao depois)

    @property
    def done(self):
        return self.state in ("scared", "miss") and self.anim <= 0

    @property
    def rect(self):
        # Hitbox generoso para facilitar o clique
        return pygame.Rect(int(self.x) - 52, int(self.y) - 22, 104, 58)

    def draw(self, surf):
        ix, iy = int(self.x), int(self.y)
        swooping = (self.y > 150)

        if self.state == "scared":
            # Foge - flip horizontal, vermelho
            tmp = pygame.Surface((90, 50), pygame.SRCALPHA)
            spr.draw_gaviao(tmp, 45, 20, self.frame, swooping=False)
            tmp = pygame.transform.flip(tmp, True, False)
            alpha_surf = pygame.Surface((90, 50), pygame.SRCALPHA)
            alpha_surf.fill((255, 80, 80, 160))
            tmp.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tmp, (ix - 45, iy - 20))
        elif self.state == "miss":
            spr.draw_gaviao(surf, ix, iy, self.frame, swooping=True)
        else:
            spr.draw_gaviao(surf, ix, iy, self.frame, swooping=swooping)

        if self.hit_flash > 0:
            fh = pygame.font.SysFont("Arial", 22, bold=True)
            ts = fh.render("XO!", True, (255, 80, 80))
            surf.blit(ts, (ix - ts.get_width() // 2, iy - 30))


class Fase1Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog    = DialogBox()
        self.hud       = HUD()
        self.frame    = 0
        self.state    = "intro"
        self.gavioes  = []
        self.score    = 0
        self.vidas    = VIDAS_INICIO
        self.nivel    = 1
        self.spawn_cd = 2.0
        self.complete = False
        self.vfx      = VFX()

        # Posicoes fixas das galinhas no gramado
        self.galinhas = [
            (360, 460, (22, 22, 22),    WHITE),
            (450, 450, (245, 245, 240), RED),
            (540, 462, (245, 245, 240), RED),
            (630, 455, (165, 55, 40),   RED),
            (720, 458, (155, 155, 150), RED),
        ]

    def on_enter(self):
        self.frame    = 0
        self.state    = "intro"
        self.gavioes  = []
        self.score    = 0
        self.vidas    = VIDAS_INICIO
        self.nivel    = 1
        self.spawn_cd = 2.5
        self.complete = False
        self.vfx.clear()
        self.hud.set_objective(f"Espante {META_GAVIOES} gavioes!", "Fase 1 - Xo Gaviao!")
        self.btn_menu = Button((30, SCREEN_H - 65, 200, 50), "Menu", DARK_GRAY, font_size=22)
        self.dialog.show(DIALOGO_INTRO, callback=self._intro_done)

    def _intro_done(self):
        self.state = "playing"

    def handle_event(self, event):
        if self.dialog.handle_event(event):
            return
        if self.btn_menu.handle_event(event) and self.btn_menu.clicked:
            self.btn_menu.reset()
            self.manager.go_to("menu")

        if self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                hit = False
                for gav in self.gavioes:
                    if gav.state == "flying" and gav.rect.collidepoint(mx, my):
                        gav.state     = "scared"
                        gav.anim      = 0.5
                        gav.hit_flash = 0.3
                        self.score   += 1
                        snd.play('kill')
                        self.vfx.burst(int(gav.x), int(gav.y), count=12,
                                       colors=[(110,75,25),(90,60,20),(200,160,60)],
                                       speed=5, size=5, gravity=80)
                        self.vfx.flash((255, 255, 100), duration=0.08, alpha=60)
                        hit = True
                        if self.score >= META_GAVIOES:
                            self.state = "win_dialog"
                            self.dialog.show(DIALOGO_DONE, callback=self._done)
                        break

        elif self.state == "complete" and self.complete:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.go_to("fase2")

    def _done(self):
        self.complete = True
        self.state    = "complete"

    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)

        if self.state == "playing":
            # Aumenta nivel a cada 4 gavioes (mais devagar)
            self.nivel = 1 + self.score // 4

            # Spawn de gavioes
            faltam      = META_GAVIOES - self.score
            voando      = len([g for g in self.gavioes if g.state == "flying"])
            force_slow  = faltam <= 3          # ultimos 3: mais lentos
            max_tela    = 3 if faltam > 3 else 2   # garante alvos na tela

            self.spawn_cd -= dt
            if self.spawn_cd <= 0:
                if voando < max_tela:
                    target = random.choice(self.galinhas)
                    self.gavioes.append(
                        Gaviao(SCREEN_W, target[0], target[1], self.nivel, force_slow)
                    )
                # Cooldown mais longo nos ultimos (mais tempo por alvo)
                self.spawn_cd = max(1.2 if force_slow else 0.9,
                                    2.5 - self.score * 0.10)

            # Update gavioes
            for gav in self.gavioes:
                gav.update(dt, SCREEN_H)
                if gav.state == "miss" and gav.done:
                    self.vidas -= 1
                    if self.vidas <= 0:
                        self.state = "game_over"

            self.gavioes = [g for g in self.gavioes if not g.done]

        self.vfx.update(dt)

    def draw(self, screen):
        spr.draw_sitio_exterior(screen, self.frame)

        # Galinhas no gramado
        for cx, cy, col, cc in self.galinhas:
            spr.draw_galinha(screen, cx, cy, col, cc, self.frame, small=True)
        spr.draw_ramona(screen, 340, 515, self.frame)

        # Marina (lateral, acenando / gritando)
        spr.draw_marina(screen, 160, 510, self.frame)

        # Papai trabalhando ao fundo
        spr.draw_papai(screen, 1050, 460, self.frame, tool=True)

        # Gavioes
        for gav in self.gavioes:
            gav.draw(screen)

        self.vfx.draw(screen)

        # HUD: vidas + score
        self._draw_hud(screen)

        if self.state == "game_over":
            self._draw_game_over(screen)
        elif self.state == "complete" and self.complete:
            self._draw_complete(screen)

        self.hud.draw(screen)
        self.dialog.draw(screen)
        self.btn_menu.draw(screen)

        if self.state == "playing" and not self.dialog.active:
            faltam = META_GAVIOES - self.score
            if faltam <= 3:
                fh  = pygame.font.SysFont("Segoe UI", 22, bold=True)
                msg = f"Falta{'m' if faltam > 1 else ''} {faltam} gaviao{'es' if faltam > 1 else ''}!"
                col = (255, 120, 50)
                if (self.frame // 20) % 2 == 0:
                    h = fh.render(msg, True, col)
                    screen.blit(h, h.get_rect(center=(SCREEN_W // 2, 60)))
            else:
                fh = pygame.font.SysFont("Arial", 18)
                h  = fh.render("Clique nos gavioes para espanta-los!", True, YELLOW)
                screen.blit(h, h.get_rect(center=(SCREEN_W // 2, 60)))

    def _draw_hud(self, screen):
        # Vidas (icones de galinha)
        fv = pygame.font.SysFont("Segoe UI", 20, bold=True)
        vt = fv.render("Vidas:", True, WHITE)
        screen.blit(vt, (SCREEN_W - 260, 55))
        for i in range(VIDAS_INICIO):
            col = (220, 80, 80) if i >= self.vidas else (255, 220, 50)
            pygame.draw.circle(screen, col, (SCREEN_W - 175 + i * 36, 66), 14)
            pygame.draw.circle(screen, WHITE, (SCREEN_W - 175 + i * 36, 66), 14, 1)

        # Score
        st = fv.render(f"Gavioes: {self.score}/{META_GAVIOES}", True, YELLOW)
        screen.blit(st, (SCREEN_W - 260, 82))

    def _draw_game_over(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        screen.blit(ov, (0, 0))
        fb = pygame.font.SysFont("Segoe UI", 60, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 26)
        t1 = fb.render("FIM DE JOGO!", True, RED)
        t2 = fs.render("Os gavioes pegaram as galinhas...", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 55)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 10)))
        if (self.frame // 30) % 2 == 0:
            t3 = fs.render("ESC = Menu", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 60)))

    def _draw_complete(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))
        for i in range(12):
            ang = (self.frame * 2 + i * 30) % 360
            r   = math.radians(ang)
            sx  = SCREEN_W // 2 + int(math.cos(r) * 210)
            sy  = SCREEN_H // 2 + int(math.sin(r) * 105)
            pygame.draw.circle(screen, YELLOW, (sx, sy), 7 + int(math.sin(self.frame * 0.1 + i) * 3))
        pygame.draw.rect(screen, (22, 72, 22),
                         (SCREEN_W//2-370, SCREEN_H//2-120, 740, 255), border_radius=18)
        pygame.draw.rect(screen, (78, 215, 78),
                         (SCREEN_W//2-370, SCREEN_H//2-120, 740, 255), 3, border_radius=18)
        fb = pygame.font.SysFont("Segoe UI", 58, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 26)
        t1 = fb.render("FASE 1 COMPLETA!", True, YELLOW)
        t2 = fs.render(f"Voce espantou {self.score} gavioes! As galinhas estao salvas!", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 65)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para continuar ->", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 58)))
        spr.draw_ramona(screen, SCREEN_W//2 - 40, SCREEN_H//2 + 160, self.frame)
        spr.draw_white(screen,  SCREEN_W//2 + 40, SCREEN_H//2 + 155, self.frame)
