# structure_loader.py
# Responsible for loading and placing prefab structures in the world

import json
import os

DATA_DIR = os.path.join("assets", "data")


def load_prefab(name):
    """
    Loads a prefab structure by name from assets/data/{name}.json
    """
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prefab not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def place_prefab(prefab_data, base_x, base_y, placed_assets):
    """
    Places a prefab's assets into the world at a given base position.

    :param prefab_data: The JSON dict loaded from a prefab file
    :param base_x: X coordinate to place the prefab
    :param base_y: Y coordinate to place the prefab
    :param placed_assets: List where the final placed object dicts will be appended
    """
    for obj in prefab_data["objects"]:
        placed_obj = {
            "filename": obj["filename"],
            "x": base_x + obj["x"],
            "y": base_y + obj["y"],
            "scale_x": obj.get("scale_x", 1.0),
            "scale_y": obj.get("scale_y", 1.0),
            "flipped": obj.get("flipped", False),
            "has_collision": obj.get("has_collision", False),
            "has_door": obj.get("has_door", False),
            "interior_id": obj.get("interior_id")
        }
        placed_assets.append(placed_obj)


def get_prefab_names():
    """
    Returns a list of all prefab structure names (no .json extension)
    """
    return [f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json") and f != "town_layout.json"]
