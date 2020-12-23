from typing import SupportsFloat
import pygame
import math
import random
from pygame.locals import K_a, K_w, K_s, K_d


width, height = 640, 480
DELTA_POS = {K_w: (0, -5), K_a: (-5, 0), K_s: (0, 5), K_d: (5, 0)}

badger_timer = 150
badgers = []

ARROW_SPEED = 10

BADGER_TIMER_MIN = 100
BADGER_TIMER_MAX = 150
RUNNING = 0
GAMEOVER = -1
YOUWIN = 1 
MAX_TIME = 90000

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
hit_sound.set_volume(0.05)
badger_sound.set_volume(0.05)
shoot_sound.set_volume(0.05)

keys = {K_w: False, K_a: False, K_s: False, K_d: False}
player_pos = [150, 150]
acc = [0, 0]
arrows = []
castle_health = 194

screen = pygame.display.set_mode((width, height))
game_status = RUNNING

pygame.mixer.music.load("resources/audio/moonlight.wav")
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(0.25)

while game_status == RUNNING:
    screen.fill(0)
    # background
    for x in range(width // grass_img.get_width() + 1):
        for y in range(height // grass_img.get_height() + 1):
            screen.blit(
                grass_img, (x * grass_img.get_width(), y * grass_img.get_width())
            )
    # castle
    for x in range(4):
        screen.blit(castle_img, (0, 105 * x + 30))

    # rabbit
    mouse_pos = pygame.mouse.get_pos()
    angle = math.atan2(
        mouse_pos[1] - (player_pos[1] + rabbit_img.get_height() / 2),
        mouse_pos[0] - (player_pos[0] + rabbit_img.get_height() / 2),
    )
    rotated_rabbit_img = pygame.transform.rotate(rabbit_img, 360 - angle * 57.29)
    rotated_player_pos = (
        player_pos[0] - rotated_rabbit_img.get_rect().width / 2,
        player_pos[1] - rotated_rabbit_img.get_rect().height / 2,
    )
    screen.blit(rotated_rabbit_img, rotated_player_pos)

    # arrow
    arrow_index = 0
    for theta, arrow in arrows:
        v_x = math.cos(theta) * ARROW_SPEED
        v_y = math.sin(theta) * ARROW_SPEED
        arrow.left += v_x
        arrow.top += v_y
        if (
            arrow.left < -arrow_img.get_width()
            or arrow.left > width
            or arrow.top < -arrow_img.get_height()
            or arrow.top > height
        ):
            arrows.pop(arrow_index)
            continue
        arrow_index += 1

    for theta, arrow in arrows:
        rotated_arrow = pygame.transform.rotate(arrow_img, 360 - theta * 57.29)
        screen.blit(rotated_arrow, (arrow.left, arrow.top))

    # badger
    if badger_timer == 0:
        badger = pygame.Rect(badger_img.get_rect())
        badger.left = width
        badger.top = random.randint(50, height - 50)
        badgers.append(badger)
        badger_timer = random.randint(BADGER_TIMER_MIN, BADGER_TIMER_MAX)

    index_badger = 0
    for badger in badgers:
        badger.left -= 3
        if badger.left < 64:
            hit_sound.play()
            castle_health -= random.randint(5, 20)
            badgers.pop(index_badger)
            continue

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
        + str((MAX_TIME - pygame.time.get_ticks() )// 1000 % 60).zfill(2)
    )
    survived_text = font.render(raw_text, True, (0, 0, 0))
    text_rect = survived_text.get_rect()
    text_rect.topright = [635, 5]
    screen.blit(survived_text, text_rect)
    screen.blit(healthbar_img, (5, 5))
    for h in range(castle_health):
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
            arrow.left = rotated_player_pos[0] + rotated_rabbit_img.get_rect().width / 2
            arrow.top = rotated_player_pos[1] + rotated_rabbit_img.get_rect().height / 2
            arrows.append((angle, arrow))

        for key, status in keys.items():
            if status:
                player_pos[0] += DELTA_POS[key][0]
                player_pos[1] += DELTA_POS[key][1]
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