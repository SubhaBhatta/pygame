import pygame
import random

class Enemy:
    def __init__(self, pos, speed, image):
        self.pos = pygame.Vector2(pos)
        self.speed = speed * 0.8
        self.image = image
        self.original_image = image.copy()  # Store original for color reset
        self.rect = self.image.get_rect(center=self.pos)  # Changed to center for better collision
        
        # Enhanced health system
        self.max_health = 3  # Increased from 1 to allow multiple hits
        self.health = self.max_health
        self.last_hit_time = 0
        self.hit_cooldown = 300  # Reduced from 500ms for more responsive combat
        self.invulnerable = False  # New state for brief invulnerability after hit
        
        # Damage effect
        self.hit_effect_duration = 150  # Reduced from 200ms
        self.is_hit = False
        self.death_time = 0
        self.death_duration = 300  # milliseconds for death animation
        self.knockback_force = 15  # New: force when hit by sword

    def move_toward(self, target_pos):
        if not self.is_dead():
            direction = (target_pos - self.pos).normalize()
            self.pos += direction * self.speed
            self.rect.center = self.pos  # Using center for more accurate collisions

    def take_damage(self, amount=1):
        current_time = pygame.time.get_ticks()
        if (not self.invulnerable and 
            not self.is_dead() and 
            current_time - self.last_hit_time > self.hit_cooldown):
            
            self.health -= amount
            self.last_hit_time = current_time
            self.is_hit = True
            self.invulnerable = True  # Become briefly invulnerable
            
            if self.is_dead():
                self.death_time = current_time
                return True  # Signal that enemy died
            return True  # Signal that damage was taken
        return False  # No damage taken

    def apply_knockback(self, source_pos, force):
        """Apply knockback effect when hit by sword"""
        if not self.is_dead():
            direction = (self.pos - source_pos).normalize()
            self.pos += direction * force
            self.rect.center = self.pos

    def is_dead(self):
        return self.health <= 0

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Reset hit effect after duration
        if self.is_hit and current_time - self.last_hit_time > self.hit_effect_duration:
            self.is_hit = False
            
        # Reset invulnerability
        if self.invulnerable and current_time - self.last_hit_time > self.hit_cooldown:
            self.invulnerable = False
            
        # Check if death animation is complete
        if self.is_dead() and current_time - self.death_time > self.death_duration:
            return True  # Mark for removal
        return False

    def get_world_rect(self):
        """Returns rect in world coordinates with proper collision size"""
        return pygame.Rect(
            self.pos.x - self.rect.width//2, 
            self.pos.y - self.rect.height//2,
            self.rect.width, 
            self.rect.height
        )

    def draw(self, surface, camera_offset):
        screen_pos = self.pos - camera_offset
        
        if self.is_dead():
            # Death animation - fade out
            progress = min(1.0, (pygame.time.get_ticks() - self.death_time) / self.death_duration)
            alpha = int(255 * (1.0 - progress))
            
            death_image = self.original_image.copy()
            death_image.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(death_image, death_image.get_rect(center=screen_pos))
        else:
            # Normal or hit drawing
            if self.is_hit:
                # Flash effect - alternate between red and normal
                flash_phase = (pygame.time.get_ticks() - self.last_hit_time) % 200
                if flash_phase < 100:  # First half of flash cycle
                    hit_image = self.original_image.copy()
                    hit_image.fill((255, 100, 100, 200), special_flags=pygame.BLEND_RGBA_MULT)
                    surface.blit(hit_image, hit_image.get_rect(center=screen_pos))
                else:
                    surface.blit(self.original_image, self.original_image.get_rect(center=screen_pos))
            else:
                surface.blit(self.original_image, self.original_image.get_rect(center=screen_pos))
            
            # Health bar - only show if damaged
            if self.health < self.max_health:
                health_width = 50
                health_height = 6
                health_ratio = self.health / self.max_health
                
                # Health bar background
                pygame.draw.rect(surface, (60, 60, 60), 
                               (screen_pos.x - health_width//2, screen_pos.y - 30, 
                                health_width, health_height))
                # Current health
                pygame.draw.rect(surface, (0, 255, 0), 
                               (screen_pos.x - health_width//2, screen_pos.y - 30, 
                                health_width * health_ratio, health_height))