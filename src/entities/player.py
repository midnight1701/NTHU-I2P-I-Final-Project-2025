from __future__ import annotations
import pygame as pg
from jedi.debug import speed

from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, GameSettings, Logger, Direction
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 3.0 * GameSettings.TILE_SIZE
    game_manager: GameManager
    map_x: float
    map_y: float

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        '''
        [TODO HACKATHON 2]
        Calculate the distance change, and then normalize the distance
        
        [TODO HACKATHON 4]
        Check if there is collision, if so try to make the movement smooth
        Hint #1 : use entity.py _snap_to_grid function or create a similar function
        Hint #2 : Beware of glitchy teleportation, you must do
                    1. Update X
                    2. If collide, snap to grid
                    3. Update Y
                    4. If collide, snap to grid
                  instead of update both x, y, then snap to grid
        
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= ...
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += ...
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= ...
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += ...
        
        self.position = ...
        '''

        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= self.speed * dt
            self.animation.switch("left")
            self.direction = Direction.LEFT
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += self.speed * dt
            self.animation.switch("right")
            self.direction = Direction.RIGHT
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= self.speed * dt
            self.animation.switch("up")
            self.direction = Direction.UP
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += self.speed * dt
            self.animation.switch("down")
            self.direction = Direction.DOWN

        normalized = dis.distance_to(Position(0, 0))
        if normalized != 0:
            dis = Position(dis.x / normalized , dis.y / normalized)

        if self.game_manager.check_collision(pg.Rect(self.position.x + dis.x * self.speed * dt, self.position.y + dis.y * self.speed * dt,
                                                     GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)):
            pass
        else:
            self.position = Position(self.position.x + dis.x * self.speed * dt, self.position.y + dis.y * self.speed * dt)


        print(self.position.x, self.position.y)
        # Check teleportation
        tp = self.game_manager.current_map.check_teleport(self.position)
        if tp:
            dest = tp.destination
            if dest == "gym.tmx":
                self.map_x, self.map_y = self.position.x, self.position.y
            self.game_manager.switch_map(dest)

        super().update(dt)

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

