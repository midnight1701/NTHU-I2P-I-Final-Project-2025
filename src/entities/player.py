from __future__ import annotations
import pygame as pg
from pygame import K_SPACE

from src.sprites.animation import Animation
from .entity import Entity
from src.core.services import input_manager, scene_manager
from src.utils import Position, PositionCamera, GameSettings, Logger, Direction
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 6.0 * GameSettings.TILE_SIZE
    game_manager: GameManager
    map_x: float
    map_y: float

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        self.animation = Animation("character/ow1.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self.blocked = False
        self.bush_collide = False

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)

        if not self.blocked:
            if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
                dis.x -= dt
                self.animation.switch("left")
                self.direction = Direction.LEFT
            if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
                dis.x += dt
                self.animation.switch("right")
                self.direction = Direction.RIGHT
            if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
                dis.y -= dt
                self.animation.switch("up")
                self.direction = Direction.UP
            if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
                dis.y += dt
                self.animation.switch("down")
                self.direction = Direction.DOWN

            normalized = dis.distance_to(Position(0, 0))
            if normalized != 0:
                dis = Position(dis.x / normalized, dis.y / normalized)

            if self.game_manager.check_collision(
                    pg.Rect(self.position.x + dis.x * self.speed * dt, self.position.y + dis.y * self.speed * dt,
                            GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)):
                pass
            else:
                self.position = Position(self.position.x + dis.x * self.speed * dt,
                                         self.position.y + dis.y * self.speed * dt)

            # Check teleportation
            tp = self.game_manager.current_map.check_teleport(self.position)
            if tp:
                dest = tp.destination
                self.game_manager.switch_map(dest)

            self.check_if_bush_collide()
            if self.bush_collide and input_manager.key_pressed(K_SPACE):
                scene_manager.change_scene("battle")
                scene_manager.monster_catch = True

        super().update(dt)

    def check_if_bush_collide(self):
        check = self.game_manager.check_bush_collision(pg.Rect(self.position.x, self.position.y, 64, 64))
        if check:
            self.bush_collide = True
        else:
            self.bush_collide = False

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @property
    @override
    def camera(self) -> PositionCamera:
        return PositionCamera(int(self.position.x) - GameSettings.SCREEN_WIDTH // 2, int(self.position.y) - GameSettings.SCREEN_HEIGHT // 2)
            
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)


    def check_if_battle_available(self):
        if len(self.game_manager.bag._monsters_data) == 1:
            if self.game_manager.bag._monsters_data[0]["hp"] == 0:
                return False
        else:
            count = 0
            for i in self.game_manager.bag._monsters_data:
                if i["hp"] == 0:
                    count += 1

            if count == len(self.game_manager.bag._monsters_data):
                return False

        return True

