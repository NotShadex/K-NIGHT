from config import *


class Button:
    def __init__(self, win, pos, text_input, size, bg_image=None, color=(255, 255, 255), hover_color=(255, 0, 0), font="assets/Fonts/pixel.ttf"):
        self.font = pygame.font.Font(font, size)
        self.text_input = text_input
        self.color, self.hover_cl = color, hover_color
        self.text = self.font.render(self.text_input, False, self.color)
        self.bg_image = self.text if bg_image is None else bg_image
        self.rect = self.bg_image.get_rect(center=(pos[0], pos[1]))
        self.text_rect = self.text.get_rect(center=(pos[0], pos[1]))
        self.hovered = False

    def draw(self, win):
        if self.bg_image is not None:
            win.blit(self.bg_image, self.rect)
        win.blit(self.text, self.text_rect)

    def input_check(self, mouse_position):
        if mouse_position[0] in range(self.rect.left, self.rect.right) and mouse_position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def hover(self, mouse_position, sfx):
        if mouse_position[0] in range(self.rect.left, self.rect.right) and mouse_position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hover_cl)
            if not self.hovered:
                sfx.play()
                self.hovered = True
        else:
            self.text = self.font.render(self.text_input, True, self.color)
            self.hovered = False


def center_image(image):
    image_width, image_height = image.get_size()
    x = (WIDTH - image_width) // 2
    y = (HEIGHT - image_height) // 2
    return x, y


def load_font(win, size, text, color=(255, 255, 255), position=(100, 100), centered=False, font="assets/Fonts/pixel.ttf"):
    """color : (tuple[int, int, int], str, optional) : you can also use the colors built in pygame e.g. 'white'
       centered (bool, optional): If True, centers text on the screen (x, y). Ignores `position` when enabled. """
    font = pygame.font.Font(font, size)
    text_surface = font.render(text, False, color)
    if centered:
        text_width, text_height = text_surface.get_size()
        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2
        print(x, y)
        win.blit(text_surface, (x, y))
    else:
        win.blit(text_surface, position)


def draw_health_bar(win, player, images):
    """Has its builtin shake function when player is invincible
       images (tuple[image(full_heart), image(empty_heart)]) : if you plan on changing it watch out!"""

    heart_spacing, x_offset, y_offset = 30, 10, 10
    heart_shake = Shake()

    for i in range(player.MAX_HEALTH):
        heart_shake.update_shake()
        if player.is_invincible and not player.is_attacking and not player.is_dashing and not player.is_parrying:
            heart_shake.trigger_shake(shake_intensity=2, duration=5)
        elif player.health == 1:
            heart_shake.trigger_shake(shake_intensity=1)
        x_offset, y_offset = heart_shake.apply_shake(x_offset, y_offset)
        if i < player.health:
            win.blit(images[0], (x_offset + i * heart_spacing, y_offset))
        else:
            win.blit(images[1], (x_offset + i * heart_spacing, y_offset))


def statistics(win, player, boss, offset_x, offset_y):
    """Purely for statistics uncomment in the main draw function"""
    can_parry = time.time() - player.last_parry_time >= player.PARRY_COOLDOWN
    load_font(win, 15, f"STATE: {player.sheet}", position=(15, 50))
    load_font(win, 15, f"BOSS HP: {boss.health}", position=(15, 65))
    load_font(win, 15, f"POSITION X: {player.rect.x} Y: {player.rect.y}", position=(15, 80))
    load_font(win, 15, f"VELOCITY X: {player.vel_x} Y: {round(player.vel_y, 2)}", position=(15, 95))
    load_font(win, 15, f"OFFSET X: {offset_x} Y: {offset_y}", position=(15, 110))
    load_font(win, 15, f"INVINCIBLE: {player.is_invincible}", position=(15, 125))
    load_font(win, 15, f"CAN PARRY: {can_parry}", position=(15, 140))
    load_font(win, 15, f"DIRECTION: {player.direction}", position=(15, 155))


def tutorial_text(win):
    x = 100 # 1.5x
    load_font(win, 40, f"CONTROLS", position=(x, 0), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'FUNCTION':<20}KEY", position=(x, 40), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Movement':<20}AD", position=(x, 60), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Jump':<20}SPACE", position=(x, 80), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Dash':<20}SHIFT", position=(x, 100), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Attack':<20}J", position=(x, 120), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Parry':<20}K", position=(x, 140), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Retry':<20}R", position=(x, 160), font="assets/Fonts/main.ttf")
    load_font(win, 30, f"{'Exit':<20}ESC", position=(x, 180), font="assets/Fonts/main.ttf")


def draw(win, player, objects, background, boss, projectiles, hearts, offset_x, offset_y):
    """Handles the drawing of all the classes/instances and the offset
       Also handles the death screen, a little messed up, but it works (I am too lazy)"""
    global PLAYED  # For playing the shriek when you enter the arena
    if not (player.dead or boss.dead):
        for tile in background:
            tile.draw(win, offset_x, offset_y)
        for obj in objects:
            obj.draw(win, offset_x, offset_y)
        boss.draw(win, offset_x, offset_y)
        player.draw(win, offset_x, offset_y)
        for proj in projectiles:
            proj.draw(win, offset_x, offset_y)
        draw_health_bar(win, player, hearts)
        # tutorial_text(win, offset_x, offset_y)
        statistics(win, player, boss, offset_x, offset_y)
    else:
        # Stops the track when you die split up the texts to look nicer looks like a lot of code purely aesthetic
        TRACK.stop()
        t1, t2 = 'PRESS "R" TO RESTART', "THANK YOU SO MUCH FOR PLAYING!"
        p1, p2 = (200, 270), (140, 270)
        if not PLAYED:
            DEATH.play()
            PLAYED = True
        boss_mask = boss.mask.to_surface(setcolor=(255, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
        player_mask = player.mask.to_surface(setcolor=(130, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
        win.fill("black")
        load_font(win, 200 if player.dead else 150, "DEATH" if player.dead else "SLAYED", centered=True, color=(100, 0, 0))
        load_font(win, 20, t1 if player.dead else t2, position=p1 if player.dead else p2, color=(100, 0, 0))
        win.blit(boss_mask, (boss.rect.x - offset_x, boss.rect.y - offset_y))
        win.blit(player_mask, (player.rect.x - offset_x, player.rect.y - offset_y))
    pygame.display.update()
