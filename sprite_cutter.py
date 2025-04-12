from config import pygame
from os import listdir
from os.path import isfile, join


# Flips all the sprites from left to right at least those requiring being flipped
def flip(sprites):
    """Flips all the sprites from left to right"""
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, width, height, direction=False, scale_factor=1.5):
    """Makes a sprite sheet. Define the width and height of the entire sprite sheet and if it is directional"""
    path = join("assets", dir1)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale_by(surface, scale_factor))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites
