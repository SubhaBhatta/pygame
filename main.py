import pygame
import sys
import os
import random
from enemy import Enemy
from npc import NPC
from player import Player
from world import World
from trash import Trash

pygame.init()
WIDTH, HEIGHT = 900, 600
MAP_WIDTH, MAP_HEIGHT = 3000, 3000
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trash Collection - Open World")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_image(name, size=None):
    path = os.path.join(BASE_DIR, name)
    if not os.path.exists(path):
        print(f"Image file missing: {path}")
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img

images = {
    "default": load_image("assets/raw2.png", (48, 48)),
    "right": load_image("assets/raw.png", (48, 48)),
    "left": load_image("assets/raw1.png", (48, 48)),
    "down": load_image("assets/User.png", (48, 48))
}
enemy_img = load_image("assets/enemy.jpg", (48, 48))
npc_img = load_image("assets/balen.jpg", (64, 64))
trash_img = load_image("assets/Trash.png", (36, 36))
landfill_img = load_image("assets/Waste.png", (150, 150))
background_img = load_image("assets/background.png")
background_img = pygame.transform.scale(background_img, (background_img.get_width() * 4, background_img.get_height() * 4))

player = Player((1800, 250), speed=3, images=images)
player.health = 4
player.max_health = 4

# Create two enemies with same speed as player
enemies = [
    Enemy((1000, 1000), speed=1, image=enemy_img),
    Enemy((1200, 1200), speed=1, image=enemy_img)
]
for enemy in enemies:
    enemy.health = 2
    enemy.max_health = 2

npc = NPC((1600, 1400), image=npc_img, safezone_radius=250, chat_radius=120)
world = World((MAP_WIDTH, MAP_HEIGHT), trash_img, landfill_img, npc.pos, npc.safezone_radius)

camera_offset = pygame.Vector2()
score = 0
mission_started = False
mission_complete = False
show_npc_message = False
message_shown_once = False

light_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
light_overlay.fill((255, 255, 220, 40))

def draw_shadow(surface, pos, size=(48, 20)):
    shadow = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 50), shadow.get_rect())
    surface.blit(shadow, shadow.get_rect(center=(pos[0] + 24, pos[1] + 45)))

def draw_message_box(surface, text):
    padding = 20
    text_surf = font.render(text, True, (0, 0, 0))
    box_rect = pygame.Rect(0, 0, text_surf.get_width() + padding * 2, text_surf.get_height() + padding * 2)
    box_rect.center = (WIDTH // 2, HEIGHT - 60)
    pygame.draw.rect(surface, WHITE, box_rect, border_radius=8)
    surface.blit(text_surf, (box_rect.x + padding, box_rect.y + padding))

def draw_health_bar(surface, x, y, current_health, max_health):
    bar_width = 200
    bar_height = 20
    fill = (current_health / max_health) * bar_width
    border_rect = pygame.Rect(x, y, bar_width, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, (255, 0, 0), fill_rect)
    pygame.draw.rect(surface, (255, 255, 255), border_rect, 2)

def player_attack():
    attack_range = pygame.Rect(player.rect.centerx - 25, player.rect.centery - 25, 50, 50)
    for enemy in enemies:
        if attack_range.colliderect(enemy.rect):
            enemy.health -= 1
            if enemy.health <= 0:
                enemies.remove(enemy)

running = True
while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and mission_complete:
                player_attack()

    # Player movement + clamp to map
    player.move()
    player.pos.x = max(0, min(player.pos.x, MAP_WIDTH - player.rect.width))
    player.pos.y = max(0, min(player.pos.y, MAP_HEIGHT - player.rect.height))
    camera_offset.x, camera_offset.y = player.pos.x - WIDTH // 2, player.pos.y - HEIGHT // 2
    player.rect.topleft = player.pos - camera_offset

    # Enemies chase player only outside NPC safe zone
    for enemy in enemies:
        if not npc.is_in_safezone(player.pos):
            enemy.move_toward(player.pos)
        enemy.rect.topleft = enemy.pos - camera_offset

    # Collision with enemies
    for enemy in enemies:
        if enemy.get_world_rect().colliderect(player.get_world_rect()):
            if not mission_complete:
                screen.fill(BLACK)
                msg = font.render("YOU WERE CAUGHT!", True, (255, 0, 0))
                screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                pygame.display.flip()
                pygame.time.wait(2000)
                pygame.quit()
                sys.exit()
            else:
                player.health -= 1
                if player.health <= 0:
                    screen.fill(BLACK)
                    msg = font.render("YOU DIED!", True, (255, 0, 0))
                    screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    pygame.quit()
                    sys.exit()

    # Start mission and show NPC message once player enters chat radius
    if npc.is_in_chat_radius(player.pos) and not mission_started:
        mission_started = True
        show_npc_message = True
        message_shown_once = True
        pause_start = pygame.time.get_ticks()

    # Draw everything
    screen.fill((150, 200, 150))

    # Tiled background
    bg_w, bg_h = background_img.get_width(), background_img.get_height()
    for x in range(int(camera_offset.x // bg_w) * bg_w, int(camera_offset.x + WIDTH) + bg_w, bg_w):
        for y in range(int(camera_offset.y // bg_h) * bg_h, int(camera_offset.y + HEIGHT) + bg_h, bg_h):
            screen.blit(background_img, (x - camera_offset.x, y - camera_offset.y))

    world.draw_landfill(screen, camera_offset)
    world.draw_trash(screen, camera_offset)

    draw_shadow(screen, player.rect.topleft)
    screen.blit(player.image, player.rect.topleft)

    for enemy in enemies:
        draw_shadow(screen, enemy.rect.topleft)
        enemy.draw(screen, camera_offset)

    npc.draw(screen, camera_offset)

    # Trash collection logic
    if mission_started and not player.carrying_trash:
        for trash in world.trash_list:
            if player.get_world_rect().colliderect(trash.get_world_rect()):
                player.carrying_trash = True
                trash.relocate()
                break

    # Trash delivery logic
    if player.carrying_trash and player.get_world_rect().colliderect(world.decomposer_zone):
        score += 1
        player.carrying_trash = False

    # UI
    screen.blit(font.render(f"Score: {score} / 5", True, BLACK), (20, 20))
    screen.blit(font.render(f"Carrying Trash: {'Yes' if player.carrying_trash else 'No'}", True, BLACK), (20, 40))
    draw_health_bar(screen, 20, 60, player.health, player.max_health)
    screen.blit(light_overlay, (0, 0))

    # Achievement notification
    if score >= 5 and not mission_complete:
        mission_complete = True
        player.image = load_image("assets/User1.jpg", (48, 48))

    if mission_complete and not npc.achievement_shown:
        msg = font.render("🎉 Achievement Unlocked: Clean Champion!", True, (0, 128, 0))
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        npc.achievement_shown = True
        pygame.display.flip()
        pygame.time.wait(2000)

    # Show NPC message and pause game for 3 seconds on first meeting
    if show_npc_message:
        draw_message_box(screen, "BALEN: Please collect 5 trash items!")
        pygame.display.flip()
        if pygame.time.get_ticks() - pause_start < 3000:
            continue
        else:
            show_npc_message = False

    pygame.display.flip()

pygame.quit()
sys.exit()
