from collections import deque

import pygame as pg
import pytmx

from src.utils import load_tmx, Position, GameSettings, PositionCamera, Teleport

# noinspection PyMethodMayBeStatic
class Map:
    # Map Properties
    path_name: str
    tmxdata: pytmx.TiledMap
    # Position Argument
    spawn: Position
    teleporters: list[Teleport]
    # Rendering Properties
    _surface: pg.Surface
    _collision_map: list[pg.Rect]

    def __init__(self, path: str, tp: list[Teleport], spawn: Position):
        self.path_name = path
        self.tmxdata = load_tmx(path)
        self.spawn = spawn
        self.teleporters = tp
        self.monster_bush = self.bush_generation()

        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        # Prebake the map
        self._surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(self._surface)

        # Prebake minimap
        self._minimap = pg.Surface((pixel_w, pixel_h))
        self._minimap.fill((0, 0, 0))
        self._render_all_layers(self._minimap)
        self._minimap = pg.transform.smoothscale(self._minimap, (280, 280 * (self.tmxdata.height/self.tmxdata.width)))

        # Prebake the collision map
        self._collision_map = self._create_collision_map()
        self.detected = False


    def update(self, dt: float):
        return


    def bfs(self, start, target, graph):
        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            node = queue.popleft()
            if node == target:
                break
            for n in graph.get(node, []):
                if n not in visited:
                    visited.add(n)
                    parent[n] = node
                    queue.append(n)

        path = []
        current = target
        while current:
            path.append(current)
            current = parent.get(current)
        path.reverse()
        if path and path[0] == start:
            return path
        return None


    def create_graph(self, enemy):
        direction = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        graph = set()
        bfs_graph = {}
        for x in range(self.tmxdata.width):
            for y in range(self.tmxdata.height):
                tile = pg.Rect(x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                if any(tile.colliderect(r) for r in self._collision_map) or any(tile.colliderect(r) for r in enemy) or self.check_if_bush_collision(tile):
                    continue

                graph.add((x, y))

        for x, y in graph:
            neighbors = []
            for dx, dy in direction:
                check_x, check_y = x + dx, y + dy
                if (check_x, check_y) in graph:
                    neighbors.append((check_x, check_y))

            bfs_graph[(x, y)] = neighbors

        return bfs_graph


    def player_pos_minimap(self, pos, screen):
        scaled_x = ((pos.x + 16)  / (self.tmxdata.width * GameSettings.TILE_SIZE) * 280)
        scaled_y = (pos.y / (self.tmxdata.height * GameSettings.TILE_SIZE) * 280 * (self.tmxdata.height/self.tmxdata.width))
        pg.draw.rect(screen, (255, 0, 0), pg.Rect(scaled_x, scaled_y, 5, 5))

    def draw_minimap(self, screen):
        rect = pg.Rect(0, 0, 280, 280 * (self.tmxdata.height/self.tmxdata.width))
        screen.blit(self._minimap, rect)
        pg.draw.rect(screen, (0, 0, 0), rect, 3)


    def draw(self, screen: pg.Surface, camera: PositionCamera):
        screen.blit(self._surface, camera.transform_position(Position(0, 0)))

        # Draw the hitboxes collision map
        if GameSettings.DRAW_HITBOXES:
            for rect in self._collision_map:
                pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(rect), 1)

            for rect in self.monster_bush:
                pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(rect), 1)

        
    def check_collision(self, rect: pg.Rect) -> bool:
        return any(rect.colliderect(r) for r in self._collision_map)


    def check_if_bush_collision(self, rect: pg.Rect):
        return any(rect.colliderect(r) for r in self.monster_bush)

        
    def check_teleport(self, pos: Position) -> Teleport | None:
        for t in self.teleporters:
            check = pg.Rect(t.pos.x, t.pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if check.colliderect(pos.x, pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE):
                return t
        return None


    def bush_generation(self):
        bush_rect = []
        bush_pos = [(9, 30), (43, 17), (31, 16), (49, 7), (56, 22), (42, 31), (42, 23), (35, 13), (49, 7)]
        for b in bush_pos:
            bush_rect.append(pg.Rect(b[0] * GameSettings.TILE_SIZE, b[1] * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))

        return bush_rect

    def _render_all_layers(self, target: pg.Surface) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer)
            # elif isinstance(layer, pytmx.TiledImageLayer) and layer.image:
            #     target.blit(layer.image, (layer.x or 0, layer.y or 0))

    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer, scale_factor=None) -> None:
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue

            image = pg.transform.scale(image, (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
            target.blit(image, (x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE))
    
    def _create_collision_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("collision" in layer.name.lower() or "house" in layer.name.lower()):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(pg.Rect(x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE,
                                             GameSettings.TILE_SIZE))

        return rects

    @classmethod
    def from_dict(cls, data: dict) -> "Map":
        tp = [Teleport.from_dict(t) for t in data["teleport"]]
        pos = Position(data["player"]["x"] * GameSettings.TILE_SIZE, data["player"]["y"] * GameSettings.TILE_SIZE)
        return cls(data["path"], tp, pos)

    def to_dict(self):
        return {
            "path": self.path_name,
            "teleport": [t.to_dict() for t in self.teleporters],
            "player": {
                "x": self.spawn.x // GameSettings.TILE_SIZE,
                "y": self.spawn.y // GameSettings.TILE_SIZE,
            }
        }
