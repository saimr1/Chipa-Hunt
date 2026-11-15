import pygame
import math

PLAYER_WIDTH = 56
PLAYER_HEIGHT = 100

BOUNDS_X = (66, 1214)
BOUNDS_Y = (50, 620)

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


def load_player_frames(filename, width, height):
    sheet = pygame.image.load(filename).convert_alpha()
    frame_width = sheet.get_width() // len(SHEET_DIRECTIONS)
    frame_height = sheet.get_height()
    frames = {}

    for index, name in enumerate(SHEET_DIRECTIONS):
        rect = pygame.Rect(index * frame_width, 0, frame_width, frame_height)
        pose = sheet.subsurface(rect).copy()
        frames[name] = pygame.transform.smoothscale(pose, (width, height))

    return frames


class Player:
    def __init__(self, x, y, width, height, tileset_file, speed):

        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.direction = "down"
        self.walk_timer = 0
        self.bob = 0
        self.health = self.max_health = 3
        self.collider_width = self.width * 0.1
        self.collider_height = self.height * 0.1
        self.heart_full = pygame.transform.scale(pygame.image.load("assets/images/heart.png").convert_alpha(), (50, 50))
        self.heart_empty = pygame.transform.scale(pygame.image.load("assets/images/heart_empty.png").convert_alpha(), (50, 50))
        self.alive = True

        self.frames = load_player_frames(tileset_file, width, height)

    def get_center(self):
        return self.rect.centerx, self.rect.centery

    def update(self, keys, up, down, left, right, game_width, game_height):

        if not self.alive:
            return

        dx = 0
        dy = 0

        if keys[up]:
            dy -= 1
        if keys[down]:
            dy += 1
        if keys[left]:
            dx -= 1
        if keys[right]:
            dx += 1

        if dx or dy:
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

            angle = math.degrees(math.atan2(dy, dx))
            sector = int((angle + 22.5) // 45) % 8
            self.direction = SECTOR_DIRECTIONS[sector]

            self.walk_timer += 1
            if self.walk_timer >= 8:
                self.walk_timer = 0
                self.bob = 2 if self.bob == 0 else 0
        else:
            self.walk_timer = 0
            self.bob = 0

        self.rect.x = max(BOUNDS_X[0], min(self.rect.x, BOUNDS_X[1] - self.width))
        self.rect.y = max(BOUNDS_Y[0], min(self.rect.y, BOUNDS_Y[1] - self.height))

    def display_ui(self, surface):
        for i in range(self.max_health):
            if i < self.health:
                img = self.heart_full
            else:
                img = self.heart_empty
            x = surface.get_width() - (i + 1) * 50 - 10
            y = 10
            surface.blit(img, (x, y))

    def check_death(self):
        if self.health <= 0:
            self.alive = False

    def draw(self, surface, ox=0, oy=0):
        frame = self.frames[self.direction]
        surface.blit(frame, (self.rect.x + ox, self.rect.y - self.bob + oy))
