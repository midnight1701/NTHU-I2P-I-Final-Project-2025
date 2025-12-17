import pygame as pg
from pygame import K_SPACE
import time

from src.sprites.animation import Animation
from src.scenes.navigation_overlay import NavigationOverlay
from src.interface.components.chat_overlay import ChatOverlay
from src.scenes.scene import Scene
from src.scenes.bag_overlay import BagOverlay
from src.scenes.setting_overlay import SettingOverlay
from src.scenes.shop_overlay import ShopOverlay
from src.core import GameManager, OnlineManager
from src.utils import Logger, PositionCamera, GameSettings, Position, Direction
from src.interface.components import Button
from src.core.services import sound_manager, resource_manager, input_manager, scene_manager
import src.core.services as services
from src.sprites import Sprite
from typing import override, Dict, Tuple

from src.utils.support import EVOLUTION_DICT


# noinspection PyMethodMayBeStatic
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
        self.clock = pg.time.Clock()

        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
            self.chat_overlay = ChatOverlay(self.online_manager.send_chat, self.online_manager.get_recent_chat)
        else:
            self.online_manager = None

        self.sprite_online = Animation("character/ow1.png", ["down", "left", "right", "up"], 4,
                                       (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self.bubble_font = pg.font.Font("assets/fonts/Minecraft.ttf")
        self._chat_bubbles: Dict[int, Tuple[str, str]] = {}
        self._last_chat_id_seen = 0


        self.setting_button = Button(
            "UI/button_setting.png", "UI/button_setting_hover.png",
            1200, 20, 50, 50,
            lambda: self.setting_open_func()
        )

        self.bag_button = Button("UI/button_backpack.png", "UI/button_backpack_hover.png",
                                 1140, 20, 50, 50,
                                 lambda: self.bag_open_func()
                                 )

        self.navigation_button = Button("ingame_ui/core_0.png", "ingame_ui/core_0.png",
                                        1080, 20, 50, 50,
                                        lambda: self.navigate_func())

        # Overlay manager (Yes, it shouldn't be here)
        self.setting_overlay = SettingOverlay()
        self.setting_open = False

        self.bag_overlay = BagOverlay()
        self.bag_open = False

        self.shop_overlay = ShopOverlay()
        self.shop_open = False

        self.navigation = NavigationOverlay(self.pathfinding)
        self.navigate_open = False

        # BFS Path Drawing
        self.enemy_pos = [pg.Rect(a.position.x // GameSettings.TILE_SIZE, a.position.y // GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE) for a in self.game_manager.enemy_trainers[self.game_manager.current_map_key]]
        self.path = None
        self.arrived = False
        self.arrow = pg.transform.scale(resource_manager.get_image("ingame_ui/navigation_mark.png"), (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self.path_surface = None

        # Evolution
        self.evolution = None
        self.base_monster = None
        self.evo_monster = None

    def pathfinding(self, target):
        player_x, player_y = (self.game_manager.player.position.x + 32) // GameSettings.TILE_SIZE, (self.game_manager.player.position.y + 32)// GameSettings.TILE_SIZE
        graph = self.game_manager.current_map.create_graph(self.enemy_pos)
        self.path = self.game_manager.current_map.bfs((player_x, player_y), target, graph)


    def load_option(self, load):
        self.game_manager = load

    def setting_open_func(self):
        self.setting_open = True

    def bag_open_func(self):
        self.bag_open = True

    def shop_open_func(self):
        self.shop_open = True

    def navigate_func(self):
        self.navigate_open = True

    def change_path(self):
        self.path = None

    def check_evolution(self):
        hollow_core, sephira_core = False, False
        for i in self.game_manager.bag._items_data:
            if i["name"] == "Hollow Core" and i["count"] >= 3:
                hollow_core = True
            elif i["name"] == "Sephira Core" and i["count"] >= 1:
                sephira_core = True

        if hollow_core and sephira_core:
            return True

        return False



    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        if self.online_manager:
            self.online_manager.enter()


    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()


    @override
    def update(self, dt: float):
        if self.path is not None:
            if pg.Rect(self.game_manager.player.position.x // GameSettings.TILE_SIZE, self.game_manager.player.position.y // GameSettings.TILE_SIZE, 64, 64).collidepoint(self.path[-1][0], self.path[-1][1]) or input_manager.key_pressed(pg.K_t):
                self.path = None

        if len(self.game_manager.next_map) != 0:
            self.enemy_pos =  [pg.Rect(a.position.x // GameSettings.TILE_SIZE, a.position.y // GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE) for a in self.game_manager.enemy_trainers[self.game_manager.next_map]]

        sound_manager.update()
        # Check if there is assigned next scene
        self.game_manager.try_switch_map()

        # Update player and other data
        if self.game_manager.player:
            self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
        for npc in self.game_manager.current_npc:
            npc.update(dt)


        # Update others
        self.game_manager.bag.update(dt)
        self.setting_button.update(dt)
        self.bag_button.update(dt)
        self.navigation_button.update(dt)

        if self.bag_open:
            self.bag_overlay.update(dt)
            if self.bag_overlay.close:
                self.bag_open = False
                self.bag_overlay.close = False
                services.game_manager.bag.index = 0
                self.game_manager.player.blocked = False

        if self.setting_open:
            if not self.setting_overlay.synchronized:
                self.setting_overlay._slider.synchronize()
                self.setting_overlay.synchronized = True
            self.setting_overlay.update(dt)
            if self.setting_overlay.close:
                self.setting_open = False
                self.setting_overlay.close = False
                self.setting_overlay.synchronized = False
                self.game_manager.player.blocked = False

        if self.shop_open:
            self.shop_overlay.update(dt)
            if self.shop_overlay.close:
                self.shop_open = False
                self.shop_overlay.close = False
                self.shop_overlay.reset()
                self.game_manager.player.blocked = False

        if self.navigate_open:
            self.navigation.update(dt)
            if self.navigation.close:
                self.navigate_open = False
                self.navigation.close = False
                self.game_manager.player.blocked = False

        if self.chat_overlay:
            if input_manager.key_pressed(pg.K_y):
                self.chat_overlay.open()
                self.game_manager.player.blocked = True
            self.chat_overlay.update(dt)
            if not self.chat_overlay.is_open:
                self.game_manager.player.blocked = False


        if self.online_manager:
            try:
                msgs = self.online_manager.get_recent_chat(50)
                max_id = self._last_chat_id_seen
                now = time.monotonic()
                for m in msgs:
                    mid = int(m.get("id", 0))
                    if mid <= self._last_chat_id_seen:
                        continue
                    sender = int(m.get("from", -1))
                    text = str(m.get("text", ""))
                    if sender >= 0 and text:
                        self._chat_bubbles[sender] = (text, now + 5.0)
                    if mid > max_id:
                        max_id = mid
                self._last_chat_id_seen = max_id
            except Exception:
                pass

        if self.game_manager.player is not None and self.online_manager is not None:
            direction = "down"
            if self.game_manager.player.direction == Direction.DOWN:
                direction = "down"
            elif self.game_manager.player.direction == Direction.LEFT:
                direction = "left"
            elif self.game_manager.player.direction == Direction.RIGHT:
                direction = "right"
            elif self.game_manager.player.direction == Direction.UP:
                direction = "up"


            _ = self.online_manager.update(
                self.game_manager.player.position.x,
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name,
                direction
            )

        self.sprite_online.update(dt)

        if self.game_manager.evolution and self.check_evolution():
            if self.game_manager.bag._monsters_dict[self.game_manager.bag.index]["name"] in EVOLUTION_DICT and self.game_manager.bag._monsters_dict[self.game_manager.bag.index]["hp"] > 0:
                for i in self.game_manager.bag._items_data:
                    if i["name"] == "Hollow Core":
                        i["count"] -= 3
                    elif i["name"] == "Sephira Core":
                        i["count"] -= 1

                base = self.game_manager.bag._monsters_dict[self.game_manager.bag.index]
                evo = EVOLUTION_DICT[base["name"]]
                self.game_manager.push_evo_info(base, evo)
                scene_manager.change_scene("evolution")
            else:
                self.game_manager.evolution_cancel()


    def draw_path(self, camera):
        surface = pg.Surface((self.game_manager.current_map.tmxdata.height * GameSettings.TILE_SIZE, self.game_manager.current_map.tmxdata.width * GameSettings.TILE_SIZE), pg.SRCALPHA)
        surface.set_alpha(255)
        for a in self.path:
            rect = pg.Rect(a[0] * GameSettings.TILE_SIZE, a[1] * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE * 0.6, GameSettings.TILE_SIZE * 0.6)
            rect = camera.transform_rect(rect)
            surface.blit(self.arrow, rect)

        return surface


    @override
    def draw(self, screen: pg.Surface):
        if self.game_manager.player:
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            self.game_manager.current_map.draw_minimap(screen)
            self.game_manager.current_map.player_pos_minimap(self.game_manager.player.position, screen)
            if self.path is not None:
                self.path_surface = self.draw_path(camera)
                screen.blit(self.path_surface)
            else:
                self.path_surface = None
            self.game_manager.player.draw(screen, camera)

        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)
        for npc in self.game_manager.current_npc:
            npc.draw(screen, camera)
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for player in list_online:
                if player["map"] == self.game_manager.current_map.path_name:
                    cam = self.game_manager.player.camera
                    pos = cam.transform_position_as_position(Position(player["x"], player["y"]))
                    self.sprite_online.update_pos(pos)
                    if player["direction"] == "left":
                        self.sprite_online.switch("left")
                    elif player["direction"] == "up":
                        self.sprite_online.switch("up")
                    elif player["direction"] == "down":
                        self.sprite_online.switch("down")
                    elif player["direction"] == "right":
                        self.sprite_online.switch("right")
                    self.sprite_online.draw(screen)

        # Draw chat bubble
        if self.chat_overlay:
            self.chat_overlay.draw(screen)
        try:
            self._draw_chat_bubbles(screen, camera)
        except Exception:
            pass

        self.bag_button.draw(screen)
        self.setting_button.draw(screen)
        self.navigation_button.draw(screen)

        if self.bag_open:
            self.bag_overlay.draw(screen)
            self.game_manager.player.blocked = True
        elif self.setting_open:
            self.setting_overlay.draw(screen)
            self.game_manager.player.blocked = True
        elif self.shop_open:
            self.shop_overlay.draw(screen)
            self.game_manager.player.blocked = True
        elif self.navigate_open:
            self.navigation.draw(screen)
            self.game_manager.player.blocked = True


    def _draw_chat_bubbles(self, screen: pg.Surface, camera: PositionCamera) -> None:
        if not self.online_manager:
             return
        # REMOVE EXPIRED BUBBLES
        now = time.monotonic()
        expired = [pid for pid, (_, ts) in self._chat_bubbles.items() if ts <= now]
        for pid in expired:
            self._chat_bubbles.pop(pid)
        if not self._chat_bubbles:
             return

        # DRAW LOCAL PLAYER'S BUBBLE
        local_pid = self.online_manager.player_id
        if self.game_manager.player and local_pid in self._chat_bubbles:
             text, _ = self._chat_bubbles[local_pid]
             self._draw_chat_bubble_for_pos(screen, camera, self.game_manager.player.position, text, self.bubble_font)

        # DRAW OTHER PLAYERS' BUBBLES
        # for pid, (text, _) in self._chat_bubbles.items():
        #     if pid == local_pid:
        #         continue
        #     pos_xy = self._online_last_pos.____(..., ...)
        #     if not pos_xy:
        #         continue
        #     px, py = pos_xy
        #     self._draw_bubble_for_pos(..., ..., ..., ..., ...)

        for pid, (text, _) in self._chat_bubbles.items():
            if pid == local_pid:
                continue
            pos_xy = self.get_online_player_pos(pid)
            if not pos_xy:
                continue
            px, py = pos_xy[0], pos_xy[1]
            pos = Position(px, py)
            self._draw_chat_bubble_for_pos(screen, camera, pos, text, self.bubble_font)



        """
        DRAWING CHAT BUBBLES:
        - When a player sends a chat message, the message should briefly appear above
        that player's character in the world, similar to speech bubbles in RPGs.
        - Each bubble should last only a few seconds before fading or disappearing.
        - Only players currently visible on the map should show bubbles.

         What you need to think about:
            ------------------------------
            1. **Which players currently have messages?**
            You will have a small structure mapping player IDs to the text they sent
            and the time the bubble should disappear.

            2. **How do you know where to place the bubble?**
            The bubble belongs above the player's *current position in the world*.
            The game already tracks each player’s world-space location.
            Convert that into screen-space and draw the bubble there.

            3. **How should bubbles look?**
            You decide. The visual style is up to you:
            - A rounded rectangle, or a simple box.
            - Optional border.
            - A small triangle pointing toward the character's head.
            - Enough padding around the text so it looks readable.

            4. **How do bubbles disappear?**
            Compare the current time to the stored expiration timestamp.
            Remove any bubbles that have expired.

            5. **In what order should bubbles be drawn?**
            Draw them *after* world objects but *before* UI overlays.

        Reminder:
        - For the local player, you can use the self.game_manager.player.position to get the player's position
        - For other players, maybe you can find some way to store other player's last position?
        - For each player with a message, maybe you can call a helper to actually draw a single bubble?
        """

    def _draw_chat_bubble_for_pos(self, screen: pg.Surface, camera: PositionCamera, world_pos: Position, text: str, font: pg.font.Font):
        """
        Steps:
            ------------------
            1. Convert a player’s world position into a location on the screen.
            (Use the camera system provided by the game engine.)

            2. Decide where "above the player" is.
            Typically a little above the sprite’s head.

            3. Measure the rendered text to determine bubble size.
            Add padding around the text.
        """
        bubble_pos = camera.transform_position_as_position(world_pos)
        text = font.render(text, True, (0, 0, 0))
        rect = pg.Rect(bubble_pos.x, bubble_pos.y - 24, text.get_width(), text.get_height())
        rect.centerx = bubble_pos.x + 30
        surface = pg.Surface((text.get_width() + 10, text.get_height()), pg.SRCALPHA)
        surface.set_alpha(255)
        pg.draw.rect(surface, (255, 255, 255), pg.Rect(0, 0, surface.width + 10, surface.height))
        surface.blit(text, pg.Rect(4, 2, surface.width, surface.height))
        screen.blit(surface, rect)

    def get_online_player_pos(self, player_id):
        for i in self.online_manager.list_players:
            if i["id"] == player_id:
                pos = (i["x"], i["y"])
                return pos

        return None

