import pygame.display
from boss import *
from player import *
from config import *


def backgrounds(win, bg0, bg1, offset_x, offset_y):
    # Background Layer 0 (PARADOX)
    size = pygame.transform.scale_by(bg0, 1.3)
    win.blit(size, (0 - offset_x * 0.05, -50 - offset_y * 0.1))

    # Background Layer 1 (EXPERIMENTAL)
    size = pygame.transform.scale_by(bg1, 1.2)
    win.blit(size, (0 - offset_x * 0.1, -50 - offset_y * 0.5))
    if offset_x > 2500:
        win.blit(size, (921 - offset_x * 0.1, -50 - offset_y * 0.5))


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


def draw(win, player, objects, boss, projectiles, hearts, offset_x, offset_y):
    # backgrounds(win, bg0, bg1, offset_x, offset_y)
    # Drawing objects
    boss.draw(win, offset_x, offset_y)
    for obj in objects:
        obj.draw(win, offset_x, offset_y)

    player.draw(win, offset_x, offset_y)
    for proj in projectiles:
        proj.draw(win, offset_x, offset_y)
    draw_health_bar(win, player, hearts)
    pygame.display.update()


def update_all_methods(player, objects, boss, projectiles, fps):
    player.update_parry()
    player.update_attack()
    player.update_dash()
    player.loop(objects, boss, fps)
    boss.loop(player, projectiles)
    for proj in projectiles:
        proj.loop(player)
        if proj.is_expired():
            projectiles.remove(proj)


def main(window):
    # BASIC SETUP VARIABLES
    running = True
    clock = pygame.time.Clock()

    # BACKGROUND
    bg0 = get_background(BACKGROUND_LAYER_0)
    bg1 = get_background(BACKGROUND_LAYER_1)

    # SCROLL & OFFSET
    offset_x, offset_y = 0, 650

    # PLAYER
    player = Player(PLAYER_START_X, PLAYER_START_Y, PLAYER_WIDTH, PLAYER_HEIGHT)

    # HEARTS
    hearts = HEARTS

    # BOSS
    boss = Boss(BOSS_START_X, BOSS_START_Y, BOSS_WIDTH, BOSS_HEIGHT)
    projectiles = []

    # COLUMN
    column = Column(0, -320, 45, 90)

    # OBJECTS & BLOCKS
    objects = OBJECTS

    # MAIN LOOP
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 1000:
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

        # PLAYER
        if not player.dead:
            update_all_methods(player, objects, boss, projectiles, FPS)
        camera.update_shake()
        window.fill("white")
        column.draw(window, offset_x, offset_y)
        column.loop()
        draw(window, player, objects, boss, projectiles, hearts, offset_x, offset_y)

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
