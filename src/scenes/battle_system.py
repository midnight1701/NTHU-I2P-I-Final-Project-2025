import pygame as pg
from src.core.services import scene_manager, sound_manager, input_manager
from src.utils.definition import MonsterBattle
import random

# noinspection PyMethodMayBeStatic
class BattleSystem:
    def __init__(self, player_info, enemy_info):
        self.player = MonsterBattle(player_info[0], player_info[1][0], player_info[1][1], player_info[1][2], player_info[1][3], player_info[1][4])
        self.enemy = MonsterBattle(enemy_info[0], enemy_info[1][0], enemy_info[1][1], enemy_info[1][2], enemy_info[1][3], enemy_info[1][4])
        self.player_turn = True
        self.player_action = None
        self.enemy_action = random.choice(["attack", "defend", "run", "potion"])
        self.overall_state = "battle_setup"
        self.battle_state = "player_choose"

        self.curr_dialogue = ""

    def update(self):
        self.get_action()

    def get_action(self):
        if self.player_turn and self.battle_state == "player_act":
            match self.player_action:
                case "attack":
                    self.attack(self.player, self.enemy)
                case "defend":
                    self.defend()
                case "run":
                    self.run()
                case "potion":
                    self.potion()


        elif not self.player_turn and self.battle_state == "enemy_act":
            match self.enemy_action:
                case "attack":
                    self.attack(self.enemy, self.player)
                case "defend":
                    self.defend()
                case "run":
                    self.run()
                case "potion":
                    self.potion()

    def change_action(self, action):
        self.player_action = action
        self.battle_state = "player_act"

    def is_player_alive(self):
        return self.player.hp > 0

    def is_enemy_alive(self):
        return self.enemy.hp > 0

    def get_dialogue(self):
        if self.battle_state == "player_act":
            match self.player_action:
                case "attack":
                    return f"{self.player.name} decides to go on the offensive"
                case "defend":
                    return f"{self.player.name} decides to go on the defensive"
                case "run":
                    return f"{self.player.name} senses a dark premonition"
                case "potion":
                    return f"{self.player.name} gains hidden power within"

        elif self.battle_state == "enemy_act":
            match self.player_action:
                case "attack":
                    return f"{self.enemy.name} decides to go on the offensive"
                case "defend":
                    return f"{self.enemy.name} decides to go on the defensive"
                case "run":
                    return f"{self.enemy.name} senses a dark premonition"
                case "potion":
                    return f"{self.enemy.name} gains hidden power within"

        elif self.battle_state == "enemy_choose":
            return f"Enemy trainer is devising a battle strategy"

        else:
            return self.curr_dialogue


    def attack(self, attacker, defender):
        actual_atk = attacker.atk - defender.defense
        defender.hp = defender.hp - actual_atk
        if defender.hp < 0:
            defender.hp = 0
        self.curr_dialogue = f"{attacker.name} attack {defender.name} and deal {actual_atk} damage"


    def run(self):
        self.overall_state = "end"
        self.curr_dialogue = "Battle ends as ally trainer flees from danger"

    def defend(self):
        pass

    def potion(self):
        pass



