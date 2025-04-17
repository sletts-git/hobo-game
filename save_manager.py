# save_manager.py
import json
import os

SAVE_PATH = "assets/data/save_data.json"

DEFAULT_DATA = {
    "selected_character": "Wizard",
    "unlocked_characters": ["Wizard"],
    "unlocked_attacks": ["basic"],
    "volume": {
        "sfx": 1.0,
        "music": 1.0
    }
}

def load_save_data():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    else:
        return DEFAULT_DATA.copy()

def save_data(data):
    with open(SAVE_PATH, "w") as f:
        json.dump(data, f, indent=4)
