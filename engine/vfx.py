"""Sistema de efeitos visuais: particulas e flash de tela."""
import pygame
import math
import random


class VFX:
    def __init__(self):
        self._p = []   # particulas: [x,y,vx,vy,t,t0,r,g,b,radius,gravity]
        self._f = []   # flashes:    [r,g,b,alpha,t,t0]

    # ------------------------------------------------------------------ API
    def burst(self, x, y, count=14, colors=None, speed=5.0, size=5, gravity=70):
        """Explosao de particulas."""
        if colors is None:
            colors = [(255, 220, 50), (255, 140, 40), (255, 80, 80)]
        for _ in range(count):
            ang = random.uniform(0, 2 * math.pi)
            sp  = random.uniform(speed * 0.45, speed)
            col = random.choice(colors)
            sz  = random.uniform(size * 0.4, size)
            t   = random.uniform(0.28, 0.65)
            self._p.append([float(x), float(y),
                            math.cos(ang) * sp, math.sin(ang) * sp,
                            t, t, *col, sz, gravity])

    def stars(self, x, y, count=8, color=(255, 250, 140)):
        """Faiscas em estrela (para ovos)."""
        r, g, b = color
        for i in range(count):
            ang = i * (2 * math.pi / count) + random.uniform(-0.2, 0.2)
            sp  = random.uniform(1.5, 4.0)
            t   = random.uniform(0.28, 0.48)
            self._p.append([float(x), float(y),
                            math.cos(ang) * sp, math.sin(ang) * sp,
                            t, t, r, g, b, random.uniform(2, 5), 0])

    def fireworks(self, screen_w, screen_h, count=3):
        """Tres explosoes espalhadas (fim de fase)."""
        positions = [
            (screen_w // 2, screen_h // 3),
            (screen_w // 4, screen_h // 4),
            (3 * screen_w // 4, screen_h // 4),
        ]
        palettes = [
            [(255, 220, 50), (255, 255, 140)],
            [(100, 200, 255), (140, 230, 255)],
            [(255, 120, 120), (255, 200, 140)],
        ]
        for (px, py), pal in zip(positions, palettes):
            self.burst(px, py, count=22, colors=pal, speed=7, size=6, gravity=45)

    def flash(self, color, duration=0.18, alpha=125):
        """Overlay de cor sobre a tela inteira (breve)."""
        r, g, b = color
        self._f.append([r, g, b, alpha, duration, duration])

    # ------------------------------------------------------------------ loop
    def update(self, dt):
        for p in self._p:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += p[10] * dt   # gravity
            p[4] -= dt
        self._p = [p for p in self._p if p[4] > 0]

        for f in self._f:
            f[4] -= dt
        self._f = [f for f in self._f if f[4] > 0]

    def draw(self, screen):
        for x, y, vx, vy, t, t0, r, g, b, radius, grav in self._p:
            frac   = t / t0
            alpha  = int(255 * frac)
            rad    = max(1, int(radius * frac))
            s = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (r, g, b, alpha), (rad + 1, rad + 1), rad)
            screen.blit(s, (int(x) - rad - 1, int(y) - rad - 1))

        if self._f:
            w, h = screen.get_size()
            for r, g, b, alpha_max, t, t0 in self._f:
                alpha = int(alpha_max * t / t0)
                s = pygame.Surface((w, h), pygame.SRCALPHA)
                s.fill((r, g, b, alpha))
                screen.blit(s, (0, 0))

    def clear(self):
        self._p.clear()
        self._f.clear()
