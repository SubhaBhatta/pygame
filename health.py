import pygame

class HealthSystem:
    def __init__(self, max_health):
        self.max_health = max_health
        self.current_health = max_health
        self.last_hit_time = 0
        self.damage_cooldown = 1000  # milliseconds
        self.health_bar_width = 200
        self.health_bar_height = 20
        self.health_bar_pos = (20, 60)

    def take_damage(self, amount=1):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time > self.damage_cooldown:
            self.current_health -= amount
            self.last_hit_time = current_time
            return True
        return False

    def is_dead(self):
        return self.current_health <= 0

    def draw_health_bar(self, surface):
        ratio = self.current_health / self.max_health
        # Background (empty health)
        pygame.draw.rect(surface, (255, 0, 0), 
                        (*self.health_bar_pos, self.health_bar_width, self.health_bar_height))
        # Foreground (current health)
        pygame.draw.rect(surface, (0, 255, 0), 
                        (*self.health_bar_pos, self.health_bar_width * ratio, self.health_bar_height))
        # Border
        pygame.draw.rect(surface, (255, 255, 255), 
                        (*self.health_bar_pos, self.health_bar_width, self.health_bar_height), 2)

    def reset(self):
        self.current_health = self.max_health
        self.last_hit_time = 0