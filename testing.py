import random

lst = [{ "name": "Pikachu",   "hp": 100,  "max_hp": 100, "atk": 20, "def": 5, "level": 1, "sprite_path": "menu_sprites/menusprite1.png" },
      { "name": "Charizard", "hp": 150, "max_hp": 200, "atk": 20, "def": 5, "level": 36, "sprite_path": "menu_sprites/menusprite2.png" },
      { "name": "Blastoise", "hp": 120, "max_hp": 180, "atk": 20, "def": 5, "level": 32, "sprite_path": "menu_sprites/menusprite3.png" },
      { "name": "Venusaur",  "hp": 90,  "max_hp": 160, "atk": 20, "def": 5, "level": 30, "sprite_path": "menu_sprites/menusprite4.png" },
      { "name": "Gengar",    "hp": 110, "max_hp": 140, "atk": 20, "def": 5, "level": 28, "sprite_path": "menu_sprites/menusprite5.png" },
      { "name": "Dragonite", "hp": 180, "max_hp": 220, "atk": 20, "def": 5, "level": 40, "sprite_path": "menu_sprites/menusprite6.png" },
      { "name": "Viper",     "hp": 120, "max_hp": 160, "atk": 20, "def": 5, "level": 10, "sprite_path": "menu_sprites/menusprite11.png"}]

print(random.choice(lst))