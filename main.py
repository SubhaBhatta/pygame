import pygame
import sys
import os
import random
from enemy import Enemy
from npc import NPC
from player import Player
from world import World
from trash import Trash
from health import HealthSystem
from audio_manager import AudioManager
import math 
from menu import StartMenu

# Initialize pygame and setup constants
pygame.init()
WIDTH, HEIGHT = 900, 600
menu = StartMenu(WIDTH, HEIGHT)
MAP_WIDTH, MAP_HEIGHT = 3000, 3000
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Setup display and fonts
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trash Collection - Open World")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
large_font = pygame.font.SysFont(None, 74)

# Helper functions
def load_image(name, size=None):
    """Load and optionally scale an image"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
    if not os.path.exists(path):
        print(f"Image file missing: {path}")
        return pygame.Surface((48, 48), pygame.SRCALPHA)
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img

def load_animation_frames(folder, size=(48, 48)):
    """Load all animation frames from a folder"""
    frames = []
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
    if os.path.exists(path):
        frame_files = sorted([f for f in os.listdir(path) if f.endswith('.png')])
        for frame in frame_files:
            frames.append(load_image(os.path.join(folder, frame), size))
    else:
        print(f"Animation folder missing: {path}")
        frames.append(pygame.Surface(size, pygame.SRCALPHA))
    return frames

def draw_shadow(surface, pos, size=(64, 20)):
    """Draw a shadow ellipse under characters"""
    shadow = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
    surface.blit(shadow, shadow.get_rect(center=(pos[0] + 5, pos[1] + 45)))

def draw_message_box(surface, text):
    """Draw a message box with text"""
    padding = 20
    text_surf = font.render(text, True, (0, 0, 0))
    box_rect = pygame.Rect(0, 0, text_surf.get_width() + padding * 2, text_surf.get_height() + padding * 2)
    box_rect.center = (WIDTH // 2, HEIGHT - 60)
    pygame.draw.rect(surface, WHITE, box_rect, border_radius=8)
    surface.blit(text_surf, (box_rect.x + padding, box_rect.y + padding))

# Game initialization
def initialize_game():
    """Initialize all game objects and state"""
    # Load assets
    player_animations = {
        'up': load_animation_frames("assets/player/up"),
        'down': load_animation_frames("assets/player/down"),
        'left': load_animation_frames("assets/player/left"),
        'right': load_animation_frames("assets/player/right")
    }
    
    enemy_img = load_image("assets/enemy.jpg", (64, 64))
    npc_img = load_image("assets/balen.jpg", (128, 128))
    trash_img = load_image("assets/Trash.png", (64, 64))
    landfill_img = load_image("assets/Waste.png", (150, 150))
    background_img = pygame.transform.scale(
        load_image("assets/background.png"),
        (load_image("assets/background.png").get_width() * 4, 
         load_image("assets/background.png").get_height() * 4)
    )
    try:
        hit_sound = pygame.mixer.Sound("assets/weapons/sword.wav")  # Add this line
        hit_sound.set_volume(0.5)  # Adjust volume as needed
    except:
        print("Could not load hit sound effect")
        hit_sound = None
    # Create game objects
    player = Player((1800, 250), speed=3, animations=player_animations)
    player.has_sword = False
    health_system = HealthSystem(max_health=10)
    
    enemies = [
        Enemy((1000, 1000), speed=1, image=enemy_img),
        Enemy((1200, 1200), speed=1, image=enemy_img),
        Enemy((800, 1500), speed=1, image=enemy_img)
    ]
    
    npc = NPC((1600, 1400), image=npc_img, safezone_radius=250, chat_radius=120)
    world = World((MAP_WIDTH, MAP_HEIGHT), trash_img, landfill_img, npc.pos, npc.safezone_radius)
    
    # Game state
    return {
        'player': player,
        'health_system': health_system,
        'enemies': enemies,
        'npc': npc,
        'world': world,
        'background_img': background_img,
        'light_overlay': pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA),
        'camera_offset': pygame.Vector2(),
        'score': 0,
        'enemies_killed': 0,
        'mission_started': False,
        'mission_complete': False,
        'second_mission_complete': False,
        'show_npc_message': False,
        'show_sword_message': False,
        'message_shown_once': False,
        'game_active': True,
        'enemy_spawn_timer': 0,
        'enemy_spawn_interval': 10000,  # 10 seconds
        'current_message': None,
        'message_time': 0,
        'hit_sound': hit_sound
    }

def reset_game(game_state):
    """Reset the game to initial state"""
    game_state.update(initialize_game())
    game_state['light_overlay'].fill((255, 255, 220, 40))

def handle_sword_attack(player, enemies, game_state):
    """Handle sword attack mechanics"""
    hit_occurred = False  # Track if we hit any enemies
    
    if player.attacking:
        sword_hitbox = player.get_sword_hitbox()
        for enemy in enemies[:]:  # Iterate over a copy
            if sword_hitbox.colliderect(enemy.get_world_rect()):
                hit_occurred = True  # We hit at least one enemy
                if enemy.take_damage(player.sword.damage):
                    # Apply knockback effect
                    knockback_dir = (enemy.pos - player.pos).normalize()
                    enemy.pos += knockback_dir * player.sword.knockback_force
                    if enemy.is_dead():
                        enemies.remove(enemy)
                        game_state['enemies_killed'] += 1
                        # Check if second mission is complete
                        if game_state['mission_complete'] and game_state['enemies_killed'] >= 20:
                            game_state['second_mission_complete'] = True
                            game_state['current_message'] = "BALEN: You've proven yourself worthy!"
                            game_state['message_time'] = pygame.time.get_ticks()
        
        # Play hit sound if we connected with an enemy
        if hit_occurred and game_state['hit_sound']:
            game_state['hit_sound'].play()

def handle_enemy_collisions(player, enemies, health_system):
    """Check for and handle collisions with enemies"""
    current_time = pygame.time.get_ticks()
    for enemy in enemies:
        if (enemy.get_world_rect().colliderect(player.get_world_rect()) and 
            health_system.take_damage()):
            # Knockback effect when player is hit
            knockback_dir = (player.pos - enemy.pos).normalize()
            player.pos += knockback_dir * 30  # Adjust knockback strength as needed
            
            if health_system.is_dead():
                return False
    return True

def spawn_new_enemy(game_state):
    """Spawn a new enemy at random edge of map"""
    current_time = pygame.time.get_ticks()
    if current_time - game_state['enemy_spawn_timer'] > game_state['enemy_spawn_interval']:
        edge = random.randint(0, 3)  # 0: top, 1: right, 2: bottom, 3: left
        if edge == 0:  # top
            x = random.randint(0, MAP_WIDTH)
            y = -50
        elif edge == 1:  # right
            x = MAP_WIDTH + 50
            y = random.randint(0, MAP_HEIGHT)
        elif edge == 2:  # bottom
            x = random.randint(0, MAP_WIDTH)
            y = MAP_HEIGHT + 50
        else:  # left
            x = -50
            y = random.randint(0, MAP_HEIGHT)
            
        new_enemy = Enemy((x, y), speed=1, image=game_state['enemies'][0].image)
        game_state['enemies'].append(new_enemy)
        game_state['enemy_spawn_timer'] = current_time

def main():
    """Main game loop"""
    if menu.run(screen):  # This will show the menu and wait for click
        # Proceed with game initialization
        game_state = initialize_game()

    game_state['light_overlay'].fill((255, 255, 220, 40))
    pygame.mixer.init()
    pygame.mixer.music.load("assets/background.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000  # Delta time in seconds
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state['mission_complete']:
                    current_time = pygame.time.get_ticks()
                    game_state['player'].attack(current_time)
                if event.key == pygame.K_r and not game_state['game_active']:
                    reset_game(game_state)
        
        if game_state['game_active']:
            # Update player
            game_state['player'].move(dt)
            game_state['player'].pos.x = max(0, min(game_state['player'].pos.x, MAP_WIDTH - game_state['player'].rect.width))
            game_state['player'].pos.y = max(0, min(game_state['player'].pos.y, MAP_HEIGHT - game_state['player'].rect.height))
            
            # Update camera
            game_state['camera_offset'].x = game_state['player'].pos.x - WIDTH // 2
            game_state['camera_offset'].y = game_state['player'].pos.y - HEIGHT // 2
            
            # Spawn new enemies periodically
            spawn_new_enemy(game_state)
            
            # Update enemies
            for enemy in game_state['enemies']:
                if not game_state['npc'].is_in_safezone(game_state['player'].pos):
                    enemy.move_toward(game_state['player'].pos)
                enemy.update()
            
            # Handle sword attacks immediately after player update
            if game_state['player'].has_sword:
                handle_sword_attack(game_state['player'], game_state['enemies'], game_state)
            
            # Handle collisions
            game_state['game_active'] = handle_enemy_collisions(
                game_state['player'], game_state['enemies'], game_state['health_system'])
            
            # Mission logic
            if game_state['npc'].is_in_chat_radius(game_state['player'].pos):
                current_time = pygame.time.get_ticks()
                message = game_state['npc'].get_message(game_state)
                if message and (current_time - game_state.get('message_time', 0) > 3000):
                    game_state['current_message'] = message
                    game_state['message_time'] = current_time
                
                if not game_state['mission_started']:
                    game_state['mission_started'] = True
                    game_state['show_npc_message'] = True
                    game_state['message_shown_once'] = True
                    game_state['pause_start'] = pygame.time.get_ticks()
            
            # Trash collection
            if game_state['mission_started'] and not game_state['player'].carrying_trash:
                for trash in game_state['world'].trash_list:
                    if game_state['player'].get_world_rect().colliderect(trash.get_world_rect()):
                        game_state['player'].carrying_trash = True
                        trash.relocate()
                        break
            
            # Trash delivery
            if (game_state['player'].carrying_trash and 
                game_state['player'].get_world_rect().colliderect(game_state['world'].decomposer_zone)):
                game_state['score'] += 1
                game_state['player'].carrying_trash = False
            
            # Mission completion
            if game_state['score'] >= 5 and not game_state['mission_complete']:
                game_state['mission_complete'] = True
                game_state['player'].has_sword = True
                game_state['show_sword_message'] = True
                game_state['sword_message_time'] = pygame.time.get_ticks()
        
        # Drawing
        screen.fill((150, 200, 150))
        
        if game_state['game_active']:
            # Draw background
            bg_w, bg_h = game_state['background_img'].get_width(), game_state['background_img'].get_height()
            for x in range(int(game_state['camera_offset'].x // bg_w) * bg_w, 
                         int(game_state['camera_offset'].x + WIDTH) + bg_w, bg_w):
                for y in range(int(game_state['camera_offset'].y // bg_h) * bg_h,
                             int(game_state['camera_offset'].y + HEIGHT) + bg_h, bg_h):
                    screen.blit(game_state['background_img'], 
                              (x - game_state['camera_offset'].x, y - game_state['camera_offset'].y))
            
            # Draw world objects
            game_state['world'].draw_landfill(screen, game_state['camera_offset'])
            game_state['world'].draw_trash(screen, game_state['camera_offset'])
            
            # Draw characters with shadows
            for enemy in game_state['enemies']:
                draw_shadow(screen, (enemy.pos - game_state['camera_offset']).xy)
                enemy.draw(screen, game_state['camera_offset'])
            
            draw_shadow(screen, (game_state['player'].pos - game_state['camera_offset']).xy)
            game_state['player'].draw(screen, game_state['camera_offset'])
            game_state['npc'].draw(screen, game_state['camera_offset'])
            
            # Draw UI
            screen.blit(font.render(f"Score: {game_state['score']} / 5", True, BLACK), (20, 20))
            screen.blit(font.render(f"Enemies Killed: {game_state['enemies_killed']}/20", True, BLACK), (20, 60))
            screen.blit(font.render(f"Carrying Trash: {'Yes' if game_state['player'].carrying_trash else 'No'}", 
                                 True, BLACK), (20, 40))
            game_state['health_system'].draw_health_bar(screen)
            screen.blit(game_state['light_overlay'], (0, 0))
            
            # Debug: Draw sword hitbox
            if game_state['player'].attacking and game_state['player'].has_sword:
                hitbox = game_state['player'].get_sword_hitbox()
                screen_hitbox = hitbox.move(-game_state['camera_offset'].x, -game_state['camera_offset'].y)
                pygame.draw.rect(screen, (255, 0, 0, 100), screen_hitbox, 1)
            
            # Achievement notification
            if game_state['mission_complete'] and not game_state['npc'].achievement_shown:
                msg = font.render("🎉 Achievement Unlocked: Clean Champion!", True, (0, 128, 0))
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                game_state['npc'].achievement_shown = True
                pygame.display.flip()
                pygame.time.wait(2000)
            
            # NPC messages
            if game_state['show_npc_message']:
                draw_message_box(screen, "BALEN: Please collect 5 trash items!")
                pygame.display.flip()
                if pygame.time.get_ticks() - game_state['pause_start'] < 3000:
                    continue
                else:
                    game_state['show_npc_message'] = False
            
            # Sword message
            if game_state.get('show_sword_message', False):
                if pygame.time.get_ticks() - game_state['sword_message_time'] < 3000:
                    draw_message_box(screen, "You got a SWORD! Press SPACE to attack")
                else:
                    game_state['show_sword_message'] = False
            
            # Current NPC message
            if game_state['current_message'] and pygame.time.get_ticks() - game_state['message_time'] < 3000:
                draw_message_box(screen, game_state['current_message'])
        else:
            # Game over screen
            game_over_text = large_font.render("YOU DIED - Press R to restart", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(game_over_text, text_rect)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()