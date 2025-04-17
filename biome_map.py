# biome_map.py
# Handles biome generation, tile selection, and environment spawning (structures disabled)
import os
import json
import random
import pygame
from structure_loader import load_prefab, place_prefab

ROCK_HITBOX_PATH = os.path.join("assets", "data", "rock_hitboxes.json")
TREE_HITBOX_PATH = os.path.join("assets", "data", "tree_hitboxes.json")

if os.path.exists(ROCK_HITBOX_PATH):
    with open(ROCK_HITBOX_PATH, "r") as f:
        ROCK_HITBOX_CONFIGS = json.load(f)
else:
    ROCK_HITBOX_CONFIGS = {}

if os.path.exists(TREE_HITBOX_PATH):
    with open(TREE_HITBOX_PATH, "r") as f:
        TREE_HITBOX_CONFIGS = json.load(f)
else:
    TREE_HITBOX_CONFIGS = {}

# === Biome Settings ===
BIOME_WEIGHTS = [
    ("woodland", 55),
    ("grassland", 30),
    ("swamp", 15)
]

BIOME_TILE_VARIANTS = {
    "woodland": ["woodland1.png", "woodland2.png", "woodland3.png"],
    "grassland": ["grassland1.png", "grassland2.png", "grassland3.png"],
    "swamp": ["swamp1.png", "swamp2.png", "swamp3.png"]
}

BIOME_SCALE = 20
VARIANT_SCALE = 7
STRUCTURE_CHANCE = 0.01
TILE_SIZE = 150

# === Internal State ===
_loaded_prefabs = {}
_structure_tiles = set()
_structure_locations = set()
_tree_colliders, _rock_colliders = [], []

def coord_seed(x, y, salt=0):
    return (x * 3042161) ^ (y * 506683) ^ salt

def calculate_biome_asset_hitbox(x, y, size, cfg):
    w_scale = cfg["collision_w_scale"]
    h_scale = cfg["collision_h_scale"]
    offset_up = cfg["collision_offset_y"]
    offset_right = cfg["collision_offset_x"]

    collision_width = int(size * w_scale)
    collision_height = int(size * h_scale)
    hitbox_x = x + int(size * offset_right) + size / 2
    hitbox_y = y - int(collision_height * (1 + offset_up)) + size

    return pygame.Rect(hitbox_x, hitbox_y, collision_width, collision_height)

def get_biome_at(tx, ty):
    rx = tx // BIOME_SCALE
    ry = ty // BIOME_SCALE
    seed = coord_seed(rx, ry, salt=1)
    rng = random.Random(seed)
    r = rng.uniform(0, 100)
    cumulative = 0
    for biome, weight in BIOME_WEIGHTS:
        cumulative += weight
        if r < cumulative:
            return biome
    return BIOME_WEIGHTS[-1][0]


def get_tile_for_biome(tx, ty, biome, load_image_fn):
    rx = tx // VARIANT_SCALE
    ry = ty // VARIANT_SCALE
    seed = coord_seed(rx, ry, salt=1)
    rng = random.Random(seed)
    variant_list = BIOME_TILE_VARIANTS[biome]
    index = rng.randint(0, len(variant_list) - 1)
    tile_name = variant_list[index]
    return load_image_fn(tile_name)


# Structure generation (currently disabled)
# def try_place_structure(tx, ty, biome, placed_assets):
#     seed = hash(("structure", tx, ty))
#     rng = random.Random(seed)
#     if rng.random() < STRUCTURE_CHANCE:
#         if biome == "swamp":
#             prefab_name = "goblin_camp"
#         elif biome == "woodland":
#             prefab_name = "town_layout"
#         else:
#             return
#         if prefab_name not in _loaded_prefabs:
#             try:
#                 _loaded_prefabs[prefab_name] = load_prefab(prefab_name)
#             except FileNotFoundError:
#                 return
#         base_x = tx * TILE_SIZE
#         base_y = ty * TILE_SIZE
#         place_prefab(_loaded_prefabs[prefab_name], base_x, base_y, placed_assets)
#         for dx in range(-5, 6):
#             for dy in range(-5, 6):
#                 _structure_tiles.add((tx + dx, ty + dy))


def spawn_natural_assets(tx, ty, biome, placed_assets):
    if (tx, ty) in _structure_tiles:
        return

    rng = random.Random(coord_seed(tx, ty, salt=3))
    world_x = tx * TILE_SIZE
    world_y = ty * TILE_SIZE

    # Trees
    tree_spawn = False
    if biome == "woodland" and rng.random() < 0.222:
        tree_spawn = True
        tree = rng.choice(["tree_basic_green1.png", "tree_basic_green2.png", "tree_basic_green3.png"])
    elif biome == "swamp" and rng.random() < 0.133:
        tree_spawn = True
        tree = "tree_dead.png"

    if tree_spawn:
        scale = 0.9 + 0.2 * random.random()
        size = int(scale * 140)
        jitter_x = rng.randint(-TILE_SIZE // 4, TILE_SIZE // 4)
        jitter_y = rng.randint(-TILE_SIZE // 4, TILE_SIZE // 4)
        placed_assets.append({
            "filename": tree,
            "x": world_x + jitter_x,
            "y": world_y + jitter_y,
            "scale_x": scale,
            "scale_y": scale,
            "has_collision": True
        })
        if tree in TREE_HITBOX_CONFIGS:
            cfg = TREE_HITBOX_CONFIGS[tree]
            rect = calculate_biome_asset_hitbox(world_x + jitter_x, world_y + jitter_y, size, cfg)
            _tree_colliders.append(rect)

        # tree spawns grass
        for _ in range(rng.randint(3, 4)):
            g = rng.choice(["grass_green1.png", "grass_green2.png", "grass_green3.png"])
            placed_assets.append({
                "filename": g,
                "x": world_x + jitter_y,
                "y": world_y + jitter_x,
                "scale_x": 0.3,
                "scale_y": 0.3
            })

    # Shrubs
    if biome in ["woodland", "grassland"] and rng.random() < (0.02 if biome == "grassland" else 0.33):
        bush = rng.choice(["bush_green1.png", "bush_green2.png", "bush_green_red_berry1.png"])
        scale = 0.25 + rng.random() * 0.15
        placed_assets.append({
            "filename": bush,
            "x": world_x + rng.randint(-10, 10),
            "y": world_y + rng.randint(-10, 10),
            "scale_x": scale,
            "scale_y": scale
        })

    # Rocks
    if rng.random() < 0.03:
        rock = rng.choice(["rock_small1.png", "rock_small2.png", "rock_medium1.png", "rock_medium2.png"])
        jitter_x = rng.randint(-TILE_SIZE // 2, TILE_SIZE // 2)
        jitter_y = rng.randint(-TILE_SIZE // 2, TILE_SIZE // 2)
        placed_assets.append({
            "filename": rock,
            "x": world_x + jitter_x,
            "y": world_y + jitter_y,
            "scale_x": 0.35,
            "scale_y": 0.35,
            "has_collision": True
        })
        if rock in ROCK_HITBOX_CONFIGS:
            base_size = 140  # consistent with visualizer
            scale = 0.35
            size = int(base_size * scale)
            cfg = ROCK_HITBOX_CONFIGS[rock]
            rect = calculate_biome_asset_hitbox(world_x + jitter_x, world_y + jitter_y, size, cfg)
            _rock_colliders.append(rect)

    # Grass
    if rng.random() < (0.333 if biome == "woodland" else 0.666):
        g = rng.choice(["grass_green1.png", "grass_green2.png", "grass_green3.png"])
        placed_assets.append({
            "filename": g,
            "x": world_x + rng.randint(-60, 60),
            "y": world_y + rng.randint(-60, 60),
            "scale_x": 0.25,
            "scale_y": 0.25
        })


def draw_ground(screen, camera_x, camera_y, tile_size, load_image_fn, placed_assets, specific_tile=None):
    if specific_tile:
        tx, ty = specific_tile
        biome = get_biome_at(tx, ty)
        # try_place_structure(tx, ty, biome, placed_assets)  # Disabled
        spawn_natural_assets(tx, ty, biome, placed_assets)
        return

    screen_width, screen_height = screen.get_size()
    start_x = camera_x // tile_size - 2
    start_y = camera_y // tile_size - 2
    end_x = (camera_x + screen_width) // tile_size + 3
    end_y = (camera_y + screen_height) // tile_size + 3

    for tx in range(start_x, end_x):
        for ty in range(start_y, end_y):
            biome = get_biome_at(tx, ty)
            tile_img = get_tile_for_biome(tx, ty, biome, load_image_fn)
            offset_x = (tx - ty) * (TILE_SIZE // 2)
            offset_y = (tx + ty) * (TILE_SIZE // 4)
            screen.blit(tile_img, (offset_x - camera_x, offset_y - camera_y))
            # try_place_structure(tx, ty, biome, placed_assets)  # Disabled
            spawn_natural_assets(tx, ty, biome, placed_assets)

def get_biome_map_colliders():
    return _tree_colliders, _rock_colliders
