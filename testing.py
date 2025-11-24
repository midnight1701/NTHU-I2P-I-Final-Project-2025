import pygame as pg

pg.font.init()

f = pg.font.Font("assets/fonts/PixeloidSans.ttf", size=20)
text = f.render(f"50/160", True, (0, 0, 0))
print(text.get_width(), text.get_height())