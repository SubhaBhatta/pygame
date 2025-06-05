import pygame

class Player:
    def __init__(self, pos, speed, images):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.images = images
        self.image = images["default"]
        self.rect = pygame.Rect(0, 0, 48, 48)
        self.carrying_trash = False

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            self.pos.x += self.speed
            self.image = self.images["right"]
        elif keys[pygame.K_a]:
            self.pos.x -= self.speed
            self.image = self.images["left"]
        elif keys[pygame.K_s]:
            self.pos.y += self.speed
            self.image = self.images["down"]
        elif keys[pygame.K_w]:
            self.pos.y -= self.speed
            self.image = self.images["default"]

    def get_world_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, 48, 48)
