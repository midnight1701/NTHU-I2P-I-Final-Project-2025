        template = resource_manager.get_image("UI/UI_Flat_Banner04a.png")
        self.ally_template = pg.transform.scale(template, (300, 90))
        self.enemy_template = pg.transform.scale(template, (300, 90))
        self.ally_info_rect = pg.Rect(self.background.rect.topleft[0] + 10, self.background.rect.topleft[1] + 10, 300, 90)
        self.enemy_info_rect = pg.Rect(self.background.rect.topright[0] - 300 - 10, self.background.rect.topright[1] + 10, 300, 90)

        # Display ally monster info
        self.ally_info_img = resource_manager.get_image(MONSTER_PATH[self.ally_monster["name"]]["sprite_path"])
        self.ally_info_img = pg.transform.scale(self.ally_info_img, (75, 75))
        self.ally_info_img_rect = pg.Rect(self.ally_info_rect.topleft[0] + 12, self.ally_info_rect.topleft[1] - 3, 75, 75)
        self.ally_name = self.alt_font.render(self.battle.player["name"], True, (0, 0, 0))
        self.ally_name_rect = pg.Rect(self.ally_info_img_rect.topright[0] + 10, self.ally_info_img_rect.topright[1] + 22, 95, 25)
        self.ally_level = self.alt_font.render(f"Lv {self.battle.player["level"]}", True, (0, 0, 0))
        self.ally_level_rect = pg.Rect(self.ally_name_rect.topright[0] + 30, self.ally_name_rect.topright[1], 59, 25)
        self.hp_rect = pg.Rect(self.ally_name_rect.bottomleft[0], self.ally_name_rect.bottomright[1] + 8, 110, 15)
        self.red_hp = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01c.png"), (110, 15))
        self.green_hp = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01a.png"), ((110 * (self.battle.player["hp"] / self.battle.player["max_hp"])), 15))
        self.hp_text = self.alt_font.render(f"{self.battle.player["hp"]}/{self.battle.player["max_hp"]}", True,(0, 0, 0))
        self.hp_text_rect = pg.Rect(self.ally_level_rect.bottomleft[0], self.hp_rect.topright[1], 91, 25)


        # Display enemy monster info
        self.enemy_info_img = resource_manager.get_image(MONSTER_PATH[self.enemy_monster["name"]]["sprite_path"])
        self.enemy_info_img = pg.transform.scale(self.enemy_info_img, (75, 75))
        self.enemy_info_img_rect = pg.Rect(self.enemy_info_rect.topleft[0] + 12, self.enemy_info_rect[1] - 3, 75, 75)
        self.enemy_name = self.alt_font.render(self.battle.enemy["name"], True, (0, 0, 0))
        self.enemy_name_rect = pg.Rect(self.enemy_info_img_rect.topright[0] + 10, self.enemy_info_img_rect.topright[1] + 22, 95, 25)
        self.enemy_level = self.alt_font.render(f"Lv {self.battle.enemy["level"]}", True, (0, 0, 0))
        self.enemy_level_rect = pg.Rect(self.enemy_name_rect.topright[0] + 30, self.enemy_name_rect.topright[1], 59, 25)
        self.enemy_hp_rect = pg.Rect(self.enemy_name_rect.bottomleft[0], self.enemy_name_rect.bottomright[1] + 8 , 110, 15)
        self.enemy_hp_text = self.alt_font.render(f"{self.battle.enemy["hp"]}/{self.battle.enemy["max_hp"]}", True,(0, 0, 0))
        self.enemy_green_hp = pg.transform.scale(resource_manager.get_image("UI/UI_Flat_BarFill01a.png"), ((110 * (self.battle.enemy["hp"] / self.battle.enemy["max_hp"])), 15))
        self.enemy_hp_text_rect = pg.Rect(self.enemy_level_rect.bottomleft[0], self.enemy_hp_rect.topright[1], 91, 25)

        self.enemy_monster = random.choice(services.game_manager.bag._game_monsters)
        self.enemy_monster_ani = AnimatedMonster(get_animation_image(MONSTER_PATH[self.enemy_monster["name"]]["animation_path"]))

        self.ally_monster = self.battle.state.return_monster()
        self.ally_monster_ani = AnimatedMonster(get_animation_image(MONSTER_PATH[self.ally_monster["name"]]["animation_path"], True))

        if isinstance(self.battle.state, BattleSetup):
                if self.battle.state.enemy_setup:
                        self.enemy_monster_ani.draw(screen, self.dt, self.enemy_monster_rect, 300)
                if self.battle.state.ally_setup:
                        self.ally_monster_ani.draw(screen, self.dt, self.ally_monster_rect, 300)
                        self.displayed = True
        if self.displayed:
                self.enemy_monster_ani.draw(screen, self.dt, self.enemy_monster_rect, 300)
                self.ally_monster_ani.draw(screen, self.dt, self.ally_monster_rect, 300)
