from config import *


class Player(pygame.sprite.Sprite):
    # SPRITES
    SPRITES = load_sprite_sheets("Player", 120, 80, True)
    ANIMATION_DELAY = 4
    # CUSTOM JUMP CONSTANTS
    JUMP_HEIGHT = 2.5
    JUMP_TIME_TO_PEAK = 0.5
    JUMP_TIME_TO_DESCEND = 0.4
    # DASH CONSTANTS
    DASH_TIME = 0.4
    DASH_COOLDOWN = 1.0
    # ATTACK CONSTANTS
    ATTACK_COOLDOWN = 0.0
    ATTACK_TIME = 0.28
    COMBO_WINDOW = 1.0
    # PARRY CONSTANTS
    PARRY_TIME = 1.0
    PARRY_COOLDOWN = 5.0
    # HEALTH
    MAX_HEALTH = 5

    def __init__(self, spawn_x, spawn_y, width, height):
        super().__init__()
        # ANIMATION AND HITBOXES
        self.rect = pygame.Rect(spawn_x, spawn_y, width, height)
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.sprite = self.SPRITES["idle_left"][0]
        self.ground_rect = None
        self.real_rect = None
        self.head_rect = None
        self.sheet = None

        # VELOCITY
        self.vel_x = 0
        self.vel_y = 0

        # JUMP // GRAVITY
        self.jump_velocity = ((2.0 * self.JUMP_HEIGHT) / self.JUMP_TIME_TO_PEAK) * -1.0
        self.jump_gravity = ((-2.0 * self.JUMP_HEIGHT) / (self.JUMP_TIME_TO_PEAK * self.JUMP_TIME_TO_PEAK)) * -1.0
        self.fall_gravity = ((-2.0 * self.JUMP_HEIGHT) / (self.JUMP_TIME_TO_DESCEND * self.JUMP_TIME_TO_DESCEND)) * -1.0
        self.is_on_floor = False
        self.jump_count = 0

        # DASH
        self.is_dashing = False
        self.dash_end_time = 0
        self.last_dash_time = 0
        self.afterimages = []

        # ATTACK
        self.is_attacking = False
        self.attack_end_time = 0
        self.last_attack_time = 0
        self.combo_start_time = 0
        self.combo_stage = 1

        # PARRY
        self.is_parrying = False
        self.parry_end_time = 0
        self.last_parry_time = 0
        self.current_parry_sprite = ""
        self.parry_middle_start_time = 0
        self.parry_end_start_time = 0
        self.parry_success = False

        # HEALTH
        self.is_invincible = False
        self.invincible_end_time = 0
        self.last_invincible_time = 0
        self.health = self.MAX_HEALTH
        self.dead = False

    # PARRY, ATTACK, DASH
    def start_inv(self, invincible_time=1.0):
        current_time = time.time()
        if not self.is_invincible and current_time - self.last_invincible_time >= 0.0:
            self.is_invincible = True
            self.invincible_end_time = current_time + invincible_time
            self.last_invincible_time = current_time

    def update_inv(self):
        if self.is_invincible:
            if time.time() >= self.invincible_end_time:
                self.is_invincible = False

    def is_hit(self, boss, projectiles):
        proj_hit_player = False

        if boss.is_attacking and pygame.sprite.collide_mask(self, boss) and boss.is_attack_active:
            if not self.is_invincible:
                pygame.time.wait(100)
                camera.trigger_shake(10)
                self.start_inv()
                self.health -= 1
                HURT.play()
            if self.is_parrying and not self.parry_success and self.health != self.MAX_HEALTH:
                self.health += 1
                self.parry_success = True
        try:  # Since I set the mask of the projectiles in __init__ to None I have to have a try except block
            for proj in projectiles:
                if pygame.sprite.collide_mask(self, proj):
                    proj_hit_player = True
                    proj.is_following = False
                    if not self.is_invincible and proj.can_hit:
                        camera.trigger_shake(5)
                        self.start_inv(invincible_time=2.0)
                        self.health -= 1
                        EXPLOSION.play()
        except TypeError:
            pass
        if self.health <= 0:
            self.dead = True
        if not boss.is_attacking:
            self.parry_success = False

        return proj_hit_player

    def start_parry(self):
        if self.is_on_floor:
            current_time = time.time()
            if not self.is_parrying and current_time - self.last_parry_time >= self.PARRY_COOLDOWN and not self.is_dashing and not self.is_attacking:
                PARRY.play()
                self.is_parrying = True
                self.parry_end_time = current_time + self.PARRY_TIME
                self.last_parry_time = current_time
                self.current_parry_sprite = "crouchtran"  # Start animation with the transition
                self.parry_middle_start_time = current_time + 0.1
                self.parry_end_start_time = self.parry_end_time - 0.1

    def update_parry(self):
        if self.is_parrying:
            current_time = time.time()
            self.start_inv(invincible_time=2)
            if self.parry_middle_start_time <= current_time < self.parry_end_start_time:
                self.current_parry_sprite = "crouch"
            elif current_time >= self.parry_end_start_time:
                self.current_parry_sprite = "crouchtran"  # End animation with a transition
            if current_time >= self.parry_end_time:
                self.is_parrying = False

    def start_attack(self):
        if self.is_on_floor:
            current_time = time.time()
            if not self.is_attacking and current_time - self.last_attack_time >= self.ATTACK_COOLDOWN and not self.is_dashing and not self.is_parrying:
                self.is_parrying = False
                if current_time - self.combo_start_time <= self.COMBO_WINDOW:
                    self.combo_stage = 2 if self.combo_stage == 1 else 1
                    HIT2.play()
                else:
                    self.combo_stage = 1
                    HIT1.play()

                self.animation_count = 0
                self.is_attacking = True
                self.attack_end_time = current_time + self.ATTACK_TIME
                self.last_attack_time = current_time
                self.combo_start_time = current_time

    def update_attack(self):
        if self.is_attacking:
            self.start_inv(invincible_time=0.28)
            if time.time() >= self.attack_end_time:
                self.is_attacking = False

            if time.time() - self.combo_start_time > self.COMBO_WINDOW:
                self.combo_stage = 1

    def start_dash(self):
        current_time = time.time()
        if not self.is_dashing and current_time - self.last_dash_time >= self.DASH_COOLDOWN:
            DASH.play()
            self.start_inv(invincible_time=0.4)
            self.is_parrying = False
            self.is_dashing = True
            self.dash_end_time = current_time + self.DASH_TIME
            self.last_dash_time = current_time

    def update_dash(self):
        if self.is_dashing:
            self.add_afterimage()
            if time.time() >= self.dash_end_time:
                self.is_dashing = False
                self.vel_x = 0

        new_afterimages = []
        for img, pos, alpha in self.afterimages:
            alpha -= 25
            if alpha > 0:
                new_afterimages.append((img, pos, alpha))
        self.afterimages = new_afterimages

    def add_afterimage(self):
        """Adds the information about the sprite and the positioning of the rect and the alpha (transparency)
           It is called only when is_dashing is True"""
        afterimage = (self.sprite, self.rect.topleft, 200)
        self.afterimages.append(afterimage)

    def draw_afterimage(self, win, offset_x, offset_y):
        """Sets the "ghost" image behind the sprite lowers the alpha every turn which is called in update_dash function
           had to keep in mind to have the player x and y offset otherwise it is behind and lower to the actual player"""
        for img, pos, alpha in self.afterimages:
            ghost = img.copy()
            ghost.set_alpha(alpha)
            win.blit(ghost, (pos[0] - offset_x, pos[1] - offset_y))

    def get_gravity(self):
        return self.jump_gravity if self.vel_y < 0.0 else self.fall_gravity

    def jump(self):
        self.jump_count += 1
        if not self.is_dashing:
            JUMP.play()
            self.vel_y = self.jump_velocity
            self.is_parrying = False

    def move_left(self, vel):
        self.vel_x = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.vel_x = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def update_sprite(self, fps):
        """Handles all the animation of the player"""
        sprite_sheet = "idle"
        if self.vel_y < 0:
            sprite_sheet = "jump"
        elif self.vel_y > self.get_gravity() / fps * 2:
            sprite_sheet = "fall"
        # TODO : This is very retarded, but it works for now so fucking leave it as it is
        elif (self.vel_y >= self.get_gravity() / fps or round(self.vel_y) == 0) and not self.is_on_floor:
            sprite_sheet = "jumptran"
        elif self.is_attacking:
            match self.combo_stage:
                case 1: sprite_sheet = "attack1"
                case 2: sprite_sheet = "attack2"
        elif self.is_parrying:
            sprite_sheet = self.current_parry_sprite
        elif self.vel_x != 0:
            if self.is_on_floor:
                sprite_sheet = "run"
        if self.is_dashing:
            sprite_sheet = "dash"
        self.sheet = sprite_sheet  # For easier access to the sheet

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        # TODO : THIS IS RETARDED
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # Used for checking ground collisions
        self.ground_rect = self.rect.copy()
        self.ground_rect.width = 55
        self.ground_rect.height = 5
        self.ground_rect.y = (self.rect.bottom + 1) - self.ground_rect.height
        self.ground_rect.centerx = self.rect.centerx
        # Used for checking horizontal collisions
        self.real_rect = self.rect.copy()
        self.real_rect.width = 70
        self.real_rect.height = 5
        self.real_rect.y = (self.rect.bottom - 10) - self.ground_rect.height
        self.real_rect.centerx = self.rect.centerx
        # Used for checking head collisions
        self.head_rect = self.rect.copy()
        self.head_rect.width = 20
        self.head_rect.height = 10
        self.head_rect.y = (self.rect.bottom - 50) - self.head_rect.height
        self.head_rect.centerx = self.rect.centerx
        # Used for pixel perfect collisions
        self.mask = pygame.mask.from_surface(self.sprite)

    def handle_vertical_collision(self, objects):
        self.is_on_floor = False
        for obj in objects:
            if self.ground_rect.colliderect(obj.rect):
                if self.vel_y >= 0:
                    self.is_on_floor = True
                    self.ground_rect.bottom = obj.rect.top
                    self.rect.bottom = obj.rect.top
                    self.vel_y = 0
            if self.head_rect.colliderect(obj.rect):
                if self.vel_y < 0:
                    self.head_rect.top = obj.rect.bottom
                    self.vel_y *= -1  # Bumps the head on the object

    def handle_horizontal_collison(self, objects, dx):
        collided_obj = False
        self.rect.x += dx
        self.update()
        for obj in objects:
            if self.real_rect.colliderect(obj.rect):
                collided_obj = True
                break
        self.rect.x += -dx
        self.update()
        return collided_obj

    def loop(self, objects, boss, projectiles, fps):
        self.update()
        keys = pygame.key.get_pressed()
        self.vel_x = 0

        self.is_hit(boss, projectiles)
        self.update_inv()

        # OPPOSITE FORCE
        collide_left = self.handle_horizontal_collison(objects, -PLAYER_VEL * 2)
        collide_right = self.handle_horizontal_collison(objects, PLAYER_VEL * 2)

        if not self.is_attacking and not self.is_parrying:
            if keys[pygame.K_a] and not keys[pygame.K_d] and not collide_left:
                self.move_left(PLAYER_VEL)
            elif keys[pygame.K_d] and not keys[pygame.K_a] and not collide_right:
                self.move_right(PLAYER_VEL)

        # HANDLE DASHING AND LOGIC
        if self.is_dashing and (collide_right or collide_left):
            self.is_dashing = False
        if self.is_dashing:
            if self.direction == "left" and not collide_left:
                self.move_left(PLAYER_VEL * 3)
            elif self.direction == "right" and not collide_right:
                self.move_right(PLAYER_VEL * 3)

        self.rect.x += self.vel_x

        if not self.is_on_floor and not self.is_dashing:
            self.vel_y += self.get_gravity() / fps
        elif self.is_on_floor:
            self.jump_count = 0
        if self.is_dashing:
            self.vel_y = 0

        self.rect.y += self.vel_y
        self.handle_vertical_collision(objects)

        self.update_sprite(fps)

    def draw(self, win, offset_x, offset_y):
        if (self.is_invincible and randint(0, 1) == 1) and not self.is_attacking and not self.dead and not self.is_parrying and not self.is_dashing:
            return
        self.draw_afterimage(win, offset_x, offset_y)
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))
        if self.is_parrying:  # Overlays a yellow color when parrying (indicator)
            mask_surface = self.mask.to_surface(setcolor=(255, 255, 0, 150), unsetcolor=(0, 0, 0, 0))
            win.blit(mask_surface, (self.rect.x - offset_x, self.rect.y - offset_y))



