import pygame as pg
from src.scenes.overlay import Overlay

from src.interface.components.checkbox import Checkbox
from src.utils import GameSettings
from src.sprites.background import BagSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class BagOverlay(Overlay):
    def __init__(self):
        super().__init__()
        self.background = pg.Rect(0, 0, 720, 540)
        self.background.center = (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)
        self.exit_button.hitbox.x = self.background.topright[0] + 10
        self.exit_button.hitbox.y = self.background.topright[1]

        self.item_display = False


    def update(self, dt):
        super().update(dt)


    def draw(self, screen):
        super().draw(screen)
        scene_manager._scenes["game"].game_manager.bag.draw(screen)
