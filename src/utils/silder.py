import pygame as pg
import math
from src.core.managers import input_manager
from src.core.managers import game_manager
from src.core import engine

class Slider:
    def __init__(self, x, y, width, height, intial_val: float, min_val: int, max_val: int, img_path: str):
        self._container = pg.Rect(x, y, width, height)
        self._intial_value = intial_val
        self._min_value = min_val
        self._max_value = max_val
        self.left, self.right = x, x + width

        self.img = pg.image.load(img_path).convert()
        self.rect = self.img.get_rect()
        self.rect.x, self.rect.y = x + (width // 2) - self.rect.width // 2, y

    def check_if_slider_update(self, mouse_1, mouse_2, mouse_button):
        if self._container.collidepoint(mouse_1, mouse_2) and mouse_button:
            return True
        else:
            return False

    def silder_update(self):
        mouse_pos = engine.input_manager.mouse_pos
        mouse_pressed = pg.mouse.get_pressed()
        if self.check_if_slider_update(mouse_pos[0], mouse_pos[1], mouse_pressed[0]):
            if self.left + 16 <= mouse_pos[0] <= self.right - 16:
                self.rect.centerx = mouse_pos[0]
            else:
                self.rect.centerx = self.left + 16 if mouse_pos[0] < self.left + 16 else self.right - 16

    def draw(self, surface):
        pg.draw.rect(surface, "grey", self._container)
        surface.blit(self.img, self.rect)

    def volume(self):
        volume_range = self.right - self.left - 32
        actual_range = self.rect.centerx - self.left - 16
        volume = (actual_range / volume_range) * (self._max_value - self._min_value) + self._min_value
        return math.ceil(volume)









