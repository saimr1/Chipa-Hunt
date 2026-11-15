import sys
import pygame

if "emscripten" in sys.platform:
    import pygbag.pygame as pygame
    pygame.mixer.pre_init(44100, -16, 2, 512)

from game.game import Game

def main():
    pygame.init()
    g = Game()
    g.run()

if __name__ == "__main__":
    main()