import pygame
import csv
from os.path import join
"""Ta koda je bila tudi kopirana od Tech with Tim, seveda sem jo prilagodil svojim potrebam"""


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, size, file_name):
        super().__init__(x, y, size, size)
        block = get_block(size, file_name)
        self.image.blit(block, (0, 0))


def read_csv(filename):
    """Reads the .csv file and returns a list"""
    sez = []
    path = join("assets", "Terrain", filename)
    with open(path) as data:
        data = csv.reader(data, delimiter=",")
        for row in data:
            sez.append(list(row))
    return sez


def get_map(csv, block_size):
    """This function draws the entire map
       block_size (int): this should be divisible with 16 and it is also used for step between the blocks"""
    x, y = -block_size, -block_size
    obj = []
    for row in range(len(csv)):
        y += block_size
        x = -block_size
        for tile in range(len(csv[row])):
            x += block_size
            if csv[row][tile] != "-1" and csv[row][tile] != "32":
                obj.append(Block(x, y, block_size, f"tile{int(csv[row][tile]):03d}.png"))
    return obj


def get_block(size, filename):
    """Assigns the image of the block to the rect
       size (int): should be divisible with 16 otherwise it won't fit!"""
    scale_factor = size // 16
    path = join("assets", "Terrain", "Tiles", filename)
    image = pygame.image.load(path).convert_alpha()
    pos_x, pos_y = 0, 0
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(pos_x, pos_y, size, size)
    surface.blit(image, (0, 0), rect)

    return pygame.transform.scale_by(surface, scale_factor)
