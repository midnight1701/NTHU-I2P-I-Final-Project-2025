import pygame

pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Slider")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_radius = height // 2
        self.handle_pos = self.get_handle_position()
        self.dragging = False

    def get_handle_position(self):
        # Calculate handle x position based on current value
        percentage = (self.value - self.min_val) / (self.max_val - self.min_val)
        return self.rect.x + int(percentage * self.rect.width)

    def draw(self, surface):
        # Draw slider track
        pygame.draw.rect(surface, GRAY, self.rect)
        # Draw slider handle
        pygame.draw.circle(surface, RED, (self.handle_pos, self.rect.centery), self.handle_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Update handle position based on mouse x coordinate
                self.handle_pos = max(self.rect.left, min(event.pos[0], self.rect.right))
                # Update slider value
                percentage = (self.handle_pos - self.rect.x) / self.rect.width
                self.value = self.min_val + (percentage * (self.max_val - self.min_val))

# Create a slider instance
slider = Slider(50, 200, 700, 20, 0, 100, 50)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        slider.handle_event(event)

    screen.fill(WHITE)
    slider.draw(screen)

    # Display slider value
    font = pygame.font.Font(None, 36)
    text = font.render(f"Value: {int(slider.value)}", True, BLACK)
    screen.blit(text, (50, 250))

    pygame.display.flip()

pygame.quit()