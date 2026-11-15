import pygame
import math
import random
from entities.GameObjects import GameObjects
from game.audio import load_sound

# ---------- Shooting function ----------
pew_sounds = None

def get_pew_sounds():
    global pew_sounds
    if pew_sounds is None:
        pew_sounds = [
            load_sound("assets/sounds/punjabi_pew1.wav", 1.0),
            load_sound("assets/sounds/punjabi_pew2.wav", 1.0),
        ]
    return pew_sounds

def shoot(player, target_pos, bullets_list):
    random.choice(get_pew_sounds()).play()


    bullet_img = pygame.image.load("assets/images/bullet.png").convert_alpha() 
    bullet_img = pygame.transform.scale(bullet_img, (16, 16)) 

    # --- Determine starting position of bullet (player center) ---
    player_center = (player.rect.centerx, player.rect.centery)
    # --- Create a bullet object at player's center --
    bullet = GameObjects(int(player_center[0]), int(player_center[1]), 16, 16, bullet_img)

    dx = target_pos[0] - player_center[0] # difference in x
    dy = target_pos[1] - player_center[1] # difference in y
    distance = math.hypot(dx, dy) # distance using Pythagoras theorem
    speed = 10 # bullet speed in pixels per frame

    if distance != 0:
        # Set velocity so bullet moves in the direction of target at given speed
        bullet.velocity = [dx / distance * speed, dy / distance * speed]
    else:
        bullet.velocity = [0, 0]
        
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