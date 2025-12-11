import pygame as pg

from src.utils.support import ITEM_PATH, ITEM_LIST, SHOP_DESCRIPTION
from src.utils import GameSettings
from src.interface.components import Button
from src.core.services import input_manager, resource_manager
from src.core import services
from src.scenes.overlay import Overlay



#noinspection PyMethodMayBeStatic
class ShopOverlay(Overlay):
    def __init__(self):
        super().__init__()

        # Shop data
        self.money = services.game_manager.bag._items_data[0]["count"]
        self.shop_data = ITEM_LIST
        self.shop_data_alt = {v: i for v, i in enumerate(self.shop_data)}
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
        self.info_font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=17)
        self.limit = 5
        self.index = 0
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(GameSettings.FPS) / 1000.0

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
        self.ui_top_bg = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_Frame03a.png"), (self.rect.width * 0.6, self.rect.height * 0.35))
        self.ui_top = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], self.rect.width * 0.6, self.rect.height * 0.35)

        self.ui_bottom_bg = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_Frame02a.png"), (self.rect.width * 0.6, self.rect.height * 0.65))
        self.ui_bottom = pg.Rect(self.ui_top.bottomleft[0], self.ui_top.bottomleft[1], self.rect.width * 0.6, self.rect.height * 0.65)

        self.button_topright = (self.ui_top.topleft[0] + 120, self.ui_top.topleft[1] + 27)
        self.buy_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                 self.button_topright[0], self.button_topright[1], 80, 40,
                                 lambda: self.buy(self.shop_data_alt[self.index]))
        self.buy_rect = pg.Rect(0, 0, 80, 40)
        self.buy_rect.center = (self.buy_button.hitbox.center[0] + 25, self.buy_button.hitbox.center[1] + 5)

        self.sell_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                 self.button_topright[0], self.button_topright[1] + 55 , 80, 40,
                                 lambda: self.sell(self.shop_data_alt[self.index]))
        self.sell_rect = pg.Rect(0, 0, 80, 40)
        self.sell_rect.center = (self.sell_button.hitbox.center[0] + 25, self.sell_button.hitbox.center[1] + 5)


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
            item_img = pg.transform.scale(item_img, (30, 30)) if "Potion" not in item["name"] else pg.transform.scale(item_img, (25, 35))
            item_img_rect = pg.Rect(self.item_rect_top[0] + 14, top + 27, item_img.get_width(), item_img.get_height()) if "Potion" not in item["name"] else pg.Rect(self.item_rect_top[0] + 17, top + 24, item_img.get_width(), item_img.get_height())

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

        # UI - top part
        item_img = resource_manager.get_image(ITEM_PATH[item["name"]])
        item_img = pg.transform.scale(item_img, (45, 45)) if "Potion" not in item["name"] else pg.transform.scale(item_img, (31.25, 50))
        item_rect = pg.Rect(self.ui_top.topleft[0] + 50, self.ui_top.topleft[1] + 50, 40, 40) if "Potion" not in item["name"] else pg.Rect(self.ui_top.topleft[0] + 55, self.ui_top.topleft[1] + 44, 31.25, 50)

        screen.blit(self.ui_top_bg, self.ui_top)
        screen.blit(item_img, item_rect)
        self.buy_button.draw(screen)
        self.sell_button.draw(screen)

        buy_text = self.info_font.render("Buy", True, (0, 0, 0))
        sell_text = self.info_font.render("Sell", True, (0, 0, 0))
        screen.blit(buy_text, self.buy_rect)
        screen.blit(sell_text, self.sell_rect)

        # UI - bottom part
        screen.blit(self.ui_bottom_bg, self.ui_bottom)
        description = SHOP_DESCRIPTION[item["name"]]

        descript_rect = pg.Rect(self.ui_bottom.topleft[0] + 16, self.ui_bottom.topleft[1] + 16, self.ui_bottom.width - 32, self.info_font.get_height())
        descript_text = self.font.render(description, True, (0, 0, 0), wraplength=descript_rect.width)
        screen.blit(descript_text, descript_rect)



    def update(self, dt):
        super().update(dt)
        self.money = services.game_manager.bag._items_data[0]["count"]
        self.buy_button.update(dt)
        self.sell_button.update(dt)
        if input_manager.key_pressed(pg.K_UP):
            self.index = self.index - 1
        elif input_manager.key_pressed(pg.K_DOWN):
            self.index = self.index + 1
        self.index = self.index % len(self.shop_data)

    def reset(self):
        self.index = 0


    def buy(self, item):
        item_name, item_price = item["name"], item["price"]
        for i in services.game_manager.bag._items_data:
            if i["name"] == item_name:
                money = self.money - item_price
                if money >= 0:
                    i["count"] += 1
                    services.game_manager.bag._items_data[0]["count"] = money


    def sell(self, item):
        item_name, item_price = item["name"], item["price"]
        for i in services.game_manager.bag._items_data:
            if i["name"] == item_name and i["count"] > 0:
                i["count"] -= 1
                services.game_manager.bag._items_data[0]["count"] += int(item_price * 0.75)




