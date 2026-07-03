"""
Fase 1 - Xo Gaviao!
Sistema de ondas: 5 ondas de gavioes, cada uma mais dificil, terminando
num mini-chefe (o Lider) que convoca reforcos. Tipos de gaviao:
  jovem      - lento, 1 clique, voa sozinho
  rapido     - muito veloz, mais dificil de acertar
  forte      - aguenta 3 cliques, mais lento
  sorrateiro - surge por tras das arvores e muda de direcao sem avisar
  lider      - mini-chefe: 6 cliques, chama jovens enquanto vive
As galinhas entram em panico quando um gaviao chega perto: correm,
cacarejam e algumas se escondem atras das moitas (escondida = salva).
3 vidas: gaviao que pega galinha a vista tira uma.
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

VIDAS_INICIO = 3

DIALOGO_INTRO = [
    ("Marina",   "Ramona! Bom diaaa! Vamos tomar cafe junt-- ESPERA! GAVIOES!"),
    ("Narrador", "Clique nos gavioes! Sao 5 ondas - e dizem que o bando tem um LIDER..."),
]

DIALOGO_DONE = [
    ("Marina",   "EBAAA! Espantei ate o lider dos gavioes!"),
    ("Ramona",   "Co-co-COROCO!!!"),
]

# hp, velocidade (px/frame), escala do sprite, hitbox (w, h)
TIPOS = {
    "jovem":      {"hp": 1, "vel": 1.5,  "escala": 0.78, "hitbox": (84, 46)},
    "rapido":     {"hp": 1, "vel": 3.4,  "escala": 0.9,  "hitbox": (80, 44)},
    "forte":      {"hp": 3, "vel": 1.15, "escala": 1.18, "hitbox": (116, 64)},
    "sorrateiro": {"hp": 1, "vel": 2.2,  "escala": 0.95, "hitbox": (96, 52)},
    "lider":      {"hp": 6, "vel": 0.9,  "escala": 1.45, "hitbox": (150, 84)},
}

ONDAS = [
    {"nome": "Filhotes curiosos",  "fila": ["jovem"] * 5,  "max_tela": 2, "cd": 1.6},
    {"nome": "Velozes!",           "fila": ["rapido"] * 6, "max_tela": 3, "cd": 1.3},
    {"nome": "Bando misturado",
     "fila": ["jovem", "rapido", "forte", "rapido", "sorrateiro", "forte", "jovem", "rapido"],
     "max_tela": 3, "cd": 1.2},
    {"nome": "ATAQUE GRANDE!",
     "fila": ["rapido", "forte", "sorrateiro", "jovem", "rapido",
              "sorrateiro", "forte", "rapido", "jovem", "forte"],
     "max_tela": 5, "cd": 0.9},
    {"nome": "O LIDER DOS GAVIOES", "fila": ["lider"], "max_tela": 4, "cd": 1.0},
]

# Moitas onde as galinhas podem se esconder
MOITAS = [(245, 498), (855, 492)]


def _draw_gaviao_tipo(surf, gav):
    """Desenha o gaviao com escala/enfeite do tipo."""
    ix, iy = int(gav.x), int(gav.y)
    esc    = gav.cfg["escala"]
    swoop  = gav.y > 150 and gav.tipo != "lider"

    tmp = pygame.Surface((120, 70), pygame.SRCALPHA)
    spr.draw_gaviao(tmp, 60, 30, gav.frame, swooping=swoop)
    if gav.tipo == "sorrateiro":
        # Tom arroxeado: o dissimulado
        tint = pygame.Surface((120, 70), pygame.SRCALPHA)
        tint.fill((210, 170, 255, 255))
        tmp.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    if gav.hit_flash > 0 and gav.hp > 0:
        # Piscada branca ao levar clique sem morrer
        flash = pygame.Surface((120, 70), pygame.SRCALPHA)
        flash.fill((255, 255, 255, 130))
        tmp.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    if esc != 1.0:
        tmp = pygame.transform.scale(tmp, (int(120 * esc), int(70 * esc)))
    surf.blit(tmp, (ix - tmp.get_width() // 2, iy - int(30 * esc)))

    # Rastro do rapido
    if gav.tipo == "rapido":
        for i, (tx, ty) in enumerate(gav.rastro):
            a = 90 - i * 28
            if a > 0:
                s = pygame.Surface((30, 8), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (255, 255, 255, a), (0, 0, 30, 8))
                surf.blit(s, (int(tx) - 15, int(ty) - 4))

    # Coroa do lider
    if gav.tipo == "lider":
        cy = iy - int(30 * esc) - 4
        pygame.draw.polygon(surf, (255, 210, 40), [
            (ix - 16, cy + 12), (ix + 16, cy + 12), (ix + 14, cy),
            (ix + 7, cy + 8), (ix, cy - 4), (ix - 7, cy + 8), (ix - 14, cy)])
        pygame.draw.polygon(surf, (180, 140, 20), [
            (ix - 16, cy + 12), (ix + 16, cy + 12), (ix + 14, cy),
            (ix + 7, cy + 8), (ix, cy - 4), (ix - 7, cy + 8), (ix - 14, cy)], 2)

    # Pontos de vida (tipos com mais de 1)
    if gav.hp_max > 1 and gav.state == "flying":
        py = iy - int(34 * esc) - (16 if gav.tipo == "lider" else 0)
        for i in range(gav.hp_max):
            cor = (230, 60, 60) if i < gav.hp else (70, 70, 70)
            pygame.draw.circle(surf, cor, (ix - gav.hp_max * 6 + 6 + i * 12, py), 4)
            pygame.draw.circle(surf, WHITE, (ix - gav.hp_max * 6 + 6 + i * 12, py), 4, 1)


class Gaviao:
    def __init__(self, tipo, galinhas):
        self.tipo    = tipo
        self.cfg     = TIPOS[tipo]
        self.hp      = self.cfg["hp"]
        self.hp_max  = self.cfg["hp"]
        self.speed   = self.cfg["vel"] + random.uniform(0, 0.25)
        self.state   = "flying"   # flying | scared | pegou | leave
        self.anim    = 0.0
        self.frame   = 0
        self.hit_flash = 0.0
        self.rastro  = []         # posicoes antigas (rapido)
        self.zig_t   = random.uniform(0.5, 1.0)   # sorrateiro muda de rumo
        self.sum_t   = 2.0        # lider convoca reforcos
        self.alvo_i  = self._escolhe_alvo(galinhas)

        if tipo == "sorrateiro":
            # Surge por tras das arvores (lateral, altura da mata)
            lado   = random.choice((-1, 1))
            self.x = -60.0 if lado < 0 else SCREEN_W + 60.0
            self.y = float(random.randint(150, 260))
            self.vx = self.speed * (1 if lado < 0 else -1)
            self.vy = 0.4
        else:
            self.x = float(random.randint(120, SCREEN_W - 120))
            self.y = float(random.randint(-70, -15))
            self.vx, self.vy = 0.0, self.speed

    def _escolhe_alvo(self, galinhas):
        visiveis = [i for i, g in enumerate(galinhas) if g["estado"] != "escondida"]
        return random.choice(visiveis) if visiveis else -1

    def _persegue(self, galinhas, giro):
        """Curva a velocidade na direcao da galinha alvo (se visivel)."""
        if self.alvo_i < 0 or galinhas[self.alvo_i]["estado"] == "escondida":
            self.alvo_i = self._escolhe_alvo(galinhas)
        if self.alvo_i < 0:
            return   # todo mundo escondido: segue reto (vai embora)
        alvo = galinhas[self.alvo_i]
        dx, dy = alvo["x"] - self.x, alvo["y"] - self.y
        d = math.hypot(dx, dy) or 1
        self.vx += (dx / d * self.speed - self.vx) * giro
        self.vy += (dy / d * self.speed - self.vy) * giro
        n = math.hypot(self.vx, self.vy) or 1
        self.vx, self.vy = self.vx / n * self.speed, self.vy / n * self.speed

    def update(self, dt, galinhas):
        self.frame    += 1
        self.hit_flash = max(0.0, self.hit_flash - dt)

        if self.state == "flying":
            if self.tipo == "lider":
                # Chefe: paira em cima fazendo zigue-zague lento
                self.x += math.sin(self.frame * 0.02) * 2.2
                self.y += (150 - self.y) * 0.01 + math.sin(self.frame * 0.05) * 0.8
                self.x = max(150, min(SCREEN_W - 150.0, self.x))
            elif self.tipo == "sorrateiro":
                self.zig_t -= dt
                if self.zig_t <= 0:
                    # Muda de direcao sem avisar
                    self.zig_t = random.uniform(0.5, 1.1)
                    ang = random.uniform(0, 2 * math.pi)
                    self.vx = math.cos(ang) * self.speed
                    self.vy = abs(math.sin(ang)) * self.speed * 0.8 + 0.4
                self._persegue(galinhas, 0.02)
                self.x += self.vx
                self.y += self.vy
            else:
                giro = {"jovem": 0.06, "rapido": 0.05, "forte": 0.04}[self.tipo]
                self._persegue(galinhas, giro)
                self.x += self.vx
                self.y += self.vy
                if self.tipo == "rapido":
                    self.rastro.insert(0, (self.x - self.vx * 4, self.y - self.vy * 4))
                    del self.rastro[3:]
            # Sem alvo visivel e ja embaixo: desiste
            if self.y > SCREEN_H - 60:
                self.state = "leave"

        elif self.state == "scared":
            self.anim -= dt
            self.x += self.vx * -3
            self.y -= abs(self.vy) * 3 + 4

        elif self.state == "pegou":
            self.anim -= dt
            self.y -= 5   # sobe levando o susto

        elif self.state == "leave":
            self.y -= 6
            if self.y < -90:
                self.anim = -1
                self.state = "scared"   # marca para remocao

    @property
    def done(self):
        return self.state in ("scared", "pegou") and self.anim <= 0

    @property
    def rect(self):
        w, h = self.cfg["hitbox"]
        return pygame.Rect(int(self.x) - w // 2, int(self.y) - h // 2, w, h)

    def draw(self, surf):
        if self.state == "scared":
            ix, iy = int(self.x), int(self.y)
            tmp = pygame.Surface((120, 70), pygame.SRCALPHA)
            spr.draw_gaviao(tmp, 60, 30, self.frame, swooping=False)
            tmp = pygame.transform.flip(tmp, True, False)
            a = pygame.Surface((120, 70), pygame.SRCALPHA)
            a.fill((255, 80, 80, 160))
            tmp.blit(a, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(tmp, (ix - 60, iy - 30))
        else:
            _draw_gaviao_tipo(surf, self)

        if self.hit_flash > 0:
            fh = pygame.font.SysFont("Arial", 22, bold=True)
            ts = fh.render("XO!", True, (255, 80, 80))
            surf.blit(ts, (int(self.x) - ts.get_width() // 2, int(self.y) - 42))


class Fase1Scene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.dialog   = DialogBox()
        self.hud      = HUD()
        self.vfx      = VFX()
        self.frame    = 0
        self.state    = "intro"
        self.complete = False
        self.font_msg  = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_sub  = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_hud  = pygame.font.SysFont("Segoe UI", 20, bold=True)

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
        self.gavioes  = []
        self.score    = 0
        self.vidas    = VIDAS_INICIO
        self.onda_i   = 0
        self.fila     = []
        self.spawn_cd = 0.0
        self.banner_t = 0.0
        self.cluck_cd = 0.0
        # Galinhas vivas: correm, cacarejam e algumas se escondem
        self.galinhas = []
        for i, (hx, hy, cor, crista) in enumerate([
                (360, 460, (22, 22, 22),    WHITE),
                (450, 450, (245, 245, 240), RED),
                (540, 462, (245, 245, 240), RED),
                (630, 455, (165, 55, 40),   RED),
                (720, 458, (155, 155, 150), RED)]):
            self.galinhas.append({
                "home": (hx, hy), "x": float(hx), "y": float(hy),
                "cor": cor, "crista": crista,
                "estado": "calma",       # calma | panico | escondida
                "dir": (0.0, 0.0), "t": 0.0,
                "esconde": i in (0, 4),  # as das pontas preferem se esconder
            })
        self._comeca_onda(0)

    def _comeca_onda(self, i):
        self.onda_i   = i
        self.fila     = list(ONDAS[i]["fila"])
        self.banner_t = 2.2
        self.spawn_cd = 0.6
        snd.play('encaixe')
        self.hud.set_objective(f"Onda {i + 1}/{len(ONDAS)}", "Fase 1 - Xo Gaviao!")

    def _intro_done(self):
        self.state = "banner"

    # ----------------------------------------------------------------- events
    def handle_event(self, event):
        if self.dialog.handle_event(event):
            return
        if self.btn_menu.handle_event(event) and self.btn_menu.clicked:
            self.btn_menu.reset()
            self.manager.go_to("menu")

        if self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for gav in self.gavioes:
                    if gav.state == "flying" and gav.rect.collidepoint(mx, my):
                        self._acerta(gav)
                        break

        elif self.state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._reinicia()
                self.state = "banner"

        elif self.state == "complete" and self.complete:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.manager.go_to("fase2")

    def _acerta(self, gav):
        gav.hp -= 1
        gav.hit_flash = 0.3
        if gav.hp > 0:
            # Aguentou: recua um pouco
            snd.play('encaixe')
            gav.y -= 26
            self.vfx.burst(int(gav.x), int(gav.y), count=6,
                           colors=[(110, 75, 25), (200, 160, 60)],
                           speed=4, size=4, gravity=80)
            return
        gav.state = "scared"
        gav.anim  = 0.5
        self.score += 1
        snd.play('kill')
        self.vfx.burst(int(gav.x), int(gav.y), count=12,
                       colors=[(110, 75, 25), (90, 60, 20), (200, 160, 60)],
                       speed=5, size=5, gravity=80)
        self.vfx.flash((255, 255, 100), duration=0.08, alpha=60)
        if gav.tipo == "lider":
            # Chefe derrotado: o bando inteiro foge!
            self.vfx.fireworks(SCREEN_W, SCREEN_H)
            for outro in self.gavioes:
                if outro.state == "flying":
                    outro.state = "scared"
                    outro.anim  = 0.6

    # ----------------------------------------------------------------- update
    def update(self, dt):
        self.frame += 1
        self.dialog.update(dt)
        self.vfx.update(dt)
        self.cluck_cd = max(0.0, self.cluck_cd - dt)

        if self.state == "banner" and not self.dialog.active:
            self.banner_t -= dt
            self._update_galinhas(dt)
            if self.banner_t <= 0:
                self.state = "playing"
            return

        if self.state != "playing" or self.dialog.active:
            return

        onda = ONDAS[self.onda_i]

        # Spawn da fila da onda
        voando = len([g for g in self.gavioes if g.state == "flying"])
        self.spawn_cd -= dt
        if self.fila and self.spawn_cd <= 0 and voando < onda["max_tela"]:
            self.gavioes.append(Gaviao(self.fila.pop(0), self.galinhas))
            self.spawn_cd = onda["cd"]

        # Lider convoca reforcos enquanto vive
        for gav in self.gavioes:
            if gav.tipo == "lider" and gav.state == "flying":
                gav.sum_t -= dt
                reforcos = len([g for g in self.gavioes
                                if g.tipo == "jovem" and g.state == "flying"])
                if gav.sum_t <= 0 and reforcos < 3:
                    gav.sum_t = 3.5
                    novo = Gaviao("jovem", self.galinhas)
                    novo.x, novo.y = gav.x, gav.y + 20
                    self.gavioes.append(novo)
                    snd.play('zumbido')
                    self.vfx.stars(gav.x, gav.y + 30, color=(255, 210, 80))

        # Gavioes: voo + captura de galinha
        for gav in self.gavioes:
            gav.update(dt, self.galinhas)
            if gav.state != "flying":
                continue
            for gal in self.galinhas:
                if gal["estado"] == "escondida":
                    continue
                if math.hypot(gal["x"] - gav.x, gal["y"] - gav.y) < 26:
                    gav.state = "pegou"
                    gav.anim  = 0.7
                    self.vidas -= 1
                    snd.play('vida')
                    self.vfx.burst(int(gal["x"]), int(gal["y"]), count=14,
                                   colors=[(240, 240, 240), (200, 200, 200), (255, 120, 120)],
                                   speed=5, size=4, gravity=50)
                    gal["estado"] = "panico"
                    gal["t"] = 0.0
                    if self.vidas <= 0:
                        self.state = "game_over"
                        snd.play('erro')
                        snd.play('gameover')
                        return
                    break

        self.gavioes = [g for g in self.gavioes if not g.done]

        self._update_galinhas(dt)

        # Onda terminou?
        if not self.fila and not any(g.state == "flying" for g in self.gavioes):
            if self.onda_i + 1 < len(ONDAS):
                self._comeca_onda(self.onda_i + 1)
                self.state = "banner"
            else:
                self.state = "win_dialog"
                snd.play('complete')
                self.vfx.fireworks(SCREEN_W, SCREEN_H)
                self.dialog.show(DIALOGO_DONE, callback=self._done)

    def _update_galinhas(self, dt):
        """Panico das galinhas: correm do gaviao, cacarejam, se escondem."""
        for gal in self.galinhas:
            # Gaviao mais proximo (voando)
            perigo, pd = None, 1e9
            for gav in self.gavioes:
                if gav.state != "flying":
                    continue
                d = math.hypot(gav.x - gal["x"], gav.y - gal["y"])
                if d < pd:
                    perigo, pd = gav, d

            if gal["estado"] == "escondida":
                gal["t"] -= dt
                if gal["t"] <= 0 and (perigo is None or pd > 240):
                    gal["estado"] = "calma"
                    gal["x"] += random.choice((-26, 26))
                continue

            assustada = perigo is not None and pd < 150
            if assustada:
                gal["estado"] = "panico"
                if self.cluck_cd <= 0:
                    snd.play('cacarejo')
                    self.cluck_cd = 1.4
                # Medrosa perto da moita? Corre para ela
                if gal["esconde"]:
                    mx, my = min(MOITAS, key=lambda m: math.hypot(m[0] - gal["x"],
                                                                  m[1] - gal["y"]))
                    dx, dy = mx - gal["x"], my - gal["y"]
                    d = math.hypot(dx, dy) or 1
                    if d < 16:
                        gal["estado"] = "escondida"
                        gal["x"], gal["y"] = float(mx), float(my)
                        gal["t"] = random.uniform(2.5, 4.0)
                        continue
                    gal["dir"] = (dx / d, dy / d)
                else:
                    # Corre em zigue-zague para longe do gaviao
                    gal["t"] -= dt
                    if gal["t"] <= 0:
                        gal["t"] = random.uniform(0.22, 0.4)
                        ang = math.atan2(gal["y"] - perigo.y, gal["x"] - perigo.x)
                        ang += random.uniform(-0.9, 0.9)
                        gal["dir"] = (math.cos(ang), math.sin(ang) * 0.4)
                gal["x"] += gal["dir"][0] * 105 * dt
                gal["y"] += gal["dir"][1] * 105 * dt
            elif gal["estado"] == "panico":
                # Acalma e volta pra casa
                hx, hy = gal["home"]
                dx, dy = hx - gal["x"], hy - gal["y"]
                d = math.hypot(dx, dy)
                if d < 6:
                    gal["estado"] = "calma"
                else:
                    gal["x"] += dx / d * 40 * dt
                    gal["y"] += dy / d * 40 * dt

            gal["x"] = max(60.0, min(SCREEN_W - 60.0, gal["x"]))
            gal["y"] = max(425.0, min(505.0, gal["y"]))

    def _done(self):
        self.complete = True
        self.state    = "complete"

    # ----------------------------------------------------------------- draw
    def draw(self, screen):
        spr.draw_sitio_exterior(screen, self.frame)

        # Galinhas (as escondidas ficam atras das moitas)
        for gal in self.galinhas:
            if gal["estado"] != "escondida":
                tremida = 2 if gal["estado"] == "panico" else 0
                gx = int(gal["x"]) + random.randint(-tremida, tremida)
                spr.draw_galinha(screen, gx, int(gal["y"]),
                                 gal["cor"], gal["crista"], self.frame, small=True)
                if gal["estado"] == "panico" and (self.frame // 12) % 2 == 0:
                    f = pygame.font.SysFont("Arial", 13, bold=True)
                    t = f.render("co-co!", True, (255, 240, 120))
                    screen.blit(t, (gx - 14, int(gal["y"]) - 34))
        spr.draw_ramona(screen, 340, 515, self.frame)

        # Moitas (esconderijos) por cima das galinhas escondidas
        for mx, my in MOITAS:
            pygame.draw.ellipse(screen, (18, 82, 18), (mx - 46, my - 20, 92, 46))
            pygame.draw.ellipse(screen, (26, 106, 26), (mx - 34, my - 30, 68, 42))
            pygame.draw.ellipse(screen, (34, 126, 32), (mx - 18, my - 34, 40, 30))

        spr.draw_marina(screen, 160, 510, self.frame)
        spr.draw_papai(screen, 1050, 460, self.frame, tool=True)

        for gav in self.gavioes:
            gav.draw(screen)

        self.vfx.draw(screen)
        self._draw_hud(screen)

        # Banner da onda
        if self.state == "banner" and not self.dialog.active:
            i = self.onda_i
            t1  = self.font_msg.render(f"ONDA {i + 1}", True, YELLOW)
            t1s = self.font_msg.render(f"ONDA {i + 1}", True, BLACK)
            t2  = self.font_sub.render(ONDAS[i]["nome"], True, WHITE)
            screen.blit(t1s, t1s.get_rect(center=(SCREEN_W // 2 + 3, 233)))
            screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, 230)))
            screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, 280)))

        if self.state == "game_over":
            self._draw_game_over(screen)
        elif self.state == "complete" and self.complete:
            self._draw_complete(screen)

        self.hud.draw(screen)
        self.dialog.draw(screen)
        self.btn_menu.draw(screen)

    def _draw_hud(self, screen):
        vt = self.font_hud.render("Vidas:", True, WHITE)
        vs = self.font_hud.render("Vidas:", True, BLACK)
        screen.blit(vs, (17, 56))
        screen.blit(vt, (16, 55))
        for i in range(VIDAS_INICIO):
            col = (255, 220, 50) if i < self.vidas else (90, 90, 90)
            pygame.draw.circle(screen, col, (95 + i * 32, 66), 12)
            pygame.draw.circle(screen, WHITE, (95 + i * 32, 66), 12, 1)
        st = self.font_hud.render(f"Espantados: {self.score}", True, YELLOW)
        ss = self.font_hud.render(f"Espantados: {self.score}", True, BLACK)
        screen.blit(ss, (17, 84))
        screen.blit(st, (16, 83))

    def _draw_game_over(self, screen):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((40, 0, 0, 175))
        screen.blit(ov, (0, 0))
        fb = pygame.font.SysFont("Segoe UI", 60, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 26)
        t1 = fb.render("OS GAVIOES VENCERAM!", True, (255, 110, 100))
        t2 = fs.render(f"Voce chegou ate a onda {self.onda_i + 1} de {len(ONDAS)}.", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 55)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10)))
        if (self.frame // 30) % 2 == 0:
            t3 = fs.render("Clique para tentar de novo", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 60)))

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
                         (SCREEN_W // 2 - 370, SCREEN_H // 2 - 120, 740, 255), border_radius=18)
        pygame.draw.rect(screen, (78, 215, 78),
                         (SCREEN_W // 2 - 370, SCREEN_H // 2 - 120, 740, 255), 3, border_radius=18)
        fb = pygame.font.SysFont("Segoe UI", 58, bold=True)
        fs = pygame.font.SysFont("Segoe UI", 26)
        t1 = fb.render("FASE 1 COMPLETA!", True, YELLOW)
        t2 = fs.render(f"5 ondas vencidas e {self.score} gavioes espantados!", True, WHITE)
        screen.blit(t1, t1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 65)))
        screen.blit(t2, t2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))
        if (self.frame // 35) % 2 == 0:
            t3 = fs.render("Clique para continuar ->", True, GRAY)
            screen.blit(t3, t3.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 58)))
        spr.draw_ramona(screen, SCREEN_W // 2 - 40, SCREEN_H // 2 + 160, self.frame)
        spr.draw_white(screen,  SCREEN_W // 2 + 40, SCREEN_H // 2 + 155, self.frame)
