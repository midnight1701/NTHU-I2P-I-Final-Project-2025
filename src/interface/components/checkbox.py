from __future__ import annotations
import pygame as pg

from src.sprites import Sprite
from src.core.services import input_manager, sound_manager
from src.utils import Logger, GameSettings
from typing import Callable, override
from src.interface.components.component import UIComponent

class Checkbox:
    def __init__(self, img_path, img_clicked_path, x, y,
                 width, height, execute: Callable[[], None] | None = None):
        self.img_default = Sprite(img_path, (width, height))
        self.img_clicked = Sprite(img_clicked_path, (width, height))
        self.img = self.img_default
        self.hitbox = pg.Rect(x, y, width, height)
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", size=25)
        self.execute = execute

        self.switched = False
        self.original_vol = None

    def update(self):
        mouse_pos = input_manager.mouse_pos
        if self.hitbox.collidepoint(mouse_pos):
            if input_manager.mouse_pressed(1):
                self.execute()

        if sound_manager.mute:
            self.img = self.img_clicked
        elif not sound_manager.mute:
            self.img = self.img_default


    def draw(self, surface):
        _ = surface.blit(self.img.image, self.hitbox)
        text = self.font.render(f"Mute: {"On" if sound_manager.mute else "Off"}", True, (255, 255, 255))
        surface.blit(text, (348, 336))


