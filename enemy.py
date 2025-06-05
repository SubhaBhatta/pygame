import pygame
import random

class Enemy:
    def __init__(self, pos, speed, image):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft=self.pos)

    def move_toward(self, target_pos):
        direction = (target_pos - self.pos).normalize()
        self.pos += direction * self.speed

    def get_world_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.rect.width, self.rect.height)

    def draw(self, surface, camera_offset):
        screen_pos = self.pos - camera_offset
        surface.blit(self.image, screen_pos)

