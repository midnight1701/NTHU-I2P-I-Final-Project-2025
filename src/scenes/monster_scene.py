import pygame as pg
from pygame import K_ESCAPE, K_SPACE
from src.scenes.battle_system import BattleSetup, BattleEnd, EnemyTurn, PlayerTurn

from src.scenes.battle_system import BattleSystem
from src.sprites import BackgroundSprite
from src.utils import GameSettings
from src.scenes.scene import Scene
from src.interface.components import Button
from src.core.services import scene_manager, sound_manager, input_manager, resource_manager

class MonsterScene(Scene):
    def __init__(self):
        super().__init__()

    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pg.Surface) -> None:
        pass


