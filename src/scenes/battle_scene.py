import random

import pygame as pg
from pygame import K_ESCAPE, K_SPACE
from src.scenes.battle_system import BattleSetup, PlayerTurn

from src.scenes.battle_system import BattleSystem
from src.sprites import BackgroundSprite
from src.utils import GameSettings
from src.utils.support import MONSTER_PATH
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager
import src.core.services as services

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

    class MonsterInfo:
        def __init__(self, side):
            self.side = side
            self.info_bg_rect = pg.Rect(0, 0, 0, 0)


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


        # Dialogue setup
        self.dialogue_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.dialogue_rect.bottomleft = (192, 720)
        self.dialogue_box = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01g.png"),(GameSettings.SCREEN_WIDTH * 0.7, GameSettings.SCREEN_HEIGHT * 0.2))
        self.dialogue_box.set_alpha(250)
        self.text_rect = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT * 0.2)
        self.text_rect.topleft = (212, 720 - GameSettings.SCREEN_HEIGHT * 0.2 + 10)


        # Enemy monster battle setup
        self.enemy_pos = (800, 318)
        self.enemy_monster_rect = pg.Rect(self.enemy_pos[0], self.enemy_pos[1], 196 * 2, 98 * 2)
        self.enemy_monster_rect.center = (964, 360)

        # Ally monster battle setup
        self.ally_monster_rect = pg.Rect(0, 0, 196 * 2, 98 * 2)
        self.ally_monster_rect.center = (430, 360)

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
        pass

    def dialouge_display(self, screen):
        screen.blit(self.dialogue_box, self.dialogue_rect)
        dialogue_text = self.font.render(self.dialogue_system(), True, (255, 255, 255))
        screen.blit(dialogue_text, self.text_rect)


    def dialogue_system(self):
        return self.battle.get_dialogue()


    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        if isinstance(self.battle.state, BattleSetup):
            self.battle.state.draw(screen)
            self.dialouge_display(screen)
        else:
            self.dialouge_display(screen)
            self.action_display(screen)









