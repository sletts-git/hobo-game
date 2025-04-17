# world.py
import os
import math
import pygame
import json
from biome_map import draw_ground, get_biome_at, get_tile_for_biome

TILE_SIZE = 150
CHUNK_SIZE = 5  # in tiles

# Asset loader
_asset_cache = {}

_last_active_chunk = None

OBJECT_ASSET_DIR = os.path.join("assets", "world")
TILE_ASSET_DIR = os.path.join("assets", "world", "tiles", "world")

def load_image(name):
    if name not in _asset_cache:
        if any(name.startswith(prefix) for prefix in ["grassland", "woodland", "swamp"]):
            path = os.path.join(TILE_ASSET_DIR, name)
            square_img = pygame.image.load(path).convert_alpha()
            rotated_img = pygame.transform.rotate(square_img, 45)
            _asset_cache[name] = rotated_img
        else:
            path = os.path.join(OBJECT_ASSET_DIR, name)
            _asset_cache[name] = pygame.image.load(path).convert_alpha()
    return _asset_cache[name]

# Global collider lists for collision checks
_tree_colliders = []
_rock_colliders = []

# Load hitbox configuration from town editor
HITBOX_CONFIG_PATH = os.path.join("assets", "data", "building_hitboxes.json")
if os.path.exists(HITBOX_CONFIG_PATH):
    with open(HITBOX_CONFIG_PATH, "r") as f:
        hitbox_config = json.load(f)
else:
    hitbox_config = {}

# Chunk system
_loaded_chunks = {}  # key = (chunk_x, chunk_y), value = (tiles, objects)

def calculate_hitbox(obj):
    cfg = hitbox_config.get(obj["filename"], {})
    scale = obj.get("scale_x", 1.0)
    image = load_image(obj["filename"])
    width = int(image.get_width() * scale)
    height = int(image.get_height() * obj.get("scale_y", 1.0))
    x, y = obj["x"], obj["y"]

    anchor_x = x + width // 2
    anchor_y = y + height

    w = int(width * cfg.get("collision_w_scale", 0.2))
    h = int(height * cfg.get("collision_h_scale", 0.2))
    ox = cfg.get("collision_offset_right_scale", 0.1)
    oy = cfg.get("collision_offset_up_scale", 0.1)

    if obj.get("flipped", False):
        ox = 1.0 - ox

    hx = anchor_x + int(width * (ox - 0.5))
    hy = anchor_y - int(h * (1 + oy))
    return pygame.Rect(hx, hy, w, h)

def generate_chunk(cx, cy):
    tile_data = []
    obj_data = []

    for dx in range(CHUNK_SIZE):
        for dy in range(CHUNK_SIZE):
            tx = cx * CHUNK_SIZE + dx
            ty = cy * CHUNK_SIZE + dy
            biome = get_biome_at(tx, ty)
            tile_img = get_tile_for_biome(tx, ty, biome, load_image)
            tile_data.append((tile_img, tx * TILE_SIZE, ty * TILE_SIZE))

            draw_ground(screen=None, camera_x=0, camera_y=0, tile_size=TILE_SIZE,
                        load_image_fn=load_image, placed_assets=obj_data, specific_tile=(tx, ty))

    _loaded_chunks[(cx, cy)] = (tile_data, obj_data)
    return tile_data, obj_data

def _update_loaded_chunks(center_chunk):
    cx, cy = center_chunk
    print(cx, cy)

    target_chunks = {
        (cx + dx, cy + dy)
        for dx in range( -2, 3)
        for dy in range( -2, 3)
    }

    for chunk in target_chunks:
        if chunk not in _loaded_chunks:
            generate_chunk(*chunk)

    for chunk in list(_loaded_chunks):
        if chunk not in target_chunks:
            del _loaded_chunks[chunk]


def get_render_data(camera_x, camera_y, player_x=None, player_y=None, screen_width=1260, screen_height=700):
    global _last_active_chunk

    tile_layers = []
    render_objects = []

    # Snap to top-left of the current chunk
    anchor_x = camera_x
    anchor_y = camera_y

    center_chunk = (
        int(anchor_x // (CHUNK_SIZE * TILE_SIZE)),
        int(anchor_y // (CHUNK_SIZE * TILE_SIZE))
    )
    _last_active_chunk = center_chunk

    _update_loaded_chunks(center_chunk)

    for (cx, cy), (tiles, objects) in _loaded_chunks.items():
        tile_layers.extend(tiles)
        render_objects.extend(objects)

    return tile_layers, render_objects, center_chunk

def get_tree_colliders():
    return _tree_colliders

def get_rock_colliders():
    return _rock_colliders
