import pygame
import math
from engine.scene_manager import Scene
from engine.ui import Button
import engine.sounds as snd
from constants import *
import characters.sprites as spr


class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.frame   = 0
        self.buttons = []

    def on_enter(self):
        snd.musica_stop()
        self.frame = 0

        self.font_title = pygame.font.SysFont("Segoe UI", 68, bold=True)
        self.font_sub   = pygame.font.SysFont("Segoe UI", 28)

        self.btn_jogar = Button(
            (SCREEN_W // 2 - 150, SCREEN_H // 2 + 55, 300, 62),
            "JOGAR", (55, 155, 55),
        )
        self.btn_sair = Button(
            (SCREEN_W // 2 - 150, SCREEN_H // 2 + 137, 300, 52),
            "Sair", DARK_GRAY,
        )
        self.buttons = [self.btn_jogar, self.btn_sair]

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

        if self.btn_jogar.clicked:
            self.btn_jogar.reset()
            self.manager.go_to("fase1")

        if self.btn_sair.clicked:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt):
        self.frame += 1

    def draw(self, screen):
        # Fundo desenhado: o sitio real (sem fotos)
        spr.draw_sitio_exterior(screen, self.frame)

        # Ramona e White desenhados no primeiro plano do menu
        spr.draw_ramona(screen, 130, 560, self.frame)
        spr.draw_white(screen,  210, 545, self.frame)

        # Algumas galinhas genericas
        spr.draw_galinha(screen, 1100, 570, (245, 245, 240), RED,         self.frame, small=True)
        spr.draw_galinha(screen, 1155, 580, (180, 100, 55),  RED,         self.frame, small=True)
        spr.draw_galinha(screen, 1050, 585, (160, 160, 155), (180, 30, 30), self.frame, small=True)

        # Marina acenando no lado direito
        spr.draw_marina(screen, 1150, 490, self.frame)

        # Papai trabalhando ao fundo (pequeno)
        spr.draw_papai(screen, 280, 430, self.frame, tool=True)

        # Painel centrado (nao cobre toda a largura)
        pw, ph2 = 820, 218
        panel = pygame.Surface((pw, ph2), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 0))
        pygame.draw.rect(panel, (8, 8, 8, 148), (0, 0, pw, ph2), border_radius=16)
        screen.blit(panel, (SCREEN_W // 2 - pw // 2, SCREEN_H // 2 - 118))

        # Titulo com sombra
        title = "Sitio Chove La Fora"
        sh = self.font_title.render(title, True, BLACK)
        ts = self.font_title.render(title, True, (255, 238, 70))
        tx = SCREEN_W // 2 - ts.get_width() // 2
        screen.blit(sh, (tx + 3, SCREEN_H // 2 - 105 + 3))
        screen.blit(ts, (tx,     SCREEN_H // 2 - 105))

        # Sub-titulo
        sub = self.font_sub.render("As Aventuras de Marina e Ramona", True, (240, 240, 240))
        screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))

        # Botoes
        for btn in self.buttons:
            btn.draw(screen)

        # Versao
        fv = pygame.font.SysFont("Arial", 14)
        vt = fv.render("v0.1", True, GRAY)
        screen.blit(vt, (SCREEN_W - vt.get_width() - 10, SCREEN_H - 22))
