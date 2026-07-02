"""Gera os icones do PWA (Ramona no gramado) - rodar uma vez: python web/gen_icons.py"""
import os
import sys
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
pygame.init()
pygame.display.set_mode((64, 64))
import characters.sprites as spr

AQUI = os.path.dirname(os.path.abspath(__file__))

# Base 512x512: ceu -> grama, sol, Ramona gigante em pixel art
icon = pygame.Surface((512, 512))
for y in range(512):
    t = y / 512
    if t < 0.62:
        c = (int(110 + 60 * t), int(175 + 40 * t), int(225 + 15 * t))
    else:
        c = (74, 150, 52)
    pygame.draw.line(icon, c, (0, y), (512, y))
pygame.draw.rect(icon, (64, 140, 44), (0, 318, 512, 194))
pygame.draw.circle(icon, (255, 235, 140), (420, 92), 52)
pygame.draw.circle(icon, (255, 245, 190), (420, 92), 40)

# Ramona desenhada pequena e ampliada (pixel art crisp)
mini = pygame.Surface((88, 88), pygame.SRCALPHA)
spr.draw_ramona(mini, 44, 52, frame=0, bobbing=False)
big = pygame.transform.scale(mini, (440, 440))
icon.blit(big, (36, 60))

pygame.image.save(icon, os.path.join(AQUI, "icon-512.png"))
pygame.image.save(pygame.transform.smoothscale(icon, (192, 192)),
                  os.path.join(AQUI, "icon-192.png"))

# Sprite da Ramona com fundo transparente (tela de abertura do site)
sprite = pygame.Surface((88, 88), pygame.SRCALPHA)
spr.draw_ramona(sprite, 44, 52, frame=0, bobbing=False)
pygame.image.save(sprite, os.path.join(AQUI, "splash-ramona.png"))
print("icones gerados em", AQUI)
