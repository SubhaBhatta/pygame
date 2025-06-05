import pygame

class NPC:
    def __init__(self, pos, image, safezone_radius=250, chat_radius=120):
        self.pos = pygame.Vector2(pos)
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.safezone_radius = safezone_radius
        self.chat_radius = chat_radius
        self.achievement_shown = False

    def is_in_safezone(self, player_pos):
        return self.pos.distance_to(player_pos) <= self.safezone_radius

    def is_in_chat_radius(self, player_pos):
        return self.pos.distance_to(player_pos) <= self.chat_radius

    def draw(self, surface, camera_offset):
        pos = self.pos - camera_offset
        surface.blit(self.image, self.image.get_rect(center=pos))
        # Optionally draw the safe zone circle
        pygame.draw.circle(surface, (255, 255, 0), (int(pos.x), int(pos.y)), self.safezone_radius, 2)
