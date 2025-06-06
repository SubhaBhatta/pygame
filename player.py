import pygame
import math
from weapon import Sword

# Key constants
K_LEFT = pygame.K_LEFT
K_RIGHT = pygame.K_RIGHT
K_UP = pygame.K_UP
K_DOWN = pygame.K_DOWN
K_a = pygame.K_a
K_d = pygame.K_d
K_w = pygame.K_w
K_s = pygame.K_s
K_SPACE = pygame.K_SPACE

class Player:
    def __init__(self, pos, speed, animations):
        # Position and movement
        self.pos = pygame.Vector2(pos)
        self.speed = speed * 80  # Adjusted for smoother movement with delta time
        self.direction = pygame.Vector2(0, 0)
        self.facing = pygame.Vector2(0, 1)  # Track facing direction for attacks
        self.knockback_force = 15
        # Animation system
        self.animations = animations
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15  # Slower for more natural movement
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=self.pos)
        
        # Inventory system
        self.carrying_trash = False
        self.trash_inventory = []
        self.max_trash_capacity = 5
        
        # Health system
        self.health = 4
        self.max_health = 4
        self.invulnerable = False
        self.last_hit_time = 0
        self.hit_cooldown = 1000  # 1 second invulnerability after being hit
        
        # Combat system
        self.has_sword = False
        self.sword = Sword(self)
        self.attacking = False
        self.attack_cooldown = 300  # milliseconds between attacks
        self.last_attack_time = 0
        
        # State tracking
        self.last_update = pygame.time.get_ticks()

    def animate(self):
        """Handle animation cycling"""
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]

    def get_input(self):
        """Handle all keyboard input"""
        keys = pygame.key.get_pressed()
        
        # Reset movement
        self.direction.x, self.direction.y = 0, 0
        
        # Horizontal movement
        if keys[K_LEFT] or keys[K_a]:
            self.direction.x = -1
            self.status = 'left'
            self.facing = pygame.Vector2(-1, 0)
        elif keys[K_RIGHT] or keys[K_d]:
            self.direction.x = 1
            self.status = 'right'
            self.facing = pygame.Vector2(1, 0)
        
        # Vertical movement
        if keys[K_UP] or keys[K_w]:
            self.direction.y = -1
            self.status = 'up'
            self.facing = pygame.Vector2(0, -1)
        elif keys[K_DOWN] or keys[K_s]:
            self.direction.y = 1
            self.status = 'down'
            self.facing = pygame.Vector2(0, 1)
        
        # Normalize diagonal movement
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
            
        # Sword attack
        if keys[K_SPACE] and self.has_sword and not self.attacking:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.attack_cooldown:
                self.attack(current_time)

    def move(self, dt):
        """Update player position and state"""
        self.get_input()
        
        # Apply movement
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos
        
        # Update animations
        if self.direction.magnitude() > 0:
            self.animate()
        else:
            # Reset to first frame when not moving
            self.frame_index = 0
            self.image = self.animations[self.status][self.frame_index]
        
        # Update sword
        if self.has_sword:
            self.sword.update()
            
        # Update invulnerability
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time - self.last_hit_time > self.hit_cooldown:
            self.invulnerable = False

    def attack(self, current_time):
        """Initiate sword attack"""
        if self.has_sword:
            self.attacking = True
            self.last_attack_time = current_time
            self.sword.attack(current_time)
            return True
        return False

    def take_damage(self, amount=1):
        """Handle taking damage from enemies"""
        current_time = pygame.time.get_ticks()
        if not self.invulnerable:
            self.health -= amount
            self.last_hit_time = current_time
            self.invulnerable = True
            
            # Apply knockback
            # (You'll need to track the damage source position)
            
            if self.health <= 0:
                return True  # Player died
            return True  # Damage taken
        return False  # No damage taken

    def get_sword_hitbox(self):
        """Get current sword hitbox for collision detection"""
        if self.has_sword and self.attacking:
            return self.sword.get_hitbox()
        return pygame.Rect(0, 0, 0, 0)  # Empty rect when not attacking

    def get_world_rect(self):
        """Get player's collision rect in world coordinates"""
        return pygame.Rect(
            self.pos.x - self.rect.width//2,
            self.pos.y - self.rect.height//2,
            self.rect.width,
            self.rect.height
        )

    def pick_trash(self, trash):
        """Pick up trash item"""
        if len(self.trash_inventory) < self.max_trash_capacity:
            self.trash_inventory.append(trash)
            self.carrying_trash = True
            return True
        return False

    def draw(self, surface, camera_offset):
        """Draw player and sword with camera offset"""
        screen_pos = self.pos - camera_offset
        
        # Draw player with invulnerability flash effect
        if self.invulnerable:
            flash_phase = (pygame.time.get_ticks() - self.last_hit_time) % 200
            if flash_phase < 100:  # Flash on/off every 100ms
                temp_image = self.image.copy()
                temp_image.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(temp_image, temp_image.get_rect(center=screen_pos))
            else:
                surface.blit(self.image, self.image.get_rect(center=screen_pos))
        else:
            surface.blit(self.image, self.image.get_rect(center=screen_pos))
        
        # Draw sword
        if self.has_sword:
            self.sword.draw(surface, camera_offset)
            
        # Debug: Draw hitbox
        # pygame.draw.rect(surface, (255, 0, 0), self.get_world_rect().move(-camera_offset.x, -camera_offset.y), 1)