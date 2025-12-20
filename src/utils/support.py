from pygame import Rect

from .settings import GameSettings
from dataclasses import dataclass
from enum import Enum
from typing import overload, TypedDict

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
    "wind": (242, 242, 242),
    "fire": (255, 90, 0),
    "water": (28, 163, 236)
}

MONSTER_PATH = {
    "Pikachu": {"sprite_path": "menu_sprites/menusprite1.png", "animation_path":"assets/images/sprites/sprite1_idle.png"},
    "Charizard": {"sprite_path": "menu_sprites/menusprite2.png",  "animation_path":"assets/images/sprites/sprite2_idle.png"},
    "Blastoise":{"sprite_path": "menu_sprites/menusprite3.png", "animation_path":"assets/images/sprites/sprite3_idle.png"},
    "Venusaur": {"sprite_path": "menu_sprites/menusprite4.png", "animation_path":"assets/images/sprites/sprite4_idle.png"},
    "Gengar": {"sprite_path": "menu_sprites/menusprite5.png", "animation_path":"assets/images/sprites/sprite5_idle.png"},
    "Dragonite": {"sprite_path": "menu_sprites/menusprite6.png", "animation_path":"assets/images/sprites/sprite6_idle.png"},
    "Viper": {"sprite_path": "menu_sprites/menusprite11.png","animation_path":"assets/images/sprites/sprite11_idle.png"},
    "Infernum": {"sprite_path": "menu_sprites/menusprite8.png", "animation_path": "assets/images/sprites/sprite8_idle.png"},
    "Flamme": {"sprite_path": "menu_sprites/menusprite7.png", "animation_path": "assets/images/sprites/sprite7_idle.png"},
    "Firestorm": {"sprite_path": "menu_sprites/menusprite9.png", "animation_path": "assets/images/sprites/sprite9_idle.png"},
    "Dolph": {"sprite_path": "menu_sprites/menusprite12.png", "animation_path": "assets/images/sprites/sprite12_idle.png"},
    "Hydolph": {"sprite_path": "menu_sprites/menusprite13.png", "animation_path": "assets/images/sprites/sprite13_idle.png"},
    "Ascendolph": {"sprite_path": "menu_sprites/menusprite14.png", "animation_path": "assets/images/sprites/sprite14_idle.png"}
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
    "ATK Potion": "ingame_ui/orange-potion.png",
    "DEF Potion": "ingame_ui/purple-potion2.png",
    "Mana Potion": "ingame_ui/blue-potion2.png",
    "Coins": "ingame_ui/coin.png",
    "Pokeball": "ingame_ui/ball.png",
    "Hollow Core": "ingame_ui/core_1.png",
    "Sephira Core": "ingame_ui/core_16.png",
    "Ultimate Aegis": "ingame_ui/ticket.png",
    "Destined Revival": "ingame_ui/core_bypass.png"
}

ITEM_LIST = [
    {"name": "Pokeball", "price": 25},
    {"name": "HP Potion", "price": 20},
    {"name": "ATK Potion", "price": 20},
    {"name": "DEF Potion", "price": 10},
    {"name": "Mana Potion", "price": 20}

]


ITEM_DESCRIPTION = {
    "Coins": "The universal currency of the region. Earned by defeating wild monsters, wandering trainers, and region leaders, coin allows you to purchase valuable supplies and consumables essential for your journey.",
    "HP Potion": "A reliable healing item capable of restoring a monster’s health during the heat of battle. HP Potions are commonly sold in shops, though they may also be awarded for triumphing over trainers or region leaders",
    "ATK Potion": "A powerful consumable that temporarily amplifies a monster’s Attack stat. When used at the perfect moment, it enables devastating strikes capable of turning the tide of battle. ATK Potions can be purchased or occasionally obtained as rare battle rewards",
    "DEF Potion": "A defensive enhancer that boosts a monster’s Defense, helping it endure stronger enemy attacks. This sturdy elixir is available in shops and may also be earned as a rare prize from difficult battles.",
    "Mana Potion": "A mystical elixir that replenishes a monster’s mana, allowing it to cast skills and abilities during battle without restraint. Mana Potions are commonly sold in shops and may also be found as rare rewards from powerful opponents. A must-have item for any trainer relying on skill-heavy strategies",
    "Pokeball": "A specialized capture device crafted for containing wild monsters. While purchasable in shops, Pokeballs are stocked in limited quantities, making each throw a strategic decision in your quest to expand your team.",
    "Hollow Core": "Relic from a lost time, filled with a mysterious power. Combined with Sephira Core, this item bestows upon monsters the ultimate ability to transcend their limits, thus evolving into a higher form, with drastically increased stats."
                   " Obtained through battle or gacha system",
    "Sephira Core": "Nobody knows how, or why it comes to existence. A mysterious remnant from unknown history, which, if combined with Hollow Core, will bestow on monsters the ultimate transformation. Can only be obtained "
                    "through battles with region leaders, minibosses & final boss, and very rarely, gacha system",
    "Ultimate Aegis": "The ultimate lifesaver in the darkest hours, allowing trainers to summon a companion capable of drastically increase monster's Health, Defense, Mana "
                      "and Attack for the entire duration of the battle. Can only be used once during battle, companion summoned"
                      " will be randomized",
    "Destined Revival": "\"From the remnants of a devastating battle, you are once again awaken from your eternal slumber. Your heart filled with determination, your body filled with unwavering strength,"
                        " you swear to pulverize all enemies ahead \". \nMonsters are revived with 1/10 of their original HP "
}

SHOP_DESCRIPTION = {
    "Coins": "Currency earned from battles; used to buy items",
    "HP Potion": "Restores a monster’s HP",
    "ATK Potion": "Temporarily boosts Attack",
    "DEF Potion": "Increases Defense and reduces damage taken",
    "Mana Potion": "Restores a monster’s energy for skills",
    "Pokeball": "Used to catch wild monsters"
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
    "poison": [],
    "fire": ["grass", "poison"],
    "water": ["fire", "poison", "grass"]
}


RANDOM_CHAR_PATH = ["character/ow1.png", "character/ow2.png", "character/ow3.png", "character/ow5.png", "character/ow6.png", "character/ow7.png", "character/ow8.png",
                    "character/ow9.png"]

PLAYER_SPAWN_TP = {
    "navigation.tmx": "navigation",
    "shop.tmx": "shop",
    "gym.tmx": "gym"
}

EVOLUTION_DICT = {
    "Pikachu": { "name": "Charizard", "hp": 300, "atk": 50, "def": 40, "speed": 70, "accuracy": 100, "mana": 200, "max_mana": 200, "max_def": 40, "max_hp": 300,
                "max_atk":  50, "max_accuracy": 100, "max_speed": 70, "element": "grass"},
    "Charizard": { "name": "Blastoise", "hp": 450, "atk": 65, "def": 50, "speed": 100, "accuracy": 100, "mana": 250, "max_mana": 250, "max_def": 50, "max_hp": 450,
                "max_atk":  65, "max_accuracy": 100, "max_speed": 100, "element": "grass"},
    "Flamme": {"name": "Infernum", "hp": 170, "atk": 60, "def": 30, "speed": 100, "accuracy": 100, "mana": 150, "max_mana": 150, "max_def": 30, "max_hp": 170,
                "max_atk":  70, "max_accuracy": 100, "max_speed": 100, "element": "fire"},
    "Infernum": { "name": "Firestorm", "hp": 420, "atk": 70, "def": 30, "speed": 100, "accuracy": 100, "mana": 220, "max_mana": 220, "max_def": 30, "max_hp": 420,
                "max_atk":  70, "max_accuracy": 100, "max_speed": 100, "element": "fire"},
    "Dolph": {"name": "Hydolph", "hp": 160, "atk": 65, "def": 20, "speed": 100, "accuracy": 100, "mana": 150, "max_mana": 150, "max_def": 20, "max_hp": 160,
          "max_atk": 65, "max_accuracy": 100, "max_speed": 100, "element": "water"},
    "Hydolph": { "name": "Ascendolph", "hp": 470, "atk": 50, "def": 50, "speed": 100, "accuracy": 100, "mana": 300, "max_mana": 300, "max_def": 50, "max_hp": 470,
                "max_atk":  50, "max_accuracy": 100, "max_speed": 100, "element": "water"}
}


AEGIS_IMG = {
    "Hikari & Tairitsu": "sprites/Hikari & Tairitsu (Next Stage).png",
    "Nell": "sprites/Nell.png",
    "Hikari (Fatalis)": "sprites/Hikari (Fatalis).png",
    "Tairitsu (Tempestissimo)": "sprites/Tairitsu (Tempestissimo).png"
}

AEGIS_POSITION = {
    "Hikari & Tairitsu": ((GameSettings.SCREEN_WIDTH / 2), (GameSettings.SCREEN_HEIGHT / 2) + 280),
    "Hikari (Fatalis)": ((GameSettings.SCREEN_WIDTH / 2), (GameSettings.SCREEN_HEIGHT / 2) + 150),
    "Tairitsu (Tempestissimo)": ((GameSettings.SCREEN_WIDTH / 2), (GameSettings.SCREEN_HEIGHT / 2) + 200),
    "Nell": ((GameSettings.SCREEN_WIDTH / 2), (GameSettings.SCREEN_HEIGHT / 2) + 130)
}

BATTLE_BG = {
    "Testify": "backgrounds/Testify.jpg",
    "Designant": "backgrounds/Designant.jpg",
    "Arghena": "backgrounds/Arghena.jpg"
}

BATTLE_MUSIC = {
    "Testify": "TestifyBG.mp3",
    "Designant": "DesignantBG.mp3",
    "Arghena": "ArghenaBG.mp3"
}

KEYMAP = {
    49: "!",
    50: "@",
    51: "#",
    52: "$",
    53: "%",
    54: "^",
    55: "&",
    56: "*",
    57: "(",
    48: ")",
    45: "_",
    61: "+",
    91: "{",
    93: "}",
    59: ":",
    39: "\"",
    92: "|",
    44: "<",
    46: ">",
    47: "?",
    104: "H",
    105: "I"

}

MONSTER_CATCH = {
        "Pikachu": { "name": "Pikachu", "hp": 120, "atk":  20,"def": 20, "speed": 50, "accuracy": 70, "mana": 150,"max_mana": 150, "max_def": 20, "max_hp": 120,
         "max_atk":  20, "max_accuracy": 70, "max_speed": 50, "element": "grass"},

        "Dolph": { "name": "Dolph",  "hp": 115, "atk": 30,"def": 20,"speed": 70, "accuracy": 70, "mana": 150, "max_mana": 150,"max_def": 20, "max_hp": 115,
          "max_atk": 30, "max_accuracy": 70, "max_speed": 70, "element": "water"},

        "Gengar": { "name": "Gengar", "hp": 105, "atk": 30,"def": 30,"speed": 20, "accuracy": 70, "mana": 150, "max_mana": 150, "max_def": 30, "max_hp": 105,
          "max_atk": 30, "max_accuracy": 70, "max_speed": 70, "element": "wind"},

        "Dragonite": { "name": "Dragonite", "hp": 130, "atk": 20,"def": 10,"speed": 20, "accuracy": 70, "mana": 150,"max_mana": 150, "max_def": 10, "max_hp": 130,
          "max_atk": 20, "max_accuracy": 70, "max_speed": 20, "element": "ice"},

        "Viper": { "name": "Viper",  "hp": 120, "atk": 30,"def": 10,"speed": 20, "accuracy": 70, "mana": 150,"max_mana": 150, "max_def": 10, "max_hp": 120,
          "max_atk": 30, "max_accuracy": 70, "max_speed": 20, "element": "poison"},

        "Flamme": { "name": "Flamme", "hp": 125, "atk": 20,"def": 20,"speed": 20, "accuracy": 70, "mana": 150,"max_mana": 150, "max_def": 20, "max_hp": 125,
          "max_atk": 20, "max_accuracy": 70, "max_speed": 20, "element": "fire"}
}

ITEM_FIRST_ROW = ["Pokeball", "HP Potion", "ATK Potion", "DEF Potion", "Mana Potion"]
ITEM_SECOND_ROW = ["Sephira Core", "Hollow Core", "Ultimate Aegis", "Destined Revival"]

ITEM_LIST_GACHA = ["Pokeball", "HP Potion", "ATK Potion", "DEF Potion", "Mana Potion", "Sephira Core", "Hollow Core",
                   "Ultimate Aegis", "Destined Revival"]

