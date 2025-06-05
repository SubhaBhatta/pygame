import pygame

class Player:
    def __init__(self, pos, speed, images):
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.images = images
        self.image = images["default"]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.carrying_trash = False
        self.trash_inventory = []  # can carry up to 5 trash items

    def move(self):
        keys = pygame.key.get_pressed()
        velocity = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            velocity.x = -self.speed
            self.image = self.images["left"]
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            velocity.x = self.speed
            self.image = self.images["right"]
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            velocity.y = -self.speed
            self.image = self.images["up"] if "up" in self.images else self.image
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            velocity.y = self.speed
            self.image = self.images["down"]

        self.pos += velocity
        self.rect.topleft = self.pos

    def get_world_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.rect.width, self.rect.height)

    def pick_trash(self, trash):
        if len(self.trash_inventory) < 5:
            self.trash_inventory.append(trash)
