import pygame as pg

from src.scenes.menu_scene import MenuScene
from src.scenes.game_scene import GameScene
from src.utils import GameSettings
from src.sprites.background import BackgroundSprite, SettingSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from typing import override

class SettingScene(Scene):
    setting: SettingSprite
    back_button: Button

    def __init__(self):
        super().__init__()
        self.setting = SettingSprite("UI/UI_Flat_Frame03a.png")
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            350, 440, 75, 75,
            lambda: scene_manager.change_scene("menu")
        )

        self.fade = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        self.fade.fill((0, 0, 0, 50))
        self.fade_check = False

    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 102 Opening (Part 2).ogg")
        pass

    @override
    def exit(self) -> None:
        self.fade_check = False
        pass

    @override
    def update(self, dt: float) -> None:
        self.back_button.update(dt)

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.setting.draw(screen)
        self.back_button.draw(screen)
        if not self.fade_check:
            screen.blit(self.fade, (0, 0))
            self.fade_check = True
        else:
            pass


