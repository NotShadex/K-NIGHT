from boss import *
from player import *
from config import *


def load_font(win, size, text, color=(255, 0, 0), position=(100, 100), centered=False):
    font = pygame.font.Font("assets/Fonts/pixel.ttf", size)
    text_surface = font.render(text, True, color)
    if centered:
        text_width, text_height = text_surface.get_size()
        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2
        win.blit(text_surface, (x, y))
    else:
        win.blit(text_surface, position)


def draw_health_bar(win, player, images):
    heart_spacing, x_offset, y_offset = 30, 10, 10
    heart_shake = Shake()

    for i in range(player.MAX_HEALTH):
        heart_shake.update_shake()
        if player.is_invincible and not player.is_attacking:
            heart_shake.trigger_shake(shake_intensity=2, duration=5)
        elif player.health == 1:
            heart_shake.trigger_shake(shake_intensity=1)
        x_offset, y_offset = heart_shake.apply_shake(x_offset, y_offset)
        if i < player.health:
            win.blit(images[0], (x_offset + i * heart_spacing, y_offset))
        else:
            win.blit(images[1], (x_offset + i * heart_spacing, y_offset))


def draw(win, player, objects, background, boss, projectiles, hearts, offset_x, offset_y):
    global PLAYED
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
    else:
        if not PLAYED:
            DEATH.play()
            PLAYED = True
        boss_mask = boss.mask.to_surface(setcolor=(255, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
        player_mask = player.mask.to_surface(setcolor=(130, 0, 0, 255), unsetcolor=(0, 0, 0, 0))
        win.fill("black")
        load_font(win, 200 if player.dead else 150, "DEATH" if player.dead else "SLAYED", centered=True, color=(100, 0, 0))
        win.blit(boss_mask, (boss.rect.x - offset_x, boss.rect.y - offset_y))
        win.blit(player_mask, (player.rect.x - offset_x, player.rect.y - offset_y))

    pygame.display.update()


def update_all_methods(player, objects, boss, projectiles, fps):
    global IN_ARENA, SHRIEK_PLAYED
    if not (player.dead or boss.dead):
        player.update_parry()
        player.update_attack()
        player.update_dash()
        player.loop(objects, boss, projectiles, fps)
        if player.rect.x > ARENA_POS or IN_ARENA:
            if not SHRIEK_PLAYED:
                camera.trigger_shake(duration=110)
                SHRIEK.play()
                SHRIEK_PLAYED = True
            boss.loop(player, projectiles)
            IN_ARENA = True
        for proj in projectiles:
            if proj.name == "fireball":
                proj.loop(player)
                if player.is_hit(boss, projectiles):
                    proj.is_following = False
            else:
                proj.loop()
            if proj.is_expired():
                projectiles.remove(proj)
    else:
        IN_ARENA = False


def main(window):
    global IN_ARENA
    # BASIC SETUP VARIABLES
    running = True
    clock = pygame.time.Clock()

    # SCROLL & OFFSET
    offset_x, offset_y = 0, 650

    # PLAYER
    player = Player(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

    # HEARTS
    hearts = HEARTS

    # BOSS
    boss = Boss(BOSS_START_X, BOSS_START_Y, BOSS_WIDTH, BOSS_HEIGHT)
    projectiles = []

    # OBJECTS & BLOCKS
    objects = OBJECTS

    # BACKGROUND
    background = BACKGROUND

    # MAIN LOOP
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
                    IN_ARENA = False
                    main(window)
        print(boss.health)
        update_all_methods(player, objects, boss, projectiles, FPS)
        camera.update_shake()
        window.fill((25, 20, 36))
        draw(window, player, objects, background, boss, projectiles, hearts, offset_x, offset_y)

        # CLOCK
        clock.tick(FPS)

        if ((player.rect.right - offset_x >= WIDTH - SCROLL_AREA_WIDTH) and player.vel_x > 0) or ((player.rect.left - offset_x <= SCROLL_AREA_WIDTH) and player.vel_x < 0):
            offset_x += player.vel_x

        if ((player.rect.top - offset_y >= HEIGHT - SCROLL_AREA_HEIGHT) and player.vel_y > 0) or ((player.rect.top - offset_y <= SCROLL_AREA_HEIGHT) and player.vel_y < 0):
            offset_y += int(player.vel_y)

        offset_x, offset_y = camera.apply_shake(offset_x, offset_y)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(WINDOW)
