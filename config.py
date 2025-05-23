from terrain import *
from effects import *
from sprite_cutter import *
"""POMEMBNO ČE ŽELITE FULLSCREEN DODAJTE ARGUMENTA, KI JIH VIDITE V KOMENTARJU POD WINDOW """


# GAME SETUP & CONST VALUES
GAME_TITLE = "K-NIGHT"
WIDTH, HEIGHT = 640, 360
FPS = 60
PLAYER_VEL = 7

# INITIALIZE DISPLAY
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT),)
# USE THIS IF YOU WANT FULLSCREEN. ADD AS AN ARGUMENT IN WINDOW: pygame.SCALED | pygame.FULLSCREEN
pygame.display.set_caption(GAME_TITLE)

# INITIALIZE MIXER
pygame.mixer.init()
pygame.mixer.set_num_channels(16)

# INITIALIZE FONTS
pygame.font.init()

# ICON
ICON = pygame.image.load('assets/GUI/icon.png')
pygame.display.set_icon(ICON)

# HEARTS
FULL_HEART = pygame.image.load("assets/GUI/full_heart.png").convert_alpha()
FULL_HEART = pygame.transform.scale2x(FULL_HEART)
NO_HEART = pygame.image.load("assets/GUI/no_heart.png").convert_alpha()
NO_HEART = pygame.transform.scale2x(NO_HEART)
HEARTS = [FULL_HEART, NO_HEART]

# SHAKE EFFECT
camera = Shake()

# SCROLL & OFFSET
SCROLL_AREA_WIDTH = 250
SCROLL_AREA_HEIGHT = 250

# BLOCK SIZE
BLOCK_SIZE = 48

# TILEMAP
OBJECTS = get_map(read_csv("new_Tiles.csv"), BLOCK_SIZE)

# BACKGROUND
BACKGROUND = get_map(read_csv("new_Background.csv"), BLOCK_SIZE)


# MAIN MENU
SWORD = pygame.image.load(join("assets", "GUI", "sword.png"))

# PLAYER INITIAL POSITION
PLAYER_START_X = 100
PLAYER_START_Y = 840
PLAYER_WIDTH = 120
PLAYER_HEIGHT = 60

# BOSS INITIAL POSITION
BOSS_START_X = 7000
BOSS_START_Y = 560
BOSS_WIDTH = 288
BOSS_HEIGHT = 160

# PLAYER IN ARENA
IN_ARENA = False
ARENA_POS = 2500

# MUSIC
TRACK = pygame.mixer.Sound("assets/Music/sonic.wav")


# MAIN MENU
SELECT = pygame.mixer.Sound("assets/Sound Effects/GUI/select.ogg")
CONFIRM = pygame.mixer.Sound("assets/Sound Effects/GUI/confirm.ogg")
PLAY = pygame.mixer.Sound("assets/Sound Effects/GUI/play.ogg")
RETURN = pygame.mixer.Sound("assets/Sound Effects/GUI/return.ogg")


# SOUND EFFECTS
path = join("assets", "Sound Effects", "")
DASH = pygame.mixer.Sound(path+"dash.wav")
JUMP = pygame.mixer.Sound(path+"jump.wav")
PARRY = pygame.mixer.Sound(path+"parry.wav")
PARRY_SUCCESS = pygame.mixer.Sound(path+"parry_success.wav")
HIT1 = pygame.mixer.Sound(path+"hit1.wav")
HIT2 = pygame.mixer.Sound(path+"hit2.wav")
BOSS_ATK = pygame.mixer.Sound(path+"boss_atk.wav")
SHRIEK = pygame.mixer.Sound(path+"shriek.wav")
CAST = pygame.mixer.Sound(path+"cast.wav")
EXPLOSION = pygame.mixer.Sound(path+"explosion.wav")
HURT = pygame.mixer.Sound(path+"hurt.wav")
COLUMN = pygame.mixer.Sound(path+"column.wav")
BOSS_HURT = pygame.mixer.Sound(path+"boss_hurt.wav")
DEATH = pygame.mixer.Sound(path+"death.wav")
PLAYED = False
SHRIEK_PLAYED = False

# VOLUME SET
SHRIEK.set_volume(0.3)
HURT.set_volume(0.3)
BOSS_HURT.set_volume(0.8)
BOSS_ATK.set_volume(0.7)
EXPLOSION.set_volume(0.5)
CAST.set_volume(0.2)
COLUMN.set_volume(0.2)
TRACK.set_volume(0.5)
