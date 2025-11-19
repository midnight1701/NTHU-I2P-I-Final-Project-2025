import pygame as pg
import json
from src.core.services import resource_manager, input_manager
from src.utils import GameSettings
from src.utils.definition import Monster, Item


class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)


        self.background = pg.Rect(0, 0, 720, 540)
        self.background.center = (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2)
        self.item_rect_top = self.background.topleft
        self.item_rect_width = self.background.width * 0.3
        self.item_rect_height = self.background.height / 6

        self._monsters_dict = {i: k for i, k in enumerate(self._monsters_data)}

        self.index = 0
        self.curr_surface = pg.display.get_surface()

    def update(self, dt: float):
        if input_manager.key_pressed(pg.K_UP):
            self.index = self.index - 1 if self.index - 1 >= 0 else 0
        elif input_manager.key_pressed(pg.K_DOWN):
            self.index = self.index + 1 if self.index + 1 <= len(self._monsters_data) - 1 else len(self._monsters_data) - 1
        self.draw(self.curr_surface)


    def draw(self, screen: pg.Surface):
        box_offset = 0 if self.index < 6 else -(self.index - 6 + 1) * self.item_rect_height
        main_rect = pg.Rect(self.item_rect_top[0], self.item_rect_top[1], self.item_rect_width, self.background.height)
        pg.draw.rect(self.curr_surface, "grey", main_rect, border_bottom_left_radius=12, border_top_left_radius=12)

        for index, m in enumerate(self._monsters_data):
            bg_color = "grey" if self.index != index else "white"

            monster_name = self.font.render(m["name"], True, (0, 0, 0))
            monster_img_path = m["sprite_path"]
            top = self.item_rect_top[1] + index * self.item_rect_height + box_offset

            monster_rect = pg.Rect(self.item_rect_top[0], top, self.item_rect_width, self.item_rect_height)

            text_rect = monster_name.get_rect()
            text_rect.midleft = monster_rect.midleft
            text_rect.x = text_rect.x + 90

            monster_icon = resource_manager.get_image(monster_img_path)
            monster_icon = pg.transform.scale(monster_icon, (55, 55))
            icon_rect = monster_icon.get_rect()
            icon_rect.midleft = monster_rect.midleft
            icon_rect.x = icon_rect.x + 20
            icon_rect.y = icon_rect.y - 8


            if monster_rect.colliderect(self.background):
                 if monster_rect.collidepoint(self.background.topleft):
                     pg.draw.rect(screen, bg_color, monster_rect, 0, 0, 12)
                 elif monster_rect.collidepoint(self.background.bottomleft[0] + 1, self.background.bottomleft[1] + -1):
                     pg.draw.rect(screen, bg_color, monster_rect, border_bottom_left_radius=12)
                 else:
                     pg.draw.rect(screen, bg_color, monster_rect)
                 screen.blit(monster_icon, icon_rect)
                 screen.blit(monster_name, text_rect)

        info_rect = pg.Rect(self.item_rect_top[0] + self.item_rect_width, self.item_rect_top[1],
                            self.background.width - self.item_rect_width, self.background.height * 0.5)

        info_text_rect = pg.Rect(self.item_rect_top[0] + self.item_rect_width + 30, self.item_rect_top[1] + 30,
                                 self.background.width - self.item_rect_width, self.background.height / 12)
        info_text_rect_alt = pg.Rect(self.item_rect_top[0] + self.item_rect_width + 30, self.item_rect_top[1] + 60,
                                     self.background.width - self.item_rect_width, self.background.height / 12)

        pg.draw.rect(self.curr_surface, (255, 156, 0), info_rect, border_top_right_radius=12)
        screen.blit(self.font.render(f"Level: {self._monsters_dict[self.index]["level"]}", True, (0, 0, 0)), info_text_rect)
        screen.blit(self.font.render(f"HP: {self._monsters_dict[self.index]["hp"]}/{self._monsters_dict[self.index]["max_hp"]}", True, (0, 0, 0)), info_text_rect_alt)

        item_rect = pg.Rect(self.background.bottomleft[0] + self.item_rect_width,
                            self.background.bottomleft[1] - self.item_rect_height * 3,
                            self.background.width - self.item_rect_width, self.background.height * 0.5)
        pg.draw.rect(self.curr_surface, (0, 128, 225), item_rect, border_bottom_right_radius=12)

        for index, i in enumerate(self._items_data):
            item_name, item_qty = i["name"], i["count"]
            item_img_path = i["sprite_path"]

            item_img = pg.transform.scale(resource_manager.get_image(item_img_path), (55, 55))
            item_text_x, item_text_y = item_rect.topleft[0] + 30, item_rect.topleft[1] + 20
            item_actual_rect = pg.Rect(item_text_x, item_text_y + index * 80, 55, 55)
            item_text_rect = pg.Rect(item_text_x + 80, item_text_y + 24 + index * 80, 100, 55)
            screen.blit(item_img, item_actual_rect)
            screen.blit(self.font.render(f"{item_name} x{item_qty}", True, (0, 0, 0)), item_text_rect)


    def to_dict(self) -> dict[str, object]:
        return {
            "monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("monsters") or []
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag