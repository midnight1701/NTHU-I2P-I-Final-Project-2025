import pygame as pg

from src.utils import GameSettings
from src.interface.components import Button



class Overlay:
    def __init__(self):
        self.fade = pg.Surface((GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT))
        self.fade.set_alpha(150)
        self.exit_button = Button("UI/button_x.png", "UI/button_x_hover.png",
                                  980, 200, 50, 50,
                                  lambda: self.close_overlay())
        self.close = False

    def draw(self, screen):
        screen.blit(self.fade, (0, 0))
        self.exit_button.draw(screen)

    def close_overlay(self):
        self.close = True

    def update(self, dt):
        self.exit_button.update(dt)
