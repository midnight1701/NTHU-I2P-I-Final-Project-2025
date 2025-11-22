elif isinstance(layer, pytmx.TiledTileLayer) and ("bush" in layer.name.lower()):
for x, y, gid in layer:
    if gid != 0 and (x, y) in bush_pos:
        rects.append(pg.Rect(x * GameSettings.TILE_SIZE, y * GameSettings.TILE_SIZE, GameSettings.TILE_SIZE,
                             GameSettings.TILE_SIZE))


bush_pos = [(9, 30), (43, 17), (31, 16), (49, 7), (56, 22), (42, 31)]