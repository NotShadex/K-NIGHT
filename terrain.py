import pygame
import csv
from os.path import join


# Object class for easier creation
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


def read_csv():
    sez = []
    path = join("assets", "Terrain", "project_Tiles.csv")
    with open(path) as data:
        data = csv.reader(data, delimiter=",")
        for row in data:
            sez.append(list(row))
    return sez


def get_map(csv, block_size):
    x, y = -block_size, -block_size
    obj = []
    for row in range(len(csv)):
        y += block_size
        x = -block_size
        for tile in range(len(csv[row])):
            x += block_size
            if csv[row][tile] != "-1":
                obj.append(Block(x, y, block_size))

    return obj


# Define the block sizes!
def get_block(size):
    path = join("assets", "Terrain", "Tiles.png")
    image = pygame.image.load(path).convert_alpha()
    pos_x, pos_y = 0, 320
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(pos_x, pos_y, size, size)
    surface.blit(image, (0, 0), rect)

    return pygame.transform.scale2x(surface)


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    return image



"""
FLOOR_BLOCKS = [i * BLOCK_SIZE for i in range(-WIDTH // BLOCK_SIZE, (WIDTH * 4) // BLOCK_SIZE)]
FLOOR_Y = HEIGHT - BLOCK_SIZE

# OBJECTS & BLOCKS

OBJECTS = [
    *[Block(x + 900, FLOOR_Y, BLOCK_SIZE) for x in FLOOR_BLOCKS[0:41]],
    Block(100, 0, BLOCK_SIZE)
]
"""
