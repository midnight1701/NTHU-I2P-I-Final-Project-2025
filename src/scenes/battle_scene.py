import pygame as pg
from pygame import K_ESCAPE, K_SPACE

from src.scenes.battle_system import BattleSystem
from src.sprites import BackgroundSprite
from src.utils import GameSettings
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager
from typing import override

# noinspection PyMethodMayBeStatic
class BattleScene(Scene):
    def __init__(self):
        super().__init__()
        # Background/ Display font
        self.background = BackgroundSprite("backgrounds/background1.png")
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)

        # Dialogue setup
        self.dialogue_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.dialogue_rect.bottomleft = (320, 720)
        self.dialogue_box = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01g.png"),
                                               (GameSettings.SCREEN_WIDTH * 0.5, GameSettings.SCREEN_HEIGHT * 0.6))
        self.dialogue_box.set_alpha(255)
        self.text_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.text_rect.topleft = (325, 720 - GameSettings.SCREEN_HEIGHT * 0.2 + 10)


        # Enemy monster battle setup
        self.enemy_pos = (800, 318)
        self.enemy_monster = [{"name": "Charizard", "hp": 150, "max_hp": 200, "atk": 20, "def": 5, "level": 36, "sprite_path": "menu_sprites/menusprite2.png" }]
        self.enemy_monster_rect = pg.Rect(self.enemy_pos[0], self.enemy_pos[1], 196 * 2, 98 * 2)
        self.enemy_monster_rect.center = (964, 360)
        self.enemy_info = self.monster_info(self.enemy_monster)
        self.enemy_monster_img = pg.transform.scale(resource_manager.get_image(self.enemy_info[2]), (250, 250))

        # Ally monster battle setup
        self.ally_monster_rect = pg.Rect(0, 0, 196 * 2, 98 * 2)
        self.ally_monster_rect.center = (430, 360)
        self.ally_monster = [{ "name": "Viper", "hp": 120, "max_hp": 160, "atk": 20, "def": 5, "level": 10, "sprite_path": "menu_sprites/menusprite11.png"}]
        self.ally_info = self.monster_info(self.ally_monster)
        self.ally_monster_img = pg.transform.flip(pg.transform.scale(resource_manager.get_image(self.ally_info[2]), (250, 250)), flip_x=True, flip_y=False)

        # Battle state...
        self.battle = BattleSystem(self.ally_info, self.enemy_info)
        self.ally_setup, self.enemy_setup = False, False


        # Display monster info

        # Button in battle scene
        self.attack_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png", self.dialogue_rect.topleft[0],
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.change_action("attack"))
        self.defend_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png", self.dialogue_rect.topleft[0] + 130,
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.change_action("defend"))
        self.run_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.dialogue_rect.topleft[0] + 260,
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.change_action("run"))
        self.potion_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.dialogue_rect.topleft[0] + 390,
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.change_action("potion"))

        self.button_text_rect = pg.rect


    def enter(self) -> None:
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        if self.battle.overall_state == "battle" and self.battle.player_turn and self.battle.battle_state == "player_choose":
            self.attack_button.update(dt)
            self.defend_button.update(dt)
            self.run_button.update(dt)
            self.potion_button.update(dt)

        if self.battle.battle_state == "player_act" or self.battle.battle_state == "enemy_act":
            self.battle.update()

        if input_manager.key_pressed(K_ESCAPE):
            scene_manager.change_scene("game")

        # Input in intermediate scene, skip with player's input
        if input_manager.key_pressed(K_SPACE):
            if self.battle.overall_state == "battle_setup":
                if not self.enemy_setup:
                    self.enemy_setup = True
                elif not self.ally_setup:
                    self.ally_setup = True
                else:
                    self.battle.overall_state= "battle"

            elif self.battle.overall_state == "battle":
                if self.battle.battle_state == "player_act":
                    self.battle.battle_state = "battle_dialogue"

                elif self.battle.battle_state == "battle_dialogue":
                    self.battle.battle_state = "enemy_choose"
                elif self.battle.battle_state == "enemy_choose":
                    self.battle.battle_state = "enemy_act"
                elif self.battle.battle_state == "enemy_act":
                    self.battle.battle_state = "battle_dialogue"
                elif self.battle.battle_state == "battle_dialogue":
                    if self.battle.is_player_alive():
                        self.battle.player_turn = True
                        self.battle.battle_state = "player_choose"

            elif self.battle.overall_state == "end":
                pass

        # Input in actual battle scene


    def action_display(self, screen):
        if self.battle.overall_state == "battle" and self.battle.player_turn and self.battle.battle_state == "player_choose":
            self.attack_button.draw(screen)
            self.defend_button.draw(screen)
            self.run_button.draw(screen)
            self.potion_button.draw(screen)


    def battle_setup(self, screen):
        if self.enemy_setup:
            screen.blit(self.enemy_monster_img, self.enemy_monster_rect)
        if self.ally_setup:
            screen.blit(self.ally_monster_img, self.ally_monster_rect)

    def monster_info(self, monster):
        info = []
        for i in monster:
            m_name = i["name"]
            m_hp, m_max_hp = i["hp"], i["max_hp"]
            m_level, m_img_path = i["level"], i["sprite_path"]
            m_atk, m_def = i["atk"], i["def"]
            info.append(m_name)
            info.append((m_hp, m_max_hp, m_level, m_atk, m_def))
            info.append(m_img_path)

        return info

    def dialouge_display(self, screen):
        screen.blit(self.dialogue_box, self.dialogue_rect)
        dialogue_text = self.font.render(self.dialogue_system(), True, (255, 255, 255))
        screen.blit(dialogue_text, self.text_rect)


    def dialogue_system(self):
        if self.battle.overall_state == "battle_setup":
            if not self.enemy_setup and not self.ally_setup:
                dialogue = "Enemy trainer challenges you to a monster battle"
                return dialogue
            elif self.enemy_setup and not self.ally_setup:
                dialogue = f"Enemy trainer selects {self.battle.enemy.name}"
                return dialogue
            else:
                dialogue = f"Ally trainer selects {self.battle.player.name}"
                return dialogue


        elif self.battle.overall_state == "battle":
            return self.battle.get_dialogue()

        elif self.battle.overall_state == "end":
            pass

        return None

    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.dialouge_display(screen)
        self.action_display(screen)
        self.battle_setup(screen)

    def reset(self):
        pass



