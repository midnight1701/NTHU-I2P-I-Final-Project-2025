from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera


class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"

@dataclass
class IdleMovement:
    def update(self, enemy: "EnemyTrainer", dt: float) -> None:
        return

class EnemyTrainer(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction

    @override
    def __init__(
        self,
        x: float,
        y: float,
        shop: str,
        game_manager: GameManager,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,


    ) -> None:

        super().__init__(x, y, game_manager)

        self.shop = shop

        self.classification = classification
        self.max_tiles = max_tiles
        if classification == EnemyTrainerClassification.STATIONARY:
            self._movement = IdleMovement()
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        self.warning_sign = Sprite("exclamation.png", (GameSettings.TILE_SIZE // 2, GameSettings.TILE_SIZE // 2))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        self.detected = False

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        self._has_los_to_player()
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            if self.shop == "False" and not self.game_manager.player.blocked:
                scene_manager.change_scene("battle")
            elif self.shop == "True":
                scene_manager._scenes["game"].shop_open_func()


        self.animation.update_pos(self.position)

        if self.detected and self.game_manager.player:
            if self.game_manager.player.position.x <= self.position.x and self.position.y - 32 <= self.game_manager.player.position.y <= self.position.y + 32:
                self._set_direction(Direction.LEFT)
            elif self.game_manager.player.position.x >= self.position.x and self.position.y - 32 <= self.game_manager.player.position.y <= self.position.y + 32:
                self._set_direction(Direction.RIGHT)
            elif self.game_manager.player.position.y >= self.position.y and self.position.x - 32 <= self.game_manager.player.position.x <= self.position.x + 32:
                self._set_direction(Direction.DOWN)
            elif self.game_manager.player.position.y <= self.position.y and self.position.x - 32 <= self.game_manager.player.position.x <= self.position.x + 32:
                self._set_direction(Direction.UP)

        else:
            self._set_direction(Direction.DOWN)

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        if self.detected and self.shop == "False":
            self.warning_sign.draw(screen, camera)
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        hitbox = pygame.Rect(self.position.x, self.position.y, self.max_tiles * 64, self.max_tiles * 64)
        hitbox.topleft = (self.position.x - ((self.max_tiles - 1) / 2) * 64, self.position.y - ((self.max_tiles - 1) / 2) * 64)
        return hitbox

    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
            return

        if los_rect.colliderect(pygame.Rect(player.position.x, player.position.y, 64, 64)):
            self.detected = True
        else:
            self.detected = False


    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "EnemyTrainer":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        shop = data.get("shop")
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            shop,
            game_manager,
            classification,
            max_tiles,
            facing,
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        return base