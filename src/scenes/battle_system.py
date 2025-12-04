import pygame as pg
from pygame import K_SPACE

from src.core.services import scene_manager
from src.utils.support import Monster, Item, COLOR, MONSTER_PATH, INFO_IMG, DISPLAY_INFO, CHAR_MAX, ITEM_PATH, ITEM_DESCRIPTION
from src.core import services
from src.utils import GameSettings
from src.utils.support import MonsterBattle, BattleState
from src.core.services import input_manager
import random

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

# noinspection PyMethodMayBeStatic

class MonsterInfoDisplay:
    def __init__(self, player_monster, enemy_monster):
        self.player_monster = player_monster
        self.enemy_monster = enemy_monster
        self.player_dict = {i: v for i, v in enumerate(self.player_monster)}
        self.index = 0
        self.limit = 10
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=17)
        self.info = ["hp", "atk", "def", "speed", "accuracy"]

        self.selection_bg = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH * 0.5, GameSettings.SCREEN_HEIGHT * 0.5)
        self.selection_bg.center = (GameSettings.SCREEN_WIDTH / 2, GameSettings.SCREEN_HEIGHT - GameSettings.SCREEN_HEIGHT * 0.5 - 40)
        self.monster_display_bg = pg.Rect(self.selection_bg.topleft[0], self.selection_bg.topleft[1], self.selection_bg.width * 0.3, self.selection_bg.height)
        self.name_rect_top = self.selection_bg.topleft
        self.name_rect_width = self.monster_display_bg.width
        self.name_rect_height = self.selection_bg.height / self.limit
        self.clock = pg.time.Clock()
        self.dt = self.clock.tick(GameSettings.FPS) / 1000.0
        self.frame_index = 0

    def draw(self, screen):
        self.draw_selection(screen)
        self.draw_info(screen)


    def draw_selection(self, screen):
        pg.draw.rect(screen, (44, 44, 44), self.monster_display_bg)
        box_offset = 0 if self.index < self.limit else -(self.index - self.limit + 1) * self.name_rect_height

        for index, monster in enumerate(self.player_monster):
            text_color = "yellow" if self.index == index else "white"
            bg_color = (44, 44, 44) if self.index != index else (169, 169, 169)
            top = self.name_rect_top[1] + index * self.name_rect_height + box_offset
            monster_name = self.font.render(monster["name"], True, text_color)
            monster_name_rect = monster_name.get_rect()
            monster_name_rect.topleft = (self.name_rect_top[0] + self.name_rect_width / 4, top + 10)
            monster_name_bg = pg.Rect(self.monster_display_bg.topleft[0], top, self.name_rect_width, self.name_rect_height)

            if monster_name_bg.colliderect(self.monster_display_bg):
                pg.draw.rect(screen, bg_color, monster_name_bg)
                screen.blit(monster_name, monster_name_rect)


    def draw_info(self, screen):
        monster = self.player_dict[self.index]
        monster_info = self.get_monster_info(monster)
        info_rect = pg.Rect(self.monster_display_bg.topright[0], self.monster_display_bg.topright[1], self.selection_bg.width * 0.7, self.selection_bg.height * 0.4)
        sprite = get_animation_image(MONSTER_PATH[monster["name"]]["animation_path"])
        self.frame_index += GameSettings.ANIMATION_SPEED * self.dt

        animated_bg = pg.Rect(0, 0, 150, 150)
        animated_bg.center = info_rect.center
        img = sprite[int(self.frame_index % len(sprite))]
        img = pg.transform.scale(img, (150, 150))
        border = pg.Rect(self.monster_display_bg.topright[0], self.monster_display_bg.topright[1], 2, self.selection_bg.height)

        info_display_bg = pg.Rect(info_rect.bottomleft[0], info_rect.bottomleft[1], self.selection_bg.width * 0.7, self.selection_bg.height * 0.6)

        pg.draw.rect(screen, COLOR[monster["element"]], info_rect)
        pg.draw.rect(screen, (44, 44, 44), info_display_bg)
        screen.blit(img, animated_bg)
        pg.draw.rect(screen, (169, 169, 169), border)

        for index, (char, val) in enumerate(monster_info.items()):
            text = self.font.render(f"{DISPLAY_INFO[char]}: {val}/{monster["max_hp"]}", True, (255, 255, 0)) if char == "hp" else self.font.render(f"{DISPLAY_INFO[char]}: "                                                                                                                        f"{val}/{CHAR_MAX[char]}", True, (255, 255, 0))
            text_rect = pg.Rect(info_display_bg.topleft[0] + 20, info_display_bg.topleft[1] + index * 30 + 10, text.get_width(), text.get_height())
            screen.blit(text, text_rect)


    def get_monster_info(self, monster):
        info = {}
        for i in monster:
            if i not in info and i in self.info:
                info[i] = monster[i]

        return info


    def update(self):
        if input_manager.key_pressed(pg.K_UP):
            self.index -= 1
        elif input_manager.key_pressed(pg.K_DOWN):
            self.index += 1

        self.index = self.index % len(self.player_monster)


class BattleSetup(BattleState):
    def __init__(self, player_monster, enemy_monster):
        self.player_monster = player_monster
        self.enemy_monster = enemy_monster
        self.player_dict = {i: v for i, v in enumerate(self.player_monster)}
        self.display = MonsterInfoDisplay(player_monster, enemy_monster)

        self.enemy_setup, self.ally_setup, self.ally_selection, self.ally_selected = False, False, False, False
        self.state_complete = False

        self.selected_monster = None
        self.index = 0


    def draw(self, screen):
        if self.ally_selection and not self.ally_setup:
            self.display.draw(screen)


    def update(self):
        if self.ally_selection and not self.ally_selected:
            self.display.update()
            self.index = self.display.index

        if input_manager.key_pressed(K_SPACE):
            if not self.ally_selection:
                self.ally_selection = True
            elif self.ally_selection and not self.ally_selected:
                self.selected_monster = self.player_dict[self.index]
                self.ally_selected = True
            elif self.ally_selected:
                self.ally_setup = True



    def dialogue(self):
        if not self.selected_monster and not self.ally_selection:
            return f"Ally trainer has encountered something unexpected"
        elif not self.ally_selected and self.ally_selection:
            return f"Please select a monster for battle"
        elif self.ally_selected and self.selected_monster is not None and not self.ally_setup:
            return f"Ally trainer has selected {self.selected_monster["name"]} for battle"
        elif self.ally_setup:
            pass

        return None


    def return_ally_monster(self):
        if self.player_monster:
            return self.player_monster

        return None


# noinspection PyMethodMayBeStatic
class PlayerTurn(BattleState):
    def __init__(self, player, enemy, atk, defend, run, potion):
        self.state_complete = False
        self.dialogue_check = False
        self.action = None
        self.player = player
        self.enemy = enemy
        self.action_text = ""
        self.atk, self.defend, self.run, self.potion = atk, defend, run, potion


    def update(self):
        if input_manager.key_pressed(K_SPACE):
            if not self.dialogue_check and self.action is not None:
                self.dialogue_check = True
                self.perform_action()
            elif self.dialogue_check:
                self.state_complete = True


    def perform_action(self):
        match self.action:
            case "attack":
                self.action_text = self.atk(self.player, self.enemy)
            case "defend":
                self.action_text = self.defend(self.player)
            case "run":
                self.action_text = self.run("ally")
            case "potion":
                self.action_text = self.potion(self.player)


    def change_action(self, action):
        self.action = action


    def dialogue(self):
        if self.action is None:
            return "What will ally trainer do?"

        if self.action is not None and not self.dialogue_check:
            match self.action:
                case "attack":
                    return f"{self.player["name"]} decides to go on the offensive"
                case "defend":
                    return f"{self.player["name"]} decides to go on the defensive"
                case "run":
                    return f"{self.player["name"]} senses a dark premonition"
                case "potion":
                    return f"{self.player["name"]} obtains a hidden power within"

        elif self.action and self.dialogue_check:
            return self.action_text

        return None

# noinspection PyMethodMayBeStatic
class EnemyTurn(BattleState):
    def __init__(self, player, enemy, atk, defend, run, potion):
        self.state_complete = False
        self.dialogue_check = False
        self.action = None
        self.player = player
        self.enemy = enemy
        self.action_text = ""
        self.atk, self.defend, self.run, self.potion = atk, defend, run, potion

    def get_action(self):
        action = ["attack", "defend", "run"]
        return random.choice(action)


    def perform_action(self):
        match self.action:
            case "attack":
                self.action_text = self.atk(self.enemy, self.player)
            case "defend":
                self.action_text = self.defend(self.enemy)
            case "run":
                self.action_text = self.run("enemy")
            case "potion":
                self.action_text = self.potion(self.enemy)


    def update(self):
        if input_manager.key_pressed(K_SPACE):
            if self.action is None:
                self.action = self.get_action()
            elif not self.dialogue_check:
                self.dialogue_check = True
                self.perform_action()
            elif self.dialogue_check:
                self.state_complete = True


    def dialogue(self):
        if not self.action:
            return "Enemy trainer is devising a battle strategy"
        elif self.action is not None and not self.dialogue_check:
            match self.action:
                case "attack":
                    return f"{self.enemy["name"]} decides to go on the offensive"
                case "defend":
                    return f"{self.enemy["name"]} decides to go on the defensive"
                case "run":
                    return f"{self.enemy["name"]} senses a dark premonition"
                case "potion":
                    return f"{self.enemy["name"]} obtains a hidden power within"
        elif self.action and self.dialogue_check:
            return self.action_text

        return None

# noinspection PyMethodMayBeStatic
class BattleEnd(BattleState):
    def __init__(self, status, side=None):
        self.status = status
        self.side = side

    def update(self):
        if input_manager.key_pressed(K_SPACE):
            scene_manager.change_scene("game")


    def dialogue(self):
        if self.status == "run":
            if self.side == "ally":
                return "Ally trainer flees from battle"
            else:
                return "Enemy trainer flees from battle"

        elif self.status == "ally_wins":
            return "Ally trainer comes out on top"

        elif self.status == "enemy_wins":
            return "Ally trainer falls to the enemy"

        return None



# noinspection PyMethodMayBeStatic
class BattleSystem:
    def __init__(self, player_lst, enemy_lst, monster_catch):
        self.player_monster_lst = player_lst
        self.enemy_monster_lst = enemy_lst
        self.player_turn = True
        self.state = BattleSetup(self.player_monster_lst, self.enemy_monster_lst)
        self.monster_catch = monster_catch

        self.curr_ally_monster, self.curr_enemy_monster = None, None


    def update(self):
        self.state.update()

        if not isinstance(self.state, BattleEnd):
            if self.state.state_complete:
                self.change_state()
        else:
            if scene_manager.monster_catch:
                if self.state.status == "ally_wins" and self.curr_ally_monster not in services.game_manager.bag._monsters_data:
                    services.game_manager.bag._monsters_data.append(self.curr_ally_monster)


    def reset(self):
        self.state = BattleSetup(self.player_monster_lst, self.enemy_monster_lst)

    def get_monster(self):
        if isinstance(self.state, BattleSetup) and self.state.ally_selection and not self.curr_ally_monster:
            self.curr_ally_monster = self.state.return_ally_monster()


    def change_state(self):
        if isinstance(self.state, BattleSetup):
            self.curr_ally_monster = self.state.return_ally_monster()
            self.state = PlayerTurn(self.curr_ally_monster, self.enemy, self.attack, self.defend, self.run, self.potion)
        elif isinstance(self.state, PlayerTurn):
            if self.is_enemy_alive():
                self.state = EnemyTurn(self.player, self.enemy, self.attack, self.defend, self.run, self.potion)
            else:
                self.state = BattleEnd(status="ally_wins", enemy=self.enemy)

        elif isinstance(self.state, EnemyTurn):
            if self.is_player_alive():
                self.state = PlayerTurn(self.player, self.enemy, self.attack, self.defend, self.run, self.potion)
            else:
                self.state = BattleEnd(status="enemy_wins", enemy=self.enemy)



    def is_player_alive(self):
        return self.player["hp"] > 0


    def is_enemy_alive(self):
        return self.enemy["hp"] > 0


    def get_dialogue(self):
        return self.state.dialogue()


    def attack(self, attacker, defender):
        actual_atk = attacker["atk"] - defender["def"] if attacker["atk"] - defender["def"] > 0 else 0
        defender["hp"] = defender["hp"] - actual_atk
        if defender["hp"] < 0:
            defender["hp"] = 0

        return f"{attacker["name"]} attacks and deals {actual_atk} damage to {defender["name"]}"


    def run(self, side):
        self.state = BattleEnd("run", side)


    def defend(self, current):
        return f"{current["name"]} defend with all its might"


    def potion(self, current):
        return f"{current["name"]} prepares for a deadly blow"



