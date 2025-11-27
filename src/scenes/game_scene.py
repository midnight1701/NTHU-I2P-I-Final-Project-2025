import pygame as pg
from src.scenes.scene import Scene
from src.scenes.bag_overlay import BagOverlay
from src.scenes.setting_overlay import SettingOverlay
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.interface.components import Button
from src.core.services import sound_manager
import src.core.services as services
from src.sprites import Sprite
from typing import override

class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    setting_button: Button
    bag_button: Button

    
    def __init__(self):
        super().__init__()
        # Game Manager
        manager = GameManager.load("saves/game0.json")
        if manager is None:
            manager = GameManager.load("saves/game0.json")
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        services.game_manager = self.game_manager

        
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
        else:
            self.online_manager = None
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))

        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            1200, 20, 50, 50,
            lambda: self.setting_open_func()
        )

        self.bag_button = Button("UI/button_backpack.png", "UI/button_backpack_hover.png",
                                 1140, 20, 50, 50,
                                 lambda: self.bag_open_func()
                                 )


        self.setting_overlay = SettingOverlay()
        self.setting_open = False

        self.bag_overlay = BagOverlay()
        self.bag_open = False

    def load_option(self, load):
        self.game_manager = load

    def setting_open_func(self):
        self.setting_open = True

    def bag_open_func(self):
        self.bag_open = True

    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")


    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
        
    @override
    def update(self, dt: float):
        sound_manager.update()
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()
        
        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
            
        # Update others
        self.game_manager.bag.update(dt)
        self.setting_button.update(dt)
        self.bag_button.update(dt)


        if self.bag_open:
            self.bag_overlay.update(dt)
            if self.bag_overlay.close:
                self.bag_open = False
                self.bag_overlay.close = False

        if self.setting_open:
            self.setting_overlay._slider.synchronize()
            self.setting_overlay.update(dt)
            if self.setting_overlay.close:
                self.setting_open = False
                self.setting_overlay.close = False


        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name
            )

        
    @override
    def draw(self, screen: pg.Surface):        
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.player.draw(screen, camera)
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        self.bag_button.draw(screen)
        self.setting_button.draw(screen)

        if self.bag_open:
            self.bag_overlay.draw(screen)
            self.game_manager.player.blocked = True
        elif not self.bag_open and not self.setting_open:
            self.game_manager.player.blocked = False

        if self.setting_open:
            self.setting_overlay.draw(screen)
            self.game_manager.player.blocked = True
        elif not self.setting_open and not self.bag_open:
            self.game_manager.player.blocked = False

        
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    self.sprite_online.draw(screen)
