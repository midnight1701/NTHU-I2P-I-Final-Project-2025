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
        self.displayed = False


        # Display monster info

        # Button in battle scene
        self.attack_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png", self.dialogue_rect.topleft[0],
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.state.change_action("attack"))
        self.defend_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png", self.dialogue_rect.topleft[0] + 130,
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.state.change_action("defend"))
        self.run_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.dialogue_rect.topleft[0] + 260,
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.state.change_action("potion"))
        self.potion_button = Button("UI/UI_Flat_Button01a_3.png", "UI/UI_Flat_Button01a_1.png",
                                    self.dialogue_rect.topleft[0] + 390,
                                    self.dialogue_rect.topleft[1], 100, 50,
                                    lambda: self.battle.state.change_action("run"))



    def enter(self) -> None:
        sound_manager.play_bgm("RBY 107 Battle! (Trainer).ogg")

    def exit(self) -> None:
        self.battle.reset()
        self.displayed = False

    def update(self, dt: float) -> None:
        if isinstance(self.battle.state, PlayerTurn) and self.battle.state.action is None:
            self.attack_button.update(dt)
            self.defend_button.update(dt)
            self.run_button.update(dt)
            self.potion_button.update(dt)

        if input_manager.key_pressed(K_ESCAPE):
            scene_manager.change_scene("game")

        self.battle.update()


    def action_display(self, screen):
        if isinstance(self.battle.state, PlayerTurn) and self.battle.state.action is None:
            self.attack_button.draw(screen)
            self.defend_button.draw(screen)
            self.run_button.draw(screen)
            self.potion_button.draw(screen)


    def battle_setup(self, screen):
        if isinstance(self.battle.state, BattleSetup):
            if self.battle.state.enemy_setup or self.displayed:
                screen.blit(self.enemy_monster_img, self.enemy_monster_rect)
            if self.battle.state.ally_setup:
                screen.blit(self.ally_monster_img, self.ally_monster_rect)
                self.displayed = True

        if self.displayed:
            screen.blit(self.enemy_monster_img, self.enemy_monster_rect)
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
        return self.battle.get_dialogue()


    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        self.battle_setup(screen)
        self.dialouge_display(screen)
        self.action_display(screen)


    def reset(self):
        pass



