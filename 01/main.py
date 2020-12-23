import math
import random
import pygame
from pygame.locals import K_a, K_w, K_s, K_d
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    BADGER_SPEED,
    DELTA_POS,
    ARROW_SPEED,
    BADGER_TIMER_MIN,
    BADGER_TIMER_MAX,
    DAMAGE_MIN,
    DAMAGE_MAX,
    RUNNING,
    GAMEOVER,
    YOUWIN,
    MAX_TIME,
    MAX_CASTLE_HEALTH,
    RABBIT_POS_X,
    RABBIT_POS_Y,
    SOUND_VOLUME,
    BGM_VOLUME,
)

pygame.init()
pygame.mixer.init()

rabbit_img = pygame.image.load("resources/images/dude.png")
grass_img = pygame.image.load("resources/images/grass.png")
castle_img = pygame.image.load("resources/images/castle.png")
arrow_img = pygame.image.load("resources/images/bullet.png")
badger_img = pygame.image.load("resources/images/badguy.png")
healthbar_img = pygame.image.load("resources/images/healthbar.png")
health_img = pygame.image.load("resources/images/health.png")
gameover_img = pygame.image.load("resources/images/gameover.png")
youwin_img = pygame.image.load("resources/images/youwin.png")

hit_sound = pygame.mixer.Sound("resources/audio/explode.wav")
badger_sound = pygame.mixer.Sound("resources/audio/enemy.wav")
shoot_sound = pygame.mixer.Sound("resources/audio/shoot.wav")
hit_sound.set_volume(SOUND_VOLUME)
badger_sound.set_volume(SOUND_VOLUME)
shoot_sound.set_volume(SOUND_VOLUME)

keys = {K_w: False, K_a: False, K_s: False, K_d: False}
rabbit_pos = [RABBIT_POS_X, RABBIT_POS_Y]
arrows = []
badger_timer = random.randint(BADGER_TIMER_MIN, BADGER_TIMER_MAX)
badgers = []
castle_health = MAX_CASTLE_HEALTH

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
game_status = RUNNING

pygame.mixer.music.load("resources/audio/moonlight.wav")
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(BGM_VOLUME)

while game_status == RUNNING:
    screen.fill(0)

    # background
    for x in range(WINDOW_WIDTH // grass_img.get_width() + 1):
        for y in range(WINDOW_HEIGHT // grass_img.get_height() + 1):
            screen.blit(
                grass_img, (x * grass_img.get_width(), y * grass_img.get_width())
            )
    # castle
    for x in range(4):
        screen.blit(castle_img, (0, 105 * x + 30))

    # rabbit
    mouse_pos = pygame.mouse.get_pos()
    rabbit_theta = math.atan2(
        mouse_pos[1] - (rabbit_pos[1] + rabbit_img.get_height() / 2),
        mouse_pos[0] - (rabbit_pos[0] + rabbit_img.get_height() / 2),
    )
    rotated_rabbit_img = pygame.transform.rotate(
        rabbit_img, 360 - rabbit_theta * 180 / math.pi
    )
    rotated_rabbit_pos = (
        rabbit_pos[0] - rotated_rabbit_img.get_rect().width / 2,
        rabbit_pos[1] - rotated_rabbit_img.get_rect().height / 2,
    )
    screen.blit(rotated_rabbit_img, rotated_rabbit_pos)

    # arrow
    arrow_index = 0
    for theta, arrow in arrows:
        v_x = math.cos(theta) * ARROW_SPEED
        v_y = math.sin(theta) * ARROW_SPEED
        arrow.left += v_x
        arrow.top += v_y
        if (
            arrow.left < -arrow_img.get_width()
            or arrow.left > WINDOW_WIDTH
            or arrow.top < -arrow_img.get_height()
            or arrow.top > WINDOW_HEIGHT
        ):
            arrows.pop(arrow_index)
            continue
        arrow_index += 1

    for theta, arrow in arrows:
        rotated_arrow = pygame.transform.rotate(arrow_img, 360 - theta * 180 / math.pi)
        screen.blit(rotated_arrow, (arrow.left, arrow.top))

    # badger
    if badger_timer == 0:
        badger = pygame.Rect(badger_img.get_rect())
        badger.left = WINDOW_WIDTH
        badger.top = random.randint(
            badger_img.get_height(), WINDOW_HEIGHT - badger_img.get_height()
        )
        badgers.append(badger)
        badger_timer = random.randint(BADGER_TIMER_MIN, BADGER_TIMER_MAX)

    index_badger = 0
    for badger in badgers:
        badger.left -= BADGER_SPEED
        if badger.left < castle_img.get_width():
            hit_sound.play()
            castle_health -= random.randint(DAMAGE_MIN, DAMAGE_MAX)
            badgers.pop(index_badger)
            continue

        # clash of badger and arrow
        clash = False
        index_arrow = 0
        for theta, arrow in arrows:
            if badger.colliderect(arrow):
                arrows.pop(index_arrow)
                clash = True
                break
            index_arrow += 1
        if clash:
            badger_sound.play()
            badgers.pop(index_badger)
            continue

        index_badger += 1

    for badger in badgers:
        screen.blit(badger_img, badger)
    badger_timer -= 1

    # healthbar
    font = pygame.font.Font(None, 24)
    raw_text = (
        str((MAX_TIME - pygame.time.get_ticks()) // 60000)
        + ":"
        + str((MAX_TIME - pygame.time.get_ticks()) // 1000 % 60).zfill(2)
    )
    survived_text = font.render(raw_text, True, (0, 0, 0))
    text_rect = survived_text.get_rect()
    text_rect.topright = [WINDOW_WIDTH - 5, 5]
    screen.blit(survived_text, text_rect)
    screen.blit(healthbar_img, (5, 5))
    for h in range(healthbar_img.get_width() * castle_health // MAX_CASTLE_HEALTH - 6):
        screen.blit(health_img, (h + 8, 8))

    # display
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # move by wasd
        if event.type == pygame.KEYDOWN and event.key in keys:
            keys[event.key] = True
        if event.type == pygame.KEYUP and event.key in keys:
            keys[event.key] = False

        # shoot
        if event.type == pygame.MOUSEBUTTONDOWN:
            shoot_sound.play()
            mouse_pos = pygame.mouse.get_pos()
            arrow = pygame.Rect(arrow_img.get_rect())
            arrow.left = rotated_rabbit_pos[0] + rotated_rabbit_img.get_rect().width / 2
            arrow.top = rotated_rabbit_pos[1] + rotated_rabbit_img.get_rect().height / 2
            arrows.append((rabbit_theta, arrow))

        # move
        for key, status in keys.items():
            if status:
                rabbit_pos[0] += DELTA_POS[key][0]
                rabbit_pos[1] += DELTA_POS[key][1]

    if pygame.time.get_ticks() >= MAX_TIME:
        game_status = YOUWIN
    if castle_health <= 0:
        game_status = GAMEOVER


screen.fill((255, 255, 255))

if game_status == YOUWIN:
    youwin = pygame.Rect(youwin_img.get_rect())
    youwin.centerx = screen.get_rect().centerx
    youwin.centery = screen.get_rect().centery
    screen.blit(youwin_img, youwin)

if game_status == GAMEOVER:
    gameover = pygame.Rect(gameover_img.get_rect())
    gameover.centerx = screen.get_rect().centerx
    gameover.centery = screen.get_rect().centery
    screen.blit(gameover_img, gameover)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    pygame.display.flip()
