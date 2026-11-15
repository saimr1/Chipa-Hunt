import pygame

class _SilentSound:
    def play(self, *a, **k): pass
    def stop(self): pass
    def set_volume(self, v): pass
    def get_num_channels(self): return 0

def load_sound(path, volume=1.0):
    try:
        sound = pygame.mixer.Sound(path)
        sound.set_volume(volume)
        return sound
    except (FileNotFoundError, pygame.error):
        return _SilentSound()