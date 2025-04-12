import time
import pygame.mixer
from os import listdir
from random import randint


def play_sound(sfx):
    """Plays the sound on multiple channels if they are free"""
    channel = pygame.mixer.find_channel()
    if channel:
        channel.play(sfx)


class SoundTimer:
    """Delays the sound played for the given cooldown"""
    def __init__(self, cooldown_seconds):
        self.cooldown = cooldown_seconds
        self.last_played = 0

    def play(self, sfx):
        current_time = time.time()
        if current_time - self.last_played >= self.cooldown:
            sfx.play()
            self.last_played = current_time
            return True
        return False


class Shake:
    def __init__(self):
        self.shake_time = 0
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 5

    def trigger_shake(self, shake_intensity=5, duration=10):
        # Duration is defined in frames so duration=10 that equals to 10 frames
        self.shake_time = duration
        self.shake_intensity = shake_intensity

    def update_shake(self):
        """You need to update shake every frames so insert it in the main loop"""
        if self.shake_time > 0:
            self.shake_time -= 1
            self.shake_x = randint(-self.shake_intensity, self.shake_intensity)
            self.shake_y = randint(-self.shake_intensity, self.shake_intensity)
        else:
            self.shake_x = 0
            self.shake_y = 0

    def apply_shake(self, x_offset, y_offset):
        """Applies the shake put it on some kind of triggers (player gets hit)"""
        return x_offset + self.shake_x, y_offset + self.shake_y
