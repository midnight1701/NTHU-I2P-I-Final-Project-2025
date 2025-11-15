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
        self.background = BagSprite("UI/UI_Flat_Frame02a.png")
        self.fade_check = False
        self.fade = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        self.fade.fill((0, 0, 0, 50))
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)

        self.close_button = Button(
            "UI/UI_Flat_IconCross01a.png", "UI/UI_Flat_IconCross01a.png",
            905,200, 25, 25,
            lambda: scene_manager.change_scene("game")
        )

    @override
    def enter(self) -> None:
        scene_manager.bag_enter_check = True

    @override
    def exit(self) -> None:
        self.fade_check = False
        scene_manager.bag_enter_check = False

    @override
    def update(self, dt: float) -> None:
        self.close_button.update(dt)
        pass

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.close_button.draw(screen)

        if not self.fade_check:
            screen.blit(self.fade, (0, 0))
            self.fade_check = True
        else:
            pass