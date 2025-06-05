import pygame

class Enemy:
    def __init__(self, pos, speed, image):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.image = image
        self.rect = self.image.get_rect(topleft=self.pos)

    def move_toward(self, target_pos):
        direction = target_pos - self.pos
        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.rect.topleft = self.pos

    def draw(self, surface, camera_offset):
        draw_pos = self.pos - camera_offset
        surface.blit(self.image, draw_pos)

    def get_world_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.rect.width, self.rect.height)
