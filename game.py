import time

from boss import *
from player import *
from interface import *


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


def main_menu(win):
    clock = pygame.time.Clock()
    trans = False
    trans_start = None
    sound = SoundTimer(2)
    play_bt = Button(win, [325, 280], "PLAY", 50, font="assets/Fonts/main.ttf")
    control_bt = Button(win, [325, 330], "CONTROLS", 50, font="assets/Fonts/main.ttf")
    while True:
        mouse_pos = pygame.mouse.get_pos()

        if not trans:
            win.fill("black")
            load_font(win, 150, "K-N1GHT", position=(80, 40), font="assets/Fonts/main.ttf")
            size = pygame.transform.smoothscale_by(SWORD, 0.25)
            win.blit(size, (center_image(size)[0] + 7, center_image(size)[1] - 50))
            for button in [play_bt, control_bt]:
                button.hover(mouse_pos, SELECT)
                button.draw(win)
        else:
            win.fill((130, 0, 0))
            size = pygame.transform.smoothscale_by(SWORD, 0.25)
            win.blit(size, (center_image(size)[0] + 7, center_image(size)[1] - 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_bt.input_check(mouse_pos):
                    trans = True
                    trans_start = pygame.time.get_ticks()
                if control_bt.input_check(mouse_pos):
                    sound.play(CONFIRM)
                    controls(win)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()

        if trans:
            now = pygame.time.get_ticks()
            sound.play(PLAY)
            if now - trans_start > 500:
                trans = False
                main(win)
        clock.tick(FPS)
        pygame.display.update()

def controls(win):
    back_bt = Button(win, [300, 280], "BACK", 50, font="assets/Fonts/main.ttf")

    while True:
        mouse_pos = pygame.mouse.get_pos()

        win.fill("black")
        tutorial_text(win)

        for button in [back_bt]:
            button.hover(mouse_pos, SELECT)
            button.draw(win)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_bt.input_check(mouse_pos):
                    pass
                    #main_menu(win)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
        pygame.display.update()

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
    main_menu(WINDOW)
