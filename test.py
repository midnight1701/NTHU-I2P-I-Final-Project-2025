import pygame as pg

for k in range(pg.K_EXCLAIM, pg.K_z + 1):
    if pg.key.get_pressed() == k:
        print(k)