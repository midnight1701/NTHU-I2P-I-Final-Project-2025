import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# --- Create overlay ONCE ---
overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
overlay.fill((0, 0, 0, 128))  # RGBA: last value is transparency (128/255)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((50, 100, 200))  # Background

    # --- Just draw the overlay, don't recreate it ---
    screen.blit(overlay, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()