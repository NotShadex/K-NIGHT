from boss import *
from player import *
from config import *


def load_font(win, size, text, color=(255, 255, 255), position=(100, 100), centered=False):
    """color : (tuple[int, int, int], str, optional) : you can also use the colors built in pygame e.g. 'white'
       centered (bool, optional): If True, centers text on the screen (x, y). Ignores `position` when enabled. """
    font = pygame.font.Font("assets/Fonts/pixel.ttf", size)
    text_surface = font.render(text, False, color)
    if centered:
        text_width, text_height = text_surface.get_size()
        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2
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


def tutorial_text(win, offset_x, offset_y):
    """INTRODUCTION for the PLAYER"""
    load_font(win, 20, "GAME BY SHADEX", position=(300 - offset_x, 730 - offset_y))
    load_font(win, 15, f"{"FUNCTION":<15}KEY", position=(300 - offset_x, 750 - offset_y))
    load_font(win, 15, f"{"Movement":<15}AD", position=(300 - offset_x, 765 - offset_y))
    load_font(win, 15, f"{"Jump":<15}SPACE", position=(300 - offset_x, 780 - offset_y))
    load_font(win, 15, f"{"Dash":<15}SHIFT", position=(300 - offset_x, 795 - offset_y))
    load_font(win, 15, f"{"Attack":<15}J", position=(300 - offset_x, 810 - offset_y))
    load_font(win, 15, f"{"Parry":<15}K", position=(300 - offset_x, 825 - offset_y))


def draw(win, player, objects, background, boss, projectiles, hearts, offset_x, offset_y):
    """Handles the drawing of all the classes/instances and the offset
       Also handles the death screen, a little messed up, but it works (I am too lazy)"""
    global PLAYED # For playing the shriek when you enter the arena
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


def update_all_methods(player, objects, boss, projectiles, camera, fps):
    """Handles the loops and updates of the classes"""
    global IN_ARENA, SHRIEK_PLAYED
    if not (player.dead or boss.dead):
        player.update_parry()
        player.update_attack()
        player.update_dash()
        player.loop(objects, boss, projectiles, fps)
        # Check if the player is in arena and if the player was 'greeted'
        if player.rect.x > ARENA_POS or IN_ARENA:
            if not SHRIEK_PLAYED:
                camera.trigger_shake(duration=110)
                TRACK.play(loops=-1)
                SHRIEK.play()
                SHRIEK_PLAYED = True
            boss.loop(player, projectiles)
            IN_ARENA = True
        # Stops following the player after the FOLLOW_TIME is over and despawns if TTL is zero
        for proj in projectiles:
            if proj.name == "fireball":
                proj.loop(player)
            else:
                proj.loop()
            if proj.is_expired():
                projectiles.remove(proj)
        camera.update_shake()
    else:
        IN_ARENA = False


def main(window):
    global IN_ARENA, PLAYED, SHRIEK_PLAYED

    running = True
    clock = pygame.time.Clock()
    offset_x, offset_y = 0, 717  # Have to set the offset_y because the player spawns lower!
    player = Player(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
    hearts = HEARTS
    boss = Boss(BOSS_START_X, BOSS_START_Y, BOSS_WIDTH, BOSS_HEIGHT)
    projectiles = []
    objects = OBJECTS
    background = BACKGROUND

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 1:
                    player.jump()
                if event.key == pygame.K_LSHIFT:
                    player.start_dash()
                if event.key == pygame.K_j:
                    player.start_attack()
                if event.key == pygame.K_k:
                    player.start_parry()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
                if event.key == pygame.K_r:
                    # Stops the track and resets the variables back to their original state (very not good for FPS)!
                    TRACK.stop()
                    PLAYED, IN_ARENA, SHRIEK_PLAYED = False, False, False
                    main(window)

        update_all_methods(player, objects, boss, projectiles, camera, FPS)
        window.fill((25, 20, 36))
        clock.tick(FPS)

        if ((player.rect.right - offset_x >= WIDTH - SCROLL_AREA_WIDTH) and player.vel_x > 0) or ((player.rect.left - offset_x <= SCROLL_AREA_WIDTH) and player.vel_x < 0):
            offset_x += player.vel_x

        if (player.rect.centery - offset_y >= HEIGHT - SCROLL_AREA_HEIGHT and player.vel_y > 0) or (player.rect.centery - offset_y <= SCROLL_AREA_HEIGHT and player.vel_y < 0):
            target_offset_y = player.rect.centery - HEIGHT // 2  # Smoother scrolling along the y-axis
            offset_y += (target_offset_y - offset_y) // 2

        # Variable shake_x and shake_y just move the offset temporarily
        shake_x, shake_y = camera.apply_shake(offset_x, offset_y)

        draw(window, player, objects, background, boss, projectiles, hearts, shake_x, shake_y)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(WINDOW)
