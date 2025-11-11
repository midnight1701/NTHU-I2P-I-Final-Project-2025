import pygame as pg

from .sprite import Sprite
from src.utils import GameSettings

class BackgroundSprite(Sprite):
    def __init__(self, image_path: str):
        super().__init__(image_path, (GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        
    def draw(self, screen: pg.Surface):
        screen.blit(self.image, (0, 0))

        
class SettingSprite(Sprite):
    def __init__(self, image_path: str):
        super().__init__(image_path, (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2))

    def draw(self, screen: pg.Surface):
        screen.blit(self.image, (320, 180))