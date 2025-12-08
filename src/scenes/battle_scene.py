import random

import pygame as pg
from pygame import K_ESCAPE, K_SPACE
from src.scenes.battle_system import BattleSetup, PlayerTurn

from src.scenes.battle_system import BattleSystem
from src.sprites import BackgroundSprite
from src.utils import GameSettings
from src.utils.support import MONSTER_PATH, INFO_BAR_COLOR
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager
import src.core.services as services


def draw_info_box(surface, x, y, width, height):
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_PEACH = (255, 209, 128)
    offset_x = offset_y = 8
    border_width = 3

    shadow_rect = pg.Rect(x - offset_x, y + offset_y, width, height)
    main_rect = pg.Rect(x, y, width, height)

    pg.draw.rect(surface, COLOR_PEACH, shadow_rect)
    pg.draw.rect(surface, COLOR_BLACK, shadow_rect, border_width)
    pg.draw.rect(surface, COLOR_WHITE, main_rect)
    pg.draw.rect(surface, COLOR_BLACK, main_rect, border_width)


def get_animation_image(path, ally=False):
    animation_sprite = []
    sprite = pg.image.load(path)
    for x in range(0, 289, 96):
        sub_rect = pg.Rect(x, 0, 96, 96)
        sub_img = sprite.subsurface(sub_rect)
        if ally:
            sub_img = pg.transform.flip(sub_img, flip_x=True, flip_y=False)
        animation_sprite.append(sub_img)

    return animation_sprite


class BattleInfoDisplay:
    def __init__(self, side, width, height, info):
        self.rect = pg.Rect(10, 10, width, height) if side == "ally" else pg.Rect(GameSettings.SCREEN_WIDTH - width - 20, 10, width, height)
        self.info = info
        self.info_img = pg.transform.scale(resource_manager.get_image(MONSTER_PATH[info["name"]]["sprite_path"]), (80, 80))
        self.info_img_rect = pg.Rect(self.rect.topleft[0] + 15, self.rect.topleft[1], self.info_img.width, self.info_img.height)
        self.avatar_rect = pg.Rect(self.info_img_rect.topleft[0], self.info_img_rect.topleft[1], self.rect.height, self.rect.height)

        self.rect_x = self.rect.topleft[0] + 25
        self.rect_y = self.rect.topleft[1] - 10 if info["name"] == "Gengar" else self.rect.topleft[1] - 4
        self.monster_img_rect = pg.Rect(self.rect_x, self.rect_y, self.info_img.width, self.info_img.height)

        self.font_alt = pg.font.Font("assets/fonts/Minecraft.ttf", size=16)
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=16)
        self.sample = self.font.render("mana", True, (0, 0, 0))
        self.sample_width = self.sample.width
        self.font_height = self.font.get_height()
        self.width, self.height = width, height

    def draw(self, screen):
        draw_info_box(screen, self.rect.topleft[0] + 15, self.rect.topleft[1], self.width, self.height)
        screen.blit(self.info_img, self.monster_img_rect)

        for index, (info, val) in enumerate(self.info.items()):
            if info in ["max_hp", "max_def", "max_mana", "name"]:
                continue

            info_text = self.font.render(info.upper(), True, (0, 0, 0))
            info_text_rect = pg.Rect(self.avatar_rect.topright[0] + 20, self.avatar_rect.topright[1] - self.font_height / 2 - 3 + index * info_text.get_height() * 1.25, self.sample_width, info_text.height)
            info_bar_rect = pg.Rect(0, 0, 160, self.font_height - 2)
            info_mana_rect = pg.Rect(0, 0, 160, self.font_height - 2)
            info_bar_rect.topleft = (info_text_rect.topright[0] + self.sample_width - 30, info_text_rect.topright[1] + 1)
            info_mana_rect.topleft = (info_text_rect.topright[0] + self.sample_width - 30, info_text_rect.topright[1] + 1)

            string = "max_" + info
            value = self.font_alt.render(f"{val}/{self.info[string]}", True, (0, 0, 0))

            red_bar = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01c.png"), (info_bar_rect.width, info_bar_rect.height))
            screen.blit(red_bar, info_bar_rect)
            screen.blit(red_bar, info_mana_rect)


            if info == "hp":
                bar = pg.transform.scale(resource_manager.get_image(INFO_BAR_COLOR[info]), (info_bar_rect.width * (val / self.info["max_hp"]), info_bar_rect.height))
                screen.blit(bar, info_bar_rect)
                screen.blit(value, pg.Rect(info_bar_rect.topleft[0] + 3, info_bar_rect.topleft[1] + 3, info_bar_rect.width, info_bar_rect.height))
            elif info == "def":
                bar = pg.transform.scale(resource_manager.get_image(INFO_BAR_COLOR[info]), (info_bar_rect.width * (val / self.info["max_def"]), info_bar_rect.height))
                screen.blit(bar, info_bar_rect)
                screen.blit(value, pg.Rect(info_bar_rect.topleft[0] + 3, info_bar_rect.topleft[1] + 3, info_bar_rect.width, info_bar_rect.height))
            else:
                info_mana_rect.width = info_mana_rect.width * (val / self.info["max_mana"])
                pg.draw.rect(screen, (71, 99, 255), info_mana_rect)
                screen.blit(value, pg.Rect(info_bar_rect.topleft[0] + 3, info_bar_rect.topleft[1] + 3, info_bar_rect.width, info_bar_rect.height))

            screen.blit(info_text, info_text_rect)


    def update(self, hp=None, defense=None, mana=None):
        if hp is not None:
            self.info["hp"] = hp
        if defense is not None:
            self.info["def"] = defense
        if mana is not None:
            self.info["mana"] = mana


class AnimatedMonster:
    def __init__(self, sprite):
        self.sprite_lst = sprite
        self.frame_index = 0

    def draw(self, screen, dt, rect, size):
        self.frame_index += GameSettings.ANIMATION_SPEED * dt
        img = self.sprite_lst[int(self.frame_index % len(self.sprite_lst))]
        img = pg.transform.scale(img, (size, size))
        screen.blit(img, rect)


# noinspection PyMethodMayBeStatic
class BattleScene(Scene):
    def __init__(self):
        super().__init__()
        random.seed(random.randint(1, 100000))
        # Background/ Display font
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=22)
        self.box_font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=25)
        self.alt_font = pg.font.Font("assets/fonts/Minecraft.ttf", size=20)
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(GameSettings.FPS) / 1000.0
        self.info_in_battle = ["hp", "max_hp", "mana", "max_mana", "def", "max_def", "name"]


        # Dialogue setup
        self.dialogue_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.dialogue_rect.bottomleft = (192, 720)
        self.dialogue_box = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01g.png"),(GameSettings.SCREEN_WIDTH * 0.7, GameSettings.SCREEN_HEIGHT * 0.2))
        self.dialogue_box.set_alpha(250)
        self.text_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH * 0.7, GameSettings.SCREEN_HEIGHT * 0.2)
        self.text_rect.topleft = (212, 720 - GameSettings.SCREEN_HEIGHT * 0.2 + 10)


        # Enemy monster battle setup
        self.enemy_pos = (830, 268)
        self.enemy_monster_rect = pg.Rect(self.enemy_pos[0], self.enemy_pos[1], 196 * 2, 98 * 2)
        self.enemy_monster_rect.center = (964, 310)
        self.enemy_monster = None
        self.enemy_monster_ani = None
        self.enemy_info = None

        # Ally monster battle setup
        self.ally_monster_rect = pg.Rect(0, 0, 196 * 2, 98 * 2)
        self.ally_monster_rect.center = (400, 310)
        self.ally_monster = None
        self.ally_monster_ani = None
        self.ally_info = None

        # Battle state...
        self.battle = BattleSystem(services.game_manager.bag._monsters_data, services.game_manager.bag._game_monsters, True) if (
                        scene_manager.monster_catch) else BattleSystem(services.game_manager.bag._monsters_data, services.game_manager.bag._game_monsters, False)
        self.displayed = False


        # Button in battle scene
        self.offset = 200
        self.attack_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png", self.dialogue_rect.topleft[0] + 50,
                                    self.dialogue_rect.topleft[1] + 50, 180, 70,
                                    lambda: self.battle.state.change_action("attack"))
        self.defend_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png", self.dialogue_rect.topleft[0] + 50 + self.offset,
                                    self.dialogue_rect.topleft[1] + 50, 180, 70,
                                    lambda: self.battle.state.change_action("defend"))
        self.run_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.dialogue_rect.topleft[0] + self.offset * 2 + 50,
                                    self.dialogue_rect.topleft[1] + 50, 180, 70,
                                    lambda: self.battle.state.change_action("run"))
        self.potion_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.dialogue_rect.topleft[0] + self.offset * 3 + 50,
                                    self.dialogue_rect.topleft[1] + 50, 180, 70,
                                    lambda: self.battle.state.change_action("potion"))

        self.attack_rect = pg.Rect(self.dialogue_rect.topleft[0] + 100, self.dialogue_rect.topleft[1] + 65, 180, 70)
        self.defend_rect = pg.Rect(self.dialogue_rect.topleft[0] + 100 + self.offset, self.dialogue_rect.topleft[1] + 65, 180, 70)
        self.potion_rect = pg.Rect(self.dialogue_rect.topleft[0] + self.offset * 3 + 105, self.dialogue_rect.topleft[1] + 65, 180, 70)
        self.run_rect = pg.Rect(self.dialogue_rect.topleft[0] + self.offset * 2 + 120, self.dialogue_rect.topleft[1] + 65, 180, 70)


    def reset(self):
        self.battle = BattleSystem(services.game_manager.bag._monsters_data, services.game_manager.bag._game_monsters, True) if (
            scene_manager.monster_catch) else BattleSystem(services.game_manager.bag._monsters_data, services.game_manager.bag._game_monsters, False)


    def enter(self) -> None:
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")
        self.reset()


    def exit(self) -> None:
        if scene_manager.monster_catch:
            services.game_manager.bag._items_data[1]["count"] -= 1
        scene_manager.monster_catch = False
        self.displayed = False
        self.battle.reset()


    def update(self, dt: float) -> None:
        if isinstance(self.battle.state, BattleSetup):
            if self.battle.state.enemy_selected and not self.battle.state.enemy_setup:
                self.enemy_monster = self.battle.get_monster()
                self.enemy_info = BattleInfoDisplay("enemy", 350, 90, self.get_monster_info(self.enemy_monster))
                self.enemy_monster_ani = AnimatedMonster(get_animation_image(MONSTER_PATH[self.enemy_monster["name"]]["animation_path"]))
            elif self.battle.state.ally_selected and not self.battle.state.ally_setup:
                self.ally_monster = self.battle.get_monster()
                self.ally_info = BattleInfoDisplay("ally", 350, 90, self.get_monster_info(self.ally_monster))
                self.ally_monster_ani = AnimatedMonster(get_animation_image(MONSTER_PATH[self.ally_monster["name"]]["animation_path"], True))

        else:
            self.ally_info.update(self.battle.curr_ally_monster["hp"], self.battle.curr_ally_monster["def"], self.battle.curr_ally_monster["mana"])
            self.enemy_info.update(self.battle.curr_enemy_monster["hp"], self.battle.curr_enemy_monster["def"], self.battle.curr_enemy_monster["mana"])

        if isinstance(self.battle.state, PlayerTurn) and self.battle.state.action is None:
            self.attack_button.update(dt)
            self.defend_button.update(dt)
            self.run_button.update(dt)
            if not self.battle.state.potion_unavailable:
                self.potion_button.update(dt)

        if input_manager.key_pressed(K_ESCAPE):
            scene_manager.change_scene("game")


        self.battle.update()


    def action_display(self, screen):
        if isinstance(self.battle.state, PlayerTurn) and self.battle.state.action is None and self.battle.state.residue_text is None:
            self.attack_button.draw(screen)
            attack_text = self.font.render("Attack", True, (0, 0, 0))
            self.defend_button.draw(screen)
            defend_text = self.font.render("Defend", True, (0, 0, 0))
            self.potion_button.draw(screen)
            potion_text = self.font.render("Potion", True, (0, 0, 0))
            self.run_button.draw(screen)
            run_text = self.font.render("Run", True, (0, 0, 0))

            screen.blit(run_text, self.run_rect)
            screen.blit(potion_text, self.potion_rect)
            screen.blit(defend_text, self.defend_rect)
            screen.blit(attack_text, self.attack_rect)


    def battle_setup(self, screen):
        if isinstance(self.battle.state, BattleSetup):
            if self.battle.state.enemy_setup:
                self.enemy_monster_ani.draw(screen, self.dt, self.enemy_monster_rect, 300)
                self.enemy_info.draw(screen)
            if self.battle.state.ally_setup:
                self.ally_monster_ani.draw(screen, self.dt, self.ally_monster_rect, 300)
                self.ally_info.draw(screen)
                self.displayed = True

        if self.displayed:
            self.ally_monster_ani.draw(screen, self.dt, self.ally_monster_rect, 300)
            self.ally_info.draw(screen)
            self.enemy_monster_ani.draw(screen, self.dt, self.enemy_monster_rect, 300)
            self.enemy_info.draw(screen)



    def dialouge_display(self, screen):
        screen.blit(self.dialogue_box, self.dialogue_rect)
        dialogue_text = self.font.render(self.dialogue_system(), True, (255, 255, 255), wraplength=int(GameSettings.SCREEN_WIDTH * 0.7 - 30))
        screen.blit(dialogue_text, self.text_rect)


    def dialogue_system(self):
        return self.battle.get_dialogue()


    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.dialouge_display(screen)
        if isinstance(self.battle.state, BattleSetup):
            self.battle_setup(screen)
            self.battle.state.draw(screen)

        elif isinstance(self.battle.state, PlayerTurn):
            self.battle_setup(screen)
            self.battle.state.draw(screen)
            self.action_display(screen)
        else:
            self.battle_setup(screen)


    def get_monster_info(self, monster):
        info = {}
        for i in monster:
            if i not in info and i in self.info_in_battle:
                info[i] = monster[i]


        return info









