import pygame as pg

from src.utils.support import ITEM_PATH, ITEM_LIST
from src.core import GameManager
from src.utils import GameSettings
from src.sprites.background import SettingSprite
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager
from src.core import services
from src.scenes.overlay import Overlay

class ShopOverlay(Overlay):
    def __init__(self):
        super().__init__()

        # Shop data
        self.shop_data = ITEM_LIST
        self.shop_data_alt = {v: i for v, i in enumerate(self.shop_data)}
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
        self.limit = 5
        self.index = 0

        # Shop background
        self.rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH * 0.55, GameSettings.SCREEN_HEIGHT * 0.6)
        self.rect.center = (GameSettings.SCREEN_WIDTH / 2, GameSettings.SCREEN_HEIGHT / 2)
        self.exit_button.hitbox.x = self.rect.topright[0] + 5
        self.exit_button.hitbox.y = self.rect.topright[1]

        # Item display
        self.main_rect = pg.Rect(0, 0, self.rect.width * 0.4, self.rect.height)
        self.main_rect.topleft = self.rect.topleft
        self.item_rect_top = self.main_rect.topleft
        self.item_rect_width, self.item_rect_height = self.main_rect.width, self.main_rect.height / self.limit

        # Item description + Buy & Sell
        self.ui_top = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], self.rect.width * 0.6, self.rect.height * 0.3)
        self.ui_bottom = pg.Rect(self.ui_top.bottomleft[0], self.ui_top.bottomleft[1], self.rect.width * 0.6, self.rect.height * 0.7)



    def draw(self, screen):
        super().draw(screen)
        self.draw_item(screen)
        self.draw_item_ui(screen)

    def draw_item(self, screen):
        pg.draw.rect(screen, (44, 44, 44), self.main_rect)
        box_offset = 0 if self.index < self.limit else -(self.index - self.limit + 1) * self.item_rect_height
        for index, item in enumerate(self.shop_data):
            text_color = "yellow" if self.index == index else "white"
            bg_color = (44, 44, 44) if self.index != index else (169, 169, 169)
            top = self.item_rect_top[1] + index * self.item_rect_height + box_offset
            item_rect = pg.Rect(self.item_rect_top[0], top, self.item_rect_width, self.item_rect_height)
            item_img = resource_manager.get_image(ITEM_PATH[item["name"]])
            item_img = pg.transform.scale(item_img, (self.item_rect_height * 0.35, self.item_rect_height * 0.35))
            item_img_rect = pg.Rect(self.item_rect_top[0] + 14, top + 27, item_img.get_width(), item_img.get_height())

            item_name = self.font.render(item["name"], True, text_color)
            name_rect = item_name.get_rect()
            name_rect.midleft = (item_rect.midleft[0] + 60, item_rect.midleft[1])

            if item_img_rect.colliderect(self.main_rect):
                pg.draw.rect(screen, bg_color, item_rect)
                screen.blit(item_img, item_img_rect)
                screen.blit(item_name, name_rect)

        for i in range(1, min(len(self.shop_data), self.limit)):
            pg.draw.line(screen, (169, 169, 169), (self.item_rect_top[0], self.item_rect_top[1] + i * self.item_rect_height), (self.main_rect.topright[0], self.main_rect.topright[1] + i * self.item_rect_height))


    def draw_item_ui(self, screen):
        item = self.shop_data_alt[self.index]
        pg.draw.rect(screen, (255, 255, 0), self.ui_top)



        pg.draw.rect(screen, (255, 0, 0), self.ui_bottom)


    def update(self, dt):
        super().update(dt)
        if input_manager.key_pressed(pg.K_UP):
            self.index = self.index - 1
        elif input_manager.key_pressed(pg.K_DOWN):
            self.index = self.index + 1
        self.index = self.index % len(self.shop_data)


    def buy(self):
        pass

    def sell(self):
        pass

