'''
Exercise 2: Hello Green

Task:
- Successfully render the screen to become green
- python exercise/exercise02.py
'''
import pygame

pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Hello Green")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    
    screen.fill((0, 255, 0))
    pygame.display.flip()
         
         