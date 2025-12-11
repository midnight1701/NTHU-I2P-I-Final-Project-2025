import pygame as pg

from src.scenes.overlay import Overlay
from src.utils import GameSettings
from src.interface.components import Button
from src.core.services import scene_manager, input_manager, resource_manager
from src.core import services

class NavigationOverlay(Overlay):
    def __init__(self, navigation):
        super().__init__()
        self.exit_button.hitbox.x -= 70
        self.exit_button.hitbox.y -= 20
        self.bg_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH * 0.4, GameSettings.SCREEN_HEIGHT * 0.4)
        self.bg_rect.center = (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2 - 35)
        self.bg_img = resource_manager.get_image("UI/UI_Flat_Frame03a.png")
        self.bg_img = pg.transform.scale(self.bg_img, (GameSettings.SCREEN_WIDTH * 0.4, GameSettings.SCREEN_HEIGHT * 0.4))
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=17)
        self.font_alt = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
        self.announce_text = self.font_alt.render("Press [T] to cancel navigation", True, (255, 255, 0))
        self.text_rect = pg.Rect(self.bg_rect.bottomleft[0] + 2, self.bg_rect.bottomleft[1], self.announce_text.get_width(), self.announce_text.get_height())

        # BFS call + Button display
        self.navigation = navigation
        self.button_rect = pg.Rect(self.bg_rect.topleft[0] + 30, self.bg_rect.topleft[1] + 30, 70, 70)
        self.shop = Button("UI/button_play.png", "UI/button_play_hover.png",
                           self.button_rect.x, self.button_rect.y, self.button_rect.width, self.button_rect.height,
                           lambda: self.navigation((52, 26)))
        self.shop_text = self.font.render("Shop", True, (0, 0, 0))
        self.shop_text_rect = pg.Rect(self.shop.hitbox.bottomleft[0], self.shop.hitbox.bottomleft[1] + 5, self.shop_text.get_width(), self.shop_text.get_height())
        self.shop_text_rect.centerx = self.button_rect.centerx

        self.gym = Button("UI/button_play.png", "UI/button_play_hover.png",
                          self.shop.hitbox.x + 100, self.shop.hitbox.y, self.button_rect.width, self.button_rect.height,
                          lambda: self.navigation((24, 23)))
        self.gym_text = self.font.render("Gym", True, (0, 0, 0))
        self.gym_text_rect = pg.Rect(0, self.gym.hitbox.bottomleft[1] + 5, self.gym_text.get_width(), self.gym_text.get_height())
        self.gym_text_rect.centerx = self.gym.hitbox.centerx


    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.bg_img, self.bg_rect)
        screen.blit(self.shop_text, self.shop_text_rect)
        screen.blit(self.gym_text, self.gym_text_rect)
        screen.blit(self.announce_text, self.text_rect)
        self.shop.draw(screen)
        self.gym.draw(screen)

    def update(self, dt):
        super().update(dt)
        self.shop.update(dt)
        self.gym.update(dt)