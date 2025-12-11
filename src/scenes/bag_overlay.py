import pygame as pg

from src.scenes.overlay import Overlay
from src.utils import GameSettings
from src.interface.components import Button
from src.core.services import scene_manager, input_manager
from src.core import services

class BagOverlay(Overlay):
    def __init__(self):
        super().__init__()
        self.background = pg.Rect(0, 0, 720, 540)
        self.background.center = (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)
        self.exit_button.hitbox.x = self.background.topright[0] + 10
        self.exit_button.hitbox.y = self.background.topright[1]
        self.switch_button = Button


    def update(self, dt):
        super().update(dt)
        if input_manager.key_pressed(pg.K_z):
            services.game_manager.bag.switch_bag()


    def draw(self, screen):
        super().draw(screen)
        scene_manager._scenes["game"].game_manager.bag.draw(screen)
