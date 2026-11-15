import pygame

class GameObjects:

    def __init__(self, x, y, width, height, image):
        self.width = width
        self.height = height

        self.rect = pygame.Rect(x, y, width, height)

        self.image = pygame.transform.scale(image, (width, height))

        self.velocity = [0, 0]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def draw(self, surface, ox, oy):
        offset = getattr(self, "draw_offset", (0, 0))
        surface.blit(self.image, (self.rect.x + ox + offset[0], self.rect.y + oy + offset[1]))

    def get_center(self):
        return self.rect.center