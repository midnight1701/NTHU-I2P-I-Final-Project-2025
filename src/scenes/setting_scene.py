import pygame as pg


from src.utils.silder import Slider
from src.interface.components.checkbox import Checkbox
from src.utils import GameSettings
from src.sprites.background import SettingSprite
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager
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

        self._slider = Slider(348, 281, 581, 32, 50.0, 0, 100,
                              "assets/images/UI/UI_Flat_FrameSlot03a.png")

        self._checkbox = Checkbox("UI/UI_Flat_ToggleOff01a.png",
                                  "UI/UI_Flat_ToggleOn01a.png",
                                  348, 321, 64,32)

        self.fade = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT), pg.SRCALPHA)
        self.fade.fill((0, 0, 0, 50))
        self.fade_check = False
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)

    @override
    def enter(self) -> None:
        scene_manager.setting_enter_check = True
        pass

    @override
    def exit(self) -> None:
        self.fade_check = False
        scene_manager.setting_enter_check = False
        pass

    @override
    def update(self, dt: float) -> None:
        self.back_button.update(dt)
        self._slider.silder_update()
        self._checkbox.update()
        sound_manager.current_bgm.set_volume(float(float(self._slider.volume()) / 100))

    @override
    def draw(self, screen: pg.Surface) -> None:
        self.setting.draw(screen)
        self.back_button.draw(screen)
        self._slider.draw(screen)
        self._checkbox.draw(screen)
        text = self.font.render(f"VOLUME: {self._slider.volume()}", True, (255, 255, 255))
        screen.blit(text, (348, 260))

        if not self.fade_check:
            screen.blit(self.fade, (0, 0))
            self.fade_check = True
        else:
            pass


