import pygame
import random
import math
from trash import Trash

class World:
    def __init__(self, map_size, trash_image, landfill_image, npc_pos, safezone_radius):
        self.map_width, self.map_height = map_size
        self.trash_image = trash_image
        self.landfill_image = landfill_image
        self.npc_pos = npc_pos
        self.safezone_radius = safezone_radius
        self.decomposer_zone = pygame.Rect(self.npc_pos[0] - 75, self.npc_pos[1] - 75, 150, 150)
        self.trash_list = []
        self.spawn_trash()

    def spawn_trash(self):
        self.trash_list = []
        num_trash = 7  # Number of trash items to spawn

        for _ in range(num_trash):
            while True:
                x = random.uniform(0, self.map_width - self.trash_image.get_width())
                y = random.uniform(0, self.map_height - self.trash_image.get_height())

                dist_to_npc = math.hypot(x - self.npc_pos[0], y - self.npc_pos[1])

                if dist_to_npc > self.safezone_radius:
                    self.trash_list.append(Trash(self.trash_image, (x, y), (self.map_width, self.map_height)))
                    break

    def draw_landfill(self, screen, camera_offset):
        pos = (self.decomposer_zone.x - camera_offset.x, self.decomposer_zone.y - camera_offset.y)
        screen.blit(self.landfill_image, pos)

    def draw_trash(self, screen, camera_offset):
        for trash in self.trash_list:
            trash.draw(screen, camera_offset)
