import pygame as pg
from pygame import K_SPACE


from src.core.services import scene_manager
from src.utils.support import COLOR, MONSTER_PATH, DISPLAY_INFO, CHAR_MAX, ADVERSARIES
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



class AttackDisplay:
    def __init__(self):
        self.choice = ["Light", "Normal", "Heavy", "Ultimate"]
        self.index = 0
        self.limit = 4
        self.font = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
        self.selection_bg = pg.Rect(0, 0, GameSettings.SCREEN_WIDTH * 0.3, GameSettings.SCREEN_HEIGHT * 0.5)
        self.selection_bg.center = (GameSettings.SCREEN_WIDTH / 2, GameSettings.SCREEN_HEIGHT - GameSettings.SCREEN_HEIGHT * 0.5 - 40)

        self.val_top = self.selection_bg.topleft
        self.val_width = self.selection_bg.width
        self.val_height = self.selection_bg.height / self.limit


    def draw(self, screen):
        pg.draw.rect(screen, (44, 44, 44), self.selection_bg)
        box_offset = 0 if self.index < self.limit else -(self.index - self.limit + 1) * self.val_height
        for index, attack_type in enumerate(self.choice):
            text_color = "yellow" if self.index == index else "white"
            bg_color = (44, 44, 44) if self.index != index else (169, 169, 169)
            center_x = self.selection_bg.centerx
            top = self.val_top[1] + index * self.val_height + box_offset
            attack_name = self.font.render(attack_type, True, text_color)
            attack_name_rect = attack_name.get_rect()
            attack_name_rect.center = (center_x, top + 40)
            attack_name_bg = pg.Rect(self.selection_bg.topleft[0], top, self.val_width, self.val_height)

            if attack_name_bg.colliderect(self.selection_bg):
                pg.draw.rect(screen, bg_color, attack_name_bg)
                screen.blit(attack_name, attack_name_rect)


    def update(self):
        if input_manager.key_pressed(pg.K_UP):
            self.index -= 1
        if input_manager.key_pressed(pg.K_DOWN):
            self.index += 1

        self.index = self.index % len(self.choice)


class Attack:
    def __init__(self, attacker, defender):
        self.attack_type = None
        self.display_attack_type = False
        self.attack_display = AttackDisplay()
        self.attacker, self.defender = attacker, defender
        self.attack_display_draw = True

        self.attacked = False
        self.final_text = ""
        self.end = False


    def draw(self, screen):
        self.attack_display.draw(screen)


    def update(self):
        if self.attack_type is None:
            self.attack_display.update()

        if input_manager.key_pressed(K_SPACE):
            if self.attack_type is None:
                self.attack_type = self.attack_display.choice[self.attack_display.index]
                self.display_attack_type = True
            elif self.attack_display_draw:
                self.attack_display_draw = False
                self.attacked = True
                self.final_text = self.perform_attack()
            else:
                self.end = True


    def perform_attack(self):
        attacked = random.choices([True, False], weights=[self.attacker["accuracy"], 100 - self.attacker["accuracy"]], k=1)
        required_mana = {"Light": 10, "Normal": 15, "Heavy": 20, "Ultimate": 80}

        if attacked == [True] and self.attacker["mana"] >= required_mana[self.attack_type]:
            self.attacker["mana"] -= required_mana[self.attack_type]
            enemy_element = self.defender["element"]
            match self.attack_type:
                case "Light":
                    atk_dmg = self.attacker["atk"] * 0.7
                case "Normal":
                    atk_dmg = self.attacker["atk"]
                case "Heavy":
                    atk_dmg = self.attacker["atk"] * 1.5
                case "Ultimate":
                    atk_dmg = self.attacker["atk"] * 2.5

            if enemy_element in ADVERSARIES[self.attacker["element"]]:
                atk_dmg = atk_dmg * 1.5
                if self.defender["def"] > 0:
                    self.defender["def"] = self.defender["def"] - 10
                    atk_dmg = int(atk_dmg - 10)
            else:
                if self.defender["def"] > 0:
                    self.defender["def"] = self.defender["def"] - 5
                    atk_dmg = int(atk_dmg - 5)

            self.defender["hp"] = self.defender["hp"] - int(atk_dmg)
            if self.defender["hp"] < 0:
                self.defender["hp"] = 0

            return f"{self.attacker["name"]} attacks and inflicts {int(atk_dmg)} damage upon the enemy"

        else:
            if self.attacker["mana"] < required_mana[self.attack_type]:
                return f"Insufficient mana. Use potion to replenish monster's mana"
            else:
                return f"{self.attacker["name"]}'s attack misses its target, {self.defender["name"]} remains unscathed"


    def dialogue(self):
        match self.attack_type:
            case "Light":
                return f"{self.attacker["name"]} strikes with minimal effort"
            case "Normal":
                return f"{self.attacker["name"]} strikes with normal strength"
            case "Heavy":
                return f"{self.attacker["name"]} strikes with more power than ever before"
            case "Ultimate":
                return f"{self.attacker["name"]} unleashes full power to obliterate its enemy"

        return None


class Potion:
    def __init__(self, item_lst, monster):
        self.potion_type = None
        self.display_potion_type = False
        self.potion_display = PotionDisplay()
        self.item_lst = item_lst
        self.potion_display_draw = True
        self.end = False
        self.potion_usage = False

        self.final_text = ""
        self.monster_alt = monster

    def draw(self, screen):
        self.potion_display.draw(screen)

    def update(self):
        if self.potion_type is None:
            self.potion_display.update()
        if input_manager.key_pressed(K_SPACE):
            if self.potion_type is None:
                self.potion_type = self.potion_display.choice[self.potion_display.index]
                self.display_potion_type = True
            elif self.potion_display_draw:
                self.potion_display_draw = False
                self.potion_usage = True
                self.final_text = self.perform_action()
            else:
                self.end = True


    def dialogue(self):
        match self.potion_type:
            case "HP Potion":
                return f"{self.monster_alt["name"]} receives healing to compensate for its damage"
            case "DEF Potion":
                return f"{self.monster_alt["name"]} strengthens its defense in preparation for upcoming perils"
            case "ATK Potion":
                return f"{self.monster_alt["name"]} upgrades its attack to obliterate the enemy ahead"
            case "Mana Potion":
                return f"{self.monster_alt["name"]} senses magical energy flowing within"

        return None

    def perform_action(self):
        if self.potion_type == "HP Potion":
            for item in self.item_lst:
                if item["name"] == "HP Potion" and item["count"] > 0:
                    item["count"] -= 1
                    self.monster_alt["hp"] += int((self.monster_alt["max_hp"] - self.monster_alt["hp"]) * 0.5)
                    if self.monster_alt["hp"] > self.monster_alt["max_hp"]:
                        self.monster_alt["hp"] = self.monster_alt["max_hp"]

                    return f"{self.monster_alt["name"]}'s HP is restored"


            return f"Potion unavailable. Should have paid attention to inventory management"


        elif self.potion_type == "DEF Potion":
            for item in self.item_lst:
                if item["name"] == "DEF Potion" and item["count"] > 0:
                    item["count"] -= 1
                    self.monster_alt["def"] = self.monster_alt["max_def"]
                    return f"{self.monster_alt["name"]}'s defense is restored to its original state"

            return f"Potion unavailable. Should have paid attention to inventory management"

        elif self.potion_type == "Mana Potion":
            for item in self.item_lst:
                if item["name"] == "Mana Potion" and item["count"] > 0:
                    item["count"] -= 1
                    self.monster_alt["mana"] = self.monster_alt["max_mana"]
                    return f"{self.monster_alt["name"]}'s energy is restored to its original state"

            return f"Potion unavailable. Attack is no longer an option"

        elif self.potion_type == "ATK Potion":
            for item in self.item_lst:
                if item["name"] == "ATK Potion" and item["count"] > 0:
                    item["count"] -= 1
                    self.monster_alt["atk"] += self.monster_alt["atk"] * 0.3
                    return f"{self.monster_alt["name"]}'s attack now inflict {int(self.monster_alt["atk"])} base damage upon enemy"

            return f"Potion unavailable. Use your original strength without relying on some strange potions"


        return None


class PotionDisplay(AttackDisplay):
    def __init__(self):
        super().__init__()
        self.choice = ["HP Potion", "DEF Potion", "ATK Potion", "Mana Potion"]



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
            text = self.font.render(f"{DISPLAY_INFO[char]}: {val}/{monster["max_hp"]}", True, (255, 255, 0)) if char == "hp" else self.font.render(f"{DISPLAY_INFO[char]}: {val}/{CHAR_MAX[char]}", True, (255, 255, 0))
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

        self.ally_setup, self.ally_selection, self.ally_selected = False, False, False
        self.enemy_setup, self.enemy_selection, self.enemy_selected = False, False, False
        self.state_complete = False

        self.selected_monster = None
        self.selected_enemy = None
        self.index = 0


    def draw(self, screen):
        if self.ally_selection and not self.ally_setup:
            self.display.draw(screen)


    def update(self):
        if self.ally_selection and not self.ally_selected:
            self.display.update()
            self.index = self.display.index


        if input_manager.key_pressed(K_SPACE):
            if not self.enemy_selection:
                self.enemy_selection = True
            elif not self.enemy_selected:
                self.enemy_selected = True
                self.selected_enemy = random.choice(self.enemy_monster)
            elif not self.enemy_setup:
                self.enemy_setup = True
            elif not self.ally_selection:
                self.ally_selection = True
            elif not self.ally_selected:
                self.selected_monster = self.player_dict[self.index]
                self.ally_selected = True
            elif not self.ally_setup:
                self.ally_setup = True
            else:
                self.state_complete = True


    def dialogue(self):
        if not self.enemy_selection:
            return f"Ally trainer has encountered something unexpected"
        elif self.enemy_selection and not self.enemy_selected:
            return f"Enemy trainer is selecting a monster for battle"
        elif self.enemy_selected and not self.ally_selection:
            return f"{self.selected_enemy["name"]} arrives with blazing determination"
        elif not self.ally_selected and self.ally_selection:
            return f"Please select a monster for battle"
        elif self.ally_selected and self.selected_monster is not None and not self.ally_setup:
            return f"Ally trainer has selected {self.selected_monster["name"]} for battle"
        elif self.ally_setup:
            return f"{self.selected_monster["name"]} enters the battleground with unyielding conviction"


        return None


    def return_ally_monster(self):
        if self.selected_monster is not None:
            return self.selected_monster

        return None

    def return_enemy_monster(self):
        if self.selected_enemy is not None:
            return self.selected_enemy

        return None


# noinspection PyMethodMayBeStatic
class PlayerTurn(BattleState):
    def __init__(self, player, enemy, run, residue_text=None):
        # Flags
        self.state_complete = False
        self.dialogue_check = False
        self.selection = False

        self.action = None
        self.player = player
        self.enemy = enemy
        self.action_text = None
        self.residue_text = residue_text

        self.potion_unavailable = False

        # Action
        self.atk, self.run, self.potion = Attack(self.player, self.enemy), run, Potion(services.game_manager.bag._items_data, monster=self.player)


    def draw(self, screen):
        if self.action == "attack" and self.atk.attack_display_draw:
            self.atk.draw(screen)
        elif self.action == "potion" and self.potion.potion_display_draw:
            self.potion.draw(screen)


    def update(self):
        if input_manager.key_pressed(K_SPACE):
            if self.residue_text is not None:
                self.residue_text = None

        if self.action == "attack":
            self.atk.update()
            if self.atk.end:
                self.state_complete = True
                self.potion_unavailable = False
                self.player["atk"] = self.player["max_atk"]

        elif self.action == "potion":
            self.potion.update()
            if self.potion.end:
                self.action = None
                self.potion_unavailable = True

        elif self.action == "run":
            if input_manager.key_pressed(K_SPACE):
                self.action_text = self.run("ally", self.player)
                if not self.dialogue_check:
                    self.dialogue_check = True
                    self.potion_unavailable = False


    def change_action(self, action):
        self.action = action


    def dialogue(self):
        if self.residue_text is not None:
            return self.residue_text
        if self.action is None:
            return "What will ally trainer do?"

        if self.action is not None:
            match self.action:
                case "attack":
                    if not self.atk.display_attack_type:
                        return f"Ally trainer decides to go on the offensive, which attack will {self.player["name"]} perform"
                    elif self.atk.display_attack_type and self.atk.attack_display_draw:
                        dialogue = self.atk.dialogue()
                        return dialogue
                    elif self.atk.attacked:
                        return self.atk.final_text


                case "run":
                    if not self.dialogue_check:
                        return f"{self.player["name"]} senses a dark premonition"
                    elif self.dialogue_check:
                        return self.action_text

                case "potion":
                    if not self.potion.potion_type:
                        return f"{self.player["name"]} obtains a hidden power within, select a potion to bring this power to light"
                    elif self.potion.display_potion_type and not self.potion.potion_usage:
                        dialogue = self.potion.dialogue()
                        return dialogue
                    elif self.potion.potion_usage:
                        return self.potion.final_text


        return None


# noinspection PyMethodMayBeStatic
class EnemyTurn(BattleState):
    def __init__(self, player, enemy, atk, defend, run, potion, residue_text=None):
        self.state_complete = False
        self.dialogue_check = False
        self.action = None
        self.player = player
        self.enemy = enemy
        self.action_text = ""
        self.atk, self.defend, self.run, self.potion = atk, defend, run, potion

        self.residue_text = residue_text


    def get_action(self):
        action = ["attack", "run", "mana", "def"]
        return random.choices(action, weights=[25, 25, 25, 25], k=1)


    def perform_action(self):
        match self.action:
            case "attack":
                self.action_text = self.atk(self.enemy, self.player)
            case "mana":
                pass
            case "run":
                self.action_text = self.run("enemy", self.enemy)
            case "def":
                pass


    def update(self):
        if input_manager.key_pressed(K_SPACE):
            if self.residue_text is not None:
                self.residue_text = None
            elif self.action is None:
                self.action = self.get_action()
            elif not self.dialogue_check:
                self.dialogue_check = True
                self.perform_action()
            elif self.dialogue_check:
                self.state_complete = True


    def dialogue(self):
        if self.residue_text is not None:
            return self.residue_text
        elif not self.action:
            return "Enemy trainer is devising a novel battle strategy"
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
                scene_manager.monster_catch_func()
                if self.state.status == "ally_wins" and self.curr_enemy_monster not in services.game_manager.bag._monsters_data:
                    services.game_manager.bag._monsters_data.append(self.curr_enemy_monster)


    def reset(self):
        self.state = BattleSetup(self.player_monster_lst, self.enemy_monster_lst)
        for monster in self.enemy_monster_lst:
            for info in ["hp", "def", "mana"]:
                monster[info] = monster[f"max_{info}"]


    def get_monster(self):
        if isinstance(self.state, BattleSetup):
            if self.state.ally_selected and not self.state.ally_setup:
                self.curr_ally_monster = self.state.return_ally_monster()
                return self.curr_ally_monster
            elif self.state.enemy_selected:
                self.curr_enemy_monster = self.state.return_enemy_monster()
                return self.curr_enemy_monster

        return None


    def change_state(self):
        if isinstance(self.state, BattleSetup):
            self.state = PlayerTurn(self.curr_ally_monster, self.curr_enemy_monster, self.run)
        elif isinstance(self.state, PlayerTurn):
            if self.is_enemy_alive():
                self.state = EnemyTurn(self.curr_ally_monster, self.curr_enemy_monster, self.attack, self.run,)
            else:
                self.state = BattleEnd(status="ally_wins", side="ally")

        elif isinstance(self.state, EnemyTurn):
            if self.is_player_alive():
                self.state = PlayerTurn(self.curr_ally_monster, self.curr_enemy_monster, self.run)
            else:
                self.state = BattleEnd(status="enemy_wins", enemy="enemy")



    def is_player_alive(self):
        return self.curr_ally_monster["hp"] > 0


    def is_enemy_alive(self):
        return self.curr_enemy_monster["hp"] > 0


    def get_dialogue(self):
        return self.state.dialogue()


    def attack(self, attacker, defender):
        pass


    def run(self, side, target):
        role = "Ally trainer" if side == "ally" else "Enemy trainer"
        probability = random.choices([True, False], [target["speed"], 100 - target["speed"]], k=1)

        if probability == [True]:
            self.state = BattleEnd("run", side)
        else:
            residue_text =  f"{role} and companion cannot escape from the grasp of the enemy, the battle continues"
            self.state = PlayerTurn(self.curr_ally_monster, self.curr_enemy_monster,self.run, residue_text) if side == "enemy" else EnemyTurn(self.curr_ally_monster, self.curr_enemy_monster, self.attack, self.defend, self.run, self.potion, residue_text)

        return None

    def mana(self, current):
        pass

    def defense(self, current):
        pass



