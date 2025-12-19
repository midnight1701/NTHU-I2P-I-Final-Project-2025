import pygame as pg
import math
from src.core.managers import resource_manager
from src.core.services import scene_manager, input_manager, sound_manager
from src.scenes.scene import Scene
from src.utils import GameSettings
from src.utils.support import MONSTER_PATH, EVOLUTION_DICT
import src.core.services as services


def get_animation_image(path, ally=False):
    animation_sprite = []
    sprite = pg.image.load(path)
    for x in range(0, 289, 96):
        sub_rect = pg.Rect(x, 0, 96, 96)
        sub_img = sprite.subsurface(sub_rect)
        if ally:
            sub_img = pg.transform.flip(sub_img, flip_x=True, flip_y=False)
        animation_sprite.append(sub_img)

    return animation_sprite[0]


# noinspection PyMethodMayBeStatic
class EvolutionScene(Scene):
    def __init__(self):
        super().__init__()
        # Animation state
        self.animation_state = "base"
        self.timer = 0
        self.scale = 1
        self.flash_alpha = 0
        self.finished = False

        self.width, self.height = GameSettings.SCREEN_WIDTH, GameSettings.SCREEN_HEIGHT
        self.surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
        self.surface.fill((0, 0, 0, 30))

        self.base, self.evolved = None, None
        self.base_img, self.evo_img = None, None

        self.fade = False

    def enter(self):
        sound_manager.play_bgm("RBY 116 Evolution.ogg")
        self.base, self.evolved = services.game_manager.base_monster, services.game_manager.evo_monster
        self.base_img = pg.transform.scale(get_animation_image(MONSTER_PATH[self.base["name"]]["animation_path"]), (300, 300))
        self.evo_img = pg.transform.scale(get_animation_image(MONSTER_PATH[self.evolved["name"]]["animation_path"]), (300, 300))
        scene_manager.evolution_check = True

    def exit(self):
        self.base, self.evolved, self.base_img, self.evo_img = None, None, None, None
        self.animation_state = "base"
        self.flash_alpha = 0
        self.timer = 0
        scene_manager.evolution_check = False
        self.fade = False
        self.finished = False



    def draw_centered(self, surface, img, scale):
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        scaled = pg.transform.smoothscale(img, (w, h))
        rect = scaled.get_rect(center=(self.width / 2, self.height / 2))
        surface.blit(scaled, rect)


    def update(self, dt):
        self.timer += dt

        if self.animation_state == "base":
            if self.timer > 8.0:
                self.animation_state = "flash"
                self.timer = 0

        elif self.animation_state == "flash":
            self.flash_alpha = self.flash_alpha + 10
            if self.flash_alpha >= 255:
                self.flash_alpha = 255
                self.animation_state = "evolved"
                self.timer = 0

        elif self.animation_state == "evolved":
            self.flash_alpha = self.flash_alpha - 10
            if self.flash_alpha <= 0:
                self.finished = True
                self.animation_state = None

        if self.finished:
            for i in range(len(services.game_manager.bag._monsters_data)):
                if self.base is not None and services.game_manager.bag._monsters_data[i]["name"] == self.base["name"]:
                    services.game_manager.bag.change_monster(i, self.evolved)
                    break

        if self.finished and input_manager.key_pressed(pg.K_RETURN):
            scene_manager.change_scene("game")
            services.game_manager.evolution_cancel()


    def draw(self, screen):
        screen.blit(self.surface, (0, 0))
        self.fade = True

        if self.animation_state == "base":
            scale = 1.0 + 0.05 * math.cos(self.timer * 3)
            self.draw_centered(screen, self.base_img, scale)


        elif self.animation_state == "flash":
            self.draw_centered(screen, self.base_img, 1.0)
            flash_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(self.flash_alpha)
            screen.blit(flash_surface, (0, 0))


        elif self.animation_state == "evolved" and not self.finished:
            self.draw_centered(screen, self.evo_img, 1)
            flash_surface = pg.Surface((self.width, self.height), pg.SRCALPHA)
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(self.flash_alpha)
            screen.blit(flash_surface, (0, 0))

        else:
            scale = 1.0 + 0.05 * math.cos(self.timer * 3)
            self.draw_centered(screen, self.evo_img, scale)








