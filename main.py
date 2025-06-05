import pygame
import sys
import os
import random
import subprocess
from player import Player
from enemy import Enemy
from world import World

# Constants
WIDTH, HEIGHT = 900, 600
MAP_WIDTH, MAP_HEIGHT = 3000, 3000
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trash Collection - Open World")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)


# Helper
def load_image(name, size=None):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        print(f"Image file missing: {path}")
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img

enemy_img = load_image("assets/enemy.jpg", (48, 48))  # Ensure the asset exists
enemy = Enemy((1000, 1000), speed=2, image=enemy_img)

# Images dictionary for the player
images = {
    "default": load_image("assets/raw2.png", (48, 48)),
    "right": load_image("assets/raw.png", (48, 48)),
    "left": load_image("assets/raw1.png", (48, 48)),
    "down": load_image("assets/User.png", (48, 48))
}

player = Player((1800, 250), speed=5, images=images)  # Pass the entire 'images' dictionary to the player

# Load assets
zoom_factor = 4
original_bg = load_image("assets/background.png")
background_img = pygame.transform.scale(original_bg, (
    original_bg.get_width() * zoom_factor,
    original_bg.get_height() * zoom_factor
))
bg_tile_w, bg_tile_h = background_img.get_width(), background_img.get_height()

trash_img = load_image("assets/Trash.png", (36, 36))
landfill_img = load_image("assets/Waste.png", (150, 150))

# Game objects
world = World((MAP_WIDTH, MAP_HEIGHT), trash_img, landfill_img)

# Overlay
light_overlay = pygame.Surface((WIDTH, HEIGHT))
light_overlay.set_alpha(40)
light_overlay.fill((255, 255, 220))

# Draw shadow
def draw_shadow(surface, pos, size=(48, 20)):
    shadow = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
    shadow_rect = shadow.get_rect(center=(pos[0] + 24, pos[1] + 45))
    surface.blit(shadow, shadow_rect)

# Main loop
score = 0
level_completed = False
running = True
camera_offset = pygame.Vector2()

while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement & logic
    player.move()
    player.pos.x = max(0, min(player.pos.x, MAP_WIDTH - player.rect.width))
    player.pos.y = max(0, min(player.pos.y, MAP_HEIGHT - player.rect.height))
    camera_offset.x = player.pos.x - WIDTH // 2
    camera_offset.y = player.pos.y - HEIGHT // 2
    player.rect.topleft = player.pos - camera_offset

    # Enemy logic
    enemy.move_toward(player.pos)
    enemy.rect.topleft = enemy.pos - camera_offset

    # Check if enemy touches the player
    if enemy.get_world_rect().colliderect(player.get_world_rect()):
        screen.fill((0, 0, 0))
        msg = pygame.font.SysFont(None, 48).render("YOU WERE CAUGHT!", True, (255, 0, 0))
        screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    # Check trash pickup
    if not player.carrying_trash:
        for i, rect in enumerate(world.trash_list):
            if player.get_world_rect().colliderect(rect):
                player.carrying_trash = True
                world.trash_list[i].topleft = (
                    random.randint(100, MAP_WIDTH - 100),
                    random.randint(100, MAP_HEIGHT - 100)
                )
                break

    # Trash delivery
    if player.carrying_trash and player.get_world_rect().colliderect(world.decomposer_zone):
        score += 1
        player.carrying_trash = False

    # Draw background
    start_x = int(camera_offset.x // bg_tile_w) * bg_tile_w
    start_y = int(camera_offset.y // bg_tile_h) * bg_tile_h
    end_x = int(camera_offset.x + WIDTH)
    end_y = int(camera_offset.y + HEIGHT)
    for x in range(start_x, end_x + bg_tile_w, bg_tile_w):
        for y in range(start_y, end_y + bg_tile_h, bg_tile_h):
            screen.blit(background_img, (x - camera_offset.x, y - camera_offset.y))

    # Draw world
    world.draw_landfill(screen, camera_offset)
    world.draw_trash(screen, camera_offset)
    draw_shadow(screen, player.rect.topleft)
    screen.blit(player.image, player.rect.topleft)

    # Draw enemy
    draw_shadow(screen, enemy.rect.topleft)
    enemy.draw(screen, camera_offset)

    # UI
    status = f"Score: {score} | Carrying Trash: {'Yes' if player.carrying_trash else 'No'}"
    screen.blit(font.render(status, True, BLACK), (20, 20))
    screen.blit(light_overlay, (0, 0))

    # Completion
    if score >= 5 and not player.carrying_trash:
        level_completed = True

    pygame.display.flip()

    if level_completed:
        pygame.time.wait(800)
        screen.fill(BLACK)
        msg1 = pygame.font.SysFont(None, 48).render("LEVEL COMPLETED!", True, WHITE)
        msg2 = pygame.font.SysFont(None, 36).render("CLOSE THE WINDOW FOR THE BOSS FIGHT!!", True, WHITE)
        screen.blit(msg1, (WIDTH // 2 - msg1.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(msg2, (WIDTH // 2 - msg2.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    subprocess.run([sys.executable, os.path.join(BASE_DIR, "BossFight.py")])
                    sys.exit()

