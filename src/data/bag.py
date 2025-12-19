import pygame as pg

from src.core.services import resource_manager, input_manager, scene_manager
from src.core import services
from src.interface.components import Button
from src.utils import GameSettings
from src.utils.support import Monster, Item, COLOR, MONSTER_PATH, INFO_IMG, DISPLAY_INFO, ITEM_PATH, ITEM_DESCRIPTION
from src.scenes.battle_scene import get_animation_image



# noinspection PyMethodMayBeStatic
class Bag:
    _monsters_data: list[Monster]
    _items_data: list[Item]

    def __init__(self, monsters_data: list[Monster] | None = None, items_data: list[Item] | None = None):
        self._monsters_data = monsters_data if monsters_data else []
        self._items_data = items_data if items_data else []

        self._monsters_dict = {i: k for i, k in enumerate(self._monsters_data)}
        self._items_dict = {i: k for i, k in enumerate(self._items_data)}
        self.info_bag = ["hp", "atk", "def", "speed", "accuracy", "max_def", "max_atk", "max_accuracy", "max_speed", "max_hp"]
        self.limit = 6
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(GameSettings.FPS) / 1000.0
        self.frame_index = 0

        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
        self.font_alt = self.font_alt = pg.font.Font("assets/fonts/Minecraft.ttf", size=20)
        self.background = pg.Rect(0, 0, 720, 540)
        self.background.center = (GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT // 2)
        self.item_rect_top = self.background.topleft
        self.item_rect_width = self.background.width * 0.3
        self.item_rect_height = self.background.height / self.limit
        self.main_rect = pg.Rect(self.item_rect_top[0], self.item_rect_top[1], self.item_rect_width, self.background.height)
        animated_bg = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], self.background.width * 0.7, self.background.height * 0.4)
        self.reference = self.font.render("Sephira Core", True, (0, 0, 0))

        # Awakening
        self.awaken_rect = pg.Rect(0, 0, 100, 50)
        self.awaken_rect.topright = self.background.topright[0] - 60, animated_bg.bottomright[1] + 20
        self.awaken_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.awaken_rect.topleft[0], self.awaken_rect.topleft[1],
                                    100, 50,
                                    lambda: services.game_manager.evolution_func())

        self.awaken_text = self.font.render("Awaken", True, (0, 0, 0))
        self.awaken_text_rect = pg.Rect(0, 0, self.awaken_text.get_width(), self.awaken_text.get_height())
        self.awaken_text_rect.center = (self.awaken_button.hitbox.center[0], self.awaken_button.hitbox.center[1] - 5)

        # Revive
        self.revive_rect = pg.Rect(0, 0, 100, 50)
        self.revive_rect.topright = self.awaken_rect.topright[0], self.awaken_rect.topright[1] + 60
        self.revive_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.revive_rect.topleft[0], self.revive_rect.topleft[1],
                                    100, 50,
                                    lambda: services.game_manager.monster_revival())

        self.revive_text = self.font.render("Revive", True, (0, 0, 0))
        self.revive_text_rect = pg.Rect(0, 0, self.revive_text.get_width(), self.awaken_text.get_height())
        self.revive_text_rect.center = (self.revive_button.hitbox.center[0], self.revive_button.hitbox.center[1] - 5)


        # Healing (outside of battle)
        self.healing_rect = pg.Rect(0, 0, 100, 50)
        self.healing_rect.topright = (self.revive_rect.topright[0], self.revive_rect.topright[1] + 60)
        self.healing_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                     self.healing_rect.topleft[0], self.healing_rect.topleft[1],
                                     100, 50,
                                     lambda: services.game_manager.monster_healing())

        self.healing_text = self.font.render("Heal", True, (0, 0, 0))
        self.healing_text_rect = pg.Rect(0, 0, self.healing_text.get_width(), self.healing_text.get_height())
        self.healing_text_rect.center = (self.healing_button.hitbox.center[0], self.healing_button.hitbox.center[1] - 5)


        self.index = 0
        self.switch = False
        self.curr_surface = pg.display.get_surface()



    def switch_bag(self):
        self.switch = not self.switch
        self.index = 0


    def update(self, dt: float):
        if services.game_manager.player.blocked:
            if input_manager.key_pressed(pg.K_UP):
                self.index = self.index - 1
            elif input_manager.key_pressed(pg.K_DOWN):
                self.index = self.index + 1
            self.index = (self.index % len(self._monsters_data)) if not self.switch else (self.index % len(self._items_data))

        self._monsters_dict = {i: k for i, k in enumerate(self._monsters_data)}
        self._items_dict = {i: k for i, k in enumerate(self._items_data)}

        self.awaken_button.update(dt)
        self.revive_button.update(dt)
        self.healing_button.update(dt)

    def change_monster(self, idx, evolved):
        self._monsters_data[idx] = evolved


    def draw(self, screen: pg.Surface):
        if not self.switch:
            self.draw_monster(screen)
            self.draw_monster_info_bg(screen)
        elif self.switch:
            self.draw_item(screen)
            self.draw_item_info(screen)
        screen.blit(self.font.render("Press [Z] to switch between item and monster bag", True, (255, 255, 0)), pg.Rect(self.background.bottomleft[0], self.background.bottomleft[1] + 10, self.background.width, self.font.get_height()))


    def draw_monster(self, screen):
        pg.draw.rect(screen, (44, 44, 44), self.main_rect, border_top_left_radius=12, border_bottom_left_radius=12)
        box_offset = 0 if self.index < self.limit else -(self.index - self.limit + 1) * self.item_rect_height
        for index, monster in enumerate(self._monsters_data):
            text_color = "yellow" if self.index == index else "white"
            bg_color = (44, 44, 44) if self.index != index else (169, 169, 169)
            top = self.item_rect_top[1] + index * self.item_rect_height + box_offset
            monster_rect = pg.Rect(self.item_rect_top[0], top, self.item_rect_width, self.item_rect_height)
            icon_rect = pg.Rect(self.item_rect_top[0] + 10, top + 10, self.item_rect_width, self.item_rect_height)
            monster_img = self.get_img(MONSTER_PATH[monster["name"]]["sprite_path"])

            monster_name = self.font.render(monster["name"], True, text_color)
            text_rect = monster_name.get_rect()
            text_rect.midleft = (monster_rect.midleft[0] + 90, monster_rect.midleft[1])

            info_bg = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], self.background.width * 0.7, self.background.height)

            if monster_rect.colliderect(self.background):
                if monster_rect.collidepoint(self.background.topleft):
                    pg.draw.rect(screen, bg_color, monster_rect, 0, 0, 12)
                elif monster_rect.collidepoint(self.background.bottomleft[0] + 1, self.background.bottomleft[1] + -1):
                    pg.draw.rect(screen, bg_color, monster_rect, border_bottom_left_radius=12)
                else:
                    pg.draw.rect(screen, bg_color, monster_rect)
                screen.blit(monster_img, icon_rect)
                screen.blit(monster_name, text_rect)

            pg.draw.rect(screen, (44, 44, 44), info_bg)

        for i in range(1, min(len(self._monsters_data), self.limit)):
            pg.draw.line(screen, (169, 169, 169), (self.item_rect_top[0], self.item_rect_top[1] + i * self.item_rect_height), (self.main_rect.topright[0], self.main_rect.topright[1] + i * self.item_rect_height))


    def draw_monster_info_bg(self, screen):
        monster = self._monsters_dict[self.index]
        sprite = get_animation_image(MONSTER_PATH[monster["name"]]["animation_path"])
        self.frame_index += GameSettings.ANIMATION_SPEED * self.dt
        img = sprite[int(self.frame_index % len(sprite))]
        img = pg.transform.scale(img, (200, 200))

        border = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], 2, self.background.height)
        animated_bg = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], self.background.width * 0.7, self.background.height * 0.4)
        animated = pg.Rect(0, 0, 200, 200)
        animated.center = (animated_bg.center[0], animated_bg.center[1] - 10)

        info_bg = pg.Rect(animated_bg.bottomleft[0], animated_bg.bottomleft[1], self.background.width * 0.35, self.background.height * 0.6)
        monster_info = self.get_monster_info(monster)
        top = (info_bg.topleft[0] + 25, info_bg.topleft[1] + 20)

        pg.draw.rect(screen, COLOR[monster["element"]], animated_bg)
        pg.draw.rect(screen, (169, 169, 169), border)
        screen.blit(img, animated)


        # Button draw
        self.awaken_button.draw(screen)
        self.revive_button.draw(screen)
        self.healing_button.draw(screen)
        screen.blit(self.awaken_text, self.awaken_text_rect)
        screen.blit(self.revive_text, self.revive_text_rect)
        screen.blit(self.healing_text, self.healing_text_rect)


        for index, (char, val) in enumerate(monster_info.items()):
            if char in ["max_def", "max_atk", "max_accuracy", "max_speed", "max_hp"]:
                continue
            text = self.font.render(DISPLAY_INFO[char], True, (255, 255, 255))
            char_img = resource_manager.get_image(INFO_IMG[char])
            char_img = pg.transform.scale(char_img, (20, 20))
            char_rect = pg.Rect(top[0], top[1] + index * 55, text.get_width(), text.get_height())
            img_rect = pg.Rect(char_rect.topright[0] + 13, char_rect.topright[1], 20, 20)
            img_rect.centery = char_rect.centery + 2

            string = "max_" + char
            val = self.font.render(f"{val}/{monster_info[string]}", True, (255, 255, 0))
            val_rect = pg.Rect(char_rect.bottomleft[0], char_rect.bottomleft[1], val.get_width(), val.get_height())

            screen.blit(text, char_rect)
            screen.blit(char_img, img_rect)
            screen.blit(val, val_rect)

        # Draw mana info
        mana_text = self.font.render("Mana", True, (255, 255, 255))
        mana_rect = pg.Rect(top[0] + 150, top[1], mana_text.get_width(), mana_text.get_height())
        mana_val_text = self.font.render(f"{monster["mana"]}/{monster["max_mana"]}", True, (255, 255, 0))
        mana_val_rect = pg.Rect(mana_rect.bottomleft[0], mana_rect.bottomleft[1], mana_val_text.get_width(), mana_val_text.get_height())
        screen.blit(mana_text, mana_rect)
        screen.blit(mana_val_text, mana_val_rect)


    def draw_item(self, screen):
        pg.draw.rect(screen, (44, 44, 44), self.main_rect, border_top_left_radius=12, border_bottom_left_radius=12)
        box_offset = 0 if self.index < self.limit else -(self.index - self.limit + 1) * self.item_rect_height
        for index, item in enumerate(self._items_data):
            text_color = "yellow" if self.index == index else "white"
            bg_color = (44, 44, 44) if self.index != index else (169, 169, 169)
            top = self.item_rect_top[1] + index * self.item_rect_height + box_offset
            item_rect = pg.Rect(self.item_rect_top[0], top, self.item_rect_width, self.item_rect_height)
            icon_rect = pg.Rect(self.item_rect_top[0] + 20, top + 25, self.item_rect_width, self.item_rect_height) if "Potion" not in item["name"] else pg.Rect(self.item_rect_top[0] + 26, top + 25, self.item_rect_width, self.item_rect_height)

            img = resource_manager.get_image(ITEM_PATH[item['name']])
            img = pg.transform.scale(img, (40, 40)) if "Potion" not in item["name"] else pg.transform.scale(img, (25, 40))

            item_name = self.font.render(item["name"], True, text_color, wraplength=self.reference.get_width())
            text_rect = item_name.get_rect()
            text_rect.midleft = (item_rect.midleft[0] + 70, item_rect.midleft[1])

            if item_rect.colliderect(self.background):
                if item_rect.collidepoint(self.background.topleft):
                    pg.draw.rect(screen, bg_color, item_rect, 0, 0, 12)
                elif item_rect.collidepoint(self.background.bottomleft[0] + 1, self.background.bottomleft[1] + -1):
                    pg.draw.rect(screen, bg_color, item_rect, border_bottom_left_radius=12)
                else:
                    pg.draw.rect(screen, bg_color, item_rect)
                screen.blit(img, icon_rect)
                screen.blit(item_name, text_rect)


        for i in range(1, min(len(self._items_data), self.limit)):
            pg.draw.line(screen, (169, 169, 169), (self.item_rect_top[0], self.item_rect_top[1] + i * self.item_rect_height),
                            (self.main_rect.topright[0], self.main_rect.topright[1] + i * self.item_rect_height))


    def draw_item_info(self, screen):
        item = self._items_dict[self.index]
        info_bg_top = pg.Rect(self.main_rect.topright[0], self.main_rect.topright[1], self.background.width * 0.7, self.background.height * 0.35)
        bg_img_top = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_Frame03a.png"), (info_bg_top.width, info_bg_top.height))
        info_bg_bottom = pg.Rect(info_bg_top.bottomleft[0], info_bg_top.bottomleft[1], info_bg_top.width, self.background.height * 0.65)
        bg_img_bottom = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_Frame02a.png"), (info_bg_bottom.width, info_bg_bottom.height))

        quantity = item["count"]
        quantity_text = self.font.render(f"Quantity: {quantity}", True, (0, 0, 0))
        quantity_rect = pg.Rect(info_bg_top.bottomleft[0] + 17, info_bg_top.bottomleft[1] - quantity_text.get_height() - 6, quantity_text.get_width(), quantity_text.get_height())
        description = ITEM_DESCRIPTION[item["name"]]
        descript_rect = pg.Rect(info_bg_bottom.topleft[0] + 16, info_bg_bottom.topleft[1] + 16, info_bg_bottom.width - 32, quantity_text.get_height())
        descript_text = self.font.render(description, True, (0, 0, 0), wraplength=descript_rect.width)

        top_item_icon = pg.transform.scale(resource_manager.get_image(ITEM_PATH[item["name"]]), (info_bg_top.height * 0.5, info_bg_top.height * 0.5) if "Potion" not in item["name"] else (info_bg_top.height * 0.3, info_bg_top.height * 0.5))
        rect = pg.Rect(0, 0, top_item_icon.width, top_item_icon.height)
        rect.center = (info_bg_top.center[0] - 14, info_bg_top.center[1])

        screen.blit(bg_img_top, info_bg_top)
        screen.blit(bg_img_bottom, info_bg_bottom)
        screen.blit(quantity_text, quantity_rect)
        screen.blit(descript_text, descript_rect)
        screen.blit(top_item_icon, rect)



    def get_img(self, path):
        img = resource_manager.get_image(path)
        img = pg.transform.scale(img, (55, 55))

        return img


    def get_monster_info(self, monster):
        info = {}
        for i in monster:
            if i not in info and i in self.info_bag:
                info[i] = monster[i]

        return info


    def to_dict(self) -> dict[str, object]:
        return {
            "initial_monsters": list(self._monsters_data),
            "items": list(self._items_data)
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Bag":
        monsters = data.get("initial_monsters") or []
        items = data.get("items") or []
        bag = cls(monsters, items)
        return bag



