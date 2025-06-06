import pygame
import sys
import os

def load_image(relative_path, size=None):
    full_path = os.path.join(os.getcwd(), "assets", relative_path)
    if not os.path.exists(full_path):
        print(f"[WARNING] Missing image file: {full_path}")
        return pygame.Surface((48, 48), pygame.SRCALPHA)
    img = pygame.image.load(full_path).convert_alpha()
    return pygame.transform.smoothscale(img, size) if size else img

class StartMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.background = None
        self.title_font = None
        self.button_font = None
        self.instruction_font = None
        self.start_button = None
        self.initialized = False

    def load_resources(self):
        try:
            self.background = load_image("menu/menu.png", size=(self.screen_width, self.screen_height))

            self.title_font = pygame.font.SysFont("comicsansms", 80, bold=True)
            self.button_font = pygame.font.SysFont("verdana", 44, bold=True)
            self.instruction_font = pygame.font.SysFont("arial", 26)

            button_width, button_height = 240, 70
            self.start_button = pygame.Rect(
                self.screen_width // 2 - button_width // 2,
                self.screen_height // 2 + 100,
                button_width,
                button_height
            )
            self.initialized = True
        except Exception as e:
            print(f"Error loading menu resources: {e}")
            self.create_fallback_menu()

    def create_fallback_menu(self):
        self.background = pygame.Surface((self.screen_width, self.screen_height))
        self.background.fill((25, 25, 60))

        self.title_font = pygame.font.SysFont("comicsansms", 80, bold=True)
        self.button_font = pygame.font.SysFont("verdana", 44, bold=True)
        self.instruction_font = pygame.font.SysFont("arial", 26)

        button_width, button_height = 240, 70
        self.start_button = pygame.Rect(
            self.screen_width // 2 - button_width // 2,
            self.screen_height // 2 + 100,
            button_width,
            button_height
        )
        self.initialized = True

    def draw_glow_text(self, screen, font, text, x, y, main_color, glow_color):
        for offset in range(6, 0, -2):
            glow = font.render(text, True, glow_color)
            screen.blit(glow, (x - offset, y - offset))
        text_surface = font.render(text, True, main_color)
        screen.blit(text_surface, (x, y))

    def draw(self, screen):
        if not self.initialized:
            self.load_resources()

        screen.blit(self.background, (0, 0))

        # Title with glow
        title_text = "Trash Collector"
        x = self.screen_width // 2 - self.title_font.size(title_text)[0] // 2
        y = self.screen_height // 4
        self.draw_glow_text(screen, self.title_font, title_text, x, y, (255, 255, 255), (0, 255, 180))

        # Hover effect for button
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.start_button.collidepoint(mouse_pos)
        button_color = (60, 180, 90) if hovering else (50, 150, 50)
        border_color = (30, 100, 30)

        # Button rectangle
        pygame.draw.rect(screen, button_color, self.start_button, border_radius=12)
        pygame.draw.rect(screen, border_color, self.start_button, 4, border_radius=12)

        # Button text
        button_text = self.button_font.render("START", True, (255, 255, 255))
        screen.blit(button_text, (
            self.start_button.centerx - button_text.get_width() // 2,
            self.start_button.centery - button_text.get_height() // 2
        ))

        # Instructions
        instructions = [
            "▶ Collect trash and bring it to the landfill",
            "⚔️ Avoid enemies until you get your sword",
            "␣ Press SPACE to attack with your sword"
        ]

        for i, line in enumerate(instructions):
            instr_surf = self.instruction_font.render(line, True, (230, 230, 230, 200))
            screen.blit(instr_surf, (
                self.screen_width // 2 - instr_surf.get_width() // 2,
                self.screen_height // 2 + 20 + i * 28
            ))

    def run(self, screen):
        if not self.initialized:
            self.load_resources()

        clock = pygame.time.Clock()
        running = True

        while running:
            screen.blit(self.background, (0, 0))
            self.draw(screen)

            mouse_pos = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True

            if self.start_button.collidepoint(mouse_pos) and mouse_clicked:
                return True

            pygame.display.flip()
            clock.tick(60)

        return False
