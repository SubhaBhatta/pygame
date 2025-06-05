import pygame
import random
import math

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Melee Boss Fight")

# Colors
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLUE = (0, 200, 255)

# Clock
clock = pygame.time.Clock()
FPS = 60

# Player
player_size = 50
player_x = WIDTH // 2
player_y = HEIGHT - player_size - 10
player_speed = 6
player_health = 100
attack_range = 70

# Boss
boss_size = 100
boss_x = WIDTH // 2 - boss_size // 2
boss_y = 50
boss_health = 200
boss_speed = 2

# Medikit
medikit_size = 30
medikit_active = False
medikit_x = 0
medikit_y = 0
medikit_timer = 0
medikit_spawn_delay = 5000  # milliseconds
last_medikit_spawn = pygame.time.get_ticks()

# Fonts
font = pygame.font.SysFont(None, 40)

# Helper functions
def draw_player(x, y):
    pygame.draw.rect(screen, YELLOW, (x, y, player_size, player_size))

def draw_boss(x, y):
    pygame.draw.rect(screen, BROWN, (x, y, boss_size, boss_size))

def draw_health_bar(x, y, health, max_health, width=100, height=10):
    ratio = max(0, health / max_health)
    pygame.draw.rect(screen, RED, (x, y, width, height))
    pygame.draw.rect(screen, GREEN, (x, y, width * ratio, height))

def is_collision(ax, ay, bx, by, size_a, size_b):
    return math.hypot(ax - bx, ay - by) < (size_a + size_b) // 2

# Game loop
running = True
game_over = False
winner = None

while running:
    screen.fill(BLACK)
    clock.tick(FPS)

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click attack
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            distance = math.hypot((player_x + player_size // 2) - (boss_x + boss_size // 2),
                                  (player_y + player_size // 2) - (boss_y + boss_size // 2))
            if distance < attack_range:
                boss_health -= 20

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
            player_y += player_speed

        # Boss movement towards player
        dx = player_x - boss_x
        dy = player_y - boss_y
        distance = math.hypot(dx, dy)
        if distance != 0:
            boss_x += boss_speed * dx / distance
            boss_y += boss_speed * dy / distance

        # Clamp boss inside screen
        boss_x = max(0, min(WIDTH - boss_size, boss_x))
        boss_y = max(0, min(HEIGHT - boss_size, boss_y))

        # Boss damages player if touches
        if is_collision(player_x, player_y, boss_x, boss_y, player_size, boss_size):
            player_health -= 1

        # Spawn medikit if enough time passed and it's not active
        if not medikit_active and current_time - last_medikit_spawn > medikit_spawn_delay:
            medikit_x = random.randint(0, WIDTH - medikit_size)
            medikit_y = random.randint(0, HEIGHT - medikit_size)
            medikit_active = True

        # Check for medikit pickup
        if medikit_active and is_collision(player_x, player_y, medikit_x, medikit_y, player_size, medikit_size):
            player_health += 20
            if player_health > 100:
                player_health = 100
            medikit_active = False
            last_medikit_spawn = pygame.time.get_ticks()

        # Win/Lose conditions
        if boss_health <= 0:
            game_over = True
            winner = "Player Wins!"
        if player_health <= 0:
            game_over = True
            winner = "Boss Wins!"

        # Draw everything
        draw_player(player_x, player_y)
        draw_boss(boss_x, boss_y)
        draw_health_bar(10, 10, player_health, 100)
        draw_health_bar(WIDTH - 110, 10, boss_health, 200)

        if medikit_active:
            pygame.draw.rect(screen, BLUE, (medikit_x, medikit_y, medikit_size, medikit_size))

    else:
        text = font.render(winner, True, WHITE)
        screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))



    pygame.display.update()

pygame.quit()
