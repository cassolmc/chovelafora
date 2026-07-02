import os

SCREEN_W = 1280
SCREEN_H = 600
FPS      = 60
TITLE    = "Sitio Chove La Fora"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Cores base
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0  )
GRAY       = (150, 150, 150)
DARK_GRAY  = (80,  80,  80 )
RED        = (220, 50,  50 )
GREEN      = (80,  180, 80 )
DARK_GREEN = (30,  100, 30 )
BLUE       = (50,  100, 220)
YELLOW     = (255, 220, 50 )
ORANGE     = (255, 140, 0  )
PINK       = (255, 150, 180)
LIGHT_PINK = (255, 200, 210)
BROWN      = (139, 90,  43 )
DARK_BROWN = (80,  50,  20 )
SKIN       = (255, 220, 177)
CREAM      = (255, 253, 230)
LIGHT_BLUE = (135, 206, 235)
PURPLE     = (150, 50,  200)

# Dialog
DIALOG_BG     = (20,  15,  5  )
DIALOG_BORDER = (200, 170, 100)
DIALOG_TEXT   = (255, 245, 220)
DIALOG_NAME   = (255, 220, 100)

# Cor por personagem no dialogo
CHAR_COLORS = {
    "Marina":   (255, 220, 100),
    "Mamae":    (255, 160, 200),
    "Papai":    (100, 180, 255),
    "Ramona":   (180, 255, 180),
    "Gilson":   (255, 190, 100),
    "Grazi":    (220, 180, 255),
    "Marcela":  (180, 230, 255),
    "Narrador": (200, 200, 200),
}
