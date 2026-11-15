import pygame
import math
import random

from entities.player import BOUNDS_X, BOUNDS_Y
from game.audio import load_sound

ENEMY_WIDTH = 75
ENEMY_HEIGHT = 100
ENEMY_SPEED = 5

SHEET_COLS = 4
SHEET_ROWS = 2

# enemy-Sheet.png, left to right, top to bottom:
# down, down-right, right, up-right
# up,   up-left,    left,  down-left
SHEET_DIRECTIONS = (
    "down",
    "down-right",
    "right",
    "up-right",
    "up",
    "up-left",
    "left",
    "down-left",
)

# 0 degrees points right, 90 points down. These are the eight 45 degree sectors.
SECTOR_DIRECTIONS = (
    "right",
    "down-right",
    "down",
    "down-left",
    "left",
    "up-left",
    "up",
    "up-right",
)

particles = []
huah_sound = None
_frames_cache = {}


def get_huah_sound():
    global huah_sound
    if huah_sound is None:
        huah_sound = load_sound("assets/sounds/huah.wav", 0.5)
    return huah_sound


def spawn_particles(x, y, width, height):
    img = pygame.image.load("assets/images/particles.png").convert_alpha()
    img = pygame.transform.scale(img, (width, height))
    particles.append({"img": img, "x": x, "y": y, "alpha": 255})


def update_particles():
    for p in particles[:]:
        p["alpha"] -= 4
        if p["alpha"] <= 0:
            particles.remove(p)
        else:
            faded = p["img"].copy()
            faded.set_alpha(p["alpha"])
            p["faded"] = faded


def draw_particles(surface, ox=0, oy=0):
    for p in particles:
        surface.blit(p.get("faded", p["img"]), (p["x"] + ox, p["y"] + oy))


def load_sheet(filename, columns, rows):
    sheet = pygame.image.load(filename).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    cell_width = sheet_width // columns
    cell_height = sheet_height // rows

    poses = []
    for row in range(rows):
        for col in range(columns):
            rect = pygame.Rect(col * cell_width, row * cell_height, cell_width, cell_height)
            poses.append(sheet.subsurface(rect).copy())
    return poses


def build_frames(filename, width, height):
    key = (filename, width, height)
    if key in _frames_cache:
        return _frames_cache[key]

    poses = load_sheet(filename, SHEET_COLS, SHEET_ROWS)
    frames = {
        name: pygame.transform.smoothscale(pose, (width, height))
        for name, pose in zip(SHEET_DIRECTIONS, poses)
    }
    _frames_cache[key] = frames
    return frames


class Enemy:
    def __init__(self, x, y, width, height, tileset_file, speed, enemy_list):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.health = 3
        self.direction = "down"
        self.start_timer = 0

        self.max_width = width
        self.max_height = height
        self.collider = [width, height]
        self.collider_width = width
        self.collider_height = height

        self.frames = build_frames(tileset_file, width, height)

        enemy_list.append(self)

    def cooldown(self):
        if self.start_timer < 1:
            self.start_timer += 0.03
            if self.start_timer > 1:
                self.start_timer = 1

    def get_center(self):
        return self.x + self.max_width / 2, self.y + self.max_height / 2

    def update(self, player):
        self.cooldown()
        if self.start_timer < 1:
            return

        player_center = (player.rect.centerx, player.rect.centery)
        enemy_center = self.get_center()
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        distance = math.hypot(dx, dy)

        if distance != 0:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

        angle = math.degrees(math.atan2(dy, dx))
        sector = int((angle + 22.5) // 45) % 8
        self.direction = SECTOR_DIRECTIONS[sector]

    def draw(self, surface, ox=0, oy=0):
        frame = self.frames[self.direction]

        if self.start_timer >= 1:
            surface.blit(frame, (self.x + ox, self.y + oy))
            return

        current_width = int(self.max_width * self.start_timer)
        current_height = int(self.max_height * self.start_timer)
        if current_width <= 0 or current_height <= 0:
            return

        scaled = pygame.transform.scale(frame, (current_width, current_height))
        draw_x = self.x + (self.max_width - current_width) / 2
        draw_y = self.y + (self.max_height - current_height) / 2
        surface.blit(scaled, (draw_x + ox, draw_y + oy))

    def take_damage(self, damage, enemy_list):
        self.health -= damage
        if self.health <= 0:
            self.destroy(enemy_list)

    def destroy(self, enemy_list, play_sound=True):
        spawn_particles(self.x, self.y, self.max_width, self.max_height)
        if play_sound:
            get_huah_sound().play()
        if self in enemy_list:
            enemy_list.remove(self)


def enemy_spawner(player, enemy_list):
    """Generator that spawns an enemy every 60 frames"""
    while True:
        for _ in range(60):
            yield

        while True:
            randomX = random.randint(BOUNDS_X[0], BOUNDS_X[1] - ENEMY_WIDTH)
            randomY = random.randint(BOUNDS_Y[0], BOUNDS_Y[1] - ENEMY_HEIGHT)
            player_center = player.rect.center
            if abs(player_center[0] - randomX) > 250 or abs(player_center[1] - randomY) > 250:
                break

        Enemy(randomX, randomY, ENEMY_WIDTH, ENEMY_HEIGHT,
              "assets/images/enemy-Sheet.png", ENEMY_SPEED, enemy_list)
