import asyncio
import pygame

from game.game import Game

async def main():
    pygame.init()

    game = Game()
    await game.run()

asyncio.run(main())