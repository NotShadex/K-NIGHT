import pygame.draw
from config import *
from sprite_cutter import *
import time
from random import *


class Boss:
    # SPRITES
    SPRITES = load_sprite_sheets("Boss", 288, 160, True, 2.5)
    ANIMATION_DELAY = 5
    # VELOCITY
    BOSS_VEL = 3
    # ATTACK CONSTANTS
    ATTACK_COOLDOWN = 0.0
    ATTACK_TIME = 1.2
    # DASH CONSTANTS
    DASH_TIME = 1.0
    DASH_COOLDOWN = 0.0
    # RAGE
    RAGE_PERCENTAGE = 30
    BOSS_HEALTH = 100
    # PROJECTILE
    PROJECTILE_COOLDOWN = 2.5

    def __init__(self, spawn_x, spawn_y, width, height):
        super().__init__()
        # ANIMATION AND HITBOXES
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.sprite = self.SPRITES["idle_right"][0]

        # MOVEMENT
        self.vel_x = self.BOSS_VEL
        self.distance = 200
        self.is_chasing = True
        self.is_standing = True

        # ATTACK
        self.is_attacking = False
        self.is_attack_active = False
        self.attack_end_time = 0
        self.last_attack_time = 0

        # DASH
        self.is_dashing = False
        self.dash_end_time = 0
        self.last_dash_time = 0
        self.afterimages = []

        # HEALTH
        self.health = self.BOSS_HEALTH
        self.is_enraged = False
        self.is_invincible = False
        self.invincible_end_time = 0
        self.last_invincible_time = 0

        # PROJECTILE
        self.last_proj_time = 0

    def start_inv(self, invincible_time=0.5):
        current_time = time.time()
        if not self.is_invincible and current_time - self.last_invincible_time >= 0.0:
            self.is_invincible = True
            self.invincible_end_time = current_time + invincible_time
            self.last_invincible_time = current_time

    def update_inv(self):
        if self.is_invincible:
            if time.time() >= self.invincible_end_time:
                self.is_invincible = False

    def is_hit(self, player):
        if player.is_attacking and pygame.sprite.collide_mask(self, player):
            if not self.is_invincible:
                self.start_inv()
                self.health -= 1
        self.update_inv()

    def add_projectile(self, projectiles):
        current_time = time.time()
        if current_time - self.last_proj_time >= self.PROJECTILE_COOLDOWN:
            projectiles.append(Projectile(self.rect.centerx + randint(-500, 500), self.rect.centery - 50, 60, 60))
            projectiles.append(Projectile(self.rect.centerx + randint(-300, 300), self.rect.centery - 50, 60, 60))
            self.last_proj_time = current_time

    def start_dash(self):
        current_time = time.time()
        if not self.is_dashing and current_time - self.last_dash_time >= self.DASH_COOLDOWN:
            self.is_dashing = True
            self.dash_end_time = current_time + self.DASH_TIME
            self.last_dash_time = current_time

    def update_dash(self):
        if self.is_dashing:
            self.add_afterimage()
            if time.time() >= self.dash_end_time:
                self.is_dashing = False

        new_afterimages = []
        for img, pos, alpha in self.afterimages:
            alpha -= 25
            if alpha > 0:
                new_afterimages.append((img, pos, alpha))
        self.afterimages = new_afterimages

    def add_afterimage(self):
        afterimage = (self.sprite, self.rect.topleft, 200)
        self.afterimages.append(afterimage)

    def draw_afterimage(self, win, offset_x, offset_y):
        for img, pos, alpha in self.afterimages:
            ghost = img.copy()
            ghost.set_alpha(alpha)
            win.blit(ghost, (pos[0] - offset_x, pos[1] - offset_y))

    def start_attack(self, player):
        current_time = time.time()
        if not self.is_attacking and current_time - self.last_attack_time >= self.ATTACK_COOLDOWN:
            if player.rect.centerx < self.rect.centerx:
                self.direction = "right"
            else:
                self.direction = "left"

            self.animation_count = 0
            self.is_attacking = True
            self.attack_end_time = current_time + self.ATTACK_TIME
            self.last_attack_time = current_time

    def update_attack(self):
        if self.is_attacking:
            attack_sprites = self.SPRITES[f"attack1_{self.direction}"]
            current_frame = (self.animation_count // self.ANIMATION_DELAY) % len(attack_sprites)

            self.is_attack_active = True if current_frame > 9 else False

            if time.time() >= self.attack_end_time:
                self.is_attacking = False
                self.is_attack_active = False

    def move_to_player(self, player, projectiles):
        self.is_standing = False

        if self.health <= self.RAGE_PERCENTAGE:
            self.add_projectile(projectiles)
            self.is_enraged = True
            return

        if self.is_chasing and not self.is_attacking:
            distance_to_player = player.rect.centerx - self.rect.centerx
            if abs(distance_to_player) > 500:
                self.start_dash()
            if player.rect.centerx < self.rect.centerx - self.distance:
                self.rect.x += -self.vel_x if not self.is_dashing else (-self.vel_x * 10)
                self.direction = "right"
            elif player.rect.centerx > self.rect.centerx + self.distance:
                self.rect.x += self.vel_x if not self.is_dashing else (self.vel_x * 10)
                self.direction = "left"
            else:

                self.start_attack(player)

                if not self.is_attacking and not self.is_enraged:
                    self.is_standing = True

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.is_chasing and not self.is_attacking:
            sprite_sheet = "run"
        if self.is_attacking:
            sprite_sheet = "attack1"
        if self.is_standing:
            sprite_sheet = "idle"
        if self.is_enraged:
            sprite_sheet = "attack2"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def loop(self, player, projectiles):
        self.update_dash()
        self.update_attack()
        self.is_hit(player)
        self.move_to_player(player, projectiles)
        self.update_sprite()

    def draw(self, win, offset_x, offset_y):
        self.draw_afterimage(win, offset_x, offset_y)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Projectile:
    SPRITES = load_sprite_sheets("Boss", 64, 64, False, 1.0)
    ANIMATION_DELAY = 5
    PROJECTILE_VEL = 5
    TTL = 2.5

    def __init__(self, spawn_x, spawn_y, width, height):
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.mask = None
        self.animation_count = 0
        self.sprite = self.SPRITES["spawn"][0]
        self.vel = self.PROJECTILE_VEL
        self.spawn_time = time.time()
        self.spawner = Spawner(spawn_x, spawn_y, width, height)

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprites = self.SPRITES["spawn"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def move_to_player(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(1, (dx**2 + dy**2) ** 0.5)

        if abs(dx) > self.vel:
            self.rect.x += (dx / dist) * self.vel
        if abs(dy) > self.vel:
            self.rect.y += (dy / dist) * self.vel

    def is_expired(self):
        return time.time() - self.spawn_time >= self.TTL

    def loop(self, player):
        self.move_to_player(player)
        self.update_sprite()
        self.spawner.update_sprite()

    def draw(self, win, offset_x, offset_y):
        self.spawner.draw(win, offset_x, offset_y)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Spawner:
    SPRITES = load_sprite_sheets("Boss", 64, 64, False, 1.0)
    ANIMATION_DELAY = 5

    def __init__(self, spawn_x, spawn_y, width, height):
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.animation_count = 0
        self.sprite = self.SPRITES["spawner"][0]

    def update_sprite(self):
        sprites = self.SPRITES["spawner"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        if sprite_index < 14:
            self.sprite = sprites[sprite_index]
            self.animation_count += 1

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
