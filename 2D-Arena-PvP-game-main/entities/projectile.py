import pygame
import math
import random
from entities.GameObjects import GameObjects
from game.audio import load_sound

pew_sounds = None
vocal_sounds = None
chappal_image = None


def get_pew_sounds():
    global pew_sounds
    if pew_sounds is None:
        pew_sounds = [
            load_sound("assets/sounds/punjabi_pew1.wav", 1.0),
            load_sound("assets/sounds/punjabi_pew2.wav", 1.0),
        ]
    return pew_sounds


def get_vocal_sounds():
    global vocal_sounds
    if vocal_sounds is None:
        vocal_sounds = [
            load_sound("assets/sounds/vocal_hah.wav", 1.0),
            load_sound("assets/sounds/vocal_ooh.wav", 1.0),
            load_sound("assets/sounds/vocal_hey.wav", 1.0),
            load_sound("assets/sounds/vocal_haa.wav", 1.0),
        ]
    return vocal_sounds


def get_chappal_image():
    global chappal_image
    if chappal_image is None:
        image = pygame.image.load("assets/images/chappal.png").convert_alpha()
        chappal_image = pygame.transform.smoothscale(image, (32, 32))
    return chappal_image


def shoot(player, target_pos, bullets_list):
    random.choice(get_pew_sounds()).play()
    random.choice(get_vocal_sounds()).play()

    player_center = (player.rect.centerx, player.rect.centery)
    dx = target_pos[0] - player_center[0]
    dy = target_pos[1] - player_center[1]
    distance = math.hypot(dx, dy)
    speed = 10

    base = get_chappal_image()
    angle = math.degrees(math.atan2(dy, dx)) if distance else 0
    image = pygame.transform.rotate(base, -angle) if distance else base

    bullet = GameObjects(int(player_center[0]) - 16, int(player_center[1]) - 16, 32, 32, base)
    bullet.image = image
    bullet.draw_offset = ((32 - image.get_width()) // 2, (32 - image.get_height()) // 2)

    if distance != 0:
        bullet.velocity = [dx / distance * speed, dy / distance * speed]
    else:
        bullet.velocity = [0, 0]

    bullet.bounces = 0
    bullets_list.append(bullet)


def check_collisions(obj1, obj2):
    x1, y1 = obj1.get_center()
    x2, y2 = obj2.get_center()

    w1 = getattr(obj1, "collider_width", obj1.width)
    h1 = getattr(obj1, "collider_height", obj1.height)
    w2 = getattr(obj2, "collider_width", obj2.width)
    h2 = getattr(obj2, "collider_height", obj2.height)

    if x1 + w1/2 > x2 - w2/2 and x1 - w1/2 < x2 + w2/2:
        return y1 + h1/2 > y2 - h2/2 and y1 - h1/2 < y2 + h2/2
    return False
