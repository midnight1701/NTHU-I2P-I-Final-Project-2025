import pygame as pg
import math
from src.core.managers import resource_manager
from src.core.services import scene_manager, input_manager, sound_manager
from src.scenes.overlay import Overlay
from src.utils import GameSettings
from src.utils.support import ITEM_LIST_GACHA, ITEM_FIRST_ROW, ITEM_PATH, ITEM_SECOND_ROW
import random
from src.interface.components import Button
import src.core.services as services


class GachaOverlay(Overlay):
    def __init__(self):
        super().__init__()
        self.gacha_lst = ITEM_LIST_GACHA
        self.bg = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH * 0.55, GameSettings.SCREEN_HEIGHT * 0.6)
        self.bg.center = (GameSettings.SCREEN_WIDTH / 2, GameSettings.SCREEN_HEIGHT / 2 - 25)
        self.bg_img = pg.transform.scale(resource_manager.load_img("UI/UI_Flat_Frame03a.png"), (self.bg.width, self.bg.height))
        self.exit_button.hitbox.x = self.bg.topright[0] + 5
        self.exit_button.hitbox.y = self.bg.topright[1]
        self.button_left_pos = self.bg.bottomleft
        self.left_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                  self.button_left_pos[0] + 120, self.button_left_pos[1] - 170,
                                  200, 70,
                                  lambda: self.one_roll())
        self.button_right_pos = self.bg.bottomright
        self.right_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                  self.button_right_pos[0] - 140 - 120 - 50, self.button_right_pos[1] - 170,
                                  200, 70,
                                   lambda: self.ten_roll())

        self.money = services.game_manager.bag._items_data[0]["count"]


        # Dialogue
        self.text = ""
        self.dialogue_rect = pg.Rect(0, 0, self.bg.width, GameSettings.SCREEN_HEIGHT * 0.2)
        self.dialogue_rect.bottomleft = (self.bg.bottomleft[0] ,720)
        self.dialogue_box = pg.transform.scale(resource_manager.load_img("UI/UI_Flat_BarFill01g.png"), (self.bg.width, GameSettings.SCREEN_HEIGHT * 0.2))
        self.dialogue_box.set_alpha(250)
        self.text_rect = pg.Rect(0, 0, self.bg.width, GameSettings.SCREEN_HEIGHT * 0.2)
        self.text_rect.topleft = self.dialogue_rect.topleft[0] + 12, self.dialogue_rect.topleft[1] + 5



        # Layout
        self.font_alt = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=24)
        self.coin_img = pg.transform.scale(resource_manager.load_img("ingame_ui/coin.png"), (33, 33))
        self.coin_rect_left = pg.Rect(0, 0, 33, 33)
        self.coin_rect_right = pg.Rect(0, 0, 33, 33)

        self.text_left = self.font.render("32", True, (0, 0, 0))
        self.text_right = self.font.render("320", True, (0, 0, 0))
        self.text_rect_left = pg.Rect(0, 0, self.text_left.get_width(), self.text_right.get_height())
        self.text_rect_right = pg.Rect(0, 0, self.text_right.get_width(), self.text_right.get_height())
        self.text_rect_left.midright = self.left_button.hitbox.midright[0] - 25, self.left_button.hitbox.midright[1] - 3
        self.text_rect_right.midright = self.right_button.hitbox.midright[0] - 12, self.right_button.hitbox.midright[1] - 3

        self.coin_rect_left.midright = self.text_rect_left.midleft[0] - 8, self.text_rect_left.midleft[1]
        self.coin_rect_right.midright = self.text_rect_right.midleft[0] - 8, self.text_rect_right.midleft[1]

        self.pull_text_left = self.font.render("1 Pull", True, (0, 0, 0))
        self.pull_text_right = self.font.render("10 Pull", True, (0, 0, 0))
        self.left_rect = self.pull_text_left.get_rect()
        self.right_rect = self.pull_text_right.get_rect()
        self.left_rect.midright = self.coin_rect_left.midleft[0] - 8, self.coin_rect_left.midleft[1]
        self.right_rect.midright = self.coin_rect_right.midleft[0] - 8, self.coin_rect_right.midleft[1]

        self.coin_rect = pg.Rect(0, 0, self.coin_img.get_width(), self.coin_img.get_height())
        self.finance_rect = pg.Rect(0, 0, 110, 50)
        self.finance_rect.bottomright = self.bg.topright[0], self.bg.topright[1] - 10
        self.coin_rect.midleft = (self.finance_rect.midleft[0] + 10, self.finance_rect.midleft[1])
        self.coin_text_rect = pg.Rect(0, 0, 110, 50)
        self.coin_text_rect.midleft = (self.coin_rect.midright[0] + 10, self.coin_rect.midright[1] + 12)

        self.item_dict_count = {
            "HP Potion": 0,
            "ATK Potion": 0,
            "DEF Potion": 0,
            "Mana Potion": 0,
            "Pokeball": 0,
            "Hollow Core": 0,
            "Sephira Core": 0,
            "Ultimate Aegis": 0,
            "Destined Revival": 0
        }

        self.img = {
            "HP Potion": resource_manager.load_img("ingame_ui/red-potion.png"),
            "ATK Potion": resource_manager.load_img("ingame_ui/orange-potion.png"),
            "DEF Potion": resource_manager.load_img("ingame_ui/purple-potion2.png"),
            "Mana Potion": resource_manager.load_img("ingame_ui/blue-potion2.png"),
            "Pokeball": resource_manager.load_img("ingame_ui/ball.png"),
            "Hollow Core": resource_manager.load_img("ingame_ui/core_1.png"),
            "Sephira Core": resource_manager.load_img("ingame_ui/core_16.png"),
            "Ultimate Aegis": resource_manager.load_img("ingame_ui/ticket.png"),
            "Destined Revival": resource_manager.load_img("ingame_ui/core_bypass.png")
        }

        # Gacha system
        self.pull_one = False
        self.pull_ten = False
        self.gacha_item = None
        self.item_weight = [42, 40, 35, 40, 40, 20, 8, 3, 5]

        self.music = False


    def update(self, dt):
        if not self.music:
            sound_manager.play_bgm("Gacha BGM.mp3")
            self.music = True

        super().update(dt)
        self.left_button.update(dt)
        self.right_button.update(dt)
        self.money = scene_manager._scenes["game"].game_manager.bag._items_data[0]["count"]

        if self.pull_one:
            if scene_manager._scenes["game"].game_manager.bag._items_data[0]["count"] >= 32:
                scene_manager._scenes["game"].game_manager.bag._items_data[0]["count"] -= 32
                self.gacha_system()
                for i in scene_manager._scenes["game"].game_manager.bag._items_data:
                    if i["name"] == self.gacha_item[0]:
                        i["count"] += 1
                        break

                self.text = f"Gacha pulled, you have obtained 1 {self.gacha_item[0]}"
                self.gacha_item = None
                self.pull_one = False

        elif self.pull_ten:
            if scene_manager._scenes["game"].game_manager.bag._items_data[0]["count"] >= 320:
                self.text = "Gacha pulled, you have obtained"
                scene_manager._scenes["game"].game_manager.bag._items_data[0]["count"] -= 320
                self.gacha_system(pull=10)
                for i in self.gacha_item:
                    if i in self.item_dict_count:
                        self.item_dict_count[i] += 1

                for i in self.item_dict_count:
                    if self.item_dict_count[i] == 0:
                        continue
                    for y in scene_manager._scenes["game"].game_manager.bag._items_data:
                        if i == y["name"]:
                            y["count"] += self.item_dict_count[i]
                            self.text += f" {y["count"]} {i},"
                            self.item_dict_count[i] = 0
                            break
                self.text = self.text[:-1]
                self.pull_ten = False


    def draw_money(self, screen):
        pg.draw.rect(screen, (255, 255, 255), self.finance_rect)
        pg.draw.rect(screen, (0, 0, 0), self.finance_rect, 3)
        screen.blit(self.coin_img, self.coin_rect)
        text = self.font_alt.render(str(self.money), True, (0, 0, 0))
        screen.blit(text, self.coin_text_rect)

    def item_draw(self, screen):
        top_pos = self.bg.topleft[0] + 120, self.bg.topleft[1] + 70
        for i in range(len(ITEM_FIRST_ROW)):
            if "Potion" in ITEM_FIRST_ROW[i]:
                item_rect = pg.Rect(top_pos[0] + i * 100 + 15, top_pos[1], 70 * (25 / 40), 70)
            else:
                item_rect = pg.Rect(top_pos[0] + i * 100, top_pos[1] + 10, 60, 60)
            item_img = pg.transform.scale(self.img[ITEM_FIRST_ROW[i]], (item_rect.width, item_rect.height))
            screen.blit(item_img, item_rect)

        bottom_pos = top_pos[0] + 55, top_pos[1] + 90
        for i in range(len(ITEM_SECOND_ROW)):
            item_rect_alt = pg.Rect(bottom_pos[0] + i * 100, bottom_pos[1], 70, 70)
            item_img = pg.transform.scale(self.img[ITEM_SECOND_ROW[i]], (item_rect_alt.width, item_rect_alt.height))
            screen.blit(item_img, item_rect_alt)

    def one_roll(self):
        self.pull_one = True

    def ten_roll(self):
        self.pull_ten = True

    def dialouge_display(self, screen):
        screen.blit(self.dialogue_box, self.dialogue_rect)
        text = self.font.render(self.text, True, (255, 255, 255), wraplength=self.bg.width - 30)
        screen.blit(text, self.text_rect)


    def draw(self, screen):
        super().draw(screen)
        screen.blit(self.bg_img, self.bg)
        self.left_button.draw(screen)
        self.right_button.draw(screen)
        screen.blit(self.text_left, self.text_rect_left)
        screen.blit(self.text_right, self.text_rect_right)
        screen.blit(self.coin_img, self.coin_rect_left)
        screen.blit(self.coin_img, self.coin_rect_right)
        screen.blit(self.pull_text_left, self.left_rect)
        screen.blit(self.pull_text_right, self.right_rect)
        self.item_draw(screen)
        self.draw_money(screen)
        self.dialouge_display(screen)


    def gacha_system(self, pull=1):
        if pull == 10:
            self.gacha_item = random.choices(self.gacha_lst, weights=self.item_weight, k=10)
        else:
            self.gacha_item = random.choices(self.gacha_lst, weights=self.item_weight, k=1)
