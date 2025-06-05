import pygame
import random

class World:
    def __init__(self, map_size, trash_img, landfill_img):
        self.map_width, self.map_height = map_size
        self.trash_img = trash_img
        self.landfill_img = landfill_img
        self.trash_list = [trash_img.get_rect(topleft=(
            random.randint(100, self.map_width - 100),
            random.randint(100, self.map_height - 100)
        )) for _ in range(5)]
        self.decomposer_zone = landfill_img.get_rect(topleft=(1600, 1600))

    def draw_trash(self, screen, offset):
        for rect in self.trash_list:
            screen.blit(self.trash_img, rect.topleft - offset)

    def draw_landfill(self, screen, offset):
        screen.blit(self.landfill_img, self.decomposer_zone.topleft - offset)
