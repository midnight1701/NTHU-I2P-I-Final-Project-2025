import pygame as pg

from src.interface.components.checkbox import Checkbox
from src.utils import GameSettings
from src.sprites.background import BagSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class BagScene(Scene):
    def __init__(self):
        super().__init__()
        self.background = pg.Rect(0, 0, 720, 540)
        self.background.center = (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2)
        self.fade_check = False
        self.fade = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        self.fade.fill((0, 0, 0, 50))
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)

    @override
    def enter(self) -> None:
        scene_manager.bag_enter_check = True

    @override
    def exit(self) -> None:
        self.fade_check = False
        scene_manager.bag_enter_check = False

    @override
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_ESCAPE):
            scene_manager.change_scene("game")
        scene_manager._scenes["game"].game_manager.bag.update(dt)


    @override
    def draw(self, screen: pg.Surface) -> None:
        scene_manager._scenes["game"].game_manager.bag.draw(screen)

        if not self.fade_check:
            screen.blit(self.fade, (0, 0))
            self.fade_check = True
        else:
            pass