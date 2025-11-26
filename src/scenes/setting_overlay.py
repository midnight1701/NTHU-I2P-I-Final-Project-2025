import pygame as pg
import time
import math

from src.core import GameManager
from src.scenes.setting_scene import SettingScene
from src.utils.silder import Slider
from src.interface.components.checkbox import Checkbox
from src.utils import GameSettings
from src.sprites.background import SettingSprite
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager
from src.scenes.overlay import Overlay

class SettingOverlay(Overlay):
    def __init__(self):
        super().__init__()
        self.setting = SettingSprite("UI/UI_Flat_Frame03a.png")
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            350, 390, 75, 75,
            lambda: self.change_scene()
        )

        self.save_button = Button(
            "UI/button_save.png", "UI/button_save_hover.png",
            550, 390, 75, 75,
            lambda: scene_manager._scenes["game"].game_manager.save("saves/new_save.json")
        )

        self.load_button = Button(
            "UI/button_load.png", "UI/button_load_hover.png",
            450, 390, 75, 75,
            lambda: scene_manager._scenes["game"].load_option(GameManager.load("saves/new_save.json"))
        )

        self._slider = Slider(348, 285, 581, 32, 50.0, 0, 100,
                              "assets/images/UI/UI_Flat_FrameSlot03a.png")


        self._checkbox = Checkbox("UI/UI_Flat_ToggleOff01a.png",
                                  "UI/UI_Flat_ToggleOn01a.png",
                                  480, 330, 64, 32,
                                  )

        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)
        self.exit_button.hitbox.x -= 3
        self.exit_button.hitbox.y -= 19

    def update(self, dt):
        self.back_button.update(dt)
        self._slider.silder_update()
        self._checkbox.update()
        self.save_button.update(dt)
        self.load_button.update(dt)
        GameSettings.volume_change((float(self._slider.volume() / 100)))
        sound_manager.update()
        super().update(dt)

    def change_scene(self):
        scene_manager.change_scene("menu")
        self.close = True


    def draw(self, screen):
        super().draw(screen)

        self.setting.draw(screen)
        self.back_button.draw(screen)
        self._slider.draw(screen)
        self._checkbox.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)

        text = self.font.render(f"Volume: {int(round(self._slider.volume(), 1))}", True, (255, 255, 255))
        screen.blit(text, (348, 260))