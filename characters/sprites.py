"""
Sprites do jogo Sitio Chove La Fora.
Todos desenhados por codigo - sem imagens externas.
Referencias visuais: fotos reais do sitio, da Ramona e da White.
"""
import pygame
import math
from constants import *


def _bzpt(p0, p1, p2, t):
    """Ponto em curva de Bezier quadratica."""
    x = (1-t)**2 * p0[0] + 2*(1-t)*t * p1[0] + t**2 * p2[0]
    y = (1-t)**2 * p0[1] + 2*(1-t)*t * p1[1] + t**2 * p2[1]
    return int(x), int(y)


# ---------------------------------------------------------------------------
# RAMONA - galinha preta pequena, penas MUITO fofas, topete punk branco/preto
# ---------------------------------------------------------------------------
def draw_ramona(surf, x, y, frame=0, bobbing=True):
    bob = int(math.sin(frame * 0.18) * 2) if bobbing else 0
    y += bob

    # Sombra
    pygame.draw.ellipse(surf, (0, 0, 0), (x - 12, y + 12, 24, 7))

    # Cauda: penas eretas e abertas
    for ang, length in [(-155, 14), (-170, 16), (-145, 12), (-135, 10)]:
        r  = math.radians(ang)
        ex = x + int(math.cos(r) * length)
        ey = y + int(math.sin(r) * length * 0.8)
        pygame.draw.line(surf, (20, 20, 20), (x - 6, y - 2), (ex, ey), 3)

    # Corpo principal: penas fofas e irregulares (muito volumoso)
    # Camadas de fora pra dentro para dar profundidade
    for radius_x, radius_y, col in [(15, 13, (20, 20, 20)), (13, 11, (28, 28, 28)), (11, 9, (35, 35, 35))]:
        body_pts = []
        for i in range(18):
            angle = i * (2 * math.pi / 18)
            # Penas fofas: raio irregular
            noise = math.sin(angle * 4 + frame * 0.04) * 2.5
            rx = (radius_x + noise) * math.cos(angle)
            ry = (radius_y + noise * 0.6) * math.sin(angle)
            body_pts.append((x + int(rx), y + int(ry)))
        pygame.draw.polygon(surf, col, body_pts)

    # Textura de penas: pequenas linhas saindo do corpo
    for i in range(10):
        ang   = i * (2 * math.pi / 10) + 0.2
        fx    = x + int(math.cos(ang) * 11)
        fy    = y + int(math.sin(ang) * 8)
        ex    = x + int(math.cos(ang) * 15)
        ey    = y + int(math.sin(ang) * 12)
        pygame.draw.line(surf, (15, 15, 15), (fx, fy), (ex, ey), 2)

    # Mancha branco-acinzentada no peito (como na foto)
    pygame.draw.ellipse(surf, (150, 145, 138), (x - 5, y + 1, 10, 8))
    pygame.draw.ellipse(surf, (130, 125, 118), (x - 3, y + 3, 7, 5))

    # Asa: ligeiramente visivel, com textura
    flutter = int(math.sin(frame * 0.22) * 1)
    pygame.draw.ellipse(surf, (40, 40, 40), (x - 7, y - 3 + flutter, 16, 9))
    pygame.draw.ellipse(surf, (50, 50, 50), (x - 5, y - 1 + flutter, 10, 5))

    # Pescoco curto (quase escondido pelas penas)
    pygame.draw.ellipse(surf, (22, 22, 22), (x - 4, y - 15, 9, 10))

    # Cabeca: redonda, preta, com penas fofas
    pygame.draw.circle(surf, (20, 20, 20), (x + 1, y - 19), 9)
    # Penas irregulares na cabeca
    for i in range(6):
        ang = i * (math.pi / 3)
        hx2 = x + 1 + int(math.cos(ang) * 9)
        hy2 = y - 19 + int(math.sin(ang) * 7)
        pygame.draw.circle(surf, (25, 25, 25), (hx2, hy2), 3)

    # TOPETE PUNK: grande, selvagem, mistura preto e branco
    # Penas pretas de base (mais longas, apontando em varias direcoes)
    topete_preto = [
        (-5, -26, -25, 14), (-2, -28, -10, 16), (1, -30, 0, 18),
        (4, -28,  10, 15),  (7, -25, 25, 12),   (-8, -23, -40, 10),
    ]
    for ox, oy, ang_deg, ln in topete_preto:
        r  = math.radians(ang_deg - 90)
        ex = x + ox + int(math.cos(r) * ln)
        ey = y + oy + int(math.sin(r) * ln)
        pygame.draw.line(surf, (15, 15, 15), (x + ox, y + oy), (ex, ey), 3)

    # Penas brancas/creme no centro do topete (o punk)
    topete_branco = [
        (-1, -28, -8,  14), (2, -30, 2,  16), (4, -27, 12, 12),
    ]
    for ox, oy, ang_deg, ln in topete_branco:
        r  = math.radians(ang_deg - 90)
        ex = x + ox + int(math.cos(r) * ln)
        ey = y + oy + int(math.sin(r) * ln)
        pygame.draw.line(surf, (220, 210, 195), (x + ox, y + oy), (ex, ey), 2)

    # Penas intermediarias cinza-claro
    topete_cinza = [(-3, -26, -18, 11), (6, -25, 18, 10)]
    for ox, oy, ang_deg, ln in topete_cinza:
        r  = math.radians(ang_deg - 90)
        ex = x + ox + int(math.cos(r) * ln)
        ey = y + oy + int(math.sin(r) * ln)
        pygame.draw.line(surf, (170, 160, 150), (x + ox, y + oy), (ex, ey), 2)

    # Bico: pequeno, amarelo-alaranjado
    pygame.draw.polygon(surf, (210, 155, 45), [
        (x + 8, y - 20), (x + 15, y - 19), (x + 8, y - 16),
    ])

    # Olho: pequeno, alaranjado-ambar
    pygame.draw.circle(surf, (195, 125, 25), (x + 5, y - 20), 2)
    pygame.draw.circle(surf, BLACK,           (x + 5, y - 20), 1)
    pygame.draw.circle(surf, WHITE,           (x + 4, y - 21), 1)

    # Patas: laranjas, curtas, quase escondidas sob o corpo fofo
    pygame.draw.line(surf, (200, 115, 25), (x - 3, y + 11), (x - 4, y + 18), 2)
    pygame.draw.line(surf, (200, 115, 25), (x + 4, y + 11), (x + 5, y + 18), 2)
    # Garras
    pygame.draw.line(surf, (175, 95, 20), (x - 4, y + 18), (x - 9, y + 21), 2)
    pygame.draw.line(surf, (175, 95, 20), (x - 4, y + 18), (x - 2, y + 22), 1)
    pygame.draw.line(surf, (175, 95, 20), (x + 5, y + 18), (x + 10, y + 21), 2)
    pygame.draw.line(surf, (175, 95, 20), (x + 5, y + 18), (x + 3,  y + 22), 1)


# ---------------------------------------------------------------------------
# WHITE - galo branco limpo, crista vermelha grande, postura ereta
# ---------------------------------------------------------------------------
def draw_white(surf, x, y, frame=0):
    bob = int(math.sin(frame * 0.15) * 1)
    y += bob

    # Sombra
    pygame.draw.ellipse(surf, (0, 0, 0), (x - 14, y + 18, 28, 8))

    # Cauda: penas brancas arqueadas (mais alta que o corpo)
    tail_pts = [
        (x - 12, y - 2), (x - 22, y - 22), (x - 18, y - 4),
        (x - 26, y - 16), (x - 15, y - 3), (x - 24, y - 9), (x - 12, y - 1),
    ]
    pygame.draw.polygon(surf, (242, 242, 238), tail_pts)
    pygame.draw.polygon(surf, (225, 225, 220), tail_pts, 1)

    # Corpo: oval branco, mais ereto que Ramona
    pygame.draw.ellipse(surf, (245, 245, 242), (x - 13, y - 5, 26, 22))
    pygame.draw.ellipse(surf, (235, 235, 230), (x - 13, y - 5, 26, 22), 1)

    # Asa
    flutter = int(math.sin(frame * 0.2) * 1)
    pygame.draw.ellipse(surf, (238, 238, 234), (x - 9, y - 2 + flutter, 18, 12))

    # Pescoco mais longo
    pygame.draw.ellipse(surf, (243, 243, 240), (x - 4, y - 17, 10, 14))

    # Cabeca
    pygame.draw.circle(surf, (245, 245, 242), (x + 1, y - 22), 10)

    # CRISTA VERMELHA (grande, de galo adulto)
    crista = [
        (x - 3, y - 29), (x - 5, y - 38), (x - 1, y - 31),
        (x + 1, y - 40), (x + 4, y - 32), (x + 5, y - 39),
        (x + 7, y - 30), (x + 6, y - 26),
    ]
    pygame.draw.polygon(surf, (200, 35, 35), crista)

    # Barbela vermelha (embaixo do bico)
    pygame.draw.ellipse(surf, (200, 35, 35), (x - 3, y - 17, 10, 9))

    # Bico: amarelo, robusto
    pygame.draw.polygon(surf, (215, 160, 45), [
        (x + 8, y - 23), (x + 17, y - 22), (x + 8, y - 18),
    ])

    # Olho: alaranjado
    pygame.draw.circle(surf, (195, 120, 25), (x + 5, y - 23), 3)
    pygame.draw.circle(surf, BLACK,           (x + 5, y - 23), 1)
    pygame.draw.circle(surf, WHITE,           (x + 4, y - 24), 1)

    # Patas: laranja, mais longas que Ramona
    wl = int(math.sin(frame * 0.2) * 2)
    wr = -wl
    pygame.draw.line(surf, (195, 125, 25), (x - 3, y + 15), (x - 3 + wl, y + 24 + wl), 2)
    pygame.draw.line(surf, (195, 125, 25), (x + 4, y + 15), (x + 4 + wr, y + 24 - wr), 2)
    pygame.draw.line(surf, (175, 105, 20), (x - 3 + wl, y + 24 + wl), (x - 8 + wl, y + 27 + wl), 2)
    pygame.draw.line(surf, (175, 105, 20), (x + 4 + wr, y + 24 - wr), (x + 9 + wr, y + 27 - wr), 2)


# ---------------------------------------------------------------------------
# MARINA - menina loira, 8 anos, vestido rosa
# ---------------------------------------------------------------------------
def draw_marina(surf, x, y, frame=0):
    # Sombra
    pygame.draw.ellipse(surf, (0, 0, 0), (x - 13, y + 36, 26, 8))

    # Pernas
    pygame.draw.rect(surf, SKIN, (x - 6, y + 22, 5, 14))
    pygame.draw.rect(surf, SKIN, (x + 2, y + 22, 5, 14))
    pygame.draw.rect(surf, DARK_BROWN, (x - 8, y + 33, 7, 5))
    pygame.draw.rect(surf, DARK_BROWN, (x + 2, y + 33, 7, 5))

    # Vestido rosa
    pygame.draw.polygon(surf, PINK, [
        (x - 7, y + 8), (x + 7, y + 8),
        (x + 12, y + 24), (x - 12, y + 24),
    ])
    pygame.draw.rect(surf, LIGHT_PINK, (x - 5, y - 2, 10, 12))

    # Braccos
    swing = int(math.sin(frame * 0.12) * 4)
    pygame.draw.line(surf, SKIN, (x - 5, y + 2),  (x - 15, y + 14 + swing), 4)
    pygame.draw.line(surf, SKIN, (x + 5, y + 2),  (x + 15, y + 14 - swing), 4)

    # Pescoco + Cabeca
    pygame.draw.rect(surf, SKIN, (x - 3, y - 4, 6, 6))
    pygame.draw.circle(surf, SKIN, (x, y - 12), 13)

    # Cabelo loiro com rabos-de-cavalo
    pygame.draw.circle(surf, YELLOW, (x, y - 17), 13)
    pygame.draw.rect(surf, YELLOW,   (x - 13, y - 18, 26, 10))
    pygame.draw.circle(surf, YELLOW, (x - 15, y - 10), 5)
    pygame.draw.circle(surf, YELLOW, (x + 15, y - 10), 5)
    pygame.draw.rect(surf, PINK, (x - 16, y - 13, 4, 6))
    pygame.draw.rect(surf, PINK, (x + 12, y - 13, 4, 6))

    # Olhos azuis
    pygame.draw.circle(surf, (70, 130, 200), (x - 4, y - 12), 3)
    pygame.draw.circle(surf, (70, 130, 200), (x + 4, y - 12), 3)
    pygame.draw.circle(surf, BLACK, (x - 3, y - 13), 1)
    pygame.draw.circle(surf, BLACK, (x + 5, y - 13), 1)
    pygame.draw.circle(surf, WHITE, (x - 5, y - 14), 1)
    pygame.draw.circle(surf, WHITE, (x + 3, y - 14), 1)

    # Sorriso + sardas
    pygame.draw.arc(surf, (200, 80, 80), (x - 4, y - 10, 8, 5), math.pi * 1.1, math.pi * 1.9, 2)
    pygame.draw.circle(surf, (200, 140, 100), (x - 6, y - 9), 1)
    pygame.draw.circle(surf, (200, 140, 100), (x + 6, y - 9), 1)


# ---------------------------------------------------------------------------
# PAPAI JEAN - homem magro, camisa clara, calcas escuras, roçadeira
# ---------------------------------------------------------------------------
def draw_papai(surf, x, y, frame=0, tool=True):
    # Sombra
    pygame.draw.ellipse(surf, (0, 0, 0), (x - 16, y + 44, 32, 10))

    # Calcas escuras (jeans)
    pygame.draw.rect(surf, (55, 75, 120), (x - 8, y + 26, 7, 20))
    pygame.draw.rect(surf, (55, 75, 120), (x + 2, y + 26, 7, 20))
    # Botas marrons
    pygame.draw.rect(surf, DARK_BROWN, (x - 10, y + 42, 9, 7))
    pygame.draw.rect(surf, DARK_BROWN, (x + 2,  y + 42, 9, 7))

    # Camisa clara (como na foto - branca/azul claro)
    pygame.draw.rect(surf, (220, 228, 235), (x - 8, y + 4, 16, 24))
    # Botoes da camisa
    for bi in range(3):
        pygame.draw.circle(surf, (180, 185, 190), (x, y + 8 + bi * 6), 1)

    # Roçadeira (ferramenta caracteristica do Jean na foto)
    if tool:
        # Cabo longo
        tool_ang = int(math.sin(frame * 0.08) * 5)
        tx1, ty1 = x + 10, y + 18
        tx2 = tx1 + int(math.cos(math.radians(100 + tool_ang)) * 40)
        ty2 = ty1 + int(math.sin(math.radians(100 + tool_ang)) * 40)
        pygame.draw.line(surf, (100, 65, 30), (tx1, ty1), (tx2, ty2), 4)
        # Cabecote da rocadeira
        pygame.draw.ellipse(surf, (130, 130, 130), (tx2 - 8, ty2 - 4, 16, 8))

    # Braccos
    sw = int(math.sin(frame * 0.12) * 3)
    pygame.draw.line(surf, SKIN, (x - 7, y + 8),  (x - 18, y + 22 + sw), 5)
    pygame.draw.line(surf, SKIN, (x + 7, y + 8),  (x + 18, y + 22 - sw), 5)

    # Pescoco + Cabeca (homem magro, rosto mais fino)
    pygame.draw.rect(surf, SKIN, (x - 3, y, 7, 8))
    pygame.draw.ellipse(surf, SKIN, (x - 11, y - 22, 23, 24))

    # Cabelo escuro / entradas
    pygame.draw.arc(surf, (55, 38, 18), (x - 11, y - 30, 23, 20), 0, math.pi, 6)

    # Barba por fazer (como na foto)
    pygame.draw.rect(surf, (95, 68, 45), (x - 7, y - 10, 14, 7))

    # Olhos
    pygame.draw.ellipse(surf, (55, 38, 18), (x - 6, y - 18, 5, 4))
    pygame.draw.ellipse(surf, (55, 38, 18), (x + 2,  y - 18, 5, 4))


# ---------------------------------------------------------------------------
# MAMAE MELINA - mulher com avental
# ---------------------------------------------------------------------------
def draw_mamae(surf, x, y, frame=0):
    pygame.draw.ellipse(surf, (0, 0, 0), (x - 13, y + 38, 26, 8))

    pygame.draw.rect(surf, SKIN, (x - 5, y + 22, 5, 14))
    pygame.draw.rect(surf, SKIN, (x + 1, y + 22, 5, 14))
    pygame.draw.rect(surf, (120, 60, 100), (x - 7, y + 32, 7, 7))
    pygame.draw.rect(surf, (120, 60, 100), (x + 1, y + 32, 7, 7))

    pygame.draw.polygon(surf, (180, 80, 140), [
        (x - 8, y + 8), (x + 8, y + 8), (x + 14, y + 24), (x - 14, y + 24),
    ])
    pygame.draw.rect(surf, (200, 100, 160), (x - 6, y - 2, 12, 12))
    # Avental
    pygame.draw.rect(surf, CREAM, (x - 5, y + 4, 10, 16))

    sw = int(math.sin(frame * 0.12) * 3)
    pygame.draw.line(surf, SKIN, (x - 6, y + 4), (x - 16, y + 16 + sw), 4)
    pygame.draw.line(surf, SKIN, (x + 6, y + 4), (x + 16, y + 16 - sw), 4)

    pygame.draw.rect(surf, SKIN, (x - 3, y - 4, 6, 6))
    pygame.draw.circle(surf, SKIN, (x, y - 12), 13)

    # Cabelo castanho preso (coque)
    pygame.draw.circle(surf, (115, 68, 28), (x, y - 16), 13)
    pygame.draw.rect(surf, (115, 68, 28), (x - 10, y - 18, 20, 8))
    pygame.draw.circle(surf, (115, 68, 28), (x, y - 24), 7)

    pygame.draw.circle(surf, (80, 50, 20), (x - 4, y - 12), 3)
    pygame.draw.circle(surf, (80, 50, 20), (x + 4, y - 12), 3)
    pygame.draw.arc(surf, (180, 60, 80), (x - 4, y - 9, 8, 5), math.pi * 1.1, math.pi * 1.9, 2)


# ---------------------------------------------------------------------------
# GALINHA GENERICA
# ---------------------------------------------------------------------------
def draw_galinha(surf, x, y, body_color, crest_color=RED, frame=0, small=False):
    s   = 0.7 if small else 1.0
    bob = int(math.sin(frame * 0.18 + x * 0.01) * 1)
    y  += bob

    bw, bh = int(18 * s), int(14 * s)
    pygame.draw.ellipse(surf, body_color, (x - bw // 2, y - bh // 2, bw, bh))

    hx, hy, hr = x + int(9 * s), y - int(7 * s), int(6 * s)
    pygame.draw.circle(surf, body_color, (hx, hy), hr)

    pygame.draw.polygon(surf, crest_color, [
        (hx - 2, hy - hr), (hx - 1, hy - hr - 5), (hx + 1, hy - hr - 2),
        (hx + 2, hy - hr - 6), (hx + 4, hy - hr),
    ])
    pygame.draw.polygon(surf, ORANGE, [
        (hx + hr, hy), (hx + hr + 5, hy + 1), (hx + hr, hy + 3),
    ])
    pygame.draw.circle(surf, BLACK, (hx + 2, hy - 1), 2)

    for ang in (150, 165):
        r  = math.radians(ang)
        ex = x + int(math.cos(r) * (bw // 2 + 4))
        ey = y + int(math.sin(r) * (bh // 2 + 2))
        pygame.draw.line(surf, body_color, (x - bw // 4, y), (ex, ey), 2)

    pygame.draw.line(surf, ORANGE, (x - 2, y + bh // 2), (x - 2, y + bh // 2 + 6), 2)
    pygame.draw.line(surf, ORANGE, (x + 4, y + bh // 2), (x + 4, y + bh // 2 + 6), 2)


# ---------------------------------------------------------------------------
# FUNDO: SITIO CHOVE LA FORA  (desenhado, sem fotos)
# Baseado nas fotos reais: casa branca telhado escuro, gramado verde intenso,
# galpao de madeira a direita, carro prata Fiat, floresta densa, muro de pedra
# ---------------------------------------------------------------------------
def draw_sitio_exterior(surf, frame=0):
    w = surf.get_width()
    h = surf.get_height()

    # ------------------------------------------------------------------ CEU
    sky_h = 318
    for sy in range(sky_h):
        t   = sy / sky_h
        col = (int(95 + 118 * t), int(158 + 68 * t), int(215 + 25 * t))
        pygame.draw.line(surf, col, (0, sy), (w, sy))

    # Nuvens (duas camadas de elipses sobrepostas, movimento lento)
    cloud_ox = int((frame * 0.22) % (w + 400)) - 200
    for ccx, ccy, cr in [(cloud_ox, 52, 46), (cloud_ox + 260, 78, 34),
                         (cloud_ox + 560, 46, 54), (cloud_ox + 900, 68, 40)]:
        cl = (238, 242, 248)
        pygame.draw.ellipse(surf, cl, (ccx - cr,       ccy - cr // 2, cr * 2,       cr))
        pygame.draw.ellipse(surf, cl, (ccx - cr // 2,  ccy - cr,      cr,            cr))
        pygame.draw.ellipse(surf, cl, (ccx + cr // 4,  ccy - cr * 3 // 4, cr * 3 // 2, cr * 3 // 4))

    # ------------------------------------------------------------------ FLORESTA (fundo)
    morro = [
        (0, 270), (0, 192), (70, 162), (190, 178), (310, 145),
        (460, 166), (618, 142), (765, 160), (920, 140), (1065, 165),
        (1215, 148), (w, 156), (w, 270),
    ]
    pygame.draw.polygon(surf, (18, 56, 14), morro)
    # Arvores sobre o morro
    for tx in range(-30, w + 60, 48):
        th  = 50 + (tx * 7 % 5) * 13
        ty  = 145 + (tx * 3 % 7) * 4
        col = (14 + (tx % 3) * 5, 50 + (tx % 4) * 8, 12)
        pygame.draw.rect(surf, (48, 28, 8), (tx + 22, ty + th // 2, 7, th // 2))
        pygame.draw.circle(surf, col, (tx + 26, ty + th // 3), th // 3)

    # ------------------------------------------------------------------ GRAMADO
    # Começa em y=268 para tapar a faixa cinza do horizonte (ceu termina em y=317)
    pygame.draw.rect(surf, (48, 112, 32), (0, 268, w, h - 268))
    pygame.draw.rect(surf, (64, 140, 44), (0, 290, w, h - 290))
    pygame.draw.rect(surf, (76, 154, 52), (0, 310, w, 28))
    for gx in range(0, w, 15):
        pygame.draw.line(surf, (48, 118, 34), (gx,      332), (gx + 3,  323), 1)
        pygame.draw.line(surf, (48, 118, 34), (gx + 7,  332), (gx + 10, 322), 1)

    # ------------------------------------------------------------------ CAMINHO DE TERRA
    # Trapezio: largo na base da tela, estreito no horizonte
    path = [(72, h), (210, h), (340, 356), (200, 356)]
    pygame.draw.polygon(surf, (148, 116, 72), path)
    for pi in range(6):
        py2 = h - 20 - pi * 28
        frac = pi / 6
        x1 = int(72  + frac * (200 - 72))
        x2 = int(210 + frac * (340 - 210))
        pygame.draw.line(surf, (132, 102, 60), (x1, py2), (x2, py2), 1)

    # ------------------------------------------------------------------ ENTRADA DO SITIO (esquerda)
    pl, pr = 62, 202   # x dos postes
    pt     = 238       # y do topo do poste

    # Postes grossos de madeira
    for px2 in (pl, pr):
        pygame.draw.rect(surf, (92, 58, 22), (px2 - 9, pt, 22, 125), border_radius=3)
        pygame.draw.rect(surf, (68, 42, 14), (px2 - 9, pt, 22, 125), 1, border_radius=3)
        # Chapeu do poste
        pygame.draw.polygon(surf, (72, 45, 14),
            [(px2 - 12, pt), (px2 + 14, pt), (px2 + 9, pt - 16), (px2 - 7, pt - 16)])

    # Viga horizontal com placa
    pygame.draw.rect(surf, (82, 52, 18), (pl - 9, pt - 22, pr - pl + 40, 22), border_radius=4)
    pygame.draw.rect(surf, (58, 36, 10), (pl - 9, pt - 22, pr - pl + 40, 22), 1, border_radius=4)
    # Plaquinha com nome
    fb_s = pygame.font.SysFont("Arial", 14, bold=True)
    tl   = fb_s.render("SITIO", True, (225, 192, 72))
    surf.blit(tl, (pl + 30, pt - 18))

    # Travessa X dentro do portao (sem barras horizontais)
    pygame.draw.line(surf, (72, 46, 16), (pl + 10, pt + 20), (pr - 10, pt + 110), 3)
    pygame.draw.line(surf, (72, 46, 16), (pr - 10, pt + 20), (pl + 10, pt + 110), 3)

    # ------------------------------------------------------------------ CASA (centro)
    hx, hy, hw, hh = 448, 188, 316, 178

    # Sombra base
    pygame.draw.ellipse(surf, (42, 110, 30), (hx - 8, hy + hh + 2, hw + 16, 14))

    # Paredes
    pygame.draw.rect(surf, (246, 246, 243), (hx, hy, hw, hh))
    pygame.draw.rect(surf, (218, 218, 214), (hx, hy, hw, hh), 1)

    # Telhado ceramica escura (duas aguas)
    ridge_x1 = hx + 28
    ridge_x2 = hx + hw - 28
    ridge_y  = hy - 90
    roof_pts = [(hx - 20, hy), (hx + hw + 20, hy), (ridge_x2, ridge_y), (ridge_x1, ridge_y)]
    pygame.draw.polygon(surf, (46, 46, 52), roof_pts)
    # Ripas do telhado (linhas sutis)
    for ri in range(5):
        frac = (ri + 1) / 6
        lx1 = int(hx - 20 + frac * (ridge_x1 - (hx - 20)))
        lx2 = int(hx + hw + 20 - frac * (hx + hw + 20 - ridge_x2))
        ly  = int(hy + frac * (ridge_y - hy))
        pygame.draw.line(surf, (36, 36, 42), (lx1, ly), (lx2, ly), 1)
    pygame.draw.line(surf, (60, 60, 68), (ridge_x1, ridge_y), (ridge_x2, ridge_y), 3)
    pygame.draw.polygon(surf, (60, 60, 68), roof_pts, 2)

    # Chamine
    pygame.draw.rect(surf, (162, 145, 128), (hx + 72, hy - 118, 28, 42))
    pygame.draw.rect(surf, (182, 162, 145), (hx + 68, hy - 122, 36, 10), border_radius=2)

    # Janelas com venezianas verdes
    for wx in [hx + 30, hx + 200]:
        # veneziana esq
        pygame.draw.rect(surf, (38, 92, 38), (wx - 12, hy + 42, 11, 56), border_radius=2)
        for sl in range(4):
            pygame.draw.line(surf, (28, 72, 28),
                (wx - 12, hy + 48 + sl * 12), (wx - 1, hy + 52 + sl * 12), 2)
        # vidro
        pygame.draw.rect(surf, (162, 202, 228), (wx, hy + 42, 60, 56))
        pygame.draw.rect(surf, (190, 195, 200), (wx, hy + 42, 60, 56), 2)
        pygame.draw.line(surf, (190, 195, 200), (wx + 30, hy + 42), (wx + 30, hy + 98), 1)
        pygame.draw.line(surf, (190, 195, 200), (wx, hy + 70), (wx + 60, hy + 70), 1)
        # veneziana dir
        pygame.draw.rect(surf, (38, 92, 38), (wx + 60, hy + 42, 11, 56), border_radius=2)
        for sl in range(4):
            pygame.draw.line(surf, (28, 72, 28),
                (wx + 61, hy + 48 + sl * 12), (wx + 71, hy + 52 + sl * 12), 2)

    # Porta vermelha com arco
    pygame.draw.rect(surf, (162, 38, 28), (hx + 128, hy + 108, 62, 70))
    pygame.draw.ellipse(surf, (162, 38, 28), (hx + 128, hy + 96, 62, 30))
    pygame.draw.rect(surf, (130, 28, 20), (hx + 128, hy + 108, 62, 70), 2)
    pygame.draw.ellipse(surf, (130, 28, 20), (hx + 128, hy + 96, 62, 30), 2)
    pygame.draw.rect(surf, (138, 30, 22), (hx + 133, hy + 115, 22, 26), 1)
    pygame.draw.rect(surf, (138, 30, 22), (hx + 163, hy + 115, 22, 26), 1)
    pygame.draw.circle(surf, (200, 168, 48), (hx + 155, hy + 148), 4)

    # Canteiros de flores embaixo das janelas
    for wx in [hx + 18, hx + 188]:
        pygame.draw.rect(surf, (108, 68, 30), (wx, hy + hh - 4, 80, 12), border_radius=3)
        flower_cols = [(218, 72, 72), (255, 205, 40), (215, 112, 195), (72, 175, 72)]
        for fi, fx2 in enumerate(range(wx + 6, wx + 74, 14)):
            pygame.draw.circle(surf, flower_cols[fi % 4], (fx2, hy + hh - 9), 5)
            pygame.draw.circle(surf, (255, 240, 80), (fx2, hy + hh - 9), 2)

    # Arbusto lateral esq
    pygame.draw.ellipse(surf, (34, 105, 30), (hx - 32, hy + hh - 36, 48, 36))
    pygame.draw.ellipse(surf, (28, 90, 24),  (hx - 26, hy + hh - 50, 38, 28))
    # Arbusto lateral dir
    pygame.draw.ellipse(surf, (34, 105, 30), (hx + hw - 16, hy + hh - 36, 48, 36))
    pygame.draw.ellipse(surf, (28, 90, 24),  (hx + hw - 10, hy + hh - 50, 38, 28))

    # ------------------------------------------------------------------ GALPAO (direita)
    gax, gay, gaw, gah = 820, 210, 345, 172

    # Interior escuro (profundidade)
    pygame.draw.rect(surf, (28, 18, 6), (gax, gay, gaw, gah))

    # Fardos de feno - pilhas arredondadas, nao blocos
    for fi in range(3):
        bx2 = gax + 22 + fi * 58
        by2 = gay + gah - 48
        pygame.draw.ellipse(surf, (140, 105, 30), (bx2 - 2, by2 + 14, 44, 22))  # base
        pygame.draw.ellipse(surf, (155, 118, 35), (bx2,     by2,      40, 30))  # meio
        pygame.draw.ellipse(surf, (168, 132, 42), (bx2 + 4, by2 - 10, 32, 22))  # topo
        pygame.draw.ellipse(surf, (125, 92,  24), (bx2,     by2,      40, 30), 1)
    # Roda de madeira no fundo
    pygame.draw.circle(surf, (80, 50, 18), (gax + gaw - 65, gay + gah - 44), 32, 5)
    for ai in range(6):
        a2 = math.radians(ai * 60)
        pygame.draw.line(surf, (80, 50, 18),
            (gax + gaw - 65, gay + gah - 44),
            (gax + gaw - 65 + int(math.cos(a2) * 28),
             gay + gah - 44 + int(math.sin(a2) * 28)), 3)
    # Ferramentas penduradas
    for ti, tx2 in enumerate([gax + 220, gax + 258, gax + 296]):
        pygame.draw.line(surf, (90, 58, 20), (tx2, gay + 18), (tx2 + (ti - 1) * 4, gay + 100), 4)
        pygame.draw.ellipse(surf, (115, 75, 28), (tx2 - 10, gay + 14, 20, 10))

    # Pilares de madeira (frente do galpao)
    for pilx in range(gax, gax + gaw + 1, gaw // 5):
        pygame.draw.rect(surf, (102, 66, 24), (pilx - 7, gay - 18, 17, gah + 34), border_radius=2)
        pygame.draw.rect(surf, (76, 48, 15),  (pilx - 7, gay - 18, 17, gah + 34), 1, border_radius=2)

    # Telhado do galpao (duas aguas, mais robusto)
    g_rdg_y  = gay - 78
    g_rdg_x1 = gax + 20
    g_rdg_x2 = gax + gaw - 20
    gteto = [(gax - 18, gay), (gax + gaw + 18, gay), (g_rdg_x2, g_rdg_y), (g_rdg_x1, g_rdg_y)]
    pygame.draw.polygon(surf, (82, 50, 16), gteto)
    for ri in range(5):
        frac = (ri + 1) / 6
        lx1 = int(gax - 18 + frac * (g_rdg_x1 - (gax - 18)))
        lx2 = int(gax + gaw + 18 - frac * (gax + gaw + 18 - g_rdg_x2))
        ly  = int(gay + frac * (g_rdg_y - gay))
        pygame.draw.line(surf, (62, 36, 10), (lx1, ly), (lx2, ly), 1)
    pygame.draw.line(surf, (115, 72, 24), (g_rdg_x1, g_rdg_y), (g_rdg_x2, g_rdg_y), 4)
    pygame.draw.polygon(surf, (60, 36, 10), gteto, 2)
    # Viga de base do galpao
    pygame.draw.rect(surf, (92, 60, 20), (gax - 18, gay + gah, gaw + 36, 12), border_radius=2)

    # Lenha empilhada (lado esquerdo do galpao)
    for li in range(7):
        pygame.draw.rect(surf, (94, 54, 20),
            (gax - 90 + li * 2, 384 + li, 72, 12), border_radius=2)
    for li in range(6):
        pygame.draw.rect(surf, (76, 42, 16),
            (gax - 88 + li * 2, 373 + li, 68, 10), border_radius=2)

    # Vaso de planta laranja (frente do galpao)
    pygame.draw.ellipse(surf, (188, 90, 36), (gax + 28, gay + gah - 32, 30, 26))
    pygame.draw.ellipse(surf, (155, 68, 26), (gax + 28, gay + gah - 32, 30, 26), 2)
    pygame.draw.ellipse(surf, (32, 120, 32), (gax + 26, gay + gah - 50, 34, 22))

    # ------------------------------------------------------------------ POSTE + FIO DE LUZ
    pole_x = hx + hw // 2
    pygame.draw.line(surf, (78, 52, 22), (pole_x, hy - 95), (pole_x, 375), 4)
    pygame.draw.line(surf, (78, 52, 22), (pole_x - 22, hy - 90), (pole_x + 22, hy - 90), 4)
    pygame.draw.line(surf, (68, 68, 72), (0, 112), (pole_x, hy - 88), 1)
    pygame.draw.line(surf, (68, 68, 72), (pole_x, hy - 88), (w, 118),  1)
    pygame.draw.circle(surf, (88, 88, 92), (pole_x - 22, hy - 90), 3)
    pygame.draw.circle(surf, (88, 88, 92), (pole_x + 22, hy - 90), 3)

    # ------------------------------------------------------------------ ARBUSTOS FRENTE
    for bx2, by2, br2 in [(36, 372, 20), (58, 378, 16), (78, 370, 13),
                           (1194, 374, 18), (1218, 380, 14), (1240, 372, 12)]:
        pygame.draw.ellipse(surf, (36, 102, 30),
            (bx2 - br2, by2 - br2 // 2, br2 * 2, int(br2 * 1.3)))


# ---------------------------------------------------------------------------
# GAVIAO - predador, asas largas, bico curvo (antagonista recorrente)
# ---------------------------------------------------------------------------
def draw_gaviao(surf, x, y, frame=0, swooping=False):
    flap = int(math.sin(frame * 0.35) * 10)

    # Cauda
    pygame.draw.polygon(surf, (88, 56, 16), [
        (x - 5, y + 6), (x - 10, y + 20), (x + 10, y + 20), (x + 5, y + 6),
    ])

    # Asas
    for side in (-1, 1):
        if swooping:
            wing = [
                (x + side * 8, y), (x + side * 40, y + 16 + flap // 2),
                (x + side * 26, y + 5), (x, y + 5),
            ]
        else:
            wing = [
                (x + side * 8, y), (x + side * 44, y - 5 + flap),
                (x + side * 28, y + 5), (x, y + 5),
            ]
        pygame.draw.polygon(surf, (78, 50, 14), wing)
        pygame.draw.polygon(surf, (58, 38, 10), wing, 1)

    # Corpo
    pygame.draw.ellipse(surf, (105, 68, 22), (x - 9, y - 5, 18, 14))

    # Cabeca
    pygame.draw.circle(surf, (118, 82, 26), (x, y - 9), 8)

    # Bico curvo de rapina
    pygame.draw.polygon(surf, (198, 165, 38), [
        (x + 5, y - 11), (x + 15, y - 7), (x + 7, y - 4),
    ])
    pygame.draw.polygon(surf, (165, 135, 28), [
        (x + 7, y - 8), (x + 14, y - 6), (x + 8, y - 4),
    ])

    # Olho amarelo de predador
    pygame.draw.circle(surf, (218, 178, 0), (x + 4, y - 9), 3)
    pygame.draw.circle(surf, BLACK,          (x + 4, y - 9), 1)

    # Garras (quando atacando)
    if swooping:
        for gx in (x - 4, x + 4):
            pygame.draw.line(surf, (178, 142, 28), (gx, y + 8),  (gx - 2, y + 18), 2)
            pygame.draw.line(surf, (178, 142, 28), (gx, y + 18), (gx - 5, y + 23), 2)
            pygame.draw.line(surf, (178, 142, 28), (gx, y + 18), (gx + 3, y + 23), 2)


# ---------------------------------------------------------------------------
# OVO - varios tipos (normal, azul da Ganiza, ruim)
# ---------------------------------------------------------------------------
def draw_ovo(surf, x, y, tipo="normal"):
    if tipo == "azul":
        col, col2 = (118, 172, 208), (92, 145, 182)
    elif tipo == "ruim":
        col, col2 = (138, 98, 58), (108, 76, 40)
    else:
        col, col2 = (228, 212, 188), (202, 185, 162)

    pygame.draw.ellipse(surf, col,  (x - 8, y - 11, 16, 20))
    pygame.draw.ellipse(surf, col2, (x - 8, y - 11, 16, 20), 1)
    # Brilho
    pygame.draw.ellipse(surf, tuple(min(c + 40, 255) for c in col), (x - 5, y - 9, 7, 6))

    if tipo == "ruim":
        pts = [(x - 2, y - 4), (x + 2, y - 9), (x, y - 2), (x + 3, y + 3)]
        pygame.draw.lines(surf, (78, 48, 18), False, pts, 1)
    elif tipo == "azul":
        for dx, dy in [(-3, -3), (2, -5), (-1, 2), (3, 1)]:
            pygame.draw.circle(surf, (68, 118, 158), (x + dx, y + dy), 1)


# ---------------------------------------------------------------------------
# GATO DO MATO - antagonista, marrom-acinzentado
# ---------------------------------------------------------------------------
def draw_gato(surf, x, y, frame=0):
    bob = int(math.sin(frame * 0.2) * 1)
    y  += bob

    pygame.draw.ellipse(surf, (0, 0, 0), (x - 16, y + 14, 32, 8))

    # Corpo
    pygame.draw.ellipse(surf, (110, 88, 60), (x - 16, y - 8, 32, 22))

    # Cabeca
    pygame.draw.circle(surf, (115, 92, 64), (x, y - 14), 12)

    # Orelhas pontudas
    pygame.draw.polygon(surf, (110, 88, 58), [(x - 9, y - 24), (x - 15, y - 12), (x - 3, y - 12)])
    pygame.draw.polygon(surf, (110, 88, 58), [(x + 9, y - 24), (x + 15, y - 12), (x + 3, y - 12)])
    pygame.draw.polygon(surf, (180, 130, 130), [(x - 8, y - 22), (x - 12, y - 13), (x - 4, y - 13)])
    pygame.draw.polygon(surf, (180, 130, 130), [(x + 8, y - 22), (x + 12, y - 13), (x + 4, y - 13)])

    # Olhos (pupila vertical de gato)
    for ox in (-4, 4):
        pygame.draw.circle(surf, (180, 148, 30), (x + ox, y - 14), 3)
        pygame.draw.rect(surf, BLACK, (x + ox - 1, y - 17, 2, 6))

    # Bigodes
    for by in (-15, -12):
        pygame.draw.line(surf, (220, 220, 220), (x - 4, y + by), (x - 18, y + by - 1), 1)
        pygame.draw.line(surf, (220, 220, 220), (x + 4, y + by), (x + 18, y + by - 1), 1)

    # Bico/nariz
    pygame.draw.circle(surf, (200, 100, 100), (x, y - 12), 2)

    # Rabo (curvado)
    rabo_pts = []
    for i in range(10):
        t   = i / 9
        rx  = x + 14 + int(t * 20)
        ry  = y + int(math.sin(t * math.pi + frame * 0.1) * 14) - 5
        rabo_pts.append((rx, ry))
    if len(rabo_pts) > 1:
        pygame.draw.lines(surf, (105, 84, 58), False, rabo_pts, 3)

    # Patas
    pygame.draw.ellipse(surf, (108, 86, 58), (x - 14, y + 10, 10, 8))
    pygame.draw.ellipse(surf, (108, 86, 58), (x + 4,  y + 10, 10, 8))


# ---------------------------------------------------------------------------
# COBRA - antagonista rastejante
# ---------------------------------------------------------------------------
def draw_cobra(surf, x, y, frame=0):
    # Corpo ondulado
    pts = []
    for i in range(10):
        off = int(math.sin(frame * 0.12 + i * 0.9) * 7)
        pts.append((x - i * 12, y + off))
    if len(pts) > 1:
        pygame.draw.lines(surf, (38, 112, 38), False, pts, 12)
        pygame.draw.lines(surf, (28, 90, 28),  False, pts, 10)
    # Cabeca
    pygame.draw.ellipse(surf, (42, 118, 42), (x + 4, y - 6, 14, 12))
    # Olhos
    pygame.draw.circle(surf, (220, 50, 50), (x + 12, y - 3), 3)
    pygame.draw.circle(surf, BLACK,          (x + 12, y - 3), 1)
    # Lingua bifurcada
    lx = x + 17
    pygame.draw.line(surf, (200, 40, 40), (lx, y + 2), (lx + 6, y + 5), 1)
    pygame.draw.line(surf, (200, 40, 40), (lx, y + 2), (lx + 6, y - 1), 1)


# ---------------------------------------------------------------------------
# UTILITARIO: texto com fundo escuro
# ---------------------------------------------------------------------------
def draw_banana_bunch(surf, x, y, frame=0):
    """Cacho de bananas - curvas de Bezier, visualmente reconheciveis."""
    bob = int(math.sin(frame * 0.07) * 2)
    y  += bob

    jx, jy = x, y + 14   # juncao: onde as bananas saem do engaco

    # (angulo_spread_graus, comprimento, curvatura_lateral)
    bananas = [
        (-40, 28, 13),
        (-20, 33, 7),
        (  0, 35, 1),
        ( 20, 33, 7),
        ( 40, 28, 13),
    ]
    draw_order = [0, 4, 1, 3, 2]   # centro por cima

    for bi in draw_order:
        spread_deg, length, curve = bananas[bi]
        sr = math.radians(spread_deg)

        ex = jx + int(math.sin(sr) * length)
        ey = jy + int(math.cos(sr) * length)

        sign = 1 if spread_deg > 0 else (-1 if spread_deg < 0 else 0)
        # Ponto de controle curva a banana para fora
        cx2 = (jx + ex) // 2 + sign * curve
        cy2 = (jy + ey) // 2 - 5

        # Desenha banana como tracos circulares ao longo da curva de Bezier
        steps = 14
        for i in range(steps + 1):
            t = i / steps
            px, py = _bzpt((jx, jy), (cx2, cy2), (ex, ey), t)
            r = max(1, int(6.5 * math.sin(t * math.pi) + 1))
            shade = int(22 * t)
            col = (max(0, 232 - shade), max(0, 208 - shade*2), 18)
            pygame.draw.circle(surf, col, (px, py), r)

        # Contorno escuro
        outline = [_bzpt((jx, jy), (cx2, cy2), (ex, ey), i/9) for i in range(10)]
        if len(outline) > 1:
            pygame.draw.lines(surf, (175, 145, 8), False, outline, 1)

        # Ponta escura
        pygame.draw.circle(surf, (55, 34, 6), (ex, ey), 2)

    # Engaco (talo grosso de cima ate a juncao)
    pygame.draw.line(surf, (62, 40, 10), (x, y - 4), (jx, jy), 5)
    pygame.draw.circle(surf, (52, 32, 6), (jx, jy), 6)
    # Raminho superior
    pygame.draw.line(surf, (52, 38, 10), (x, y - 4), (x + 4, y - 14), 3)
    pygame.draw.circle(surf, (42, 62, 12), (x + 4, y - 14), 4)


def draw_gilson(surf, x, y, frame=0, has_banana=False):
    """Gilson - irmaon do Papai, camisa laranja, bigode, carrega bananas."""
    sw = int(math.sin(frame * 0.12) * 3)

    # Sombra
    pygame.draw.ellipse(surf, (0, 0, 0), (x - 16, y + 44, 32, 10))

    # Calcas
    pygame.draw.rect(surf, (65, 55, 35), (x - 8, y + 26, 7, 20))
    pygame.draw.rect(surf, (65, 55, 35), (x + 2,  y + 26, 7, 20))
    pygame.draw.rect(surf, (80, 55, 25), (x - 10, y + 42, 9, 7))
    pygame.draw.rect(surf, (80, 55, 25), (x + 2,  y + 42, 9, 7))

    # Camisa laranja
    pygame.draw.rect(surf, (220, 110, 30), (x - 8, y + 4, 16, 24))

    if has_banana:
        # Braco direito levantado segurando bananas
        pygame.draw.line(surf, SKIN, (x - 7, y + 8), (x - 22, y + sw), 5)
        pygame.draw.line(surf, SKIN, (x + 7, y + 8), (x + 16, y + 22 - sw), 5)
        draw_banana_bunch(surf, x - 26, y - 10, frame)
    else:
        pygame.draw.line(surf, SKIN, (x - 7, y + 8), (x - 18, y + 22 + sw), 5)
        pygame.draw.line(surf, SKIN, (x + 7, y + 8), (x + 18, y + 22 - sw), 5)

    # Pescoco + Cabeca
    pygame.draw.rect(surf, SKIN, (x - 3, y, 7, 8))
    pygame.draw.ellipse(surf, SKIN, (x - 11, y - 22, 23, 24))

    # Cabelo castanho escuro
    pygame.draw.arc(surf, (65, 40, 15), (x - 11, y - 30, 23, 20), 0, math.pi, 7)

    # Bigode
    pygame.draw.ellipse(surf, (80, 50, 20), (x - 8, y - 9, 16, 5))

    # Olhos
    pygame.draw.ellipse(surf, (55, 38, 18), (x - 6, y - 18, 5, 4))
    pygame.draw.ellipse(surf, (55, 38, 18), (x + 2,  y - 18, 5, 4))


def draw_label(surf, font, text, x, y, color=WHITE, bg=(0, 0, 0)):
    s  = font.render(text, True, color)
    bx = x - s.get_width() // 2 - 3
    pygame.draw.rect(surf, bg, (bx, y - 2, s.get_width() + 6, s.get_height() + 2))
    surf.blit(s, (x - s.get_width() // 2, y))
