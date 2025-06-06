import pygame
import os
import math
from pathlib import Path

class Sword:
    def __init__(self, player):
        self.player = player
        self.attacking = False
        self.attack_frame = 0
        self.attack_speed = 0.5  # Faster animation speed
        self.damage = 1
        self.cooldown = 300  # milliseconds (shorter cooldown)
        self.last_attack_time = 0
        self.attack_range = 80  # Increased range
        self.active_hit_frames = {1, 2}  # Frames when hitbox is active
        self.knockback_force = 15
        self.swing_sound = None  # Sound effect
        
        # Load directional sword images
        self.sword_images = {
            'up': None,
            'down': None,
            'left': None,
            'right': None
        }
        self.load_images()
        self.load_sound()
        self.current_image = self.sword_images['down']

    def load_images(self):
        """Load directional sword images"""
        try:
            assets_dir = Path(__file__).parent / "assets" / "weapons"
            self.sword_images['up'] = pygame.image.load(str(assets_dir / "up.png")).convert_alpha()
            self.sword_images['down'] = pygame.image.load(str(assets_dir / "down.png")).convert_alpha()
            self.sword_images['left'] = pygame.image.load(str(assets_dir / "left.png")).convert_alpha()
            self.sword_images['right'] = pygame.image.load(str(assets_dir / "right.png")).convert_alpha()
            
            # Scale images if needed
            for direction in self.sword_images:
                if self.sword_images[direction]:
                    self.sword_images[direction] = pygame.transform.scale(
                        self.sword_images[direction], 
                        (50, 70)  # Slightly larger
                    )
        except Exception as e:
            print(f"Error loading sword images: {e}")
            self.create_fallback_graphics()

    def load_sound(self):
        """Load sword sound effect"""
        try:
            assets_dir = Path(__file__).parent / "assets" / "weapons"
            sound_path = assets_dir / "sword.wav"
            self.swing_sound = pygame.mixer.Sound(str(sound_path))
            self.swing_sound.set_volume(0.3)  # Adjust volume as needed
        except Exception as e:
            print(f"Error loading sword sound: {e}")
            self.swing_sound = None

    def create_fallback_graphics(self):
        """Create simple placeholder graphics if images can't be loaded"""
        for direction in self.sword_images:
            surf = pygame.Surface((50, 70), pygame.SRCALPHA)
            if direction == 'right':
                pygame.draw.rect(surf, (200, 200, 200), (10, 30, 15, 15))  # Hilt
                pygame.draw.polygon(surf, (230, 230, 230), 
                                  [(25, 35), (45, 35), (35, 15)])  # Blade
            elif direction == 'left':
                pygame.draw.rect(surf, (200, 200, 200), (25, 30, 15, 15))
                pygame.draw.polygon(surf, (230, 230, 230), 
                                  [(25, 35), (5, 35), (15, 15)])
            elif direction == 'up':
                pygame.draw.rect(surf, (200, 200, 200), (25, 30, 15, 15))
                pygame.draw.polygon(surf, (230, 230, 230), 
                                  [(35, 20), (35, 40), (15, 30)])
            else:  # down
                pygame.draw.rect(surf, (200, 200, 200), (25, 25, 15, 15))
                pygame.draw.polygon(surf, (230, 230, 230), 
                                  [(35, 45), (35, 25), (55, 35)])
            self.sword_images[direction] = surf

    def attack(self, current_time):
        """Start attack animation if not on cooldown"""
        if current_time - self.last_attack_time > self.cooldown:
            self.attacking = True
            self.attack_frame = 0
            self.last_attack_time = current_time
            # Play sound effect if available
            if self.swing_sound:
                self.swing_sound.play()
            return True
        return False

    def update(self):
        """Update attack animation"""
        if self.attacking:
            self.attack_frame += self.attack_speed
            if self.attack_frame >= 4:  # 4-frame attack animation
                self.attacking = False
                self.attack_frame = 0

    def get_hitbox(self):
        """Calculate current hitbox based on player direction"""
        if not self.attacking or int(self.attack_frame) not in self.active_hit_frames:
            return pygame.Rect(0, 0, 0, 0)  # No hitbox when not attacking
        
        # Larger hitbox during active frames
        hitbox_size = 60
        offset_x, offset_y = 0, 0
        
        if self.player.status == 'right':
            offset_x = self.attack_range
        elif self.player.status == 'left':
            offset_x = -self.attack_range
        elif self.player.status == 'up':
            offset_y = -self.attack_range
        else:  # down
            offset_y = self.attack_range

        return pygame.Rect(
            self.player.rect.centerx + offset_x - hitbox_size//2,
            self.player.rect.centery + offset_y - hitbox_size//2,
            hitbox_size, hitbox_size
        )

    def draw(self, surface, camera_offset):
        """Draw sword with proper positioning and attack effects"""
        self.current_image = self.sword_images[self.player.status]
        pos = pygame.Vector2(self.player.rect.center)
        
        # Base position offsets
        direction_offsets = {
            'right': (35, 0),
            'left': (-35, 0),
            'up': (0, -35),
            'down': (0, 35)
        }
        pos.x += direction_offsets[self.player.status][0]
        pos.y += direction_offsets[self.player.status][1]

        # Attack animation effects
        if self.attacking:
            progress = self.attack_frame / 4
            # Add slight movement during attack
            if self.player.status in ['left', 'right']:
                pos.y += math.sin(progress * math.pi * 2) * 10
            else:
                pos.x += math.sin(progress * math.pi * 2) * 10
            
            # Visual feedback during active hit frames
            if int(self.attack_frame) in self.active_hit_frames:
                highlight = self.current_image.copy()
                highlight.fill((255, 255, 0, 50), special_flags=pygame.BLEND_ADD)
                self.current_image = highlight

        screen_pos = pos - camera_offset
        surface.blit(self.current_image, self.current_image.get_rect(center=screen_pos))