import random

import pygame as pg
from pygame import K_ESCAPE, K_SPACE
from src.scenes.battle_system import BattleSetup, BattleEnd, EnemyTurn, PlayerTurn

from src.scenes.battle_system import BattleSystem
from src.sprites import BackgroundSprite
from src.utils import GameSettings
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager


# noinspection PyMethodMayBeStatic
class BattleScene(Scene):
    def __init__(self):
        super().__init__()
        # Background/ Display font
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=22)
        self.box_font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=25)

        # Dialogue setup
        self.dialogue_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.dialogue_rect.bottomleft = (192, 720)
        self.dialogue_box = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01g.png"),
                                               (GameSettings.SCREEN_WIDTH * 0.7, GameSettings.SCREEN_HEIGHT * 0.2))
        self.dialogue_box.set_alpha(255)
        self.text_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.text_rect.topleft = (212, 720 - GameSettings.SCREEN_HEIGHT * 0.2 + 10)


        # Enemy monster battle setup
        self.enemy_pos = (800, 318)
        self.enemy_monster = [random.choice(scene_manager._scenes["game"].game_manager.bag._game_monsters)]
        self.enemy_monster_rect = pg.Rect(self.enemy_pos[0], self.enemy_pos[1], 196 * 2, 98 * 2)
        self.enemy_monster_rect.center = (964, 360)
        self.enemy_info = self.monster_info(self.enemy_monster)
        self.enemy_monster_img = pg.transform.scale(resource_manager.get_image(self.enemy_info[len(self.enemy_info) - 1]), (250, 250))

        # Ally monster battle setup
        self.ally_monster_rect = pg.Rect(0, 0, 196 * 2, 98 * 2)
        self.ally_monster_rect.center = (430, 360)
        self.ally_monster = [random.choice(scene_manager._scenes["game"].game_manager.bag._monsters_data)]
        self.ally_info = self.monster_info(self.ally_monster)
        self.ally_monster_img = pg.transform.flip(pg.transform.scale(resource_manager.get_image(self.ally_info[len(self.ally_info) - 1]), (250, 250)), flip_x=True, flip_y=False)

        # Battle state...
        self.battle = BattleSystem(self.ally_info, self.enemy_info, True) if scene_manager.monster_catch else BattleSystem(self.ally_info, self.enemy_info, False)
        self.displayed = False


        # Display monster info
        self.ally_info_rect = pg.Rect(self.background.rect.topleft[0] + 10, self.background.rect.topleft[1] + 10, 300, 90)
        self.enemy_info_rect = pg.Rect(self.background.rect.topright[0] - 300 - 10, self.background.rect.topright[1] + 10, 300, 90)

        template = resource_manager.get_image("UI/UI_Flat_Banner04a.png")
        self.ally_template = pg.transform.scale(template, (300, 90))
        self.enemy_template = pg.transform.scale(template, (300, 90))


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


    def enter(self) -> None:
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")
        self.displayed = False
        self.enemy_monster = [random.choice(scene_manager._scenes["game"].game_manager.bag._game_monsters)]
        self.ally_monster = [random.choice(scene_manager._scenes["game"].game_manager.bag._monsters_data)]
        self.enemy_info = self.monster_info(self.enemy_monster)
        self.ally_info = self.monster_info(self.ally_monster)
        self.enemy_monster_img = pg.transform.scale(
            resource_manager.get_image(self.enemy_info[len(self.enemy_info) - 1]), (250, 250))
        self.ally_monster_img = pg.transform.flip(
            pg.transform.scale(resource_manager.get_image(self.ally_info[len(self.ally_info) - 1]), (250, 250)),
            flip_x=True, flip_y=False)
        self.battle = BattleSystem(self.ally_info, self.enemy_info, True) if scene_manager.monster_catch else BattleSystem(self.ally_info, self.enemy_info, False)


    def exit(self) -> None:
        scene_manager.monster_catch = False


    def update(self, dt: float) -> None:
        if isinstance(self.battle.state, PlayerTurn) and self.battle.state.action is None:
            self.attack_button.update(dt)
            self.defend_button.update(dt)
            self.run_button.update(dt)
            self.potion_button.update(dt)

        if isinstance(self.battle.state, BattleEnd) and self.battle.state.status == "ally_wins" and scene_manager.monster_catch:
            for m in self.enemy_monster:
                print(m)
                if m not in scene_manager._scenes["game"].game_manager.bag._monsters_data:
                    scene_manager._scenes["game"].game_manager.bag._monsters_data.append(m)


        if input_manager.key_pressed(K_ESCAPE):
            scene_manager.change_scene("game")

        self.battle.update()


    def action_display(self, screen):
        if isinstance(self.battle.state, PlayerTurn) and self.battle.state.action is None:
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
                screen.blit(self.enemy_monster_img, self.enemy_monster_rect)
                screen.blit(self.enemy_template, self.enemy_info_rect)


            if self.battle.state.ally_setup:
                screen.blit(self.ally_monster_img, self.ally_monster_rect)
                screen.blit(self.ally_template, self.ally_info_rect)
                self.displayed = True


        if self.displayed:
            screen.blit(self.enemy_monster_img, self.enemy_monster_rect)
            screen.blit(self.enemy_template, self.enemy_info_rect)


            screen.blit(self.ally_monster_img, self.ally_monster_rect)
            screen.blit(self.ally_template, self.ally_info_rect)


    def monster_info(self, monster):
        info = []
        for i in monster:
            m_name = i["name"]
            m_hp, m_max_hp = i["hp"], i["max_hp"]
            m_level, m_img_path = i["level"], i["sprite_path"]
            m_atk, m_def = i["atk"], i["def"]
            info.append(m_name)
            info.append(m_hp)
            info.append(m_max_hp)
            info.append(m_level)
            info.append(m_atk)
            info.append(m_def)
            info.append(m_img_path)

        return info


    def dialouge_display(self, screen):
        screen.blit(self.dialogue_box, self.dialogue_rect)
        dialogue_text = self.font.render(self.dialogue_system(), True, (255, 255, 255))
        screen.blit(dialogue_text, self.text_rect)


    def dialogue_system(self):
        return self.battle.get_dialogue()


    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.battle_setup(screen)
        self.dialouge_display(screen)
        self.action_display(screen)






