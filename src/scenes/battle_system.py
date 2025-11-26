import pygame as pg
from pygame import K_SPACE

from src.core.services import scene_manager, sound_manager, input_manager
from src.utils.support import MonsterBattle, BattleState
from src.core.services import input_manager
import random

# noinspection PyMethodMayBeStatic
class BattleSetup(BattleState):
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.enemy_setup, self.ally_setup = False, False
        self.state_complete = False


    def update(self):
        if input_manager.key_pressed(K_SPACE):
            if not self.ally_setup and not self.enemy_setup:
                self.enemy_setup = True
            elif not self.ally_setup and self.enemy_setup:
                self.ally_setup = True
            else:
                self.state_complete = True


    def dialogue(self):
        if not self.enemy_setup and not self.ally_setup:
            dialogue = "Enemy trainer challenges you to a monster battle"
            return dialogue
        elif self.enemy_setup and not self.ally_setup:
            dialogue = f"Enemy trainer selects {self.enemy.name}"
            return dialogue
        else:
            dialogue = f"Ally trainer selects {self.player.name}"
            return dialogue


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
                    return f"{self.player.name} decides to go on the offensive"
                case "defend":
                    return f"{self.player.name} decides to go on the defensive"
                case "run":
                    return f"{self.player.name} senses a dark premonition"
                case "potion":
                    return f"{self.player.name} obtains a hidden power within"

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
        action = ["attack"]
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
                    return f"{self.enemy.name} decides to go on the offensive"
                case "defend":
                    return f"{self.enemy.name} decides to go on the defensive"
                case "run":
                    return f"{self.enemy.name} senses a dark premonition"
                case "potion":
                    return f"{self.enemy.name} obtains a hidden power within"
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

####################################################################

# noinspection PyMethodMayBeStatic
class BattleSystem:
    def __init__(self, player_info, enemy_info, monster_catch):
        self.player = MonsterBattle(player_info["name"], player_info["hp"], player_info["max_hp"], player_info["level"], player_info["atk"], player_info["def"])
        self.enemy = MonsterBattle(enemy_info["name"], enemy_info["hp"], enemy_info["max_hp"], enemy_info["level"], enemy_info["atk"], enemy_info["def"])
        self.player_turn = True
        self.state = BattleSetup(self.player, self.enemy)
        self.monster_catch = monster_catch


    def update(self):
        self.state.update()

        if not isinstance(self.state, BattleEnd):
            if self.state.state_complete:
                self.change_state()


    def change_state(self):
        if isinstance(self.state, BattleSetup):
            self.state = PlayerTurn(self.player, self.enemy, self.attack, self.defend, self.run, self.potion)
        elif isinstance(self.state, PlayerTurn):
            if self.is_enemy_alive():
                self.state = EnemyTurn(self.player, self.enemy, self.attack, self.defend, self.run, self.potion)
            else:
                self.state = BattleEnd(status="ally_wins")
        elif isinstance(self.state, EnemyTurn):
            if self.is_player_alive():
                self.state = PlayerTurn(self.player, self.enemy, self.attack, self.defend, self.run, self.potion)
            else:
                self.state = BattleEnd(status="enemy_wins")


    def is_player_alive(self):
        return self.player.hp > 0


    def is_enemy_alive(self):
        return self.enemy.hp > 0


    def get_dialogue(self):
        return self.state.dialogue()


    def attack(self, attacker, defender):
        actual_atk = attacker.atk - defender.defense if attacker.atk - defender.defense > 0 else 0
        defender.hp = defender.hp - actual_atk
        if defender.hp < 0:
            defender.hp = 0

        return f"{attacker.name} attacks and deals {actual_atk} damage to {defender.name}"


    def run(self, side):
        self.state = BattleEnd("run", side)


    def defend(self, current):
        return f"{current.name} defend with all its might"


    def potion(self, current):
        return f"{current.name} prepares for a deadly blow"



