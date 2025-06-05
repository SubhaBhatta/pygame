import pygame
import random

class Trash:
    def __init__(self, image, x, y):
        self.image = image
        self.pos = pygame.Vector2(x, y)
        self.rect = self.image.get_rect(topleft=self.pos)

    def draw(self, screen, camera_offset):
        screen.blit(self.image, self.pos - camera_offset)

    def relocate(self):
        # Implement if you want trash to randomly relocate
        pass

    def get_world_rect(self):
        return self.rect
