import pygame
from constants import *

CHAR_DELAY = 0.025  # segundos por letra


class DialogBox:
    def __init__(self):
        self.active      = False
        self.lines       = []
        self.index       = 0
        self.callback    = None
        self._name       = ""
        self._text       = ""
        self._count      = 0
        self._timer      = 0.0
        self.box_rect    = pygame.Rect(40, SCREEN_H - 185, SCREEN_W - 80, 165)
        self._fonts_ready = False

    def _ensure_fonts(self):
        if self._fonts_ready:
            return
        for fname in ("Segoe UI", "Arial", "Calibri"):
            try:
                self.fn = pygame.font.SysFont(fname, 22, bold=True)
                self.ft = pygame.font.SysFont(fname, 20)
                self.fh = pygame.font.SysFont(fname, 15)
                self._fonts_ready = True
                return
            except Exception:
                pass
        self.fn = pygame.font.Font(None, 24)
        self.ft = pygame.font.Font(None, 22)
        self.fh = pygame.font.Font(None, 18)
        self._fonts_ready = True

    def show(self, lines, callback=None):
        self._ensure_fonts()
        self.lines    = lines
        self.index    = 0
        self.active   = True
        self.callback = callback
        self._load()

    def _load(self):
        name, text = self.lines[self.index][0], self.lines[self.index][1]
        self._name  = name
        self._text  = text
        self._count = 0
        self._timer = 0.0

    def advance(self):
        if self._count < len(self._text):
            self._count = len(self._text)
        else:
            self.index += 1
            if self.index >= len(self.lines):
                self.active = False
                if self.callback:
                    self.callback()
            else:
                self._load()

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.advance()
            return True
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_z):
            self.advance()
            return True
        return False

    def update(self, dt):
        if not self.active or self._count >= len(self._text):
            return
        self._timer += dt
        add = int(self._timer / CHAR_DELAY)
        if add:
            self._count = min(self._count + add, len(self._text))
            self._timer %= CHAR_DELAY

    def draw(self, screen):
        if not self.active:
            return
        self._ensure_fonts()

        # Fundo semi-transparente
        bg = pygame.Surface((self.box_rect.w, self.box_rect.h), pygame.SRCALPHA)
        bg.fill((20, 15, 5, 230))
        screen.blit(bg, self.box_rect.topleft)
        pygame.draw.rect(screen, DIALOG_BORDER, self.box_rect, 2, border_radius=8)

        # Nome do personagem
        color = CHAR_COLORS.get(self._name, DIALOG_NAME)
        ns = self.fn.render(self._name, True, color)
        screen.blit(ns, (self.box_rect.x + 16, self.box_rect.y + 10))

        # Separador
        pygame.draw.line(screen, DIALOG_BORDER,
                         (self.box_rect.x + 10,  self.box_rect.y + 38),
                         (self.box_rect.right - 10, self.box_rect.y + 38), 1)

        # Texto com quebra de linha
        visible = self._text[:self._count]
        self._draw_wrapped(screen, visible,
                           self.box_rect.x + 16, self.box_rect.y + 48,
                           self.box_rect.w - 32)

        # Dica piscando
        if self._count >= len(self._text):
            if (pygame.time.get_ticks() // 400) % 2 == 0:
                hint = self.fh.render("clique ou [Espaco] para continuar", True, GRAY)
                screen.blit(hint, (self.box_rect.right - hint.get_width() - 12,
                                   self.box_rect.bottom - 20))

    def _draw_wrapped(self, screen, text, x, y, max_w):
        words = text.split(" ")
        line  = ""
        cy    = y
        lh    = self.ft.get_linesize() + 2
        for word in words:
            test = line + word + " "
            if self.ft.size(test)[0] > max_w and line:
                screen.blit(self.ft.render(line.rstrip(), True, DIALOG_TEXT), (x, cy))
                cy  += lh
                line = word + " "
            else:
                line = test
        if line.strip():
            screen.blit(self.ft.render(line.rstrip(), True, DIALOG_TEXT), (x, cy))
