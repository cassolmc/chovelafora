import pygame
from constants import *


class Button:
    def __init__(self, rect, text, color=GREEN, hover_color=None,
                 text_color=WHITE, font_size=28):
        self.rect        = pygame.Rect(rect)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color or tuple(min(c + 50, 255) for c in color)
        self.text_color  = text_color
        self.font        = pygame.font.SysFont("Segoe UI", font_size, bold=True)
        self.hovered     = False
        self.clicked     = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False

    def draw(self, screen):
        c = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, c, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)
        surf = self.font.render(self.text, True, self.text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def reset(self):
        self.clicked = False


class ProgressBar:
    def __init__(self, rect, color=GREEN, bg=DARK_GRAY):
        self.rect  = pygame.Rect(rect)
        self.value = 0.0
        self.color = color
        self.bg    = bg

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg, self.rect, border_radius=4)
        fw = int(self.rect.w * max(0.0, min(1.0, self.value)))
        if fw > 0:
            pygame.draw.rect(screen, self.color,
                             pygame.Rect(self.rect.x, self.rect.y, fw, self.rect.h),
                             border_radius=4)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=4)


class Hotspot:
    """Area clicavel invisivel numa cena."""
    def __init__(self, rect, label=""):
        self.rect    = pygame.Rect(rect)
        self.label   = label
        self.hovered = False
        self.clicked = False

    def update_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False

    def reset(self):
        self.clicked = False

    def draw_outline(self, screen, color=(255, 255, 0)):
        if self.hovered:
            pygame.draw.rect(screen, color, self.rect, 2, border_radius=4)


class HUD:
    def __init__(self):
        self._fonts_ready = False
        self.objective    = ""
        self.phase_name   = ""

    def _ensure_fonts(self):
        if self._fonts_ready:
            return
        self.font = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self._fonts_ready = True

    def set_objective(self, text, phase=""):
        self.objective  = text
        self.phase_name = phase

    def draw(self, screen):
        if not self.objective:
            return
        self._ensure_fonts()
        bar = pygame.Surface((SCREEN_W, 44), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 160))
        screen.blit(bar, (0, 0))
        if self.phase_name:
            ps = self.font.render(self.phase_name, True, YELLOW)
            screen.blit(ps, (16, 12))
        os_ = self.font.render("Objetivo: " + self.objective, True, WHITE)
        screen.blit(os_, (SCREEN_W - os_.get_width() - 16, 12))
