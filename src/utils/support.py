from pygame import Rect

from .settings import GameSettings
from dataclasses import dataclass
from enum import Enum
from typing import overload, TypedDict, Protocol

MouseBtn = int
Key = int

Direction = Enum('Direction', ['UP', 'DOWN', 'LEFT', 'RIGHT', 'NONE'])

@dataclass
class Position:
    x: float
    y: float
    
    def copy(self):
        return Position(self.x, self.y)
        
    def distance_to(self, other: "Position") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
        
@dataclass
class PositionCamera:
    x: int
    y: int
    
    def copy(self):
        return PositionCamera(self.x, self.y)
        
    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)
        
    def transform_position(self, position: Position) -> tuple[int, int]:
        return (int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_position_as_position(self, position: Position) -> Position:
        return Position(int(position.x) - self.x, int(position.y) - self.y)
        
    def transform_rect(self, rect: Rect) -> Rect:
        return Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)

@dataclass
class Teleport:
    pos: Position
    destination: str
    
    @overload
    def __init__(self, x: int, y: int, destination: str) -> None: ...
    @overload
    def __init__(self, pos: Position, destination: str) -> None: ...

    def __init__(self, *args, **kwargs):
        if isinstance(args[0], Position):
            self.pos = args[0]
            self.destination = args[1]
        else:
            x, y, dest = args
            self.pos = Position(x, y)
            self.destination = dest
    
    def to_dict(self):
        return {
            "x": self.pos.x // GameSettings.TILE_SIZE,
            "y": self.pos.y // GameSettings.TILE_SIZE,
            "destination": self.destination
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, data["destination"])
    
class Monster(TypedDict):
    name: str
    hp: int
    max_hp: int
    level: int
    sprite_path: str

class Item(TypedDict):
    name: str
    count: int
    sprite_path: str

class MonsterBattle:
    def __init__(self, name, hp, max_hp, level, atk, defense):
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.level = level
        self.atk = atk
        self.defense = defense


class BattleState:
    def enter (self):
        ...

    def exit(self):
        ...

    def update(self):
        ...


COLOR = {
    "grass": (88, 234, 66),
    "earth": (128, 96, 67),
    "ice": (185, 232, 234),
    "poison": (186, 85, 211),
    "wind": (242, 242, 242)
}

MONSTER_PATH = {
    "Pikachu": {"sprite_path": "menu_sprites/menusprite1.png", "animation_path":"assets/images/sprites/sprite1_idle.png"},
    "Charizard": {"sprite_path": "menu_sprites/menusprite2.png",  "animation_path":"assets/images/sprites/sprite2_idle.png"},
    "Blastoise":{"sprite_path": "menu_sprites/menusprite3.png", "animation_path":"assets/images/sprites/sprite3_idle.png"},
    "Venusaur": {"sprite_path": "menu_sprites/menusprite4.png", "animation_path":"assets/images/sprites/sprite4_idle.png"},
    "Gengar": {"sprite_path": "menu_sprites/menusprite5.png", "animation_path":"assets/images/sprites/sprite5_idle.png"},
    "Dragonite": {"sprite_path": "menu_sprites/menusprite6.png", "animation_path":"assets/images/sprites/sprite6_idle.png"},
    "Viper": {"sprite_path": "menu_sprites/menusprite11.png","animation_path":"assets/images/sprites/sprite11_idle.png"}
}

INFO_IMG = {
            "hp": "ingame_ui/baricon2.png",
            "accuracy": "ingame_ui/baricon3.png",
            "atk": "ingame_ui/baricon7.png",
            "speed": "ingame_ui/baricon5.png",
            "def": "ingame_ui/baricon4.png"
}

ITEM_PATH = {
    "HP Potion": "ingame_ui/red-potion.png",
    "ATK Potion": "ingame_ui/blue-potion2.png",
    "DEF Potion": "ingame_ui/purple-potion2.png",
    "Coins": "ingame_ui/coin.png",
    "Pokeball": "ingame_ui/ball.png"
}

ITEM_LIST = [
    {"name": "Pokeball", "price": 50},
    {"name": "HP Potion", "price": 45},
    {"name": "ATK Potion", "price": 35},
    {"name": "DEF Potion", "price": 40}

]

ITEM_DESCRIPTION = {
    "Coins": "An in-game currency (maybe the only in-game currency), giving player the ability to obtain consumables. This item can be "
             "\nobtained via battles with wandering trainers, region leaders and wild monsters",
    "HP Potion": "An incredibly powerful item, giving trainers the ability to heal their monsters during battle. This consumable item can be obtained"
                 " via shop or occasionally, through battles with wandering trainers & region leaders",
    "ATK Potion": "A consumable item with unlimited (not really) potential, increasing the attack damage of monsters, thus allowing them to deal the most deadly blow"
                  " in the most unexpected moment (if used at the right moment). Can be obtained via shop and, occasionally, battles with other trainers",
    "DEF Potion": "A defensive-type item, bestowed on monsters unyielding protection even against the deadliest attack (not really) by increasing their defense, thereby"
                  " decreasing the amount of damage taken",
    "Pokeball": "The only item in the game that allows trainers to catch wild monsters. Can be obtained through shop; however, "
                "the number of pokeballs that can be purchased is limited, so use them wisely."


}

DISPLAY_INFO = {
    "hp": "Health",
    "atk": "Attack",
    "def": "Defense",
    "speed": "Speed",
    "level": "Level",
    "accuracy": "Accuracy"
}

CHAR_MAX = {
    "atk": 100,
    "def": 100,
    "speed": 100,
    "accuracy": 100
}

INFO_BAR_COLOR = {
    "hp": "UI/UI_Flat_BarFill01a.png",
    "def": "UI/UI_Flat_BarFill01f.png",
}

ADVERSARIES = {
    "grass": ["poison", "earth"],
    "earth": ["poison", "fire"],
    "wind": ["grass", "fire"],
    "ice": ["poison", "earth", "grass"],
    "poison": []
}


RANDOM_CHAR_PATH = ["character/ow1.png", "character/ow2.png", "character/ow3.png", "character/ow5.png", "character/ow6.png", "character/ow7.png", "character/ow8.png",
                    "character/ow9.png"]