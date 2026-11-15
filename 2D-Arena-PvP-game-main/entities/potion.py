import math
import random

import pygame

from entities.player import BOUNDS_X, BOUNDS_Y


class Potion:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2.6, 4.0)
        self.velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.phase = random.uniform(0, math.tau)

    def update(self):
        self.rect.x += round(self.velocity[0])
        self.rect.y += round(self.velocity[1])

        if self.rect.left <= BOUNDS_X[0] and self.velocity[0] < 0:
            self.rect.left = BOUNDS_X[0]
            self.velocity[0] = -self.velocity[0]
        elif self.rect.right >= BOUNDS_X[1] and self.velocity[0] > 0:
            self.rect.right = BOUNDS_X[1]
            self.velocity[0] = -self.velocity[0]

        if self.rect.top <= BOUNDS_Y[0] and self.velocity[1] < 0:
            self.rect.top = BOUNDS_Y[0]
            self.velocity[1] = -self.velocity[1]
        elif self.rect.bottom >= BOUNDS_Y[1] and self.velocity[1] > 0:
            self.rect.bottom = BOUNDS_Y[1]
            self.velocity[1] = -self.velocity[1]

    def draw(self, surface, ox=0, oy=0):
        bob = math.sin(pygame.time.get_ticks() / 250 + self.phase) * 3
        surface.blit(self.image, (self.rect.x + ox, self.rect.y + bob + oy))
