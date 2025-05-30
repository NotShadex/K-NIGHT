from config import *


class Boss:
    # SPRITES
    SPRITES = load_sprite_sheets("Boss", 288, 160, True, 2.5)
    ANIMATION_DELAY = 5
    # VELOCITY
    BOSS_VEL = 3
    # ATTACK CONSTANTS
    ATTACK_COOLDOWN = 1.2
    ATTACK_TIME = 1.2
    # DASH CONSTANTS
    DASH_TIME = 1.0
    DASH_COOLDOWN = 0.0
    # RAGE
    RAGE_PERCENTAGE = 20
    BOSS_HEALTH = 35
    # PROJECTILE
    PROJECTILE_COOLDOWN = 1.5

    def __init__(self, spawn_x, spawn_y, width, height):
        super().__init__()
        # ANIMATION AND HITBOXES
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.sprite = self.SPRITES["idle_right"][0]
        self.shriek = SoundTimer(2)

        # MOVEMENT
        self.vel_x = self.BOSS_VEL
        self.distance = 200
        self.is_chasing = True

        # ATTACK
        self.is_attacking = False
        self.is_attack_active = False
        self.attack_end_time = 0
        self.last_attack_time = 0
        self.sound_played = True

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
        self.dead = False

        # PROJECTILE & COLUMN
        self.last_proj_time = 0
        self.last_column_time = 0

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
                BOSS_HURT.play()
                camera.trigger_shake(shake_intensity=2, duration=5)
                self.start_inv()
                self.health -= 1
        if self.health <= 0:
            self.dead = True
        self.update_inv()

    def add_projectile(self, projectiles):
        """Spawns two projectiles at the same time then applies cooldown"""
        current_time = time.time()
        if current_time - self.last_proj_time >= self.PROJECTILE_COOLDOWN:
            projectiles.append(Projectile(self.rect.centerx + randint(-500, -50), self.rect.centery - 70, 60, 60))
            projectiles.append(Projectile(self.rect.centerx + randint(50, 500), self.rect.centery - 70, 60, 60))
            self.last_proj_time = current_time

    def collumn_attack(self, projectiles):
        """Spawns 6 columns with randomized spacing and applied cooldown"""
        current_time = time.time()
        spacing = 300 if randint(0, 1) == 1 else 100
        column_count = 5
        if current_time - self.last_column_time >= 3.0:
            start_x = self.rect.centerx - (column_count // 2) * spacing
            for i in range(column_count):
                column_x = start_x + i * spacing
                projectiles.append(Column(column_x, self.rect.y + 79, 45, 90))
            self.last_column_time = current_time

    def start_dash(self):
        current_time = time.time()
        if not self.is_dashing and current_time - self.last_dash_time >= self.DASH_COOLDOWN:
            self.is_dashing = True
            self.dash_end_time = current_time + self.DASH_TIME
            self.last_dash_time = current_time

    def update_dash(self):
        if self.is_dashing:
            if randint(0, 5) == 1:  # Less afterimages for performance
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
        """Unpacks the values so it can draw afterimages"""
        for img, pos, alpha in self.afterimages:
            ghost = img.copy()
            ghost.set_alpha(alpha)
            win.blit(ghost, (pos[0] - offset_x, pos[1] - offset_y))

    def start_attack(self, player, projectiles):
        current_time = time.time()
        if not self.is_attacking and current_time - self.last_attack_time >= self.ATTACK_COOLDOWN:
            # This line is so the boss doesn't switch direction after starting an attack
            if player.rect.centerx < self.rect.centerx:
                self.direction = "right"
            else:
                self.direction = "left"
            if randint(0, 3) == 1:  # 1 in 4 chance to spawn projectiles
                projectiles.append(Projectile(self.rect.centerx, self.rect.centery - 70, 60, 60))
            self.collumn_attack(projectiles)
            self.animation_count = 0
            self.is_attacking = True
            self.attack_end_time = current_time + self.ATTACK_TIME
            self.last_attack_time = current_time

    def update_attack(self):
        if self.is_attacking:
            # This code makes sure that the boss doesn't damage the player while winding up the attack
            attack_sprites = self.SPRITES[f"attack1_{self.direction}"]
            current_frame = (self.animation_count // self.ANIMATION_DELAY) % len(attack_sprites)
            self.is_attack_active = True if current_frame > 9 else False

            if self.is_attack_active:
                camera.trigger_shake(shake_intensity=3, duration=2)

            if current_frame == 9 and not self.sound_played:
                # Plays the sound when hitting the ground and the bool makes sure it is played once
                BOSS_ATK.play()
                self.sound_played = True

            if time.time() >= self.attack_end_time:
                self.sound_played = False
                self.is_attacking = False
                self.is_attack_active = False

    def move_to_player(self, player, projectiles):
        # If the boss is enraged ignore movement and attack options
        if 10 < self.health <= self.RAGE_PERCENTAGE:
            camera.trigger_shake(shake_intensity=3, duration=5)
            self.add_projectile(projectiles)
            self.is_enraged = True
            # Plays the shriek every 2 seconds using the class I implemented
            self.shriek.play(SHRIEK)
            return
        else:
            self.is_enraged = False

        if self.is_chasing and not self.is_attacking:
            if abs(player.rect.centerx - self.rect.centerx) > 500:
                self.start_dash()
            if player.rect.centerx < self.rect.centerx - self.distance:
                self.rect.x += -self.vel_x if not self.is_dashing else (-self.vel_x * 10)
                self.direction = "right"
            elif player.rect.centerx > self.rect.centerx + self.distance:
                self.rect.x += self.vel_x if not self.is_dashing else (self.vel_x * 10)
                self.direction = "left"
            else:
                if not self.is_attacking:
                    self.start_attack(player, projectiles)

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.is_chasing and not self.is_attacking:
            sprite_sheet = "run"
        if self.is_attacking:
            sprite_sheet = "attack1"
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
        if self.is_invincible and randint(0, 1) == 1:  # When boss is hit colors him red 1 in 2 chance
            mask_surface = self.mask.to_surface(setcolor=(255, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
            win.blit(mask_surface, (self.rect.x - offset_x, self.rect.y - offset_y))
            return
        self.draw_afterimage(win, offset_x, offset_y)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Projectile:
    SPRITES = load_sprite_sheets("Boss", 64, 64, False, 1.0)
    ANIMATION_DELAY = 5
    PROJECTILE_VEL = 5
    TTL = 7.0
    FOLLOW_TIME = 3.0

    def __init__(self, spawn_x, spawn_y, width, height):
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.mask = None
        self.name = "fireball"  # So I can have projectiles and columns in the same list
        self.animation_count = 0
        self.sprite = self.SPRITES["spawn"][0]
        self.vel = self.PROJECTILE_VEL
        self.spawn_time = time.time()
        self.spawner = Spawner(spawn_x, spawn_y, width, height)
        self.is_following = True
        self.move_x, self.move_y = 0, 0
        self.can_hit = True
        play_sound(CAST)

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprites = self.SPRITES["spawn"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def move_to_player(self, player):
        if self.is_following:
            # To mi je pomagal chat-gpt za bolj 'smooth' movement na premikanju do igralca
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery

            dist = max(1, (dx**2 + dy**2) ** 0.5)

            # Writes the last recorded position of the player
            self.move_x = (dx / dist) * self.vel
            self.move_y = (dy / dist) * self.vel

            if abs(dx) > self.vel:
                self.rect.x += (dx / dist) * self.vel
            if abs(dy) > self.vel:
                self.rect.y += (dy / dist) * self.vel

            if time.time() - self.spawn_time >= self.FOLLOW_TIME:
                self.is_following = False
        else:
            # Moves to the last direction the player was seen
            self.rect.x += self.move_x
            self.rect.y += self.move_y

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
    """Purely for aesthetic value. Nothing else nothing more"""
    SPRITES = load_sprite_sheets("Boss", 64, 64, False, 1.0)
    ANIMATION_DELAY = 6

    def __init__(self, spawn_x, spawn_y, width, height):
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.animation_count = 0
        self.sprite = self.SPRITES["spawner"][0]

    def update_sprite(self):
        sprites = self.SPRITES["spawner"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        if sprite_index < 14:  # Stops at index 14 so it looks cool!
            self.sprite = sprites[sprite_index]
            self.animation_count += 1

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Column:
    SPRITES = load_sprite_sheets("Boss", 45, 90, False, 4.0)
    ANIMATION_DELAY = 5
    PROJECTILE_VEL = 5
    TTL = 2.0
    INDICATOR_TIME = 1.0

    def __init__(self, spawn_x, spawn_y, width, height):
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.mask = None
        self.name = "column"
        self.animation_count = 0
        self.sprite = self.SPRITES["column"][0]
        self.spawn_time = time.time()
        self.can_hit = False
        self.sound = SoundTimer(1.5)

    def update(self):
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_sprite(self):
        sprites = self.SPRITES["column"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)

        if time.time() - self.spawn_time <= self.INDICATOR_TIME:
            self.can_hit = False
            return
        self.can_hit = True
        self.sound.play(COLUMN)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def is_expired(self):
        return time.time() - self.spawn_time >= self.TTL

    def loop(self):
        self.update_sprite()

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
