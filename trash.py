import pygame
import random

class Trash:
    def __init__(self, image, pos, map_size):
        self.image = image
        self.pos = pygame.Vector2(pos)
        self.map_width, self.map_height = map_size
        self.rect = self.image.get_rect(topleft=self.pos)

    def relocate(self):
        margin = 50
        x = random.randint(margin, self.map_width - margin)
        y = random.randint(margin, self.map_height - margin)
        self.pos = pygame.Vector2(x, y)
        self.rect.topleft = self.pos

    def draw(self, screen, camera_offset):
        screen.blit(self.image, (self.pos.x - camera_offset.x, self.pos.y - camera_offset.y))

    def get_world_rect(self):
        return self.rect
