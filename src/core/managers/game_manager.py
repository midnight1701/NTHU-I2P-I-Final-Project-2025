from __future__ import annotations


from src.utils import Logger, GameSettings, Position, Teleport
import json, os
import pygame as pg
from typing import TYPE_CHECKING
from src.utils.support import PLAYER_SPAWN_TP

if TYPE_CHECKING:
    from src.entities.shop_npc import ShopNPC
    from src.maps.map import Map
    from src.entities.player import Player
    from src.entities.enemy_trainer import EnemyTrainer
    from src.data.bag import Bag

class GameManager:
    # Entities
    player: Player | None
    enemy_trainers: dict[str, list[EnemyTrainer]]
    bag: "Bag"
    
    # Map properties
    current_map_key: str
    maps: dict[str, Map]
    
    # Changing Scene properties
    should_change_scene: bool
    next_map: str
    
    def __init__(self, maps: dict[str, Map], start_map: str, 
                 player: Player | None,
                 enemy_trainers: dict[str, list[EnemyTrainer]],
                 npc: dict,
                 bag: Bag | None = None,
                 enemy_monster: dict | None = None):
                     
        from src.data.bag import Bag
        # Game Properties
        self.maps = maps
        self.current_map_key = start_map
        self.player = player
        self.enemy_trainers = enemy_trainers
        self.npc = npc
        self.enemy_monster = enemy_monster

        # Evolution
        self.evolution = False
        self.base_monster = None
        self.evo_monster = None
        self.boss_encounter = False

        self.bag = bag if bag is not None else Bag([], [])
        
        # Check If you should change scene
        self.teleported = ""
        self.should_change_scene = False
        self.next_map = ""
        
    @property
    def current_map(self) -> Map:
        return self.maps[self.current_map_key]
        
    @property
    def current_enemy_trainers(self) -> list[EnemyTrainer]:
        return self.enemy_trainers[self.current_map_key]

    @property
    def current_roaming_monster(self):
        return self.enemy_monster[self.current_map_key]

    @property
    def current_npc(self):
        return self.npc[self.current_map_key]
        
    @property
    def current_teleporter(self) -> list[Teleport]:
        return self.maps[self.current_map_key].teleporters
    
    def switch_map(self, target: str) -> None:
        if target not in self.maps:
            Logger.warning(f"Map '{target}' not loaded; cannot switch.")
            return
        
        self.next_map = target
        self.should_change_scene = True

        if self.current_map_key != "map.tmx":
            self.teleported = PLAYER_SPAWN_TP[self.current_map_key]
            
    def try_switch_map(self) -> None:
        if self.should_change_scene:
            self.current_map_key = self.next_map
            self.next_map = ""
            self.should_change_scene = False
            if self.player:
                if self.current_map_key == "map.tmx":
                    match self.teleported:
                        case "shop":
                            self.player.position = Position(52 * GameSettings.TILE_SIZE, 27 * GameSettings.TILE_SIZE)
                            self.teleported = ""
                        case "gym":
                            self.player.position = Position(24 * GameSettings.TILE_SIZE, 24 * GameSettings.TILE_SIZE)
                            self.teleported = ""

                else:
                    self.player.position = self.maps[self.current_map_key].spawn

            
    def check_collision(self, rect: pg.Rect) -> bool:
        if self.maps[self.current_map_key].check_collision(rect):
            return True
        for entity in self.enemy_trainers[self.current_map_key]:
            if rect.colliderect(entity.animation.rect):
                return True
        
        return False

    def check_bush_collision(self, rect: pg.Rect):
        if self.maps[self.current_map_key].check_if_bush_collision(rect):
            return True

        return False

    def monster_revival(self):
        monster = self.bag._monsters_dict[self.bag.index]
        for i in self.bag._items_data:
            if i["name"] == "Destined Revival" and i["count"] >= 1 and monster["hp"] == 0:
                i["count"] -= 1
                monster["hp"] = int(monster["max_hp"] * 0.1)
                break

    def monster_healing(self):
        monster = self.bag._monsters_dict[self.bag.index]
        for i in self.bag._items_data:
            if i["name"] == "HP Potion" and i["count"] >= 1 and monster["hp"] > 0:
                i["count"] -= 1
                monster["hp"] += int(monster["max_hp"] * 0.1)
                break

        if monster["hp"] > monster["max_hp"]:
            monster["hp"] = monster["max_hp"]


    def push_evo_info(self, base, evo):
        self.base_monster = base
        self.evo_monster = evo

    def reset_evo_info(self):
        self.base_monster, self.evo_monster = None, None

    def evolution_func(self):
        self.evolution = True

    def evolution_cancel(self):
        self.evolution = False

    def boss(self):
        self.boss_encounter = True

    def boss_cancel(self):
        self.boss_encounter = False
        self.base_monster, self.evo_monster = None

    def save(self, path: str) -> None:
        try:
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            Logger.info(f"Game saved to {path}")
        except Exception as e:
            Logger.warning(f"Failed to save game: {e}")
             
    @classmethod
    def load(cls, path: str) -> "GameManager | None":
        if not os.path.exists(path):
            Logger.error(f"No file found: {path}, ignoring load function")
            return None

        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, object]:
        map_blocks: list[dict[str, object]] = []
        for key, m in self.maps.items():
            block = m.to_dict()
            print(block)
            block["enemy_trainers"] = [t.to_dict() for t in self.enemy_trainers.get(key, [])]
            block["others"] = [n.to_dict() for n in self.npc.get(key, [])]
            block["roaming_mobs"] = [k for k in self.enemy_monster.get(key, [])]
            map_blocks.append(block)
        return {
            "map": map_blocks,
            "current_map": self.current_map_key,
            "player": self.player.to_dict() if self.player is not None else None,
            "bag": self.bag.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "GameManager":
        from src.entities.shop_npc import ShopNPC
        from src.maps.map import Map
        from src.entities.player import Player
        from src.entities.enemy_trainer import EnemyTrainer
        from src.data.bag import Bag
        
        Logger.info("Loading maps")
        maps_data = data["map"]
        maps: dict[str, Map] = {}
        player_spawns: dict[str, Position] = {}
        trainers: dict[str, list[EnemyTrainer]] = {}
        npc: dict = {}
        enemy_monster: dict = {}

        for entry in maps_data:
            path = entry["path"]
            maps[path] = Map.from_dict(entry)
            sp = entry.get("player")
            if sp:
                player_spawns[path] = Position(
                    sp["x"] * GameSettings.TILE_SIZE,
                    sp["y"] * GameSettings.TILE_SIZE
                )
        current_map = data["current_map"]
        gm = cls(
            maps, current_map,
            None, # Player
            trainers,
            npc,
            None,
            enemy_monster,
        )
        gm.current_map_key = current_map
        
        Logger.info("Loading enemy trainers")
        for m in data["map"]:
            raw_data = m["enemy_trainers"]
            raw_data_alt = m["others"]
            gm.enemy_trainers[m["path"]] = [EnemyTrainer.from_dict(t, gm) for t in raw_data]
            gm.npc[m["path"]] = [ShopNPC.from_dict(t, gm) for t in raw_data_alt]
            gm.enemy_monster[m["path"]] = m["roaming_mobs"]

        Logger.info("Loading Player")
        if data.get("player"):
            gm.player = Player.from_dict(data["player"], gm)

        Logger.info("Loading bag")
        from src.data.bag import Bag as _Bag
        gm.bag = Bag.from_dict(data.get("bag", {})) if data.get("bag") else _Bag([], [])

        return gm