from terrain import *
from visual import *

# GAME SETUP & CONST VALUES
GAME_TITLE = "K-NIGHT"
WIDTH, HEIGHT = 640, 360
FPS = 60
PLAYER_VEL = 7

# INITIALIZE
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT),)  # pygame.SCALED | pygame.FULLSCREEN
pygame.display.set_caption(GAME_TITLE)

# HEARTS
heart_full = pygame.image.load("assets/GUI/full_heart.png").convert_alpha()
heart_full = pygame.transform.scale2x(heart_full)
NO_HEART = pygame.image.load("assets/GUI/no_heart.png").convert_alpha()
NO_HEART = pygame.transform.scale2x(NO_HEART)
HEARTS = [heart_full, NO_HEART]

# SHAKE EFFECT
camera = Shake()

# SCROLL & OFFSET
SCROLL_AREA_WIDTH = 250
SCROLL_AREA_HEIGHT = 250

# BLOCK SIZE
BLOCK_SIZE = 48

# BACKGROUND
BACKGROUND_LAYER_0 = "Background_0.png"
BACKGROUND_LAYER_1 = "Background_1.png"

# TILEMAP
OBJECTS = get_map(read_csv(), BLOCK_SIZE)

# PLAYER INITIAL POSITION
PLAYER_START_X = 100
PLAYER_START_Y = 1000
PLAYER_WIDTH = 120
PLAYER_HEIGHT = 60

# BOSS INITIAL POSITION
BOSS_START_X = 1500
BOSS_START_Y = 81
BOSS_WIDTH = 288
BOSS_HEIGHT = 160

"""
# FLOOR
FLOOR_BLOCKS = [i * BLOCK_SIZE for i in range(-WIDTH // BLOCK_SIZE, (WIDTH * 4) // BLOCK_SIZE)]
FLOOR_Y = HEIGHT - BLOCK_SIZE

# OBJECTS & BLOCKS

OBJECTS = [
    *[Block(x + 900, FLOOR_Y, BLOCK_SIZE) for x in FLOOR_BLOCKS[0:41]],
    Block(100, 0, BLOCK_SIZE)
]
"""
