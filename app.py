"""
🌾 FARMVILLE ULTIMATE — BUILDING UPGRADES EDITION
==================================================
Tiered buildings with visual progression and powerful upgrades.

NEW FEATURES
------------
  • 4-Tier System     — Basic → Improved → Advanced → Master
  • Visual Progression — tier-colored borders, stars, size growth
  • Scaling Bonuses   — capacity, production, defense, HP per tier
  • Upgrade Tool      — dedicated tool (key 9) to upgrade buildings
  • Upgrade Panel     — click building to see upgrade options
  • Master Buildings  — tier 4 legendary versions with unique effects
  • Upgrade Effects   — particles, glow, and animations on upgrade
"""

import pygame, sys, time, random, json, os, math

# =============================================================================
# §1. CONFIG
# =============================================================================
TILE = 80
WORLD_COLS, WORLD_ROWS = 32, 20
FARM_X, FARM_Y = 6, 4
FARM_COLS, FARM_ROWS = 20, 12
LEFT_PANEL = 150
TOP_BAR = 60
BOTTOM_BAR = 150
SCREEN_W, SCREEN_H = 1280, 800
FPS = 60
SAVE_FILE = "farm_save.json"
EMOJI_FONT_NAMES = ["seguoemj","Segoe UI Emoji","Apple Color Emoji","Noto Color Emoji","Symbola"]

# =============================================================================
# §2. BIOMES
# =============================================================================
class Biome:
    PLAINS="plains"; FOREST="forest"; DESERT="desert"
    SWAMP="swamp"; TUNDRA="tundra"; MOUNTAINS="mountains"

BIOME_INFO = {
    Biome.PLAINS:    {"name":"Plains","emoji":"🌾","color":(110,175,85),"unlock":1,"grow_mod":1.0},
    Biome.FOREST:    {"name":"Forest","emoji":"🌲","color":(60,110,50),"unlock":3,"grow_mod":0.85},
    Biome.DESERT:    {"name":"Desert","emoji":"🏜️","color":(220,190,120),"unlock":6,"grow_mod":1.3},
    Biome.SWAMP:     {"name":"Swamp","emoji":"🌿","color":(80,120,90),"unlock":9,"grow_mod":0.9},
    Biome.TUNDRA:    {"name":"Tundra","emoji":"❄️","color":(180,200,210),"unlock":12,"grow_mod":1.4},
    Biome.MOUNTAINS: {"name":"Mountains","emoji":"⛰️","color":(140,140,140),"unlock":15,"grow_mod":1.2},
}

# =============================================================================
# §3. BUILDING TIERS — the heart of the upgrade system
# =============================================================================
BUILDING_TIERS = {
    1: {
        "name": "Basic",
        "cost_mult": 1.0,
        "cap_mult": 1.0,
        "prod_mult": 1.0,
        "def_mult": 1.0,
        "hp_mult": 1.0,
        "size": 1,
        "lvl_req": 1,
        "border_color": (180, 180, 180),  # gray
        "star_count": 0,
        "glow": False,
        "emoji_scale": 1.0,
    },
    2: {
        "name": "Improved",
        "cost_mult": 2.5,
        "cap_mult": 1.5,
        "prod_mult": 1.4,
        "def_mult": 1.3,
        "hp_mult": 1.5,
        "size": 1,
        "lvl_req": 5,
        "border_color": (180, 220, 120),  # green
        "star_count": 1,
        "glow": False,
        "emoji_scale": 1.1,
    },
    3: {
        "name": "Advanced",
        "cost_mult": 6.0,
        "cap_mult": 2.0,
        "prod_mult": 1.8,
        "def_mult": 1.6,
        "hp_mult": 2.0,
        "size": 2,
        "lvl_req": 10,
        "border_color": (100, 180, 255),  # blue
        "star_count": 2,
        "glow": True,
        "glow_color": (100, 180, 255, 60),
        "emoji_scale": 1.25,
    },
    4: {
        "name": "Master",
        "cost_mult": 15.0,
        "cap_mult": 3.0,
        "prod_mult": 2.5,
        "def_mult": 2.2,
        "hp_mult": 3.0,
        "size": 2,
        "lvl_req": 18,
        "border_color": (255, 200, 50),  # gold
        "star_count": 3,
        "glow": True,
        "glow_color": (255, 215, 0, 80),
        "emoji_scale": 1.4,
        "master": True,
    },
}

# =============================================================================
# §4. BUILDINGS DATA — base stats (tier 1)
# =============================================================================
BUILDINGS = {
    "chicken_coop": {
        "name": "Chicken Coop", "emoji": "🐔", "cost": 100,
        "capacity": 6, "hp": 100,
        "accepts": ["fluffy_bunny","white_cat","meadow_lark","prairie_dog","tiny_mouse"],
        "produces": [("egg", 20, 15)],
        "desc": "Houses small animals, produces eggs",
        "unlock": 1,
        "master_emoji": "🏯",  # tier 4 visual
    },
    "cow_pen": {
        "name": "Cow Pen", "emoji": "🐄", "cost": 250,
        "capacity": 4, "hp": 200,
        "accepts": ["gentle_horse","brown_bear","spotted_fawn"],
        "produces": [("milk", 30, 30)],
        "desc": "Houses large animals, produces milk",
        "unlock": 3,
        "master_emoji": "🏰",
    },
    "pig_pen": {
        "name": "Pig Pen", "emoji": "🐖", "cost": 200,
        "capacity": 5, "hp": 150,
        "accepts": ["red_fox","golden_retriever"],
        "produces": [("truffle", 40, 40)],
        "desc": "Foragers find truffles",
        "unlock": 4,
        "master_emoji": "🏛️",
    },
    "sheep_pasture": {
        "name": "Sheep Pasture", "emoji": "🐑", "cost": 300,
        "capacity": 6, "hp": 180,
        "accepts": ["moss_sloth","berry_hedgehog","arctic_hare","snow_fox"],
        "produces": [("wool", 35, 35)],
        "desc": "Fluffy animals produce wool",
        "unlock": 5,
        "master_emoji": "🏯",
    },
    "stable": {
        "name": "Stable", "emoji": "🐴", "cost": 400,
        "capacity": 3, "hp": 250,
        "accepts": ["gentle_horse","noble_stag","dune_rider","rock_goat"],
        "produces": [("leather", 50, 60)],
        "desc": "Houses noble steeds",
        "unlock": 7,
        "master_emoji": "🏰",
    },
    "kennel": {
        "name": "Kennel", "emoji": "🐕", "cost": 180,
        "capacity": 4, "hp": 150,
        "accepts": ["golden_retriever","red_fox","snow_fox","desert_fennec"],
        "produces": [],
        "defense": 10,
        "desc": "Guard dogs defend the farm",
        "unlock": 2,
        "master_emoji": "🏯",
    },
    "aviary": {
        "name": "Aviary", "emoji": "🦜", "cost": 350,
        "capacity": 8, "hp": 120,
        "accepts": ["wise_owl","green_parrot","snow_owl","thunder_hawk","solar_eagle","meadow_lark"],
        "produces": [("feather", 25, 20)],
        "desc": "Houses birds, produces feathers",
        "unlock": 6,
        "master_emoji": "🏰",
    },
    "dragon_roost": {
        "name": "Dragon Roost", "emoji": "🐉", "cost": 1000,
        "capacity": 2, "hp": 500,
        "accepts": ["crystal_dragon","ice_dragon","swamp_dragon","sun_phoenix","cloud_phoenix"],
        "produces": [("dragon_scale", 120, 200)],
        "defense": 50,
        "desc": "Legendary lair, powerful defense",
        "unlock": 15,
        "master_emoji": "🏰",
    },
    "watchtower": {
        "name": "Watch Tower", "emoji": "🗼", "cost": 500,
        "capacity": 0, "hp": 300,
        "accepts": [],
        "produces": [],
        "defense": 25,
        "range": 3,
        "desc": "Attacks nearby monsters",
        "unlock": 8,
        "master_emoji": "🏯",
    },
    "stone_wall": {
        "name": "Stone Wall", "emoji": "🧱", "cost": 50,
        "capacity": 0, "hp": 400,
        "accepts": [],
        "produces": [],
        "defense": 0,
        "block": True,
        "desc": "Blocks monster movement",
        "unlock": 1,
        "master_emoji": "🏰",
    },
    "windmill": {
        "name": "Windmill", "emoji": "🌬️", "cost": 600,
        "capacity": 0, "hp": 200,
        "accepts": [],
        "produces": [("flour", 40, 50)],
        "desc": "Processes grain into flour",
        "unlock": 9,
        "master_emoji": "🏯",
    },
    "alchemist_lab": {
        "name": "Alchemist Lab", "emoji": "⚗️", "cost": 800,
        "capacity": 0, "hp": 250,
        "accepts": [],
        "produces": [("potion", 60, 100)],
        "defense": 15,
        "desc": "Brews potions, minor defense",
        "unlock": 12,
        "master_emoji": "🏰",
    },
}

# =============================================================================
# §5. PLANT GENERATOR (120+ plants)
# =============================================================================
class PlantGenerator:
    TEMPLATES = {
        Biome.PLAINS: [("sun","flower","🌱","🌿","🌻"),("moon","bloom","🌱","🌿","🌼"),
            ("star","petal","🌱","🌿","⭐"),("gold","wheat","🌱","🌿","🌾"),
            ("red","corn","🌱","🌿","🌽"),("sweet","carrot","🌱","🌿","🥕"),
            ("wild","pumpkin","🌱","🌿","🎃"),("fire","tomato","🌱","🌿","🍅"),
            ("dew","berry","🌱","🌿","🫐"),("honey","melon","🌱","🌿","🍈"),
            ("silver","oat","🌱","🌿","🌾"),("copper","rye","🌱","🌿","🌾"),
            ("pearl","rice","🌱","🌿","🍚"),("amber","barley","🌱","🌿","🌾"),
            ("jade","pea","🌱","🌿","🟢"),("ruby","radish","🌱","🌿","🔴"),
            ("opal","onion","🌱","🌿","🧅"),("topaz","turnip","🌱","🌿","🟡"),
            ("silk","soybean","🌱","🌿","🫘"),("velvet","squash","🌱","🌿","🎃")],
        Biome.FOREST: [("shadow","mushroom","🌱","🍄","🍄"),("ghost","truffle","🌱","🍄","🍄"),
            ("ancient","ginseng","🌱","🌿","🌿"),("mystic","herb","🌱","🌿","🌿"),
            ("dark","blueberry","🌱","🌿","🫐"),("thorn","blackberry","🌱","🌿","🫐"),
            ("moss","fern","🌱","🌿","🌿"),("bark","lichen","🌱","🌿","🌿"),
            ("root","ginger","🌱","🌿","🌿"),("vine","grape","🌱","🌿","🍇"),
            ("owl","nut","🌱","🌿","🌰"),("bear","berry","🌱","🌿","🫐"),
            ("wolf","fang","🌱","🌿","🌿"),("deer","clover","🌱","🌿","🍀"),
            ("fox","glove","🌱","🌿","🌸"),("raven","seed","🌱","🌿","🖤"),
            ("pine","cone","🌱","🌿","🌲"),("oak","acorn","🌱","🌿","🌰"),
            ("maple","syrup","🌱","🌿","🍁"),("birch","bark","🌱","🌿","🪵")],
        Biome.DESERT: [("sand","cactus","🌱","🌵","🌵"),("dune","aloe","🌱","🌿","🌿"),
            ("heat","pepper","🌱","🌶️","🌶️"),("dust","sage","🌱","🌿","🌿"),
            ("sun","palm","🌱","🌴","🌴"),("fire","agave","🌱","🌿","🌿"),
            ("dry","reed","🌱","🌿","🌿"),("thorn","rose","🌱","🌹","🌹"),
            ("gold","date","🌱","🌴","🌴"),("copper","fig","🌱","🌿","🌿"),
            ("mirage","lily","🌱","🌸","🌸"),("storm","succulent","🌱","🌿","🌿"),
            ("flame","poppy","🌱","🌺","🌺"),("scorch","vine","🌱","🌿","🌿"),
            ("blaze","bloom","🌱","🌼","🌼"),("ember","root","🌱","🌿","🌿"),
            ("solar","fruit","🌱","🌿","🍊"),("desert","melon","🌱","🌿","🍉"),
            ("prickly","pear","🌱","🌵","🌵"),("arid","herb","🌱","🌿","🌿")],
        Biome.SWAMP: [("bog","moss","🌱","🌿","🌿"),("murk","lotus","🌱","🌿","🪷"),
            ("slime","algae","🌱","🌿","🟢"),("mist","lily","🌱","🌸","🌸"),
            ("rot","cap","🌱","🍄","🍄"),("swamp","reed","🌱","🌿","🌿"),
            ("dark","water","🌱","🌿","💧"),("toxic","spore","🌱","🍄","🍄"),
            ("green","sludge","🌱","🌿","🌿"),("wet","fern","🌱","🌿","🌿"),
            ("frog","leaf","🌱","🌿","🍃"),("snake","root","🌱","🌿","🌿"),
            ("gator","moss","🌱","🌿","🌿"),("heron","grass","🌱","🌿","🌿"),
            ("catfish","weed","🌱","🌿","🌿"),("turtle","vine","🌱","🌿","🌿"),
            ("cypress","knee","🌱","🌿","🌲"),("mangrove","root","🌱","🌿","🌳"),
            ("cattail","fluff","🌱","🌿","🌾"),("duck","weed","🌱","🌿","🌿")],
        Biome.TUNDRA: [("ice","flower","🌱","❄️","❄️"),("frost","moss","🌱","🌿","🌿"),
            ("snow","berry","🌱","🌿","🫐"),("blizzard","bloom","🌱","❄️","❄️"),
            ("polar","lichen","🌱","🌿","🌿"),("arctic","willow","🌱","🌿","🌿"),
            ("frozen","root","🌱","🌿","🌿"),("crystal","petal","🌱","💎","💎"),
            ("glacier","herb","🌱","🌿","🌿"),("aurora","blossom","🌱","🌸","🌸"),
            ("white","poppy","🌱","🌼","🌼"),("cold","snap","🌱","🌿","🌿"),
            ("hail","seed","🌱","🌿","🌿"),("sleet","grass","🌱","🌿","🌿"),
            ("tundra","rose","🌱","🌹","🌹"),("penguin","moss","🌱","🌿","🌿"),
            ("seal","wort","🌱","🌿","🌿"),("walrus","kelp","🌱","🌿","🌿"),
            ("yeti","fur","🌱","🌿","🌿"),("northern","light","🌱","✨","✨")],
        Biome.MOUNTAINS: [("stone","crop","🌱","🌿","🌿"),("rock","rose","🌱","🌹","🌹"),
            ("peak","lily","🌱","🌸","🌸"),("cliff","herb","🌱","🌿","🌿"),
            ("alpine","edelweiss","🌱","🌸","🌸"),("summit","bloom","🌱","🌼","🌼"),
            ("crystal","flower","🌱","💎","💎"),("gem","orchid","🌱","🌺","🌺"),
            ("diamond","petal","🌱","💎","💎"),("ruby","thorn","🌱","🌹","🌹"),
            ("sapphire","vine","🌱","🌿","🌿"),("emerald","moss","🌱","🌿","🌿"),
            ("granite","root","🌱","🌿","🌿"),("marble","blossom","🌱","🌸","🌸"),
            ("obsidian","spore","🌱","🍄","🍄"),("quartz","crystal","🌱","💎","💎"),
            ("eagle","feather","🌱","🌿","🪶"),("goat","grass","🌱","🌿","🌿"),
            ("snow","leopard","🌱","🌿","🌿"),("thunder","bolt","🌱","⚡","⚡")],
    }
    def __init__(self):
        self.plants = {}
        for biome, tpls in self.TEMPLATES.items():
            for i,(p,s,e1,e2,e3) in enumerate(tpls):
                name = f"{p}_{s}"
                lvl = max(1, BIOME_INFO[biome]["unlock"] + i//5)
                bc = 10+i*5+lvl*3
                self.plants[name] = {"biome":biome,"cost":bc,"sell":bc*3,"time":8+lvl*3+i%5*2,
                    "xp":5+lvl*2,"lvl":lvl,"emojis":[e1,e2,e3],
                    "rarity":"common" if i<8 else "uncommon" if i<14 else "rare" if i<18 else "legendary",
                    "display":f"{p.title()} {s.title()}"}
    def get_plants_for_biome(self, biome, max_level):
        return {n:d for n,d in self.plants.items() if d["biome"]==biome and d["lvl"]<=max_level}

# =============================================================================
# §6. CREATURE GENERATOR (120+ creatures)
# =============================================================================
class CreatureGenerator:
    TEMPLATES = {
        Biome.PLAINS: [("fluffy","bunny","🐰","tame",20,2,15),("golden","retriever","🐕","tame",40,8,30),
            ("spotted","fawn","🦌","tame",25,3,20),("tiny","mouse","🐭","tame",8,1,5),
            ("red","fox","🦊","tame",30,6,25),("gentle","horse","🐴","tame",60,10,50),
            ("white","cat","🐱","tame",15,4,12),("brown","bear","🐻","tame",80,15,60),
            ("wild","boar","🐗","monster",50,12,35),("angry","bull","🐂","monster",70,18,45),
            ("sneaky","rat","🐀","monster",15,5,10),("giant","spider","🕷️","monster",35,10,25),
            ("venomous","snake","🐍","monster",25,14,20),("rabid","wolf","🐺","monster",45,16,30),
            ("plague","crow","🐦‍⬛","monster",20,8,15),("dust","devil","🌪️","monster",55,13,40),
            ("shadow","coyote","🐺","monster",40,11,28),("thunder","hawk","🦅","tame",35,9,35),
            ("prairie","dog","🐕","tame",12,2,8),("meadow","lark","🐦","tame",10,1,6)],
        Biome.FOREST: [("wise","owl","🦉","tame",20,5,20),("green","parrot","🦜","tame",15,3,18),
            ("noble","stag","🦌","tame",50,8,40),("tiny","fairy","🧚","tame",10,2,30),
            ("ancient","treant","🌳","tame",100,12,80),("mushroom","sprite","🍄","tame",12,3,15),
            ("forest","unicorn","🦄","tame",70,14,100),("woodland","elf","🧝","tame",45,10,50),
            ("dark","goblin","👺","monster",30,10,20),("cursed","wraith","👻","monster",40,15,35),
            ("poison","toad","🐸","monster",25,8,15),("giant","centipede","🐛","monster",35,12,25),
            ("shadow","panther","🐆","monster",55,18,40),("blood","bat","🦇","monster",20,9,12),
            ("bone","skeleton","💀","monster",45,14,30),("swamp","troll","👹","monster",80,20,55),
            ("rot","zombie","🧟","monster",60,16,35),("bark","golem","🗿","monster",90,10,50),
            ("moss","sloth","🦥","tame",30,2,10),("berry","hedgehog","🦔","tame",18,4,14)],
        Biome.DESERT: [("sand","camel","🐪","tame",60,6,35),("desert","fennec","🦊","tame",15,4,20),
            ("golden","scarab","🪲","tame",10,2,25),("sun","phoenix","🔥","tame",80,20,120),
            ("dune","rider","🏇","tame",50,12,45),("oasis","turtle","🐢","tame",40,3,18),
            ("mirage","djinn","🧞","tame",70,16,90),("palm","gecko","🦎","tame",8,1,5),
            ("sand","wyrm","🐉","monster",100,22,70),("dust","golem","🗿","monster",85,15,50),
            ("heat","serpent","🐍","monster",45,18,35),("scorch","demon","👿","monster",75,20,55),
            ("venom","scorpion","🦂","monster",30,14,25),("sand","storm","🌪️","monster",60,12,40),
            ("mummy","king","🧟","monster",90,18,65),("desert","bandit","🥷","monster",40,13,30),
            ("fire","ant","🐜","monster",20,8,12),("thorn","lizard","🦎","monster",25,10,18),
            ("solar","eagle","🦅","tame",40,11,40),("dune","hare","🐇","tame",12,2,8)],
        Biome.SWAMP: [("swamp","frog","🐸","tame",15,3,10),("mud","turtle","🐢","tame",35,4,20),
            ("green","heron","🦢","tame",25,6,22),("bog","otter","🦦","tame",30,7,25),
            ("mist","spirit","👻","tame",20,5,30),("cypress","snake","🐍","tame",20,5,15),
            ("swamp","dragon","🐉","tame",90,18,100),("lily","fairy","🧚","tame",12,3,20),
            ("toxic","slime","🟢","monster",50,10,25),("rot","ghoul","🧟","monster",55,14,30),
            ("swamp","hydra","🐍","monster",100,20,70),("mud","golem","🗿","monster",80,12,45),
            ("bog","witch","🧙‍♀️","monster",45,16,35),("plague","leech","🪱","monster",20,8,10),
            ("dark","caiman","🐊","monster",70,18,50),("mist","wraith","👻","monster",40,14,30),
            ("swamp","thing","👾","monster",85,16,55),("mud","crab","🦀","monster",30,9,18),
            ("reed","duck","🦆","tame",10,1,6),("marsh","wren","🐦","tame",8,1,5)],
        Biome.TUNDRA: [("snow","fox","🦊","tame",25,5,20),("ice","penguin","🐧","tame",20,3,15),
            ("frost","wolf","🐺","tame",50,12,45),("polar","bear","🐻‍❄️","tame",90,18,80),
            ("arctic","hare","🐇","tame",12,2,8),("snow","owl","🦉","tame",22,6,18),
            ("ice","dragon","🐉","tame",100,22,120),("frost","giant","🧊","tame",120,15,90),
            ("blizzard","yeti","👹","monster",110,20,75),("ice","wraith","👻","monster",50,16,40),
            ("frost","spider","🕷️","monster",35,12,25),("snow","serpent","🐍","monster",60,14,35),
            ("frozen","skeleton","💀","monster",55,15,30),("aurora","phantom","👻","monster",45,18,45),
            ("hail","golem","🗿","monster",95,12,55),("tundra","mammoth","🦣","monster",130,20,80),
            ("ice","lich","💀","monster",70,22,60),("frost","banshee","👻","monster",40,17,35),
            ("snow","seal","🦭","tame",30,4,12),("arctic","tern","🐦","tame",10,1,6)],
        Biome.MOUNTAINS: [("rock","goat","🐐","tame",35,6,20),("eagle","king","🦅","tame",45,14,50),
            ("mountain","lion","🦁","tame",70,16,60),("crystal","dragon","🐉","tame",120,25,150),
            ("stone","golem","🗿","tame",100,10,70),("cloud","phoenix","🔥","tame",80,20,100),
            ("summit","griffin","🦅","tame",90,18,90),("peak","yeti","👹","tame",110,14,80),
            ("thunder","titan","⚡","monster",150,25,100),("lava","dragon","🐉","monster",130,28,90),
            ("rock","troll","👹","monster",90,18,50),("storm","giant","🌩️","monster",120,20,70),
            ("cave","wyrm","🐍","monster",80,16,45),("obsidian","golem","🗿","monster",110,14,60),
            ("diamond","skeleton","💀","monster",70,20,55),("mountain","demon","👿","monster",100,22,65),
            ("cliff","harpy","🦅","monster",50,15,35),("summit","wraith","👻","monster",60,18,45),
            ("alpine","marmot","🐿️","tame",15,2,8),("peak","condor","🦅","tame",40,10,35)],
    }
    def __init__(self):
        self.creatures = {}
        for biome, tpls in self.TEMPLATES.items():
            for i,(p,s,e,t,hp,atk,val) in enumerate(tpls):
                name = f"{p}_{s}"
                lvl = max(1, BIOME_INFO[biome]["unlock"]+i//4)
                sc = 1+(lvl-1)*0.15
                self.creatures[name] = {"biome":biome,"type":t,"emoji":e,
                    "hp":int(hp*sc),"max_hp":int(hp*sc),"atk":int(atk*sc),"value":int(val*sc),
                    "lvl":lvl,"display":f"{p.title()} {s.title()}",
                    "tame_chance":max(0.1,0.8-lvl*0.03) if t=="tame" else 0}
    def spawn_random(self, biome, player_level):
        avail = [n for n,d in self.creatures.items() if d["biome"]==biome and d["lvl"]<=player_level+3]
        if not avail: return None, None
        name = random.choice(avail)
        data = self.creatures[name].copy(); data["hp"] = data["max_hp"]
        return name, data

# =============================================================================
# §7. UTILITIES
# =============================================================================
class Camera:
    def __init__(self, ww, wh, vp):
        self.world_w,self.world_h = ww,wh; self.viewport = vp
        self.x=self.y=0.0; self.zoom=self.tx=self.ty=self.tz=1.0
        self.min_zoom,self.max_zoom = 0.3,2.0
        self.smooth,self.edge_speed,self.edge_margin = 10.0,400,20
        self.tx=(ww-vp.width)/2; self.ty=(wh-vp.height)/2
        self.x,self.y = self.tx,self.ty
    def world_to_screen(self, wx, wy):
        return ((wx-self.x)*self.zoom+self.viewport.x, (wy-self.y)*self.zoom+self.viewport.y)
    def screen_to_world(self, sx, sy):
        return ((sx-self.viewport.x)/self.zoom+self.x, (sy-self.viewport.y)/self.zoom+self.y)
    def scaled_size(self, s): return int(s*self.zoom)
    def visible_rect(self):
        return pygame.Rect(self.x, self.y, self.viewport.width/self.zoom, self.viewport.height/self.zoom)
    def zoom_at(self, sx, sy, d):
        wx,wy = self.screen_to_world(sx,sy)
        self.tz = max(self.min_zoom, min(self.max_zoom, self.tz+d))
        self.tx = wx-(sx-self.viewport.x)/self.tz; self.ty = wy-(sy-self.viewport.y)/self.tz
        self._clamp()
    def pan(self, dx, dy): self.tx+=dx; self.ty+=dy; self._clamp()
    def center_on(self, wx, wy):
        vw=self.viewport.width/self.zoom; vh=self.viewport.height/self.zoom
        self.tx=wx-vw/2; self.ty=wy-vh/2; self._clamp()
    def _clamp(self):
        vw=self.viewport.width/self.zoom; vh=self.viewport.height/self.zoom
        self.tx=max(0,min(max(0,self.world_w-vw),self.tx))
        self.ty=max(0,min(max(0,self.world_h-vh),self.ty))
    def update(self, dt, keys, mp):
        sp=500/self.zoom
        if keys[pygame.K_w] or keys[pygame.K_UP]: self.pan(0,-sp*dt)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: self.pan(0,sp*dt)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: self.pan(-sp*dt,0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.pan(sp*dt,0)
        if self.viewport.collidepoint(mp):
            mx,my=mp; es=self.edge_speed/self.zoom
            if mx<self.viewport.left+self.edge_margin: self.pan(-es*dt,0)
            elif mx>self.viewport.right-self.edge_margin: self.pan(es*dt,0)
            if my<self.viewport.top+self.edge_margin: self.pan(0,-es*dt)
            elif my>self.viewport.bottom-self.edge_margin: self.pan(0,es*dt)
        f=1-math.exp(-self.smooth*dt)
        self.x+=(self.tx-self.x)*f; self.y+=(self.ty-self.y)*f; self.zoom+=(self.tz-self.zoom)*f

class EmojiCache:
    def __init__(self):
        self.font=None; self.cache={}
        for n in EMOJI_FONT_NAMES:
            try:
                f=pygame.font.SysFont(n,40)
                if f.render("🌾",True,(255,255,255)).get_width()>10: self.font=f; break
            except: pass
        if not self.font: self.font=pygame.font.SysFont(None,40)
    def get(self, emoji, size):
        size=max(4,(int(size)+2)//4*4); key=(emoji,size)
        if key not in self.cache:
            base=self.font.render(emoji,True,(255,255,255))
            if base.get_width()>0:
                sc=min(size/base.get_width(),size/base.get_height())
                surf=pygame.transform.smoothscale(base,(max(1,int(base.get_width()*sc)),max(1,int(base.get_height()*sc)))) if abs(sc-1)>0.05 and sc>0.1 else base
            else: surf=pygame.Surface((1,1),pygame.SRCALPHA)
            try: surf=surf.convert_alpha() if surf.get_flags()&pygame.SRCALPHA else surf.convert()
            except: pass
            self.cache[key]=surf
        return self.cache[key]

class TextCache:
    def __init__(self): self.cache={}
    def get(self, text, color, font):
        key=(text,color,id(font))
        if key not in self.cache: self.cache[key]=font.render(text,True,color)
        return self.cache[key]
    def invalidate(self): self.cache.clear()

class FloatingText:
    def __init__(self, text, pos, color=(255,255,120)):
        self.text=text; self.x,self.y=pos; self.vy=-40; self.life=1.5; self.color=color
    def update(self, dt): self.y+=self.vy*dt; self.life-=dt
    def draw(self, screen, font):
        if self.life<=0: return
        s=font.render(self.text,True,self.color)
        s.set_alpha(int(max(0,min(1,self.life))*255))
        screen.blit(s,(int(self.x)-s.get_width()//2,int(self.y)))

class Particle:
    def __init__(self, pos, color):
        self.x,self.y=pos; a=random.uniform(0,6.283); s=random.uniform(40,120)
        self.vx=s*math.cos(a); self.vy=s*math.sin(a)-40
        self.color=color; self.life=random.uniform(0.5,1.0); self.size=random.randint(2,4)
    def update(self, dt): self.x+=self.vx*dt; self.y+=self.vy*dt; self.vy+=200*dt; self.life-=dt
    def draw(self, screen):
        if self.life<=0: return
        pygame.draw.circle(screen,self.color,(int(self.x),int(self.y)),self.size)

# =============================================================================
# §8. BUILDING CLASS — with tier system
# =============================================================================
class Building:
    """A placed building with tiered upgrades."""
    def __init__(self, building_type, world_x, world_y):
        self.type = building_type
        self.base_data = BUILDINGS[building_type].copy()
        self.x = world_x
        self.y = world_y
        self.tier = 1
        self._recalc_stats()
        self.animals = []
        self.production_timers = {item: 0 for item, _, _ in self.base_data["produces"]}
        self.attack_cooldown = 0
        self.upgrade_flash = 0  # visual feedback on upgrade

    def _recalc_stats(self):
        """Recalculate stats based on current tier."""
        t = BUILDING_TIERS[self.tier]
        base = self.base_data
        self.name = f"{base['name']} ({t['name']})"
        self.capacity = int(base["capacity"] * t["cap_mult"])
        self.max_hp = int(base["hp"] * t["hp_mult"])
        if self.tier == 1:
            self.hp = self.max_hp
        else:
            # Preserve HP ratio on upgrade
            ratio = self.hp / self._prev_max_hp() if hasattr(self, '_prev_max_hp_val') else 1.0
            self.hp = min(self.max_hp, max(self.hp, int(self.max_hp * 0.5)))
        self.defense = int(base.get("defense", 0) * t["def_mult"])
        self.range_tiles = base.get("range", 2)
        self.size = t["size"]
        self.radius = self.size * TILE // 2 + 20
        self.emoji_scale = t["emoji_scale"]
        # Production intervals scale inversely with prod_mult
        self.prod_intervals = {}
        for item, interval, value in base["produces"]:
            self.prod_intervals[item] = (interval / t["prod_mult"], int(value * t["prod_mult"]))

    def _prev_max_hp(self):
        if self.tier <= 1: return self.base_data["hp"]
        return int(self.base_data["hp"] * BUILDING_TIERS[self.tier-1]["hp_mult"])

    def contains_world_point(self, wx, wy):
        dx = wx - self.x; dy = wy - self.y
        return abs(dx) < self.size*TILE/2 and abs(dy) < self.size*TILE/2

    def can_add_animal(self, creature_name):
        if len(self.animals) >= self.capacity:
            return False
        return creature_name in self.base_data["accepts"]

    def add_animal(self, creature_name, creature_data):
        if not self.can_add_animal(creature_name):
            return False
        self.animals.append((creature_name, creature_data))
        return True

    def get_upgrade_info(self, player_level):
        """Return info about next tier upgrade, or None if maxed."""
        if self.tier >= 4:
            return None
        next_tier = self.tier + 1
        next_t = BUILDING_TIERS[next_tier]
        cost = int(self.base_data["cost"] * next_t["cost_mult"])
        lvl_req = next_t["lvl_req"]
        can_afford = True  # caller checks coins
        meets_level = player_level >= lvl_req
        return {
            "next_tier": next_tier,
            "name": next_t["name"],
            "cost": cost,
            "lvl_req": lvl_req,
            "meets_level": meets_level,
            "cap_bonus": int(self.base_data["capacity"] * next_t["cap_mult"]) - self.capacity,
            "hp_bonus": int(self.base_data["hp"] * next_t["hp_mult"]) - self.max_hp,
            "def_bonus": int(self.base_data.get("defense",0) * next_t["def_mult"]) - self.defense,
            "prod_mult": next_t["prod_mult"] / BUILDING_TIERS[self.tier]["prod_mult"],
        }

    def upgrade(self):
        """Upgrade to next tier. Returns True if successful."""
        if self.tier >= 4:
            return False
        self._prev_max_hp_val = self.max_hp
        self.tier += 1
        self._recalc_stats()
        self.upgrade_flash = 2.0
        return True

    def update(self, dt, game):
        # Production
        for item in list(self.prod_intervals.keys()):
            interval, value = self.prod_intervals[item]
            if self.animals or not self.base_data["accepts"]:
                # Non-housing buildings produce even without animals
                self.production_timers[item] = self.production_timers.get(item, 0) + dt
                if self.production_timers[item] >= interval:
                    self.production_timers[item] = 0
                    bonus = max(1, len(self.animals))
                    earned = value * bonus
                    game.coins += earned
                    game.inventory[item] = game.inventory.get(item, 0) + bonus
                    sx, sy = game.camera.world_to_screen(self.x, self.y)
                    game.floats.append(FloatingText(
                        f"+${earned} {item}", (sx, sy - 30), (255, 220, 100)))

        # Defense
        if self.defense > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                target = self._find_target(game.siege_monsters, self.range_tiles * TILE)
                if target:
                    target.hp -= self.defense
                    self.attack_cooldown = 1.5
                    sx, sy = game.camera.world_to_screen(self.x, self.y)
                    game.floats.append(FloatingText(
                        f"🏹 -{self.defense}", (sx, sy - 40), (255, 150, 100)))
                    if target.hp <= 0:
                        game.coins += target.value // 2
                        game.add_xp(target.value // 4)

        if self.upgrade_flash > 0:
            self.upgrade_flash -= dt

    def _find_target(self, monsters, range_px):
        closest = None
        closest_dist = range_px
        for m in monsters:
            dx = m.x - self.x; dy = m.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < closest_dist:
                closest_dist = dist
                closest = m
        return closest

    def take_damage(self, dmg):
        self.hp -= dmg
        return self.hp <= 0

    def repair(self, amount=50):
        if self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + amount)
            return True
        return False

    def draw(self, screen, camera, emoji_cache, font, now):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sx < -150 or sx > screen.get_width()+150 or sy < -150 or sy > screen.get_height()+150:
            return

        tier_data = BUILDING_TIERS[self.tier]
        base_size = camera.scaled_size(self.size * TILE - 10)

        # Master tier glow (underneath)
        if tier_data.get("glow"):
            glow_size = int(base_size * 1.4)
            pulse = 0.7 + 0.3 * math.sin(now * 2)
            glow = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            glow_color = tier_data.get("glow_color", (255, 215, 0, 80))
            pygame.draw.circle(glow, (*glow_color[:3], int(glow_color[3] * pulse)),
                               (glow_size//2, glow_size//2), glow_size//2)
            screen.blit(glow, (int(sx - glow_size/2), int(sy - glow_size/2)))

        # Shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 60),
                            (int(sx-base_size/2), int(sy+base_size/3), base_size, base_size//3))

        # Tier border (colored rectangle around building)
        border_rect = pygame.Rect(int(sx-base_size/2), int(sy-base_size/2), base_size, base_size)
        pygame.draw.rect(screen, tier_data["border_color"], border_rect, 3, border_radius=6)

        # Building emoji (use master emoji at tier 4)
        if self.tier == 4 and "master_emoji" in self.base_data:
            emoji_to_use = self.base_data["master_emoji"]
        else:
            emoji_to_use = self.base_data["emoji"]
        emoji_size = camera.scaled_size(int(self.size * 60 * self.emoji_scale))
        emoji_surf = emoji_cache.get(emoji_to_use, emoji_size)
        if emoji_surf.get_width() > 4:
            screen.blit(emoji_surf, (
                int(sx - emoji_surf.get_width()/2),
                int(sy - emoji_surf.get_height()/2)))

        # Upgrade flash effect
        if self.upgrade_flash > 0:
            flash_size = int(base_size * (1.0 + (2.0 - self.upgrade_flash) * 0.3))
            flash = pygame.Surface((flash_size, flash_size), pygame.SRCALPHA)
            alpha = int(200 * (self.upgrade_flash / 2.0))
            pygame.draw.circle(flash, (255, 255, 150, alpha),
                               (flash_size//2, flash_size//2), flash_size//2)
            screen.blit(flash, (int(sx - flash_size/2), int(sy - flash_size/2)))

        # HP bar (if damaged)
        if self.hp < self.max_hp:
            bw = camera.scaled_size(50)
            bx, by = int(sx-bw/2), int(sy-camera.scaled_size(45))
            pygame.draw.rect(screen, (60,0,0), (bx, by, bw, 5))
            fill = int(bw * self.hp/self.max_hp)
            pygame.draw.rect(screen, (50,200,50), (bx, by, fill, 5))

        # Animals orbiting (faster at higher tiers)
        orbit_speed = 0.5 + (self.tier - 1) * 0.3
        for i, (name, data) in enumerate(self.animals[:6]):
            angle = (i / max(1, len(self.animals))) * 2 * math.pi + now * orbit_speed
            orbit_r = camera.scaled_size(35 + self.tier * 3)
            ox = math.cos(angle) * orbit_r
            oy = math.sin(angle) * camera.scaled_size(15) + camera.scaled_size(25)
            anim_surf = emoji_cache.get(data["emoji"], camera.scaled_size(18 + self.tier))
            if anim_surf.get_width() > 2:
                screen.blit(anim_surf, (int(sx+ox-anim_surf.get_width()/2),
                                        int(sy+oy-anim_surf.get_height()/2)))

        # Tier stars + count label
        if camera.zoom > 0.5:
            # Stars
            star_count = tier_data["star_count"]
            if star_count > 0:
                star_str = "⭐" * star_count
                star_txt = font.render(star_str, True, (255, 220, 80))
                star_bg = star_txt.get_rect()
                star_bg.center = (int(sx), int(sy - camera.scaled_size(40)))
                pygame.draw.rect(screen, (0,0,0,180), star_bg.inflate(4,2), border_radius=3)
                screen.blit(star_txt, star_bg)

            # Capacity label
            if self.capacity > 0:
                count_txt = font.render(f"{len(self.animals)}/{self.capacity}",
                                        True, (255, 255, 255))
                bg = count_txt.get_rect()
                bg.center = (int(sx), int(sy + camera.scaled_size(45)))
                pygame.draw.rect(screen, (0,0,0), bg.inflate(6,3), border_radius=3)
                screen.blit(count_txt, bg)

            # Tier badge (bottom-right)
            tier_txt = font.render(f"T{self.tier}", True, tier_data["border_color"])
            tbg = tier_txt.get_rect()
            tbg.bottomright = (int(sx + base_size/2 - 4), int(sy + base_size/2 - 4))
            pygame.draw.rect(screen, (0,0,0), tbg.inflate(4,2), border_radius=3)
            screen.blit(tier_txt, tbg)

# =============================================================================
# §9. SIEGE MONSTER
# =============================================================================
class SiegeMonster:
    def __init__(self, name, data, x, y):
        self.name = name
        self.data = data.copy()
        self.hp = data["max_hp"]; self.max_hp = data["max_hp"]
        self.atk = data["atk"]; self.value = data["value"]
        self.emoji = data["emoji"]
        self.x = x; self.y = y
        self.speed = 40 + data["lvl"] * 2
        self.target = None
        self.attack_cooldown = 0

    def update(self, dt, buildings, plots, game):
        self.attack_cooldown -= dt
        if self.target is None or (hasattr(self.target, 'hp') and self.target.hp <= 0):
            self.target = self._pick_target(buildings, plots)
        if self.target is None:
            farm_cx = (FARM_X + FARM_COLS/2) * TILE
            farm_cy = (FARM_Y + FARM_ROWS/2) * TILE
            dx = farm_cx - self.x; dy = farm_cy - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 5:
                self.x += (dx/dist) * self.speed * dt
                self.y += (dy/dist) * self.speed * dt
            return
        tx, ty = (self.target.x, self.target.y) if hasattr(self.target, 'x') else (
            self.target.world_rect.centerx, self.target.world_rect.centery)
        dx = tx - self.x; dy = ty - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > TILE * 0.8:
            self.x += (dx/dist) * self.speed * dt
            self.y += (dy/dist) * self.speed * dt
        else:
            if self.attack_cooldown <= 0:
                if hasattr(self.target, 'take_damage'):
                    destroyed = self.target.take_damage(self.atk)
                    if destroyed and isinstance(self.target, Building):
                        if self.target in game.buildings:
                            game.buildings.remove(self.target)
                            game.floats.append(FloatingText(
                                f"💥 {self.target.base_data['name']} destroyed!",
                                game.camera.world_to_screen(self.target.x, self.target.y),
                                (255, 80, 80)))
                self.attack_cooldown = 2.0
                sx, sy = game.camera.world_to_screen(self.x, self.y)
                game.floats.append(FloatingText(f"💢 -{self.atk}", (sx, sy-30), (255, 100, 100)))

    def _pick_target(self, buildings, plots):
        best = None; best_dist = float('inf')
        for b in buildings:
            dx = b.x - self.x; dy = b.y - self.y
            dist = dx*dx + dy*dy
            if dist < best_dist: best_dist = dist; best = b
        if best is None:
            for p in plots:
                if p.state == "planted":
                    dx = p.world_rect.centerx - self.x
                    dy = p.world_rect.centery - self.y
                    dist = dx*dx + dy*dy
                    if dist < best_dist: best_dist = dist; best = p
        return best

    def draw(self, screen, camera, emoji_cache, now):
        sx, sy = camera.world_to_screen(self.x, self.y)
        if sx < -60 or sx > screen.get_width()+60 or sy < -60 or sy > screen.get_height()+60:
            return
        size = camera.scaled_size(50)
        surf = emoji_cache.get(self.emoji, size)
        if surf.get_width() > 4:
            bob = math.sin(now*4 + self.x*0.01) * 4
            screen.blit(surf, (int(sx-surf.get_width()/2), int(sy-surf.get_height()/2+bob)))
        if self.hp < self.max_hp:
            bw = camera.scaled_size(40)
            bx, by = int(sx-bw/2), int(sy-camera.scaled_size(35))
            pygame.draw.rect(screen, (60,0,0), (bx, by, bw, 5))
            fill = int(bw * self.hp/self.max_hp)
            pygame.draw.rect(screen, (255,50,50), (bx, by, fill, 5))

# =============================================================================
# §10. WORLD GENERATION
# =============================================================================
class WorldGenerator:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 2**31-1)
        self.rng = random.Random(self.seed)
        self.width, self.height = WORLD_COLS, WORLD_ROWS
        self.biomes = [[Biome.PLAINS]*self.width for _ in range(self.height)]
        self.tile_variant = [[0]*self.width for _ in range(self.height)]
        self.decorations = []; self.wild_plants = []; self.npc_spots = []
        self.plant_grid_cell = TILE*4; self.plant_grid = {}
        self.generate()
    def generate(self):
        self._gen_biomes(); self._carve_farm(); self._npc_spots()
        self._decorations(); self._wild_plants(); self._variants(); self._build_grid()
    def _gen_biomes(self):
        centers = [(self.width//2, self.height//2, Biome.PLAINS)]
        for i, b in enumerate([Biome.FOREST,Biome.DESERT,Biome.SWAMP,Biome.TUNDRA,Biome.MOUNTAINS]):
            a = (i/5)*2*math.pi + self.rng.uniform(-0.3,0.3)
            r = min(self.width,self.height)*0.38
            x = max(2,min(self.width-3, int(self.width//2+r*math.cos(a))))
            y = max(2,min(self.height-3, int(self.height//2+r*math.sin(a))))
            centers.append((x,y,b))
        for y in range(self.height):
            for x in range(self.width):
                md = float('inf'); cb = Biome.PLAINS
                for cx,cy,b in centers:
                    d = math.sqrt((x-cx)**2+(y-cy)**2)+self.rng.uniform(-0.8,0.8)
                    if d < md: md=d; cb=b
                self.biomes[y][x] = cb
    def _carve_farm(self):
        for y in range(FARM_Y-1, FARM_Y+FARM_ROWS+1):
            for x in range(FARM_X-1, FARM_X+FARM_COLS+1):
                if 0<=x<self.width and 0<=y<self.height: self.biomes[y][x]=Biome.PLAINS
    def _npc_spots(self):
        cands = []
        for y in range(self.height):
            for x in range(self.width):
                if FARM_X-1<=x<FARM_X+FARM_COLS+1 and FARM_Y-1<=y<FARM_Y+FARM_ROWS+1: continue
                b = self.biomes[y][x]
                sc = 5 if b==Biome.PLAINS else 3 if b==Biome.FOREST else 1
                d = math.sqrt((x-FARM_X-FARM_COLS/2)**2+(y-FARM_Y-FARM_ROWS/2)**2)
                if 5<d<13: sc+=3
                cands.append((sc,x,y,b))
        cands.sort(reverse=True); self.npc_spots = []
        for sc,x,y,b in cands:
            if len(self.npc_spots)>=8: break
            if all(math.sqrt((x*TILE-sx)**2+(y*TILE-sy)**2)>=4*TILE for sx,sy,_ in self.npc_spots):
                self.npc_spots.append((x*TILE+TILE//2, y*TILE+TILE//2, b))
    def _decorations(self):
        decs = {Biome.PLAINS:["🌾","🌼","🌻"],Biome.FOREST:["🌲","🌳","🍄"],Biome.DESERT:["🌵","🏜️"],
                Biome.SWAMP:["🌿","🐸","🪷"],Biome.TUNDRA:["❄️","⛄"],Biome.MOUNTAINS:["⛰️","🪨"]}
        for y in range(self.height):
            for x in range(self.width):
                if FARM_X-1<=x<FARM_X+FARM_COLS+1 and FARM_Y-1<=y<FARM_Y+FARM_ROWS+1: continue
                if self.rng.random()<0.3:
                    self.decorations.append((x*TILE+TILE//2+self.rng.randint(-20,20),
                        y*TILE+TILE//2+self.rng.randint(-20,20),
                        self.rng.choice(decs[self.biomes[y][x]]), self.rng.randint(30,50)))
    def _wild_plants(self):
        wp = {Biome.PLAINS:[("🌾",5,12)],Biome.FOREST:[("🍄",15,30)],Biome.DESERT:[("🌵",25,50)],
              Biome.SWAMP:[("🌿",12,25)],Biome.TUNDRA:[("❄️",20,45)],Biome.MOUNTAINS:[("💎",80,150)]}
        for y in range(self.height):
            for x in range(self.width):
                if FARM_X-1<=x<FARM_X+FARM_COLS+1 and FARM_Y-1<=y<FARM_Y+FARM_ROWS+1: continue
                if self.rng.random()<0.15:
                    e,mn,mx = self.rng.choice(wp[self.biomes[y][x]])
                    self.wild_plants.append({"x":x*TILE+TILE//2,"y":y*TILE+TILE//2,"emoji":e,
                        "biome":self.biomes[y][x],"collected":False,"value":self.rng.randint(mn,mx),"respawn_at":0})
    def _variants(self):
        for y in range(self.height):
            for x in range(self.width): self.tile_variant[y][x]=self.rng.randint(0,2)
    def _build_grid(self):
        self.plant_grid = {}; c = self.plant_grid_cell
        for i,p in enumerate(self.wild_plants):
            k = (int(p["x"]//c), int(p["y"]//c))
            self.plant_grid.setdefault(k,[]).append(i)
    def get_plants_in_rect(self, r):
        c = self.plant_grid_cell; res = []
        for cy in range(int(r.top//c), int(r.bottom//c)+1):
            for cx in range(int(r.left//c), int(r.right//c)+1):
                res.extend(self.plant_grid.get((cx,cy),[]))
        return res
    def get_biome_at(self, wx, wy):
        tx,ty = int(wx//TILE), int(wy//TILE)
        if 0<=tx<self.width and 0<=ty<self.height: return self.biomes[ty][tx]
        return Biome.PLAINS

# =============================================================================
# §11. PLOT
# =============================================================================
class Plot:
    def __init__(self, col, row, biome):
        self.col=col; self.row=row; self.biome=biome
        self.world_rect = pygame.Rect((FARM_X+col)*TILE, (FARM_Y+row)*TILE, TILE, TILE)
        self.state="empty"; self.crop=None; self.crop_biome=None
        self.planted_at=0.0; self.grow_time=0.0; self.base_grow_time=0.0
        self.water=100.0; self.wilt_timer=0.0
        self.fertilized=False; self.pest=False; self.greenhouse=False
    def till(self):
        if self.state=="empty": self.state="tilled"; return True
        return False
    def plant(self, name, now, data, biome):
        if self.state!="tilled": return False
        self.crop=name; self.crop_biome=biome; self.state="planted"; self.planted_at=now
        gm = BIOME_INFO[self.biome]["grow_mod"]
        if not self.greenhouse and self.biome!=biome: gm*=1.5
        self.base_grow_time = data["time"]*gm
        self.grow_time = self.base_grow_time*(0.5 if self.fertilized else 1.0)
        self.water=100.0; self.wilt_timer=0.0; self.pest=False; return True
    def water_plot(self):
        if self.state=="planted": self.water=min(100,self.water+60); return True
        return False
    def fertilize(self):
        if self.state=="planted" and not self.fertilized:
            self.fertilized=True; self.grow_time=self.base_grow_time*0.5; return True
        return False
    def clear(self):
        if self.state in ("weed","wilted","tilled"): self.state="empty"; self.crop=None; return True
        return False
    def spawn_weed(self):
        if self.state=="empty" and random.random()<0.15: self.state="weed"; return True
        return False
    def progress(self, now):
        if self.state!="planted": return None
        return min((now-self.planted_at)/self.grow_time, 1.0)
    def ready(self, now): return self.state=="planted" and self.progress(now)>=1.0
    def update(self, now, dt):
        if self.state=="planted":
            drain = (1.5 if self.fertilized else 2.0) * (0.5 if self.biome==Biome.DESERT else 1.0)
            self.water = max(0, self.water-drain*dt)
            if self.water<=0:
                self.wilt_timer+=dt
                if self.wilt_timer>=12: self.state="wilted"; self.crop=None
    def harvest(self, now, data):
        if not self.ready(now): return 0,0,None,None,False,False
        name=self.crop; rarity=data["rarity"]
        double = self.biome==Biome.SWAMP and random.random()<0.2
        gem = self.biome==Biome.MOUNTAINS and random.random()<0.15
        self.state="tilled"; self.crop=None
        return data["sell"], data["xp"], name, rarity, double, gem

# =============================================================================
# §12. MAIN GAME
# =============================================================================
class Game:
    def __init__(self, seed=None):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🏰 Farmville — Building Upgrades")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("arial",20,bold=True)
        self.font = pygame.font.SysFont("arial",16,bold=True)
        self.font_small = pygame.font.SysFont("arial",13)
        self.emoji_cache = EmojiCache()
        self.text_cache = TextCache()

        self.plant_gen = PlantGenerator()
        self.creature_gen = CreatureGenerator()

        self.world_seed = seed or random.randint(0, 2**31-1)
        self.world = WorldGenerator(self.world_seed)
        self.world_w = WORLD_COLS*TILE; self.world_h = WORLD_ROWS*TILE
        self.viewport = pygame.Rect(LEFT_PANEL, TOP_BAR, SCREEN_W-LEFT_PANEL, SCREEN_H-TOP_BAR-BOTTOM_BAR)
        self.camera = Camera(self.world_w, self.world_h, self.viewport)

        self.plots = [Plot(c,r,self._farm_biome(c,r)) for r in range(FARM_ROWS) for c in range(FARM_COLS)]
        self.coins=500; self.xp=0; self.level=1; self.day=1; self.season="spring"
        self.day_start=time.time()
        self.tool="hoe"; self.selected_seed="wheat"; self.selected_biome=Biome.PLAINS
        self.floats=[]; self.particles=[]
        self.message=f"🏰 Click buildings to upgrade! (Tool 9)"
        self.msg_time=time.time()
        self.rain_timer=random.uniform(40,70); self.raining=0; self.raindrops=[]
        self.level_up_flash=0; self.hover_plot=None; self.hover_biome=Biome.PLAINS
        self.dragging=False; self.drag_start=None; self.drag_cam_start=None
        self.total_harvests=0

        self.world_creatures = []
        self.creature_spawn_timer = random.uniform(15, 30)
        self.tamed_creatures = []
        self.inventory = {}

        self.buildings = []
        self.build_mode = False
        self.selected_building = None

        # Upgrade UI
        self.upgrade_panel_building = None  # building whose upgrade panel is open

        self.siege_monsters = []
        self.siege_wave = 0
        self.next_siege_time = time.time() + 120
        self.siege_warning = 0
        self.siege_active = False

        self.npcs = []; self._create_npcs()
        self.camera.center_on((FARM_X+FARM_COLS/2)*TILE, (FARM_Y+FARM_ROWS/2)*TILE)
        self._try_load()

    def _farm_biome(self, c, r):
        d = math.sqrt((c-FARM_COLS/2)**2+(r-FARM_ROWS/2)**2)
        if d < 3.5: return Biome.PLAINS
        a = math.atan2(r-FARM_ROWS/2, c-FARM_COLS/2)
        bs = [Biome.FOREST,Biome.MOUNTAINS,Biome.TUNDRA,Biome.SWAMP,Biome.DESERT,Biome.FOREST]
        return bs[int(((a+math.pi)/(2*math.pi))*len(bs))%len(bs)]

    def _create_npcs(self):
        used = set()
        for i,(px,py,b) in enumerate(self.world.npc_spots[:8]):
            while True:
                n = random.choice(["Ella","Finn","Gus","Hazel","Ivy","Jasper","Kira","Leo","Mae","Nolan"])
                if n not in used: used.add(n); break
            npc = type('NPC',(object,),{})()
            npc.id=i; npc.name=n; npc.biome=b
            npc.emoji=["👨‍🍳","👩‍🌾","🧙","🧑‍🍳","👵","🧓","👸","🤴"][i%8]
            npc.position=(px,py); npc.radius=40
            npc.bob_phase=random.uniform(0,6.28)
            self.npcs.append(npc)

    def set_message(self, t): self.message=t; self.msg_time=time.time()
    def xp_for_next_level(self): return self.level*50
    def add_xp(self, amt):
        self.xp += amt; leveled = False
        while self.xp >= self.xp_for_next_level():
            self.xp -= self.xp_for_next_level(); self.level += 1; leveled = True
        if leveled:
            self.level_up_flash=2.0; self.text_cache.invalidate()
            for b,info in BIOME_INFO.items():
                if info["unlock"]==self.level:
                    self.set_message(f"🎉 LEVEL {self.level}! Unlocked {info['emoji']} {info['name']}!"); return
            self.set_message(f"🎉 LEVEL UP! Now level {self.level}")

    def unlocked_biomes(self): return [b for b,i in BIOME_INFO.items() if i["unlock"]<=self.level]
    def unlocked_buildings(self):
        return [k for k,v in BUILDINGS.items() if v["unlock"]<=self.level]

    # --- UI rects ---
    def tool_rects(self):
        tools = ["hoe","water","hand","fertilizer","greenhouse","net","sword","build","repair","upgrade"]
        rects=[]; y=TOP_BAR+15
        for t in tools:
            rects.append((t, pygame.Rect(10,y,LEFT_PANEL-20,32))); y+=34
        return rects

    def biome_rects(self):
        rects=[]; x=LEFT_PANEL+15; y=SCREEN_H-BOTTOM_BAR+8
        for b in self.unlocked_biomes():
            rects.append((b, pygame.Rect(x,y,70,32))); x+=75
        return rects

    def seed_rects(self):
        rects=[]; x=LEFT_PANEL+15; y=SCREEN_H-BOTTOM_BAR+45
        crops = self.plant_gen.get_plants_for_biome(self.selected_biome, self.level)
        for i,name in enumerate(list(crops.keys())[:10]):
            rects.append((name, pygame.Rect(x,y,80,95))); x+=85
            if (i+1)%10==0: x=LEFT_PANEL+15; y+=100
        return rects

    def building_rects(self):
        rects=[]; x=SCREEN_W//2-220; y=SCREEN_H//2-180
        for i, btype in enumerate(self.unlocked_buildings()):
            rects.append((btype, pygame.Rect(x + (i%4)*110, y + (i//4)*90, 100, 80)))
        return rects

    # --- Input ---
    def handle_click(self, pos, button):
        # Upgrade panel takes priority
        if self.upgrade_panel_building:
            if self._handle_upgrade_panel_click(pos): return

        # Build mode UI
        if self.build_mode:
            if self._handle_build_click(pos): return

        if hasattr(self,'save_rect') and self.save_rect.collidepoint(pos): self.save(); return
        if hasattr(self,'load_rect') and self.load_rect.collidepoint(pos): self.load(); return

        for t,r in self.tool_rects():
            if r.collidepoint(pos):
                if t == "build":
                    self.build_mode = not self.build_mode
                    self.set_message("🏗️ Build mode ON" if self.build_mode else "Build mode OFF")
                elif t == "upgrade":
                    self.set_message("🔼 Click a building to upgrade it!")
                    self.tool = t
                else:
                    self.build_mode = False
                    self.tool = t
                    self.set_message(f"Tool: {t.capitalize()}")
                return

        if not self.build_mode:
            for b,r in self.biome_rects():
                if r.collidepoint(pos):
                    self.selected_biome=b
                    crops = self.plant_gen.get_plants_for_biome(b, self.level)
                    if crops: self.selected_seed = list(crops.keys())[0]
                    self.set_message(f"Selected {BIOME_INFO[b]['emoji']} {BIOME_INFO[b]['name']}"); return
            for name,r in self.seed_rects():
                if r.collidepoint(pos): self.selected_seed=name; self.tool="hoe"; self.set_message(f"Selected: {name}"); return

        if not self.viewport.collidepoint(pos): return
        if button==1:
            wx,wy = self.camera.screen_to_world(*pos)

            if self.build_mode and self.selected_building:
                self._place_building(wx, wy); return

            # Buildings
            for bld in self.buildings:
                if bld.contains_world_point(wx, wy):
                    self._interact_building(bld, pos); return

            # Siege monsters
            for m in self.siege_monsters[:]:
                dx=wx-m.x; dy=wy-m.y
                if dx*dx+dy*dy < 900:
                    self._attack_monster(m, pos); return

            # Wild creatures
            for wc in self.world_creatures[:]:
                dx=wx-wc.x; dy=wy-wc.y
                if dx*dx+dy*dy < 900:
                    self._interact_creature(wc, pos); return

            # Wild plants
            for i in self.world.get_plants_in_rect(self.camera.visible_rect()):
                p = self.world.wild_plants[i]
                if p["collected"] or p["respawn_at"]>time.time(): continue
                if (wx-p["x"])**2+(wy-p["y"])**2 < 400:
                    p["collected"]=True; p["respawn_at"]=time.time()+random.uniform(60,180)
                    self.coins+=p["value"]
                    self.floats.append(FloatingText(f"+${p['value']} {p['emoji']}",pos,(150,255,150)))
                    self.set_message(f"Foraged {p['emoji']}! +${p['value']}"); return

            # Plots
            for p in self.plots:
                if p.world_rect.collidepoint(wx,wy): self._act_on_plot(p,pos); return
        elif button==2:
            self.dragging=True; self.drag_start=pos; self.drag_cam_start=(self.camera.tx,self.camera.ty)
        elif button==3:
            wx,wy = self.camera.screen_to_world(*pos); self.camera.center_on(wx,wy)

    def _handle_build_click(self, pos):
        panel_rect = self._build_panel_rect()
        if not panel_rect.collidepoint(pos):
            if self.viewport.collidepoint(pos) and self.selected_building:
                wx, wy = self.camera.screen_to_world(*pos)
                self._place_building(wx, wy)
                return True
            if not self.selected_building:
                self.build_mode = False
                self.set_message("Build mode OFF")
                return True
            return False
        for btype, r in self.building_rects():
            if r.collidepoint(pos):
                self.selected_building = btype
                data = BUILDINGS[btype]
                self.set_message(f"Selected {data['emoji']} {data['name']} (${data['cost']})")
                return True
        return True

    def _build_panel_rect(self):
        unlocked = self.unlocked_buildings()
        cols = 4; rows = (len(unlocked) + cols - 1) // cols
        w = cols * 110 + 40; h = rows * 90 + 100
        return pygame.Rect(SCREEN_W//2-w//2, SCREEN_H//2-h//2, w, h)

    def _place_building(self, wx, wy):
        if not self.selected_building: return
        data = BUILDINGS[self.selected_building]
        if self.coins < data["cost"]:
            self.set_message(f"Not enough coins! Need ${data['cost']} 🪙"); return
        for b in self.buildings:
            dx = b.x - wx; dy = b.y - wy
            if abs(dx) < TILE * (b.size + BUILDING_TIERS[1]["size"])/2 and abs(dy) < TILE * (b.size + BUILDING_TIERS[1]["size"])/2:
                self.set_message("Too close to another building!"); return
        for p in self.plots:
            if p.world_rect.collidepoint(wx, wy):
                self.set_message("Can't build on farm plots!"); return
        bld = Building(self.selected_building, wx, wy)
        self.buildings.append(bld)
        self.coins -= data["cost"]
        self.set_message(f"🏗️ Built {data['emoji']} {data['name']}!")
        sx, sy = self.camera.world_to_screen(wx, wy)
        self._spawn_particles((sx, sy), (200, 200, 100), 15)

    def _interact_building(self, bld, screen_pos):
        """Handle clicks on buildings based on current tool."""
        if self.tool == "upgrade":
            # Open upgrade panel
            self.upgrade_panel_building = bld
            return
        if self.tool == "hand":
            info = f"{bld.base_data['emoji']} {bld.name} | HP:{bld.hp}/{bld.max_hp}"
            if bld.capacity > 0:
                info += f" | Animals: {len(bld.animals)}/{bld.capacity}"
            if bld.defense:
                info += f" | Defense: {bld.defense}"
            self.set_message(info)
        elif self.tool == "net":
            if not self.tamed_creatures:
                self.set_message("No tamed creatures! Catch some first."); return
            if bld.capacity == 0:
                self.set_message(f"{bld.base_data['name']} can't house animals."); return
            if len(bld.animals) >= bld.capacity:
                self.set_message(f"{bld.base_data['name']} is full!"); return
            for i, (name, data) in enumerate(self.tamed_creatures):
                if name in bld.base_data["accepts"]:
                    bld.add_animal(name, data)
                    self.tamed_creatures.pop(i)
                    self.set_message(f"🏠 Placed {data['emoji']} in {bld.base_data['name']}!")
                    self._spawn_particles(screen_pos, (100, 255, 100), 10)
                    return
            self.set_message(f"No compatible creatures for {bld.base_data['name']}")
        elif self.tool == "repair":
            cost = 20 + bld.tier * 10
            if self.coins >= cost and bld.hp < bld.max_hp:
                self.coins -= cost
                bld.repair(50)
                self.set_message(f"🔧 Repaired {bld.base_data['name']}! (-${cost})")
                self._spawn_particles(screen_pos, (200, 200, 200), 8)
            elif bld.hp >= bld.max_hp:
                self.set_message("Building at full HP!")
            else:
                self.set_message(f"Need ${cost} to repair!")

    def _handle_upgrade_panel_click(self, pos):
        """Handle clicks in the upgrade panel."""
        panel_rect = self._upgrade_panel_rect()
        bld = self.upgrade_panel_building

        # Close button
        close_rect = pygame.Rect(panel_rect.right - 30, panel_rect.top + 5, 25, 25)
        if close_rect.collidepoint(pos):
            self.upgrade_panel_building = None
            return True

        if not panel_rect.collidepoint(pos):
            self.upgrade_panel_building = None
            return True

        # Upgrade button
        info = bld.get_upgrade_info(self.level)
        if info:
            btn_rect = pygame.Rect(panel_rect.centerx - 80, panel_rect.bottom - 60, 160, 40)
            if btn_rect.collidepoint(pos):
                if not info["meets_level"]:
                    self.set_message(f"Need level {info['lvl_req']} to upgrade!")
                elif self.coins < info["cost"]:
                    self.set_message(f"Not enough coins! Need ${info['cost']} 🪙")
                else:
                    self.coins -= info["cost"]
                    bld.upgrade()
                    self.set_message(f"🎉 Upgraded to {BUILDING_TIERS[bld.tier]['name']}! Tier {bld.tier}")
                    sx, sy = self.camera.world_to_screen(bld.x, bld.y)
                    # Big particle burst
                    tier_color = BUILDING_TIERS[bld.tier]["border_color"]
                    self._spawn_particles((sx, sy), tier_color, 30)
                    self._spawn_particles((sx, sy), (255, 255, 150), 20)
                    self.floats.append(FloatingText(f"⬆️ TIER {bld.tier}!", (sx, sy-40), (255, 220, 80)))
                    self.upgrade_panel_building = None
                return True
        return True

    def _upgrade_panel_rect(self):
        w, h = 420, 380
        return pygame.Rect(SCREEN_W//2-w//2, SCREEN_H//2-h//2, w, h)

    def _attack_monster(self, m, screen_pos):
        if self.tool == "sword":
            dmg = 10 + self.level * 5
            m.hp -= dmg
            self.floats.append(FloatingText(f"-{dmg} HP", screen_pos, (255,80,80)))
            self._spawn_particles(screen_pos, (255,80,80), 8)
            if m.hp <= 0:
                reward = m.value
                self.coins += reward
                self.add_xp(reward // 2)
                self.floats.append(FloatingText(f"+${reward} 💀", screen_pos, (255,220,100)))
                self.set_message(f"⚔️ Defeated {m.data['display']}! +${reward}")
                self.siege_monsters.remove(m)
            else:
                self.set_message(f"⚔️ Hit {m.data['display']}! ({m.hp}/{m.max_hp} HP)")
        elif self.tool == "net":
            self.set_message("⚔️ Can't tame monsters! Use sword.")
        else:
            self.set_message(f"{m.emoji} {m.data['display']} | HP:{m.hp}/{m.max_hp}")

    def _interact_creature(self, wc, screen_pos):
        if self.tool == "net":
            if wc.hostile:
                self.set_message(f"⚔️ {wc.data['display']} is hostile!"); return
            chance = wc.data.get("tame_chance", 0.3)
            if random.random() < chance:
                self.tamed_creatures.append((wc.name, wc.data))
                self.world_creatures.remove(wc)
                self.set_message(f"🎉 Tamed {wc.data['emoji']}! Put in a building.")
                self.floats.append(FloatingText(f"TAMED!", screen_pos, (100,255,100)))
                self._spawn_particles(screen_pos, (100,255,100), 15)
                self.add_xp(wc.data["value"])
            else:
                self.set_message(f"❌ {wc.data['display']} escaped!")
                wc.fleeing = True
        elif self.tool == "sword":
            dmg = 10 + self.level * 3
            wc.data["hp"]-=dmg
            self.floats.append(FloatingText(f"-{dmg} HP", screen_pos, (255,80,80)))
            self._spawn_particles(screen_pos, (255,80,80), 8)
            if wc.data["hp"] <= 0:
                reward = wc.data["value"]
                self.coins += reward; self.add_xp(reward // 2)
                self.floats.append(FloatingText(f"+${reward} 💀", screen_pos, (255,220,100)))
                self.set_message(f"⚔️ Defeated {wc.data['display']}! +${reward}")
                self.world_creatures.remove(wc)
            else:
                self.set_message(f"⚔️ Hit {wc.data['display']}! ({wc.data['hp']}/{wc.data['max_hp']} HP)")
        else:
            info = f"{wc.data['emoji']} {wc.data['display']} | HP:{wc.data['hp']}/{wc.data['max_hp']} | {'⚔️ HOSTILE' if wc.hostile else '💚 Tamable'}"
            self.set_message(info)

    def _act_on_plot(self, p, screen_pos):
        now = time.time()
        if self.tool == "hoe":
            if p.state=="empty":
                if p.till(): self.set_message(f"Tilled ⛏️")
            elif p.state=="tilled":
                crops = self.plant_gen.get_plants_for_biome(self.selected_biome, self.level)
                cd = crops.get(self.selected_seed)
                if cd:
                    if self.coins >= cd["cost"]:
                        if p.plant(self.selected_seed, now, cd, self.selected_biome):
                            self.coins -= cd["cost"]
                            self.set_message(f"Planted {cd['display']} 🌱")
                            self._spawn_particles(screen_pos, (120,80,40), 6)
                    else: self.set_message("Not enough coins! 🪙")
        elif self.tool == "water":
            if p.water_plot(): self.set_message("Watered 💧"); self._spawn_particles(screen_pos,(100,180,240),8)
        elif self.tool == "fertilizer":
            if p.fertilize():
                if self.coins>=20: self.coins-=20; self.set_message("Fertilized ✨")
                else: self.set_message("Need $20!")
        elif self.tool == "greenhouse":
            if not p.greenhouse:
                if self.coins>=100: self.coins-=100; p.greenhouse=True; self.set_message("🏠 Greenhouse!")
                else: self.set_message("Need $100!")
        elif self.tool == "hand":
            if p.ready(now):
                cd = self.plant_gen.plants.get(p.crop)
                if cd:
                    reward,xp,name,rarity,double,gem = p.harvest(now, cd)
                    if double: reward*=2; self.floats.append(FloatingText("DOUBLE! 🎉",screen_pos,(255,200,100)))
                    if gem:
                        gv=random.randint(30,80); reward+=gv
                        self.floats.append(FloatingText(f"💎 +${gv}",screen_pos,(200,255,255)))
                    self.coins+=reward; self.add_xp(xp); self.total_harvests+=1
                    self.floats.append(FloatingText(f"+${reward}",screen_pos,(255,240,100)))
                    self._spawn_particles(screen_pos,(255,220,80),14)
                    self.set_message(f"Harvested {cd['display']}! +${reward} 🌟")
            elif p.state in ("weed","wilted"):
                p.clear(); self.set_message("Cleared 🧹")

    def _spawn_particles(self, pos, color, n):
        for _ in range(n): self.particles.append(Particle(pos, color))

    # --- Update ---
    def update(self, dt):
        now = time.time()
        keys = pygame.key.get_pressed()
        mp = pygame.mouse.get_pos()
        if not self.build_mode and not self.upgrade_panel_building: self.camera.update(dt, keys, mp)
        for p in self.plots: p.update(now, dt)
        if now-self.day_start>=60:
            self.day+=1; self.day_start=now; self.text_cache.invalidate()
            for p in self.plots: p.spawn_weed()
            if self.day%7==0:
                self.season = ["spring","summer","fall","winter"][(self.day//7)%4]
                self.set_message(f"🍃 Season: {self.season}!")
            for pl in self.world.wild_plants:
                if pl["collected"] and pl["respawn_at"]<=now: pl["collected"]=False
        self.rain_timer-=dt
        if self.rain_timer<=0 and self.raining<=0:
            if random.random()<0.4:
                self.raining=8.0
                for p in self.plots:
                    if p.biome==Biome.PLAINS and p.state=="planted": p.water=100
            self.rain_timer=random.uniform(50,90)
        if self.raining>0:
            self.raining-=dt
            for _ in range(3): self.raindrops.append([random.randint(0,SCREEN_W),-10,random.randint(300,500)])
        for rd in self.raindrops: rd[1]+=rd[2]*dt
        self.raindrops = [rd for rd in self.raindrops if rd[1]<SCREEN_H]

        self.creature_spawn_timer -= dt
        if self.creature_spawn_timer <= 0 and len(self.world_creatures) < 15:
            self._spawn_creature()
            self.creature_spawn_timer = random.uniform(15, 35)
        for wc in self.world_creatures[:]:
            wc.update(dt, self.plots, self)
            if not wc.is_alive(): self.world_creatures.remove(wc)

        for bld in self.buildings:
            bld.update(dt, self)

        self._update_siege(now, dt)

        for f in self.floats: f.update(dt)
        self.floats = [f for f in self.floats if f.life>0]
        for pa in self.particles: pa.update(dt)
        self.particles = [pa for pa in self.particles if pa.life>0]
        if self.level_up_flash>0: self.level_up_flash-=dt
        self.hover_plot=None; self.hover_biome=Biome.PLAINS
        if self.viewport.collidepoint(mp) and not self.build_mode and not self.upgrade_panel_building:
            wx,wy = self.camera.screen_to_world(*mp)
            self.hover_biome = self.world.get_biome_at(wx,wy)
            for p in self.plots:
                if p.world_rect.collidepoint(wx,wy): self.hover_plot=p; break

    def _spawn_creature(self):
        biomes = self.unlocked_biomes()
        if not biomes: return
        b = random.choice(biomes)
        name, data = self.creature_gen.spawn_random(b, self.level)
        if not name: return
        x = random.uniform(0, WORLD_COLS*TILE); y = random.uniform(0, WORLD_ROWS*TILE)
        wc = type('WC',(object,),{})()
        wc.name=name; wc.data=data.copy(); wc.data["hp"]=data["max_hp"]
        wc.x=x; wc.y=y
        wc.vx=random.uniform(-30,30); wc.vy=random.uniform(-30,30)
        wc.life=random.uniform(40,80); wc.attack_cooldown=0
        wc.hostile=data["type"]=="monster"; wc.fleeing=False
        wc.update = lambda dt,plots,game: self._wc_update(wc, dt, plots, game)
        wc.is_alive = lambda: wc.life>0 and wc.data["hp"]>0
        wc.draw = lambda screen,cam,ec,font: self._wc_draw(wc, screen, cam, ec)
        self.world_creatures.append(wc)

    def _wc_update(self, wc, dt, plots, game):
        wc.life -= dt; wc.attack_cooldown -= dt
        if wc.fleeing: wc.vx*=1.02; wc.vy*=1.02
        elif random.random()<0.02:
            wc.vx=random.uniform(-30,30); wc.vy=random.uniform(-30,30)
        wc.x+=wc.vx*dt; wc.y+=wc.vy*dt
        wc.x=max(0,min(WORLD_COLS*TILE,wc.x)); wc.y=max(0,min(WORLD_ROWS*TILE,wc.y))
        if wc.hostile and wc.attack_cooldown<=0:
            for p in plots:
                dx=wc.x-(p.world_rect.x+TILE//2); dy=wc.y-(p.world_rect.y+TILE//2)
                if dx*dx+dy*dy<(TILE*1.5)**2 and p.state=="planted":
                    if random.random()<0.3:
                        p.pest=True
                        game.floats.append(FloatingText(f"{wc.data['emoji']} Attack!",
                            (p.world_rect.centerx,p.world_rect.top),(255,100,100)))
                    wc.attack_cooldown=4.0; break

    def _wc_draw(self, wc, screen, camera, emoji_cache):
        sx,sy = camera.world_to_screen(wc.x,wc.y)
        if sx<-60 or sx>screen.get_width()+60 or sy<-60 or sy>screen.get_height()+60: return
        size = camera.scaled_size(45)
        surf = emoji_cache.get(wc.data["emoji"], size)
        if surf.get_width()>4:
            bob = math.sin(time.time()*3+wc.x*0.01)*3
            screen.blit(surf,(int(sx-surf.get_width()//2),int(sy-surf.get_height()//2+bob)))
        if wc.data["hp"]<wc.data["max_hp"]:
            bw=camera.scaled_size(40); bx=int(sx-bw//2); by=int(sy-camera.scaled_size(30))
            pygame.draw.rect(screen,(60,0,0),(bx,by,bw,5))
            fill=int(bw*wc.data["hp"]/wc.data["max_hp"])
            pygame.draw.rect(screen,(255,50,50) if wc.hostile else (50,200,50),(bx,by,fill,5))

    # === SIEGE SYSTEM ===
    def _update_siege(self, now, dt):
        if not self.siege_active and now >= self.next_siege_time - 20:
            if self.siege_warning == 0:
                self.siege_warning = 20
                self.set_message("⚠️ SIEGE INCOMING! Prepare defenses!")
            self.siege_warning -= dt
        if not self.siege_active and now >= self.next_siege_time:
            self._start_siege()
        for m in self.siege_monsters[:]:
            m.update(dt, self.buildings, self.plots, self)
            if m.hp <= 0:
                self.coins += m.value // 2
                self.add_xp(m.value // 4)
                self.siege_monsters.remove(m)
        if self.siege_active and len(self.siege_monsters) == 0:
            self.siege_active = False
            bonus = 100 + self.siege_wave * 50
            self.coins += bonus
            self.set_message(f"🏆 Siege wave {self.siege_wave} cleared! +${bonus}")
            self.next_siege_time = now + 180
            self.siege_warning = 0

    def _start_siege(self):
        self.siege_wave += 1
        self.siege_active = True
        num_monsters = 3 + self.siege_wave * 2
        for _ in range(num_monsters):
            edge = random.choice(["top","bottom","left","right"])
            if edge == "top": x = random.uniform(0, WORLD_COLS*TILE); y = 0
            elif edge == "bottom": x = random.uniform(0, WORLD_COLS*TILE); y = WORLD_ROWS*TILE
            elif edge == "left": x = 0; y = random.uniform(0, WORLD_ROWS*TILE)
            else: x = WORLD_COLS*TILE; y = random.uniform(0, WORLD_ROWS*TILE)
            available = [n for n,d in self.creature_gen.creatures.items()
                         if d["type"]=="monster" and d["lvl"]<=self.level+self.siege_wave]
            if not available:
                available = [n for n,d in self.creature_gen.creatures.items() if d["type"]=="monster"]
            name = random.choice(available)
            data = self.creature_gen.creatures[name].copy()
            wave_scale = 1 + (self.siege_wave - 1) * 0.2
            data["max_hp"] = int(data["max_hp"] * wave_scale)
            data["hp"] = data["max_hp"]
            data["atk"] = int(data["atk"] * wave_scale)
            data["value"] = int(data["value"] * wave_scale)
            self.siege_monsters.append(SiegeMonster(name, data, x, y))
        self.set_message(f"💀 SIEGE WAVE {self.siege_wave}! {num_monsters} monsters!")

    # --- Draw ---
    def draw(self):
        now = time.time()
        self.screen.fill((90,140,70))
        self.screen.set_clip(self.viewport)
        # Terrain
        vr = self.camera.visible_rect()
        sx_start = max(0,int(vr.x//TILE)); sx_end = min(WORLD_COLS,int(vr.right//TILE)+1)
        sy_start = max(0,int(vr.y//TILE)); sy_end = min(WORLD_ROWS,int(vr.bottom//TILE)+1)
        for ty in range(sy_start, sy_end):
            for tx in range(sx_start, sx_end):
                b = self.world.biomes[ty][tx]; v = self.world.tile_variant[ty][tx]
                base = BIOME_INFO[b]["color"]; c = (max(0,min(255,base[0]+(v-1)*8)),max(0,min(255,base[1]+(v-1)*8)),max(0,min(255,base[2]+(v-1)*8)))
                sx,sy = self.camera.world_to_screen(tx*TILE,ty*TILE)
                sw = self.camera.scaled_size(TILE)
                pygame.draw.rect(self.screen, c, (int(sx),int(sy),sw+1,sw+1))
        # Decorations
        for dx,dy,emoji,size in self.world.decorations:
            if dx<vr.x-50 or dx>vr.right+50 or dy<vr.y-50 or dy>vr.bottom+50: continue
            sx,sy = self.camera.world_to_screen(dx,dy)
            s = self.emoji_cache.get(emoji, self.camera.scaled_size(size))
            if s.get_width()>4: self.screen.blit(s,(int(sx-s.get_width()//2),int(sy-s.get_height()//2)))
        # Wild plants
        for i in self.world.get_plants_in_rect(vr):
            pl = self.world.wild_plants[i]
            if pl["collected"]: continue
            sx,sy = self.camera.world_to_screen(pl["x"],pl["y"])
            s = self.emoji_cache.get(pl["emoji"], self.camera.scaled_size(25))
            if s.get_width()>4:
                bob = math.sin(now*2+pl["x"]*0.1)*3
                self.screen.blit(s,(int(sx-s.get_width()//2),int(sy-s.get_height()//2+bob)))

        # Plots
        for p in self.plots:
            sx,sy = self.camera.world_to_screen(p.world_rect.x, p.world_rect.y)
            sw = self.camera.scaled_size(TILE); r = pygame.Rect(int(sx),int(sy),sw,sw)
            if r.right<self.viewport.left or r.left>self.viewport.right: continue
            if r.bottom<self.viewport.top or r.top>self.viewport.bottom: continue
            bc = BIOME_INFO[p.biome]["color"]
            sc = (max(0,bc[0]//2+40),max(0,bc[1]//3+20),max(0,bc[2]//4+10))
            pygame.draw.rect(self.screen, sc, r)
            pygame.draw.rect(self.screen, (60,35,15), r, 2)
            if p.greenhouse:
                ov = pygame.Surface((sw,sw), pygame.SRCALPHA); ov.fill((200,230,255,60))
                self.screen.blit(ov,(r.x,r.y)); pygame.draw.rect(self.screen,(150,200,240),r,2)
            cx,cy = r.center
            if p.state=="weed":
                s=self.emoji_cache.get("🍀",self.camera.scaled_size(35)); self.screen.blit(s,(cx-s.get_width()//2,cy-s.get_height()//2))
            elif p.state=="wilted":
                s=self.emoji_cache.get("🥀",self.camera.scaled_size(35)); self.screen.blit(s,(cx-s.get_width()//2,cy-s.get_height()//2))
            elif p.state=="planted":
                prog = p.progress(now); idx = min(int(prog*3),2)
                cd = self.plant_gen.plants.get(p.crop)
                if cd:
                    s = self.emoji_cache.get(cd["emojis"][idx], self.camera.scaled_size(25+int(prog*25)))
                    self.screen.blit(s,(cx-s.get_width()//2,cy-s.get_height()//2))
                bw=r.w-14; bx,by=r.x+7,r.bottom-10
                pygame.draw.rect(self.screen,(40,40,40),(bx,by,bw,5))
                fill=int(bw*(p.water/100))
                pygame.draw.rect(self.screen,(70,150,230) if p.water>30 else (220,80,80),(bx,by,fill,5))
                if p.ready(now):
                    pulse=abs((now*3)%2-1)
                    pygame.draw.rect(self.screen,(255,220,80),r,3+int(pulse*2))
            if self.hover_plot is p:
                pygame.draw.rect(self.screen,(255,255,255),r,2)

        # Buildings
        for bld in self.buildings:
            bld.draw(self.screen, self.camera, self.emoji_cache, self.font_small, now)

        # Roaming creatures
        for wc in self.world_creatures:
            wc.draw(self.screen, self.camera, self.emoji_cache, self.font_small)

        # Siege monsters
        for m in self.siege_monsters:
            m.draw(self.screen, self.camera, self.emoji_cache, now)

        # NPCs
        for npc in self.npcs:
            sx,sy = self.camera.world_to_screen(*npc.position)
            if sx<-100 or sx>SCREEN_W+100 or sy<-100 or sy>SCREEN_H+100: continue
            s = self.emoji_cache.get(npc.emoji, self.camera.scaled_size(45))
            bob = math.sin(now*2+npc.bob_phase)*3*self.camera.zoom
            if s.get_width()>4: self.screen.blit(s,(int(sx-s.get_width()//2),int(sy-s.get_height()//2+bob)))

        # FX
        for pa in self.particles: pa.draw(self.screen)
        for f in self.floats: f.draw(self.screen, self.font)
        if self.raining>0:
            for rd in self.raindrops:
                pygame.draw.line(self.screen,(150,200,240),(int(rd[0]),int(rd[1])),(int(rd[0])-2,int(rd[1])+8),1)

        # Siege red tint
        if self.siege_active:
            pulse = abs(math.sin(now*2))
            ov = pygame.Surface((self.viewport.width, self.viewport.height), pygame.SRCALPHA)
            ov.fill((255, 0, 0, int(30 * pulse)))
            self.screen.blit(ov, self.viewport.topleft)

        # Build mode preview
        if self.build_mode and self.selected_building and self.viewport.collidepoint(pygame.mouse.get_pos()):
            mx, my = pygame.mouse.get_pos()
            wx, wy = self.camera.screen_to_world(mx, my)
            sx, sy = self.camera.world_to_screen(wx, wy)
            data = BUILDINGS[self.selected_building]
            size = self.camera.scaled_size(BUILDING_TIERS[1]["size"] * TILE - 10)
            preview = pygame.Surface((size, size), pygame.SRCALPHA)
            preview.fill((100, 200, 100, 80))
            self.screen.blit(preview, (int(sx-size/2), int(sy-size/2)))
            emoji_size = self.camera.scaled_size(BUILDING_TIERS[1]["size"] * 60)
            es = self.emoji_cache.get(data["emoji"], emoji_size)
            if es.get_width() > 4:
                es.set_alpha(150)
                self.screen.blit(es, (int(sx-es.get_width()/2), int(sy-es.get_height()/2)))

        self.screen.set_clip(None)

        if self.level_up_flash>0:
            ov = pygame.Surface((SCREEN_W,SCREEN_H),pygame.SRCALPHA)
            ov.fill((255,255,150,int(60*self.level_up_flash))); self.screen.blit(ov,(0,0))

        self._draw_ui()

        if self.build_mode:
            self._draw_build_panel()

        if self.upgrade_panel_building:
            self._draw_upgrade_panel()

    def _draw_build_panel(self):
        panel_rect = self._build_panel_rect()
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 120))
        self.screen.blit(dim, (0, 0))
        pygame.draw.rect(self.screen, (50, 40, 30), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, (200, 170, 100), panel_rect, 3, border_radius=10)
        title = self.font_big.render("🏗️ Build Mode", True, (255, 230, 150))
        self.screen.blit(title, (panel_rect.x + 20, panel_rect.y + 15))
        hint = self.font_small.render("Click a building, then click world to place.",
                                       True, (200, 200, 200))
        self.screen.blit(hint, (panel_rect.x + 20, panel_rect.y + 45))
        for btype, r in self.building_rects():
            data = BUILDINGS[btype]
            selected = self.selected_building == btype
            can_afford = self.coins >= data["cost"]
            base = (100, 160, 100) if selected else (80, 80, 80) if can_afford else (60, 40, 40)
            pygame.draw.rect(self.screen, base, r, border_radius=6)
            pygame.draw.rect(self.screen, (255, 220, 80) if selected else (180, 180, 180), r, 2, border_radius=6)
            es = self.emoji_cache.get(data["emoji"], 30)
            self.screen.blit(es, (r.centerx - es.get_width()//2, r.y + 5))
            name_txt = self.font_small.render(data["name"], True, (255, 255, 255))
            self.screen.blit(name_txt, (r.x + 4, r.y + 40))
            cost_color = (180, 255, 180) if can_afford else (255, 120, 120)
            cost_txt = self.font_small.render(f"🪙{data['cost']}", True, cost_color)
            self.screen.blit(cost_txt, (r.x + 4, r.y + 58))

    def _draw_upgrade_panel(self):
        """Draw the upgrade panel for a selected building."""
        bld = self.upgrade_panel_building
        panel_rect = self._upgrade_panel_rect()

        # Dim background
        dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 140))
        self.screen.blit(dim, (0, 0))

        # Panel background with tier color
        tier_data = BUILDING_TIERS[bld.tier]
        panel_color = (
            tier_data["border_color"][0] // 4 + 30,
            tier_data["border_color"][1] // 4 + 20,
            tier_data["border_color"][2] // 4 + 15,
        )
        pygame.draw.rect(self.screen, panel_color, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, tier_data["border_color"], panel_rect, 3, border_radius=10)

        # Close button
        close_rect = pygame.Rect(panel_rect.right - 30, panel_rect.top + 5, 25, 25)
        pygame.draw.rect(self.screen, (150, 60, 60), close_rect, border_radius=4)
        close_txt = self.font.render("X", True, (255, 255, 255))
        self.screen.blit(close_txt, (close_rect.x + 6, close_rect.y + 2))

        # Header
        emoji_surf = self.emoji_cache.get(bld.base_data["emoji"], 50)
        self.screen.blit(emoji_surf, (panel_rect.x + 20, panel_rect.y + 15))
        name_txt = self.font_big.render(bld.name, True, (255, 230, 150))
        self.screen.blit(name_txt, (panel_rect.x + 80, panel_rect.y + 20))
        tier_stars = "⭐" * tier_data["star_count"] if tier_data["star_count"] > 0 else "(no stars)"
        tier_txt = self.font_small.render(f"Tier {bld.tier} {tier_stars}",
                                           True, tier_data["border_color"])
        self.screen.blit(tier_txt, (panel_rect.x + 80, panel_rect.y + 48))

        pygame.draw.line(self.screen, (150, 120, 70),
                         (panel_rect.x + 15, panel_rect.y + 80),
                         (panel_rect.right - 15, panel_rect.y + 80), 2)

        # Current stats
        y = panel_rect.y + 95
        stats = [
            f"❤️ HP: {bld.hp}/{bld.max_hp}",
            f"📦 Capacity: {len(bld.animals)}/{bld.capacity}",
            f"🛡️ Defense: {bld.defense}",
        ]
        for stat in stats:
            stat_txt = self.font.render(stat, True, (220, 220, 220))
            self.screen.blit(stat_txt, (panel_rect.x + 20, y))
            y += 22

        y += 10
        info = bld.get_upgrade_info(self.level)
        if info is None:
            max_txt = self.font_big.render("✨ MAX TIER REACHED! ✨", True, (255, 215, 0))
            self.screen.blit(max_txt, (panel_rect.centerx - max_txt.get_width()//2, y))
        else:
            next_tier_data = BUILDING_TIERS[info["next_tier"]]
            header_txt = self.font_big.render(
                f"⬆️ Upgrade to {next_tier_data['name']} (Tier {info['next_tier']})",
                True, next_tier_data["border_color"])
            self.screen.blit(header_txt, (panel_rect.x + 20, y))
            y += 30

            # Requirements
            lvl_color = (150, 255, 150) if info["meets_level"] else (255, 120, 120)
            lvl_txt = self.font.render(
                f"🌟 Level: {self.level}/{info['lvl_req']} {'✅' if info['meets_level'] else '❌'}",
                True, lvl_color)
            self.screen.blit(lvl_txt, (panel_rect.x + 20, y))
            y += 22

            cost_color = (150, 255, 150) if self.coins >= info["cost"] else (255, 120, 120)
            cost_txt = self.font.render(
                f"🪙 Cost: {self.coins}/{info['cost']} {'✅' if self.coins >= info['cost'] else '❌'}",
                True, cost_color)
            self.screen.blit(cost_txt, (panel_rect.x + 20, y))
            y += 30

            # Benefits
            benefits_txt = self.font.render("Benefits:", True, (255, 230, 150))
            self.screen.blit(benefits_txt, (panel_rect.x + 20, y))
            y += 22

            benefits = []
            if info["cap_bonus"] > 0:
                benefits.append(f"📦 +{info['cap_bonus']} capacity")
            if info["hp_bonus"] > 0:
                benefits.append(f"❤️ +{info['hp_bonus']} max HP")
            if info["def_bonus"] > 0:
                benefits.append(f"🛡️ +{info['def_bonus']} defense")
            if info["prod_mult"] > 1.0:
                benefits.append(f"⚡ {int((info['prod_mult']-1)*100)}% faster production")
            if next_tier_data.get("master"):
                benefits.append("👑 Master-tier visual upgrade!")
            if next_tier_data["size"] > BUILDING_TIERS[bld.tier]["size"]:
                benefits.append("📐 Larger building size")

            for benefit in benefits:
                b_txt = self.font_small.render(benefit, True, (180, 255, 180))
                self.screen.blit(b_txt, (panel_rect.x + 30, y))
                y += 18

            # Upgrade button
            btn_rect = pygame.Rect(panel_rect.centerx - 80, panel_rect.bottom - 60, 160, 40)
            can_upgrade = info["meets_level"] and self.coins >= info["cost"]
            btn_color = (80, 180, 80) if can_upgrade else (80, 80, 80)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, (255, 220, 80) if can_upgrade else (120, 120, 120),
                             btn_rect, 2, border_radius=6)
            btn_txt = self.font.render("⬆️ UPGRADE", True, (255, 255, 255))
            self.screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width()//2,
                                        btn_rect.centery - btn_txt.get_height()//2))

    def _draw_ui(self):
        # Top bar
        pygame.draw.rect(self.screen,(50,35,20),(0,0,SCREEN_W,TOP_BAR))
        pygame.draw.line(self.screen,(30,20,10),(0,TOP_BAR),(SCREEN_W,TOP_BAR),2)
        self.screen.blit(self.emoji_cache.get("🌟",22),(10,18))
        self.screen.blit(self.text_cache.get(f"Lv{self.level}",(255,230,150),self.font_big),(36,20))
        xn = self.xp_for_next_level()
        pygame.draw.rect(self.screen,(30,30,30),(90,22,100,14),border_radius=4)
        pygame.draw.rect(self.screen,(100,200,120),(90,22,int(100*self.xp/xn),14),border_radius=4)
        self.screen.blit(self.emoji_cache.get("🪙",22),(210,18))
        self.screen.blit(self.text_cache.get(f"{self.coins}",(255,220,80),self.font_big),(236,20))
        se = {"spring":"🌸","summer":"☀️","fall":"🍂","winter":"❄️"}
        self.screen.blit(self.emoji_cache.get(se[self.season],22),(320,18))
        self.screen.blit(self.text_cache.get(f"Day {self.day}",(220,220,220),self.font),(346,22))

        if self.siege_active:
            siege_txt = self.text_cache.get(f"💀 SIEGE W{self.siege_wave} ({len(self.siege_monsters)})",
                                             (255, 100, 100), self.font)
            self.screen.blit(siege_txt, (420, 22))
        elif self.siege_warning > 0:
            warn_txt = self.text_cache.get(f"⚠️ Siege in {int(self.siege_warning)}s",
                                            (255, 200, 100), self.font)
            self.screen.blit(warn_txt, (420, 22))
        else:
            time_to = max(0, int(self.next_siege_time - time.time()))
            next_txt = self.text_cache.get(f"🛡️ Next siege: {time_to}s",
                                            (200, 200, 200), self.font_small)
            self.screen.blit(next_txt, (420, 24))

        # Building tier stats
        tier_counts = {1:0, 2:0, 3:0, 4:0}
        for b in self.buildings:
            tier_counts[b.tier] = tier_counts.get(b.tier, 0) + 1
        tier_str = f"🏠 T1:{tier_counts[1]} T2:{tier_counts[2]} T3:{tier_counts[3]} T4:{tier_counts[4]}"
        self.screen.blit(self.text_cache.get(tier_str, (200,220,255), self.font_small), (600, 24))
        self.screen.blit(self.text_cache.get(f"🌱{self.world_seed}",(180,220,180),self.font_small),(820,24))

        # Save/Load
        save_r = pygame.Rect(SCREEN_W-130,15,50,28); load_r = pygame.Rect(SCREEN_W-70,15,50,28)
        pygame.draw.rect(self.screen,(80,120,80),save_r,border_radius=4)
        pygame.draw.rect(self.screen,(120,80,80),load_r,border_radius=4)
        self.screen.blit(self.emoji_cache.get("💾",18),(save_r.x+4,save_r.y+4))
        self.screen.blit(self.emoji_cache.get("📂",18),(load_r.x+4,load_r.y+4))
        self.screen.blit(self.text_cache.get("Save",(255,255,255),self.font_small),(save_r.x+24,save_r.y+6))
        self.screen.blit(self.text_cache.get("Load",(255,255,255),self.font_small),(load_r.x+24,load_r.y+6))
        self.save_rect=save_r; self.load_rect=load_r

        # Tool panel
        pygame.draw.rect(self.screen,(60,40,25),(0,TOP_BAR,LEFT_PANEL,SCREEN_H-TOP_BAR-BOTTOM_BAR))
        pygame.draw.line(self.screen,(30,20,10),(LEFT_PANEL,TOP_BAR),(LEFT_PANEL,SCREEN_H-BOTTOM_BAR),2)
        self.screen.blit(self.text_cache.get("Tools",(255,230,150),self.font),(10,TOP_BAR+2))
        te = {"hoe":"⛏️","water":"💧","hand":"✋","fertilizer":"✨","greenhouse":"🏠",
              "net":"🥅","sword":"⚔️","build":"🏗️","repair":"🔧","upgrade":"⬆️"}
        for t,r in self.tool_rects():
            sel = t==self.tool or (t=="build" and self.build_mode)
            pygame.draw.rect(self.screen,(100,160,100) if sel else (80,80,80),r,border_radius=6)
            pygame.draw.rect(self.screen,(255,255,255) if sel else (180,180,180),r,2,border_radius=6)
            es = self.emoji_cache.get(te[t],16)
            self.screen.blit(es,(r.centerx-es.get_width()//2,r.centery-es.get_height()//2-2))
            lb = self.text_cache.get(t.capitalize(),(255,255,255),self.font_small)
            self.screen.blit(lb,(r.x+(r.width-lb.get_width())//2,r.bottom-10))

        # Seed panel
        pygame.draw.rect(self.screen,(50,35,20),(0,SCREEN_H-BOTTOM_BAR,SCREEN_W,BOTTOM_BAR))
        pygame.draw.line(self.screen,(30,20,10),(0,SCREEN_H-BOTTOM_BAR),(SCREEN_W,SCREEN_H-BOTTOM_BAR),2)
        bi = BIOME_INFO[self.selected_biome]
        self.screen.blit(self.text_cache.get(f"{bi['emoji']} {bi['name']} Seeds",
                                              (255,230,150),self.font),(LEFT_PANEL+15,SCREEN_H-BOTTOM_BAR+5))
        for b,r in self.biome_rects():
            info = BIOME_INFO[b]; sel = b==self.selected_biome; locked = info["unlock"]>self.level
            pygame.draw.rect(self.screen,(80,140,80) if sel else (60,60,60) if locked else (100,100,100),r,border_radius=4)
            pygame.draw.rect(self.screen,(255,220,80) if sel else (180,180,180),r,2,border_radius=4)
            es = self.emoji_cache.get(info["emoji"],18)
            self.screen.blit(es,(r.x+4,r.y+6))
            if locked:
                self.screen.blit(self.text_cache.get(f"Lv{info['unlock']}",(255,120,120),self.font_small),(r.x+26,r.y+9))
            else:
                self.screen.blit(self.text_cache.get(info["name"][:5],(255,255,255),self.font_small),(r.x+26,r.y+9))
        for name,r in self.seed_rects():
            cd = self.plant_gen.plants.get(name)
            if not cd: continue
            sel = name==self.selected_seed
            pygame.draw.rect(self.screen,(80,140,80) if sel else (100,100,100),r,border_radius=6)
            pygame.draw.rect(self.screen,(255,220,80) if sel else (180,180,180),r,2,border_radius=6)
            es = self.emoji_cache.get(cd["emojis"][2],26)
            self.screen.blit(es,(r.x+r.width//2-es.get_width()//2,r.y+4))
            self.screen.blit(self.text_cache.get(cd["display"][:10],(255,255,255),self.font_small),(r.x+4,r.y+36))
            self.screen.blit(self.text_cache.get(f"🪙{cd['cost']}",(220,220,220),self.font_small),(r.x+4,r.y+52))
            self.screen.blit(self.text_cache.get(f"→{cd['sell']}",(180,255,180),self.font_small),(r.x+4,r.y+66))
            self.screen.blit(self.text_cache.get(f"⏱️{cd['time']}s",(180,220,255),self.font_small),(r.x+4,r.y+80))

        # Biome info
        info = BIOME_INFO[self.hover_biome]
        pr = pygame.Rect(self.viewport.left+10,self.viewport.top+10,240,60)
        pygame.draw.rect(self.screen,(30,30,30,200),pr,border_radius=6)
        pygame.draw.rect(self.screen,(200,200,200),pr,1,border_radius=6)
        self.screen.blit(self.emoji_cache.get(info["emoji"],24),(pr.x+8,pr.y+8))
        self.screen.blit(self.text_cache.get(info["name"],(255,230,150),self.font_big),(pr.x+40,pr.y+8))
        mod = info["grow_mod"]
        mt = f"⚡{int((1-mod)*100)}% faster" if mod<1 else f"🐢{int((mod-1)*100)}% slower" if mod>1 else "✅ Normal"
        mc = (150,255,150) if mod<1 else (255,180,150) if mod>1 else (220,220,220)
        self.screen.blit(self.text_cache.get(mt,mc,self.font_small),(pr.x+10,pr.y+38))

        # Message
        if time.time()-self.msg_time<4:
            msg = self.font.render(self.message,True,(255,255,220))
            bg = msg.get_rect()
            bg.center = (LEFT_PANEL+(SCREEN_W-LEFT_PANEL)//2, SCREEN_H-BOTTOM_BAR+135)
            pygame.draw.rect(self.screen,(0,0,0),bg.inflate(16,8),border_radius=6)
            self.screen.blit(msg,bg)

    # --- Save/Load ---
    def save(self):
        data = {
            "world_seed":self.world_seed,"coins":self.coins,"xp":self.xp,"level":self.level,
            "day":self.day,"season":self.season,"selected_seed":self.selected_seed,
            "selected_biome":self.selected_biome,"total_harvests":self.total_harvests,
            "tamed_creatures":self.tamed_creatures,"inventory":self.inventory,
            "siege_wave":self.siege_wave,"next_siege_time":self.next_siege_time,
            "camera":{"x":self.camera.tx,"y":self.camera.ty,"zoom":self.camera.tz},
            "plots":[{"state":p.state,"crop":p.crop,"crop_biome":p.crop_biome,
                "planted_at":p.planted_at,"grow_time":p.grow_time,"base_grow_time":p.base_grow_time,
                "water":p.water,"wilt_timer":p.wilt_timer,"fertilized":p.fertilized,
                "pest":p.pest,"greenhouse":p.greenhouse} for p in self.plots],
            "buildings":[{"type":b.type,"x":b.x,"y":b.y,"hp":b.hp,"tier":b.tier,
                          "animals":b.animals} for b in self.buildings],
        }
        try:
            with open(SAVE_FILE,"w") as f: json.dump(data,f)
            self.set_message("💾 Saved!")
        except Exception as e: self.set_message(f"Save failed: {e}")

    def load(self):
        if not os.path.exists(SAVE_FILE): self.set_message("📂 No save"); return
        try:
            with open(SAVE_FILE) as f: data=json.load(f)
            ss = data.get("world_seed")
            if ss!=self.world_seed: self.world_seed=ss; self.world=WorldGenerator(self.world_seed); self.npcs=[]; self._create_npcs()
            self.coins=data["coins"]; self.xp=data["xp"]; self.level=data["level"]
            self.day=data["day"]; self.season=data.get("season","spring")
            self.selected_seed=data.get("selected_seed","wheat")
            self.selected_biome=data.get("selected_biome",Biome.PLAINS)
            self.total_harvests=data.get("total_harvests",0)
            self.tamed_creatures=data.get("tamed_creatures",[])
            self.inventory=data.get("inventory",{})
            self.siege_wave=data.get("siege_wave",0)
            self.next_siege_time=data.get("next_siege_time",time.time()+120)
            cam=data.get("camera",{})
            self.camera.tx=cam.get("x",self.camera.tx); self.camera.ty=cam.get("y",self.camera.ty)
            self.camera.tz=cam.get("zoom",1.0)
            self.camera.x,self.camera.y,self.camera.zoom=self.camera.tx,self.camera.ty,self.camera.tz
            for p,pd in zip(self.plots,data["plots"]):
                p.state=pd["state"]; p.crop=pd["crop"]; p.crop_biome=pd.get("crop_biome",p.biome)
                p.planted_at=pd["planted_at"]; p.grow_time=pd["grow_time"]
                p.base_grow_time=pd.get("base_grow_time",p.grow_time)
                p.water=pd["water"]; p.wilt_timer=pd["wilt_timer"]
                p.fertilized=pd.get("fertilized",False); p.pest=pd.get("pest",False)
                p.greenhouse=pd.get("greenhouse",False)
            self.buildings = []
            for bd in data.get("buildings", []):
                bld = Building(bd["type"], bd["x"], bd["y"])
                bld.tier = bd.get("tier", 1)
                bld._recalc_stats()
                bld.hp = bd["hp"]
                bld.animals = bd.get("animals", [])
                self.buildings.append(bld)
            self.day_start=time.time(); self.text_cache.invalidate(); self.set_message("📂 Loaded!")
        except Exception as e: self.set_message(f"Load failed: {e}")

    def _try_load(self):
        if os.path.exists(SAVE_FILE): self.load()

    # --- Main loop ---
    def run(self):
        running=True; last=time.time()
        while running:
            now=time.time(); dt=min(now-last,0.1); last=now
            for event in pygame.event.get():
                if event.type==pygame.QUIT: running=False
                elif event.type==pygame.MOUSEBUTTONDOWN: self.handle_click(event.pos,event.button)
                elif event.type==pygame.MOUSEBUTTONUP:
                    if event.button==2: self.dragging=False
                elif event.type==pygame.MOUSEMOTION:
                    if self.dragging and self.drag_start:
                        self.camera.tx = self.drag_cam_start[0]-(event.pos[0]-self.drag_start[0])/self.camera.zoom
                        self.camera.ty = self.drag_cam_start[1]-(event.pos[1]-self.drag_start[1])/self.camera.zoom
                        self.camera._clamp()
                elif event.type==pygame.MOUSEWHEEL:
                    if self.viewport.collidepoint(pygame.mouse.get_pos()) and not self.build_mode and not self.upgrade_panel_building:
                        self.camera.zoom_at(*pygame.mouse.get_pos(), event.y*0.15)
                elif event.type==pygame.KEYDOWN:
                    k=event.key; m=pygame.key.get_mods()
                    if k==pygame.K_ESCAPE:
                        if self.upgrade_panel_building: self.upgrade_panel_building=None
                        elif self.build_mode: self.build_mode=False; self.selected_building=None; self.set_message("Build mode OFF")
                        else: running=False
                    elif k==pygame.K_b:
                        self.build_mode = not self.build_mode
                        self.set_message("🏗️ Build mode ON" if self.build_mode else "Build mode OFF")
                    elif k==pygame.K_u:
                        self.tool = "upgrade"
                        self.set_message("🔼 Click a building to upgrade!")
                    elif k==pygame.K_s and m&pygame.KMOD_CTRL: self.save()
                    elif k==pygame.K_l and m&pygame.KMOD_CTRL: self.load()
                    elif k==pygame.K_1: self.tool="hoe"; self.build_mode=False
                    elif k==pygame.K_2: self.tool="water"; self.build_mode=False
                    elif k==pygame.K_3: self.tool="hand"; self.build_mode=False
                    elif k==pygame.K_4: self.tool="fertilizer"; self.build_mode=False
                    elif k==pygame.K_5: self.tool="greenhouse"; self.build_mode=False
                    elif k==pygame.K_6: self.tool="net"; self.build_mode=False
                    elif k==pygame.K_7: self.tool="sword"; self.build_mode=False
                    elif k==pygame.K_8: self.tool="repair"; self.build_mode=False
                    elif k==pygame.K_9: self.tool="upgrade"; self.build_mode=False
                    elif k==pygame.K_HOME:
                        self.camera.center_on((FARM_X+FARM_COLS/2)*TILE,(FARM_Y+FARM_ROWS/2)*TILE)
                        self.camera.tz=1.0
                    elif k==pygame.K_f:
                        self.camera.tz=min(self.viewport.width/self.world_w,self.viewport.height/self.world_h)*0.95
                        self.camera.center_on(self.world_w/2,self.world_h/2)
            self.update(dt); self.draw(); pygame.display.flip(); self.clock.tick(FPS)
        self.save(); pygame.quit(); sys.exit()

# =============================================================================
# §13. ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    Game().run()