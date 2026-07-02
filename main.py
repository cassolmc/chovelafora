import asyncio
import pygame
import sys

from constants import *
import engine.sounds as snd
from engine.scene_manager import SceneManager
from scenes.menu import MenuScene
from scenes.fase1_bom_dia import Fase1Scene
from scenes.fase2_galinheiro import Fase2Scene
from scenes.fase3_doentes import Fase3Scene
from scenes.fase4_ovos import Fase4Scene
from scenes.fase5_anoitecer import Fase5Scene


async def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    snd.init()

    flags  = pygame.SCALED
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
    pygame.display.set_caption(TITLE)

    clock = pygame.time.Clock()

    manager = SceneManager(screen)
    manager.register("menu",  MenuScene)
    manager.register("fase1", Fase1Scene)
    manager.register("fase2", Fase2Scene)
    manager.register("fase3", Fase3Scene)
    manager.register("fase4", Fase4Scene)
    manager.register("fase5", Fase5Scene)

    manager.go_to("menu")

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                manager.go_to("menu")
            manager.handle_event(event)

        manager.update(dt)
        manager.draw()
        pygame.display.flip()

        await asyncio.sleep(0)


asyncio.run(main())
