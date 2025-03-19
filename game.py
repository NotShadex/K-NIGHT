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


def draw(win, player, objects, boss, projectiles, offset_x, offset_y, bg0, bg1):
    # backgrounds(win, bg0, bg1, offset_x, offset_y)
    # Drawing objects
    boss.draw(win, offset_x, offset_y)
    for obj in objects:
        obj.draw(win, offset_x, offset_y)

    player.draw(win, offset_x, offset_y)
    for proj in projectiles:
        proj.draw(win, offset_x, offset_y)
    pygame.display.update()


def update_all_methods(player, objects, boss, projectiles, fps):
    player.update_parry()
    player.update_attack()
    player.update_dash()
    player.loop(objects, boss, fps)
    boss.loop(player, projectiles)
    print(projectiles)
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

    # BOSS
    boss = Boss(BOSS_START_X, BOSS_START_Y, BOSS_WIDTH, BOSS_HEIGHT)
    projectiles = []

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

        window.fill("white")
        draw(window, player, objects, boss, projectiles, offset_x, offset_y, bg0, bg1)
        # CLOCK
        clock.tick(FPS)

        if ((player.rect.right - offset_x >= WIDTH - SCROLL_AREA_WIDTH) and player.vel_x > 0) or ((player.rect.left - offset_x <= SCROLL_AREA_WIDTH) and player.vel_x < 0):
            offset_x += player.vel_x

        if ((player.rect.top - offset_y >= HEIGHT - SCROLL_AREA_HEIGHT) and player.vel_y > 0) or ((player.rect.top - offset_y <= SCROLL_AREA_HEIGHT) and player.vel_y < 0):
            offset_y += player.vel_y

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(WINDOW)
